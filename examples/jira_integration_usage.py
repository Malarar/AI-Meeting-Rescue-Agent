"""
Example usage of JiraIntegration for creating Jira tickets from action items
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.jira_integration import JiraIntegration


def example_create_tickets():
    """
    Example of creating Jira tickets from action items
    
    Note: This requires valid Jira credentials in .env file:
    - JIRA_URL=https://your-domain.atlassian.net
    - JIRA_EMAIL=your-email@example.com
    - JIRA_API_TOKEN=your-api-token
    """
    print("=" * 80)
    print("Jira Integration - Create Tickets Example")
    print("=" * 80)
    print()
    
    # Sample action items from meeting analysis
    action_items = [
        {
            "id": "AI-001",
            "action": "Complete user authentication feature",
            "owner": "Bob Smith",
            "deadline": "2026-04-22",
            "priority": "high",
            "dependencies": ["API documentation"],
            "mentioned_at": "00:02:00"
        },
        {
            "id": "AI-002",
            "action": "Update design system documentation",
            "owner": "Carol Davis",
            "deadline": "2026-04-24",
            "priority": "medium",
            "dependencies": [],
            "mentioned_at": "00:02:45"
        },
        {
            "id": "AI-003",
            "action": "Set up testing framework",
            "owner": "Carol Davis",
            "deadline": "2026-04-25",
            "priority": "high",
            "dependencies": ["Authentication feature"],
            "mentioned_at": "00:04:15"
        },
        {
            "id": "AI-004",
            "action": "Review security requirements",
            "owner": "Unassigned",
            "deadline": "No deadline",
            "priority": "urgent",
            "dependencies": [],
            "mentioned_at": "00:05:00"
        }
    ]
    
    # Assignee mapping (owner names to Jira usernames)
    assignee_map = {
        "Bob Smith": "bob.smith",
        "Carol Davis": "carol.davis",
        "Alice Chen": "alice.chen"
    }
    
    try:
        print("Initializing Jira integration...")
        jira = JiraIntegration()
        
        # Test connection
        print("Testing Jira connection...")
        if not jira.test_connection():
            print("❌ Failed to connect to Jira. Check your credentials.")
            return
        
        print("✅ Connected to Jira successfully")
        print()
        
        # Create tickets
        project_key = "PROJ"  # Replace with your Jira project key
        print(f"Creating {len(action_items)} tickets in project {project_key}...")
        print()
        
        results = jira.create_tickets(
            action_items=action_items,
            project_key=project_key,
            assignee_map=assignee_map
        )
        
        # Display results
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        
        # Created tickets
        created = results['created_tickets']
        if created:
            print(f"✅ Successfully created {len(created)} ticket(s):")
            print()
            for ticket in created:
                print(f"  {ticket['key']}: {ticket['summary']}")
                print(f"  URL: {ticket['url']}")
                print()
        
        # Failed tickets
        failed = results['failed_tickets']
        if failed:
            print(f"❌ Failed to create {len(failed)} ticket(s):")
            print()
            for failure in failed:
                print(f"  Task: {failure['action_item']}")
                print(f"  Error: {failure['error']}")
                print()
        
        # Summary
        print("=" * 80)
        print(f"Summary: {len(created)} created, {len(failed)} failed")
        print("=" * 80)
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print()
        print("Make sure you have set the following environment variables:")
        print("  - JIRA_URL")
        print("  - JIRA_EMAIL")
        print("  - JIRA_API_TOKEN")
        print()
        print("You can set these in your .env file:")
        print("  JIRA_URL=https://your-domain.atlassian.net")
        print("  JIRA_EMAIL=your-email@example.com")
        print("  JIRA_API_TOKEN=your-api-token")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def example_with_workflow():
    """
    Example of integrating Jira ticket creation with meeting analysis workflow
    """
    print("\n" + "=" * 80)
    print("Integrated Workflow Example")
    print("=" * 80)
    print()
    
    print("This example shows how to:")
    print("1. Analyze a meeting transcript")
    print("2. Extract action items")
    print("3. Automatically create Jira tickets")
    print()
    
    # This would be the typical workflow:
    code_example = """
from services.meeting_analysis_workflow import MeetingAnalysisWorkflow
from services.jira_integration import JiraIntegration

# Analyze meeting
workflow = MeetingAnalysisWorkflow()
results = workflow.analyze_meeting(transcript_data, format_type='txt')

# Extract action items
action_items = results['action_items']['action_items']

# Create Jira tickets
jira = JiraIntegration()
assignee_map = {
    "Alice Chen": "alice.chen",
    "Bob Smith": "bob.smith"
}

ticket_results = jira.create_tickets(
    action_items=action_items,
    project_key="PROJ",
    assignee_map=assignee_map
)

print(f"Created {len(ticket_results['created_tickets'])} Jira tickets")
"""
    
    print("Code example:")
    print("-" * 80)
    print(code_example)
    print("-" * 80)


if __name__ == "__main__":
    # Run the basic example
    example_create_tickets()
    
    # Show integrated workflow example
    example_with_workflow()

# Made with Bob
