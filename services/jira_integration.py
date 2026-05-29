"""
Jira Integration Service
Creates Jira tickets from meeting action items
"""
import logging
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JiraIntegration:
    """
    Integrates with Jira to create tickets from action items
    
    Uses Jira REST API to automatically create tasks from meeting action items,
    including proper assignment, priority mapping, and due dates.
    """
    
    # Priority mapping: action item priority -> Jira priority name
    PRIORITY_MAP = {
        'urgent': 'Highest',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    }
    
    def __init__(
        self,
        jira_url: Optional[str] = None,
        api_token: Optional[str] = None,
        email: Optional[str] = None
    ):
        """
        Initialize Jira integration with credentials
        
        Args:
            jira_url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            api_token: Jira API token
            email: Email associated with the API token
            
        Raises:
            ValueError: If required credentials are missing
        """
        # Load from environment if not provided
        self.jira_url = jira_url or os.getenv('JIRA_URL')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        self.email = email or os.getenv('JIRA_EMAIL')
        
        # Validate credentials
        if not self.jira_url:
            raise ValueError("JIRA_URL is required")
        if not self.api_token:
            raise ValueError("JIRA_API_TOKEN is required")
        if not self.email:
            raise ValueError("JIRA_EMAIL is required")
        
        # Remove trailing slash from URL
        self.jira_url = self.jira_url.rstrip('/')
        
        # Setup authentication
        self.auth = (self.email, self.api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        logger.info("JiraIntegration initialized successfully")
    
    def create_tickets(
        self,
        action_items: List[Dict[str, Any]],
        project_key: str,
        assignee_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create Jira tickets for all action items
        
        Args:
            action_items: List of action item dictionaries
            project_key: Jira project key (e.g., "PROJ")
            assignee_map: Optional mapping of owner names to Jira usernames
                         e.g., {"Alice Chen": "alice.chen", "Bob Smith": "bob.smith"}
            
        Returns:
            Dictionary with:
            - created_tickets: List of successfully created tickets
            - failed_tickets: List of failed ticket creations with errors
        """
        if not action_items:
            logger.warning("No action items provided")
            return {
                'created_tickets': [],
                'failed_tickets': []
            }
        
        logger.info(f"Creating {len(action_items)} Jira tickets in project {project_key}")
        
        created_tickets = []
        failed_tickets = []
        
        for i, item in enumerate(action_items, 1):
            try:
                # Create ticket
                ticket = self._create_single_ticket(item, project_key, assignee_map)
                created_tickets.append(ticket)
                logger.info(f"Created ticket {ticket['key']}: {ticket['url']}")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to create ticket for action item {i}: {error_msg}")
                failed_tickets.append({
                    'action_item': item.get('action') or item.get('task', 'Unknown'),
                    'error': error_msg
                })
        
        logger.info(f"Created {len(created_tickets)} tickets, {len(failed_tickets)} failed")
        
        return {
            'created_tickets': created_tickets,
            'failed_tickets': failed_tickets
        }
    
    def _create_single_ticket(
        self,
        action_item: Dict[str, Any],
        project_key: str,
        assignee_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a single Jira ticket from an action item
        
        Args:
            action_item: Action item dictionary
            project_key: Jira project key
            assignee_map: Optional mapping of owner names to Jira usernames
            
        Returns:
            Dictionary with ticket id, key, and url
            
        Raises:
            Exception: If ticket creation fails
        """
        # Extract action item details
        task = action_item.get('action') or action_item.get('task', 'Untitled Task')
        owner = action_item.get('owner', 'Unassigned')
        deadline = action_item.get('deadline')
        priority = action_item.get('priority', 'medium')
        dependencies = action_item.get('dependencies', [])
        
        # Build description
        description = self._build_description(action_item, dependencies)
        
        # Map priority
        jira_priority = self._map_priority(priority)
        
        # Map assignee
        assignee = self._map_assignee(owner, assignee_map)
        
        # Build issue data
        issue_data = {
            'fields': {
                'project': {
                    'key': project_key
                },
                'summary': task,
                'description': description,
                'issuetype': {
                    'name': 'Task'
                },
                'priority': {
                    'name': jira_priority
                }
            }
        }
        
        # Add assignee if mapped
        if assignee:
            issue_data['fields']['assignee'] = {
                'name': assignee
            }
        
        # Add due date if provided
        if deadline and deadline != 'No deadline':
            # Ensure date is in YYYY-MM-DD format
            try:
                # Parse and reformat if needed
                if 'T' in deadline:
                    deadline = deadline.split('T')[0]
                datetime.strptime(deadline, '%Y-%m-%d')
                issue_data['fields']['duedate'] = deadline
            except ValueError:
                logger.warning(f"Invalid deadline format: {deadline}")
        
        # Create the issue
        url = f"{self.jira_url}/rest/api/2/issue"
        
        try:
            response = requests.post(
                url,
                json=issue_data,
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            # Handle different error cases
            if response.status_code == 401:
                raise Exception("Authentication failed. Check your Jira credentials.")
            elif response.status_code == 404:
                raise Exception(f"Project '{project_key}' not found or you don't have access.")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif response.status_code >= 400:
                error_detail = response.json().get('errors', {}) or response.json().get('errorMessages', [])
                raise Exception(f"Jira API error: {error_detail}")
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            ticket_key = result['key']
            ticket_id = result['id']
            ticket_url = f"{self.jira_url}/browse/{ticket_key}"
            
            return {
                'id': ticket_id,
                'key': ticket_key,
                'url': ticket_url,
                'summary': task
            }
            
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Jira server may be slow or unreachable.")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error. Check your Jira URL and network connection.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _build_description(
        self,
        action_item: Dict[str, Any],
        dependencies: List[str]
    ) -> str:
        """
        Build Jira ticket description from action item
        
        Args:
            action_item: Action item dictionary
            dependencies: List of dependencies
            
        Returns:
            Formatted description string
        """
        description_parts = []
        
        # Add task details
        task = action_item.get('action') or action_item.get('task', 'N/A')
        description_parts.append(f"*Task:* {task}")
        
        # Add owner
        owner = action_item.get('owner', 'Unassigned')
        description_parts.append(f"*Owner:* {owner}")
        
        # Add deadline
        deadline = action_item.get('deadline', 'No deadline')
        description_parts.append(f"*Deadline:* {deadline}")
        
        # Add priority
        priority = action_item.get('priority', 'medium')
        description_parts.append(f"*Priority:* {priority.capitalize()}")
        
        # Add dependencies if any
        if dependencies:
            description_parts.append(f"\n*Dependencies:*")
            for dep in dependencies:
                description_parts.append(f"- {dep}")
        
        # Add metadata
        description_parts.append(f"\n_Created from meeting analysis on {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
        
        return '\n'.join(description_parts)
    
    def _map_priority(self, priority_str: str) -> str:
        """
        Map action item priority to Jira priority
        
        Args:
            priority_str: Priority string (urgent/high/medium/low)
            
        Returns:
            Jira priority name
        """
        priority_lower = priority_str.lower() if priority_str else 'medium'
        return self.PRIORITY_MAP.get(priority_lower, 'Medium')
    
    def _map_assignee(
        self,
        owner_name: str,
        assignee_map: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Map owner name to Jira username
        
        Args:
            owner_name: Owner name from action item
            assignee_map: Optional mapping of names to Jira usernames
            
        Returns:
            Jira username or None if not mapped/unassigned
        """
        if not owner_name or owner_name.lower() == 'unassigned':
            return None
        
        if assignee_map and owner_name in assignee_map:
            return assignee_map[owner_name]
        
        # If no mapping provided, try to convert name to username format
        # e.g., "Alice Chen" -> "alice.chen"
        # This is a fallback and may not work for all Jira instances
        username = owner_name.lower().replace(' ', '.')
        logger.debug(f"No mapping for '{owner_name}', using generated username: {username}")
        
        return username
    
    def test_connection(self) -> bool:
        """
        Test connection to Jira
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = f"{self.jira_url}/rest/api/2/myself"
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Successfully connected to Jira as {user_data.get('displayName')}")
                return True
            else:
                logger.error(f"Connection test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# Made with Bob