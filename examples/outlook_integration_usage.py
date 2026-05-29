"""
Example usage of OutlookIntegration for sending meeting summaries and creating calendar events
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.outlook_integration import OutlookIntegration


def example_send_summary():
    """
    Example of sending meeting summary email
    
    Note: This requires valid Microsoft Graph API credentials in .env file:
    - OUTLOOK_CLIENT_ID=your-azure-ad-client-id
    - OUTLOOK_CLIENT_SECRET=your-azure-ad-client-secret
    - OUTLOOK_TENANT_ID=your-azure-ad-tenant-id
    """
    print("=" * 80)
    print("Outlook Integration - Send Summary Email Example")
    print("=" * 80)
    print()
    
    # Sample meeting summary data
    summary_data = {
        'health': {
            'score': 85,
            'status': 'healthy',
            'emoji': '✅'
        },
        'summary': {
            'executive_summary': 'Productive sprint planning meeting with clear action items and no major blockers.',
            'key_highlights': [
                'Prioritized authentication feature for Sprint 15',
                'Decided to use React with TypeScript for frontend',
                'All team members have clear assignments'
            ],
            'top_priorities': [
                'Complete authentication feature by Tuesday',
                'Update design system documentation',
                'Set up testing framework'
            ],
            'red_flags': [],
            'next_steps': [
                'Bob to complete authentication by Tuesday 5 PM',
                'Carol to update documentation by Thursday',
                'Team check-in on Wednesday'
            ]
        },
        'decisions': [
            {
                'decision': 'Prioritize authentication feature first',
                'decision_maker': 'Alice Chen'
            },
            {
                'decision': 'Use React with TypeScript for frontend',
                'decision_maker': 'Team'
            }
        ],
        'action_items': {
            'action_items': [
                {
                    'action': 'Complete user authentication feature',
                    'owner': 'Bob Smith',
                    'deadline': '2026-04-22',
                    'priority': 'high'
                },
                {
                    'action': 'Update design system documentation',
                    'owner': 'Carol Davis',
                    'deadline': '2026-04-24',
                    'priority': 'medium'
                }
            ]
        },
        'blockers': {
            'blockers': []
        }
    }
    
    try:
        print("Initializing Outlook integration...")
        outlook = OutlookIntegration()
        
        # Send summary email
        recipients = [
            'alice.chen@example.com',
            'bob.smith@example.com',
            'carol.davis@example.com'
        ]
        
        meeting_title = "Sprint Planning - Week 15"
        
        print(f"Sending summary email to {len(recipients)} recipient(s)...")
        print()
        
        success = outlook.send_summary_email(
            recipients=recipients,
            meeting_title=meeting_title,
            summary_data=summary_data,
            sender_email='meeting-bot@example.com'  # Optional: specify sender
        )
        
        if success:
            print("✅ Summary email sent successfully!")
        else:
            print("❌ Failed to send summary email")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print()
        print("Make sure you have set the following environment variables:")
        print("  - OUTLOOK_CLIENT_ID")
        print("  - OUTLOOK_CLIENT_SECRET")
        print("  - OUTLOOK_TENANT_ID")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def example_create_calendar_events():
    """
    Example of creating calendar events for action item deadlines
    """
    print("\n" + "=" * 80)
    print("Outlook Integration - Create Calendar Events Example")
    print("=" * 80)
    print()
    
    # Sample action items
    action_items = [
        {
            'action': 'Complete user authentication feature',
            'owner': 'bob.smith@example.com',
            'deadline': '2026-04-22',
            'priority': 'high'
        },
        {
            'action': 'Update design system documentation',
            'owner': 'carol.davis@example.com',
            'deadline': '2026-04-24',
            'priority': 'medium'
        },
        {
            'action': 'Set up testing framework',
            'owner': 'carol.davis@example.com',
            'deadline': '2026-04-25',
            'priority': 'high'
        }
    ]
    
    try:
        print("Initializing Outlook integration...")
        outlook = OutlookIntegration()
        
        print(f"Creating calendar events for {len(action_items)} action items...")
        print()
        
        results = outlook.create_deadline_events(
            action_items=action_items,
            calendar_owner='meeting-bot@example.com'  # Optional: specify calendar owner
        )
        
        # Display results
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        
        # Created events
        created = results['events_created']
        if created:
            print(f"✅ Successfully created {len(created)} calendar event(s):")
            print()
            for event in created:
                print(f"  Task: {event['task']}")
                print(f"  Deadline: {event['deadline']}")
                print(f"  Event ID: {event['event_id']}")
                print()
        
        # Failed events
        failed = results['failed_events']
        if failed:
            print(f"❌ Failed to create {len(failed)} event(s):")
            print()
            for failure in failed:
                print(f"  Task: {failure.get('task', 'Unknown')}")
                print(f"  Error: {failure['error']}")
                print()
        
        # Summary
        print("=" * 80)
        print(f"Summary: {len(created)} created, {len(failed)} failed")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def example_integrated_workflow():
    """
    Example of complete workflow: analyze meeting, send summary, create events
    """
    print("\n" + "=" * 80)
    print("Integrated Workflow Example")
    print("=" * 80)
    print()
    
    print("This example shows the complete workflow:")
    print("1. Analyze meeting transcript")
    print("2. Send summary email to participants")
    print("3. Create calendar events for action item deadlines")
    print()
    
    code_example = """
from services.meeting_analysis_workflow import MeetingAnalysisWorkflow
from services.outlook_integration import OutlookIntegration

# Step 1: Analyze meeting
workflow = MeetingAnalysisWorkflow()
results = workflow.analyze_meeting(transcript_data, format_type='txt')

# Step 2: Send summary email
outlook = OutlookIntegration()

participants = results['metadata'].get('participants', [])
recipient_emails = [f"{p.lower().replace(' ', '.')}@example.com" for p in participants]

outlook.send_summary_email(
    recipients=recipient_emails,
    meeting_title=results['metadata']['title'],
    summary_data=results
)

# Step 3: Create calendar events
action_items = results['action_items']['action_items']
outlook.create_deadline_events(action_items)

print("✅ Meeting analyzed, summary sent, and calendar events created!")
"""
    
    print("Code example:")
    print("-" * 80)
    print(code_example)
    print("-" * 80)


if __name__ == "__main__":
    # Run examples
    example_send_summary()
    example_create_calendar_events()
    example_integrated_workflow()

# Made with Bob
