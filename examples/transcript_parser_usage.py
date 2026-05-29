"""
Example usage of TranscriptParser for parsing meeting transcripts
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.transcript_parser import TranscriptParser
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


def example_json_parsing():
    """Example: Parse JSON format transcript"""
    print("\n=== Example 1: JSON Format Parsing ===")
    
    # Sample JSON transcript
    json_transcript = json.dumps({
        "meeting_title": "Weekly Team Sync",
        "date": "2024-01-15",
        "messages": [
            {
                "timestamp": "09:00:00",
                "speaker": "Alice",
                "text": "Good morning everyone! Let's start with project updates."
            },
            {
                "timestamp": "09:01:30",
                "speaker": "Bob",
                "text": "I've completed the frontend redesign. Ready for review."
            },
            {
                "timestamp": "09:03:15",
                "speaker": "Charlie",
                "text": "Great work Bob! I'll review it by end of day."
            },
            {
                "timestamp": "09:05:00",
                "speaker": "Alice",
                "text": "Perfect. Any blockers we need to discuss?"
            },
            {
                "timestamp": "09:06:30",
                "speaker": "Bob",
                "text": "I need access to the staging environment."
            },
            {
                "timestamp": "09:08:00",
                "speaker": "Alice",
                "text": "I'll get that sorted today. Anything else?"
            },
            {
                "timestamp": "09:10:00",
                "speaker": "Charlie",
                "text": "All good on my end. Thanks everyone!"
            }
        ]
    })
    
    try:
        # Parse transcript
        parser = TranscriptParser()
        result = parser.parse(json_transcript, 'json')
        
        # Display results
        print(f"Meeting Title: {result['metadata']['meeting_title']}")
        print(f"Date: {result['metadata']['date']}")
        print(f"Duration: {result['metadata']['duration_minutes']} minutes")
        print(f"Total Speakers: {result['metadata']['total_speakers']}")
        print(f"Speakers: {', '.join(result['metadata']['speaker_list'])}")
        print(f"Total Messages: {result['metadata']['total_messages']}")
        print(f"\nFirst message: [{result['parsed_transcript'][0]['timestamp']}] "
              f"{result['parsed_transcript'][0]['speaker']}: "
              f"{result['parsed_transcript'][0]['text']}")
        
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")


def example_txt_parsing():
    """Example: Parse TXT format transcript"""
    print("\n=== Example 2: TXT Format Parsing ===")
    
    # Sample TXT transcript
    txt_transcript = """Product Planning Meeting
[14:00:00] Sarah: Welcome everyone to our product planning session.
[14:01:15] John: Thanks for organizing this Sarah. I have some ideas to share.
[14:02:30] Sarah: Great! Let's hear them.
[14:03:45] John: I think we should focus on mobile-first design for the next quarter.
[14:05:00] Mike: I agree with John. Our mobile traffic has increased by 40%.
[14:06:30] Sarah: Excellent point. Let's make that a priority.
[14:08:00] John: I can draft a proposal by Friday.
[14:09:15] Sarah: Perfect. Mike, can you provide the analytics data?
[14:10:30] Mike: Sure, I'll send it by tomorrow.
[14:12:00] Sarah: Great! Let's reconvene next week to review the proposal."""
    
    try:
        # Parse transcript
        parser = TranscriptParser()
        result = parser.parse(txt_transcript, 'txt')
        
        # Display results
        print(f"Meeting Title: {result['metadata']['meeting_title']}")
        print(f"Duration: {result['metadata']['duration_minutes']} minutes")
        print(f"Total Speakers: {result['metadata']['total_speakers']}")
        print(f"Speakers: {', '.join(result['metadata']['speaker_list'])}")
        print(f"Total Messages: {result['metadata']['total_messages']}")
        print(f"Time Range: {result['metadata']['start_time']} - {result['metadata']['end_time']}")
        
    except Exception as e:
        logger.error(f"Error parsing TXT: {e}")


def example_format_for_llm():
    """Example: Format parsed transcript for LLM"""
    print("\n=== Example 3: Format for LLM ===")
    
    # Sample transcript
    json_transcript = json.dumps({
        "meeting_title": "Sprint Planning",
        "date": "2024-01-20",
        "messages": [
            {"timestamp": "10:00:00", "speaker": "Manager", "text": "Let's plan our sprint."},
            {"timestamp": "10:02:00", "speaker": "Dev1", "text": "I can take the API tasks."},
            {"timestamp": "10:04:00", "speaker": "Dev2", "text": "I'll handle the UI components."},
            {"timestamp": "10:06:00", "speaker": "Manager", "text": "Sounds good. Let's aim for completion by Friday."}
        ]
    })
    
    try:
        # Parse and format
        parser = TranscriptParser()
        result = parser.parse(json_transcript, 'json')
        formatted = parser.format_for_llm(result)
        
        print("Formatted transcript for LLM:")
        print("-" * 80)
        print(formatted)
        
    except Exception as e:
        logger.error(f"Error formatting: {e}")


def example_error_handling():
    """Example: Error handling for invalid formats"""
    print("\n=== Example 4: Error Handling ===")
    
    parser = TranscriptParser()
    
    # Test invalid JSON
    print("\n4a. Invalid JSON:")
    try:
        parser.parse("not valid json", 'json')
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test missing required fields
    print("\n4b. Missing required fields:")
    try:
        invalid_json = json.dumps({"meeting_title": "Test"})  # Missing 'messages'
        parser.parse(invalid_json, 'json')
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test unsupported format
    print("\n4c. Unsupported format:")
    try:
        parser.parse("some data", 'xml')
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test invalid TXT format
    print("\n4d. Invalid TXT format (no matching lines):")
    try:
        parser.parse("Just some random text without proper format", 'txt')
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")


def example_metadata_extraction():
    """Example: Detailed metadata extraction"""
    print("\n=== Example 5: Metadata Extraction ===")
    
    # Longer transcript with multiple speakers
    json_transcript = json.dumps({
        "meeting_title": "Q1 Review Meeting",
        "date": "2024-01-25",
        "messages": [
            {"timestamp": "15:00:00", "speaker": "CEO", "text": "Welcome to Q1 review."},
            {"timestamp": "15:05:00", "speaker": "CFO", "text": "Revenue is up 25%."},
            {"timestamp": "15:10:00", "speaker": "CTO", "text": "We launched 3 new features."},
            {"timestamp": "15:15:00", "speaker": "CMO", "text": "Marketing campaigns performed well."},
            {"timestamp": "15:20:00", "speaker": "CEO", "text": "Excellent work team!"},
            {"timestamp": "15:25:00", "speaker": "CFO", "text": "Q2 projections look strong."},
            {"timestamp": "15:30:00", "speaker": "CTO", "text": "We have 5 features planned."},
            {"timestamp": "15:35:00", "speaker": "CMO", "text": "New campaign launches next week."},
            {"timestamp": "15:40:00", "speaker": "CEO", "text": "Great! Let's keep the momentum."}
        ]
    })
    
    try:
        parser = TranscriptParser()
        result = parser.parse(json_transcript, 'json')
        metadata = result['metadata']
        
        print("Detailed Metadata:")
        print(f"  Meeting Title: {metadata['meeting_title']}")
        print(f"  Date: {metadata['date']}")
        print(f"  Start Time: {metadata['start_time']}")
        print(f"  End Time: {metadata['end_time']}")
        print(f"  Duration: {metadata['duration_minutes']} minutes")
        print(f"  Total Messages: {metadata['total_messages']}")
        print(f"  Total Speakers: {metadata['total_speakers']}")
        print(f"  Speaker List:")
        for speaker in metadata['speaker_list']:
            speaker_messages = [m for m in result['parsed_transcript'] if m['speaker'] == speaker]
            print(f"    - {speaker}: {len(speaker_messages)} messages")
        
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """Run all examples"""
    print("=" * 80)
    print("TranscriptParser Usage Examples")
    print("=" * 80)
    
    # Run examples
    example_json_parsing()
    example_txt_parsing()
    example_format_for_llm()
    example_error_handling()
    example_metadata_extraction()
    
    print("\n" + "=" * 80)
    print("Examples completed")
    print("=" * 80)


if __name__ == "__main__":
    main()


# Made with Bob