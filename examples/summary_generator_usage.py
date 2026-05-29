"""
Example usage of SummaryGenerator for creating executive meeting summaries
"""
import sys
import os
import json

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import directly to avoid dependency issues
import importlib.util

# Load SummaryGenerator
spec = importlib.util.spec_from_file_location(
    "summary_generator",
    os.path.join(os.path.dirname(__file__), '..', 'skills', 'summary_generator.py')
)
summary_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary_module)
SummaryGenerator = summary_module.SummaryGenerator

# Load HealthCalculator
spec = importlib.util.spec_from_file_location(
    "health_calculator",
    os.path.join(os.path.dirname(__file__), '..', 'utils', 'health_calculator.py')
)
health_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_module)
HealthCalculator = health_module.HealthCalculator


def example_summary_generation():
    """
    Example of generating an executive meeting summary
    
    Note: This example will only work if you have valid watsonx.ai credentials
    configured in your .env file. Otherwise, it will return default values.
    """
    print("=" * 80)
    print("Executive Meeting Summary Generation Example")
    print("=" * 80)
    print()
    
    # Sample meeting data
    metadata = {
        "title": "Q4 Product Planning Meeting",
        "date": "2024-01-15",
        "duration": "60 minutes",
        "participants": ["Alice (PM)", "Bob (Engineering)", "Carol (Design)", "Dave (Marketing)"]
    }
    
    confusion = {
        "confusion_score": 0.3,
        "confused_topics": [
            {
                "topic": "API integration timeline",
                "timestamp": "00:15:30",
                "indicators": ["multiple clarification requests", "repeated explanations"]
            }
        ],
        "unanswered_questions": [
            "What's the budget for the new feature?",
            "Who will handle the mobile app updates?"
        ],
        "confusion_signals": [
            {
                "timestamp": "00:15:30",
                "speaker": "Bob",
                "signal": "Wait, can you clarify the timeline?"
            }
        ]
    }
    
    decisions = [
        {
            "decision": "Launch new feature in Q2 2024",
            "rationale": "Market research shows strong demand",
            "owner": "Alice"
        },
        {
            "decision": "Hire 2 additional engineers",
            "rationale": "Current team at capacity",
            "owner": "Bob"
        },
        {
            "decision": "Redesign mobile app UI",
            "rationale": "User feedback indicates confusion",
            "owner": "Carol"
        }
    ]
    
    action_items = [
        {
            "action": "Create detailed project timeline",
            "owner": "Alice",
            "deadline": "2024-01-20"
        },
        {
            "action": "Draft job descriptions for engineering roles",
            "owner": "Bob",
            "deadline": "2024-01-18"
        },
        {
            "action": "Conduct user research for mobile redesign",
            "owner": "Carol",
            "deadline": "2024-01-25"
        },
        {
            "action": "Prepare marketing campaign proposal",
            "owner": "Dave",
            "deadline": "2024-02-01"
        }
    ]
    
    blockers = [
        {
            "blocker": "Budget approval pending from finance",
            "severity": "high",
            "impact": "Cannot proceed with hiring"
        },
        {
            "blocker": "API documentation incomplete",
            "severity": "medium",
            "impact": "Integration timeline at risk"
        }
    ]
    
    # Calculate health score
    health = HealthCalculator.calculate(
        confusion_score=0.3,
        decisions_count=3,
        action_items_count=4,
        blockers_count=2,
        unassigned_tasks=0
    )
    
    print("Meeting Health Score:")
    print(f"  Score: {health['score']}/100")
    print(f"  Status: {health['status']} {health['emoji']}")
    print()
    
    try:
        # Initialize the summary generator
        print("Initializing SummaryGenerator...")
        generator = SummaryGenerator()
        
        print("Generating executive summary...")
        print("(This requires valid watsonx.ai credentials)")
        print()
        
        # Generate the summary
        summary = generator.generate(
            metadata=metadata,
            confusion=confusion,
            decisions=decisions,
            action_items=action_items,
            blockers=blockers,
            health=health
        )
        
        # Display the results
        print("=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        print()
        print(summary['executive_summary'])
        print()
        
        print("=" * 80)
        print("KEY HIGHLIGHTS")
        print("=" * 80)
        for i, highlight in enumerate(summary['key_highlights'], 1):
            print(f"{i}. {highlight}")
        print()
        
        print("=" * 80)
        print("TOP PRIORITIES")
        print("=" * 80)
        for i, priority in enumerate(summary['top_priorities'], 1):
            print(f"{i}. {priority}")
        print()
        
        if summary['red_flags']:
            print("=" * 80)
            print("🔴 RED FLAGS")
            print("=" * 80)
            for i, flag in enumerate(summary['red_flags'], 1):
                print(f"{i}. {flag}")
            print()
        
        print("=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        for i, step in enumerate(summary['next_steps'], 1):
            print(f"{i}. {step}")
        print()
        
        # Also show as JSON
        print("=" * 80)
        print("JSON OUTPUT")
        print("=" * 80)
        print(json.dumps(summary, indent=2))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the prompt template file exists.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: If you see credential errors, make sure you have:")
        print("1. Created a .env file based on .env.example")
        print("2. Added your watsonx.ai credentials")
        print("3. Installed required dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    example_summary_generation()

# Made with Bob
