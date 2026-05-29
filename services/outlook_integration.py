"""
Outlook Integration Service
Sends meeting summaries via email and creates calendar events using Microsoft Graph API
"""
import logging
import os
import base64
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OutlookIntegration:
    """
    Integrates with Microsoft Outlook via Graph API
    
    Features:
    - Send formatted meeting summary emails to participants
    - Create calendar events for action item deadlines
    - OAuth2 authentication with Microsoft Graph API
    """
    
    # Microsoft Graph API endpoints
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    AUTH_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """
        Initialize Outlook integration with Microsoft Graph API credentials
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
            
        Raises:
            ValueError: If required credentials are missing
        """
        # Load from environment if not provided
        self.client_id = client_id or os.getenv('OUTLOOK_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('OUTLOOK_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('OUTLOOK_TENANT_ID')
        
        # Validate credentials
        if not self.client_id:
            raise ValueError("OUTLOOK_CLIENT_ID is required")
        if not self.client_secret:
            raise ValueError("OUTLOOK_CLIENT_SECRET is required")
        if not self.tenant_id:
            raise ValueError("OUTLOOK_TENANT_ID is required")
        
        # Access token (will be obtained on first use)
        self.access_token = None
        
        logger.info("OutlookIntegration initialized successfully")
    
    def _authenticate(self) -> str:
        """
        Authenticate with Microsoft Graph API using OAuth2 client credentials flow
        
        Returns:
            Access token
            
        Raises:
            Exception: If authentication fails
        """
        try:
            auth_url = self.AUTH_URL.format(tenant_id=self.tenant_id)
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(auth_url, data=data, timeout=30)
            
            if response.status_code == 401:
                raise Exception("Authentication failed. Check your client credentials.")
            elif response.status_code == 400:
                error_detail = response.json().get('error_description', 'Unknown error')
                raise Exception(f"Authentication error: {error_detail}")
            
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            logger.info("Successfully authenticated with Microsoft Graph API")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Authentication request failed: {str(e)}")
    
    def send_summary_email(
        self,
        recipients: List[str],
        meeting_title: str,
        summary_data: Dict[str, Any],
        attachment_path: Optional[str] = None,
        sender_email: Optional[str] = None
    ) -> bool:
        """
        Send meeting summary email to participants
        
        Args:
            recipients: List of recipient email addresses
            meeting_title: Title of the meeting
            summary_data: Dictionary containing summary, decisions, action items, etc.
            attachment_path: Optional path to PDF report attachment
            sender_email: Email address to send from (must have permissions)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not recipients:
            logger.warning("No recipients provided for email")
            return False
        
        try:
            # Ensure we have an access token
            if not self.access_token:
                self._authenticate()
            
            # Format email body as HTML
            html_body = self._format_summary_html(meeting_title, summary_data)
            
            # Build email message
            message = {
                'subject': f"Meeting Summary & Action Items - {meeting_title}",
                'body': {
                    'contentType': 'HTML',
                    'content': html_body
                },
                'toRecipients': [
                    {'emailAddress': {'address': email}} for email in recipients
                ]
            }
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                filename = os.path.basename(attachment_path)
                message['attachments'] = [{
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': filename,
                    'contentBytes': file_content
                }]
            
            # Send email
            if sender_email:
                # Send on behalf of specific user
                url = f"{self.GRAPH_API_BASE}/users/{sender_email}/sendMail"
            else:
                # Send as application (requires Mail.Send permission)
                url = f"{self.GRAPH_API_BASE}/me/sendMail"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {'message': message}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 401:
                # Token expired, re-authenticate and retry
                self._authenticate()
                headers['Authorization'] = f'Bearer {self.access_token}'
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            
            logger.info(f"Successfully sent summary email to {len(recipients)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False
    
    def create_deadline_events(
        self,
        action_items: List[Dict[str, Any]],
        calendar_owner: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create calendar events for action item deadlines
        
        Args:
            action_items: List of action item dictionaries
            calendar_owner: Email of calendar owner (if not provided, uses app calendar)
            
        Returns:
            Dictionary with events_created (list of event IDs) and failed_events (list of errors)
        """
        if not action_items:
            logger.warning("No action items provided")
            return {'events_created': [], 'failed_events': []}
        
        try:
            # Ensure we have an access token
            if not self.access_token:
                self._authenticate()
            
            events_created = []
            failed_events = []
            
            for item in action_items:
                try:
                    # Skip items without deadlines
                    deadline = item.get('deadline')
                    if not deadline or deadline == 'No deadline':
                        continue
                    
                    # Create event
                    event_id = self._create_single_event(item, calendar_owner)
                    if event_id:
                        events_created.append({
                            'event_id': event_id,
                            'task': item.get('action') or item.get('task', 'Unknown'),
                            'deadline': deadline
                        })
                    
                except Exception as e:
                    logger.error(f"Failed to create event for action item: {str(e)}")
                    failed_events.append({
                        'task': item.get('action') or item.get('task', 'Unknown'),
                        'error': str(e)
                    })
            
            logger.info(f"Created {len(events_created)} calendar events, {len(failed_events)} failed")
            
            return {
                'events_created': events_created,
                'failed_events': failed_events
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar events: {str(e)}", exc_info=True)
            return {'events_created': [], 'failed_events': [{'error': str(e)}]}
    
    def _create_single_event(
        self,
        action_item: Dict[str, Any],
        calendar_owner: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a single calendar event for an action item deadline
        
        Args:
            action_item: Action item dictionary
            calendar_owner: Email of calendar owner
            
        Returns:
            Event ID if successful, None otherwise
        """
        task = action_item.get('action') or action_item.get('task', 'Untitled Task')
        owner = action_item.get('owner', 'Unassigned')
        deadline = action_item.get('deadline')
        priority = action_item.get('priority', 'medium')
        
        # Parse deadline date
        try:
            if 'T' in deadline:
                deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
        except (ValueError, AttributeError):
            logger.warning(f"Invalid deadline format: {deadline}")
            return None
        
        # Set event time to 9:00 AM on deadline date
        event_start = deadline_date.replace(hour=9, minute=0, second=0, microsecond=0)
        event_end = event_start + timedelta(hours=1)
        
        # Build event description
        description = f"Task: {task}\n"
        description += f"Owner: {owner}\n"
        description += f"Priority: {priority.capitalize()}\n"
        description += f"Deadline: {deadline}\n"
        description += f"\nThis is an automated reminder for the action item deadline."
        
        # Build event data
        event_data = {
            'subject': f"Deadline: {task}",
            'body': {
                'contentType': 'Text',
                'content': description
            },
            'start': {
                'dateTime': event_start.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': event_end.isoformat(),
                'timeZone': 'UTC'
            },
            'reminderMinutesBeforeStart': 1440,  # 24 hours
            'isReminderOn': True
        }
        
        # Add attendee if owner is specified and not "Unassigned"
        if owner and owner.lower() != 'unassigned':
            # Try to extract email if owner is in "Name <email>" format
            if '<' in owner and '>' in owner:
                email = owner.split('<')[1].split('>')[0]
            else:
                # Assume owner is email or convert name to email format
                email = owner.lower().replace(' ', '.') + '@example.com'
            
            event_data['attendees'] = [{
                'emailAddress': {
                    'address': email,
                    'name': owner
                },
                'type': 'required'
            }]
        
        # Create event
        if calendar_owner:
            url = f"{self.GRAPH_API_BASE}/users/{calendar_owner}/calendar/events"
        else:
            url = f"{self.GRAPH_API_BASE}/me/calendar/events"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=event_data, headers=headers, timeout=30)
        
        if response.status_code == 401:
            # Token expired, re-authenticate and retry
            self._authenticate()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.post(url, json=event_data, headers=headers, timeout=30)
        
        response.raise_for_status()
        
        event_result = response.json()
        return event_result.get('id')
    
    def _format_summary_html(
        self,
        meeting_title: str,
        summary_data: Dict[str, Any]
    ) -> str:
        """
        Format meeting summary as HTML email
        
        Args:
            meeting_title: Title of the meeting
            summary_data: Dictionary containing summary, decisions, action items, etc.
            
        Returns:
            HTML formatted email body
        """
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #0f62fe; border-bottom: 3px solid #0f62fe; padding-bottom: 10px; }}
                h2 {{ color: #161616; margin-top: 30px; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
                h3 {{ color: #393939; margin-top: 20px; }}
                .health-score {{ background: #f4f4f4; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .health-score .score {{ font-size: 48px; font-weight: bold; }}
                .health-healthy {{ color: #24a148; }}
                .health-at-risk {{ color: #f1c21b; }}
                .health-critical {{ color: #da1e28; }}
                .summary-text {{ background: #f4f4f4; padding: 15px; border-left: 4px solid #0f62fe; margin: 15px 0; }}
                ul, ol {{ margin: 10px 0; padding-left: 25px; }}
                li {{ margin: 8px 0; }}
                .action-item {{ background: #e5f6ff; padding: 12px; margin: 10px 0; border-radius: 6px; }}
                .blocker {{ background: #fff1f1; padding: 12px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #da1e28; }}
                .priority-urgent {{ color: #da1e28; font-weight: bold; }}
                .priority-high {{ color: #f1c21b; font-weight: bold; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>🚑 {meeting_title}</h1>
        """
        
        # Health Score
        health = summary_data.get('health', {})
        score = health.get('score', 0)
        status = health.get('status', 'unknown')
        emoji = health.get('emoji', '')
        
        health_class = f"health-{status}"
        html += f"""
            <div class="health-score">
                <div class="score {health_class}">{emoji} {score}/100</div>
                <div>Meeting Health: <strong>{status.capitalize()}</strong></div>
            </div>
        """
        
        # Executive Summary
        summary = summary_data.get('summary', {})
        exec_summary = summary.get('executive_summary', '')
        if exec_summary:
            html += f"""
            <h2>Executive Summary</h2>
            <div class="summary-text">{exec_summary}</div>
            """
        
        # Key Highlights
        highlights = summary.get('key_highlights', [])
        if highlights:
            html += "<h2>Key Highlights</h2><ul>"
            for highlight in highlights:
                html += f"<li>{highlight}</li>"
            html += "</ul>"
        
        # Decisions
        decisions = summary_data.get('decisions', [])
        if decisions:
            html += "<h2>✅ Decisions Made</h2><ol>"
            for decision in decisions:
                dec_text = decision.get('decision') or decision.get('description', 'N/A')
                html += f"<li>{dec_text}</li>"
            html += "</ol>"
        
        # Action Items
        action_items = summary_data.get('action_items', {}).get('action_items', [])
        if action_items:
            html += "<h2>📋 Action Items</h2>"
            for item in action_items:
                task = item.get('action') or item.get('task', 'N/A')
                owner = item.get('owner', 'Unassigned')
                deadline = item.get('deadline', 'No deadline')
                priority = item.get('priority', 'medium')
                
                priority_class = f"priority-{priority.lower()}"
                html += f"""
                <div class="action-item">
                    <strong>{task}</strong><br>
                    Owner: {owner} | Deadline: {deadline} | 
                    <span class="{priority_class}">Priority: {priority.capitalize()}</span>
                </div>
                """
        
        # Blockers
        blockers = summary_data.get('blockers', {}).get('blockers', [])
        if blockers:
            html += "<h2>🚫 Blockers</h2>"
            for blocker in blockers:
                desc = blocker.get('blocker') or blocker.get('description', 'N/A')
                severity = blocker.get('severity', 'medium')
                html += f"""
                <div class="blocker">
                    <strong>[{severity.upper()}]</strong> {desc}
                </div>
                """
        
        # Top Priorities
        priorities = summary.get('top_priorities', [])
        if priorities:
            html += "<h2>🎯 Top Priorities</h2><ol>"
            for priority in priorities:
                html += f"<li>{priority}</li>"
            html += "</ol>"
        
        # Red Flags
        red_flags = summary.get('red_flags', [])
        if red_flags:
            html += "<h2>🔴 Red Flags</h2><ul>"
            for flag in red_flags:
                html += f"<li style='color: #da1e28;'><strong>{flag}</strong></li>"
            html += "</ul>"
        
        # Next Steps
        next_steps = summary.get('next_steps', [])
        if next_steps:
            html += "<h2>➡️ Next Steps</h2><ul>"
            for step in next_steps:
                html += f"<li>{step}</li>"
            html += "</ul>"
        
        # Footer
        html += f"""
            <div class="footer">
                <p>This summary was automatically generated by AI Meeting Rescue Agent</p>
                <p>Powered by watsonx Orchestrate + Granite LLM</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html


# Made with Bob