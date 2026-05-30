"""
Example usage of the AI Meeting Rescue Agent API
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:5000"

# Sample meeting transcript
sample_transcript = """
Alice: Good morning everyone. Let's start our sprint planning meeting.
Bob: Thanks Alice. I wanted to discuss the database migration issue.
Charlie: Before we start, I'm confused about the timeline for the new feature.
Alice: Good point Charlie. Let me clarify - we need to deliver by end of month.
Bob: That's tight. I'm currently blocked on getting the staging environment set up.
Charlie: I can help with that Bob. Let's make that a priority.
Alice: Agreed. So our decisions today are: 1) Database migration is priority one, 2) Charlie helps Bob with staging.
Bob: Perfect. I'll work on the migration schema and have it ready by Wednesday.
Charlie: And I'll get the staging environment configured by tomorrow.
Alice: Great. Any other blockers we should discuss?
Bob: Just one - we're waiting on the API documentation from the backend team.
Alice: I'll follow up with them today. Let's reconvene on Thursday to review progress.
"""

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_full_analysis():
    """Test full transcript analysis"""
    print("\n" + "="*60)
    print("Testing Full Analysis")
    print("="*60)
    
    payload = {
        "transcript": sample_transcript,
        "meeting_id": "sprint-planning-2026-05-28",
        "metadata": {
            "date": "2026-05-28",
            "participants": ["Alice", "Bob", "Charlie"]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nMeeting ID: {result['meeting_id']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        print(f"\nAnalysis Results:")
        print(json.dumps(result['analysis'], indent=2))
    else:
        print(f"Error: {response.json()}")


def test_single_skill(skill_name):
    """Test a single skill analysis"""
    print("\n" + "="*60)
    print(f"Testing {skill_name} Skill")
    print("="*60)
    
    payload = {
        "transcript": sample_transcript
    }
    
    response = requests.post(
        f"{BASE_URL}/api/analyze/{skill_name}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nSkill: {result['skill']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        print(f"\nResult:")
        print(json.dumps(result['result'], indent=2))
    else:
        print(f"Error: {response.json()}")


def test_list_skills():
    """Test listing available skills"""
    print("\n" + "="*60)
    print("Testing List Skills Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/skills")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI Meeting Rescue Agent - API Usage Examples")
    print("="*60)
    print("\nMake sure the server is running on http://localhost:5000")
    print("Start the server with: python app.py")
    
    try:
        # Test health check
        test_health_check()
        
        # Test listing skills
        test_list_skills()
        
        # Test individual skills
        test_single_skill("confusion_detector")
        test_single_skill("decision_extractor")
        test_single_skill("action_item_parser")
        test_single_skill("blocker_identifier")
        
        # Test full analysis (this will take longer)
        test_full_analysis()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the server is running on http://localhost:5000")
        print("Start it with: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# Made with Bob
