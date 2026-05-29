"""
Example usage of ConfusionDetector for detecting confusion in meeting transcripts
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skills.confusion_detector_v2 import ConfusionDetector
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


def example_clear_meeting():
    """Example: Analyze a clear meeting with no confusion"""
    print("\n=== Example 1: Clear Meeting (Low Confusion) ===")
    
    transcript = """
[09:00:00] Manager: Good morning team. Today we'll review the Q1 results.
[09:01:00] Alice: Sounds good. I have the report ready.
[09:02:00] Manager: Great. Let's start with revenue numbers.
[09:03:00] Alice: Revenue was $2.5M, up 15% from last quarter.
[09:04:00] Bob: That's excellent growth. Well done team!
[09:05:00] Manager: Agreed. Any questions?
[09:06:00] Charlie: No questions from me. Everything is clear.
[09:07:00] Manager: Perfect. Let's move to next quarter planning.
"""
    
    try:
        detector = ConfusionDetector()
        result = detector.detect(transcript)
        
        print(f"Confusion Score: {result['confusion_score']:.2f}")
        print(f"Confusion Signals: {len(result['confusion_signals'])}")
        print(f"Confused Topics: {len(result['confused_topics'])}")
        print(f"Unanswered Questions: {len(result['unanswered_questions'])}")
        print(f"\nSummary: {detector.get_summary(result)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


def example_confusing_meeting():
    """Example: Analyze a meeting with confusion signals"""
    print("\n=== Example 2: Confusing Meeting (High Confusion) ===")
    
    transcript = """
[10:00:00] Manager: Let's discuss the new API architecture.
[10:01:00] Dev1: I'm lost. What API are we talking about?
[10:02:00] Manager: The customer data API we discussed last week.
[10:03:00] Dev2: Wait what? I thought we were doing the payment API first?
[10:04:00] Manager: No, we changed priorities. Customer data is first.
[10:05:00] Dev1: Can you clarify the timeline again?
[10:06:00] Manager: We need it by end of month.
[10:07:00] Dev2: I don't understand how we'll finish in time.
[10:08:00] Dev1: What about the database schema? Is that finalized?
[10:09:00] Manager: Let's move on to the next topic.
[10:10:00] Dev2: But what about the schema question?
[10:11:00] Manager: We'll circle back to that later.
[10:12:00] Dev1: I'm confused about the requirements. Can we review them?
[10:13:00] Manager: We're running out of time. Let's wrap up.
"""
    
    try:
        detector = ConfusionDetector()
        result = detector.detect(transcript)
        
        print(f"Confusion Score: {result['confusion_score']:.2f}")
        print(f"\nConfusion Signals ({len(result['confusion_signals'])}):")
        for signal in result['confusion_signals']:
            print(f"  [{signal['timestamp']}] {signal['speaker']}: {signal['signal']}")
        
        print(f"\nConfused Topics ({len(result['confused_topics'])}):")
        for topic in result['confused_topics']:
            print(f"  - {topic['topic']} (at {topic['timestamp']})")
            print(f"    Indicators: {', '.join(topic['indicators'])}")
        
        print(f"\nUnanswered Questions ({len(result['unanswered_questions'])}):")
        for question in result['unanswered_questions']:
            print(f"  - {question}")
        
        print(f"\nSummary: {detector.get_summary(result)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


def example_mixed_meeting():
    """Example: Meeting with some confusion but mostly clear"""
    print("\n=== Example 3: Mixed Meeting (Moderate Confusion) ===")
    
    transcript = """
[14:00:00] Lead: Let's review the sprint progress.
[14:01:00] Dev1: I completed the login feature.
[14:02:00] Lead: Great! Any blockers?
[14:03:00] Dev2: I'm stuck on the authentication flow. Can you clarify the OAuth setup?
[14:04:00] Lead: Sure, we're using OAuth 2.0 with PKCE flow.
[14:05:00] Dev2: Got it, thanks for clarifying.
[14:06:00] Dev3: What about the user roles? Are those defined yet?
[14:07:00] Lead: Yes, we have Admin, User, and Guest roles.
[14:08:00] Dev3: Perfect, that's clear now.
[14:09:00] Dev1: One question - what's the deadline for the profile page?
[14:10:00] Lead: End of this sprint, so Friday.
[14:11:00] Dev1: Understood. I'll have it ready.
"""
    
    try:
        detector = ConfusionDetector()
        result = detector.detect(transcript)
        
        print(f"Confusion Score: {result['confusion_score']:.2f}")
        print(f"Confusion Signals: {len(result['confusion_signals'])}")
        print(f"Confused Topics: {len(result['confused_topics'])}")
        print(f"Unanswered Questions: {len(result['unanswered_questions'])}")
        
        if result['confusion_signals']:
            print("\nConfusion Signals:")
            for signal in result['confusion_signals']:
                print(f"  [{signal['timestamp']}] {signal['speaker']}: {signal['signal']}")
        
        print(f"\nSummary: {detector.get_summary(result)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


def example_error_handling():
    """Example: Error handling with default values"""
    print("\n=== Example 4: Error Handling ===")
    
    # Empty transcript
    print("\n4a. Empty transcript:")
    try:
        detector = ConfusionDetector()
        result = detector.detect("")
        print(f"Result: {result}")
        print("✓ Handled gracefully with default values")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Very short transcript
    print("\n4b. Very short transcript:")
    try:
        detector = ConfusionDetector()
        result = detector.detect("Hello world")
        print(f"Confusion Score: {result['confusion_score']:.2f}")
        print("✓ Handled gracefully")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_custom_prompt_template():
    """Example: Using custom prompt template path"""
    print("\n=== Example 5: Custom Prompt Template ===")
    
    try:
        # Initialize with default template
        detector = ConfusionDetector(prompt_template_path="prompts/confusion_prompt.txt")
        
        transcript = """
[15:00:00] Alice: I don't understand the new process.
[15:01:00] Bob: Which part is unclear?
[15:02:00] Alice: The approval workflow. Can you explain it again?
"""
        
        result = detector.detect(transcript)
        print(f"Confusion Score: {result['confusion_score']:.2f}")
        print(f"Confusion Signals: {len(result['confusion_signals'])}")
        print("✓ Successfully used custom template path")
        
    except Exception as e:
        logger.error(f"Error: {e}")


def example_detailed_analysis():
    """Example: Detailed analysis with all fields"""
    print("\n=== Example 6: Detailed Analysis ===")
    
    transcript = """
[11:00:00] PM: Let's discuss the database migration strategy.
[11:01:00] DBA: Wait what? I thought we postponed this.
[11:02:00] PM: No, it's scheduled for next week.
[11:03:00] Dev: I'm lost. What database are we migrating?
[11:04:00] PM: The customer database from MySQL to PostgreSQL.
[11:05:00] DBA: Can you clarify the downtime window?
[11:06:00] PM: We have a 4-hour window on Saturday night.
[11:07:00] Dev: I don't understand the rollback plan. What if something fails?
[11:08:00] PM: We'll discuss rollback procedures in the next meeting.
[11:09:00] DBA: What about data validation? How do we verify the migration?
[11:10:00] PM: Let's move on to the next agenda item.
"""
    
    try:
        detector = ConfusionDetector()
        result = detector.detect(transcript)
        
        print("=" * 80)
        print("CONFUSION DETECTION REPORT")
        print("=" * 80)
        
        print(f"\nOverall Confusion Score: {result['confusion_score']:.2f}")
        
        if result['confusion_score'] < 0.3:
            print("Assessment: Meeting was mostly clear")
        elif result['confusion_score'] < 0.6:
            print("Assessment: Some confusion present, follow-up recommended")
        else:
            print("Assessment: Significant confusion, immediate clarification needed")
        
        print(f"\n--- Confusion Signals ({len(result['confusion_signals'])}) ---")
        for i, signal in enumerate(result['confusion_signals'], 1):
            print(f"{i}. [{signal['timestamp']}] {signal['speaker']}")
            print(f"   Signal: \"{signal['signal']}\"")
        
        print(f"\n--- Confused Topics ({len(result['confused_topics'])}) ---")
        for i, topic in enumerate(result['confused_topics'], 1):
            print(f"{i}. {topic['topic']} (at {topic['timestamp']})")
            print(f"   Indicators: {', '.join(topic['indicators'])}")
        
        print(f"\n--- Unanswered Questions ({len(result['unanswered_questions'])}) ---")
        for i, question in enumerate(result['unanswered_questions'], 1):
            print(f"{i}. {question}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """Run all examples"""
    print("=" * 80)
    print("ConfusionDetector Usage Examples")
    print("=" * 80)
    
    # Run examples
    example_clear_meeting()
    example_confusing_meeting()
    example_mixed_meeting()
    example_error_handling()
    example_custom_prompt_template()
    example_detailed_analysis()
    
    print("\n" + "=" * 80)
    print("Examples completed")
    print("=" * 80)


if __name__ == "__main__":
    main()


# Made with Bob