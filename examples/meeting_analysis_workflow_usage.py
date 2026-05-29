"""
Example usage of MeetingAnalysisWorkflow for complete meeting analysis
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

# Load MeetingAnalysisWorkflow
spec = importlib.util.spec_from_file_location(
    "meeting_analysis_workflow",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'meeting_analysis_workflow.py')
)
workflow_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow_module)
MeetingAnalysisWorkflow = workflow_module.MeetingAnalysisWorkflow


def example_complete_workflow():
    """
    Example of running the complete meeting analysis workflow
    
    Note: This example requires valid watsonx.ai credentials in .env file
    """
    print("=" * 80)
    print("Meeting Analysis Workflow - Complete Example")
    print("=" * 80)
    
    # Sample meeting transcript in TXT format
    sample_transcript = """[00:00:15] Alice: Good morning everyone. Let's start with the Q4 planning discussion.
[00:00:30] Bob: Thanks Alice. I'm a bit confused about the timeline. Can you clarify when we need to deliver?
[00:01:00] Alice: We need to deliver by end of Q4, so December 31st.
[00:01:15] Carol: I'll handle the design mockups. Should have them ready by next week.
[00:01:30] Dave: Wait, what about the API integration? I'm lost on that part.
[00:02:00] Bob: The API integration is blocked by the vendor. We're waiting on their documentation.
[00:02:30] Alice: That's a critical blocker. Bob, can you follow up with the vendor today?
[00:02:45] Bob: Yes, I'll reach out immediately.
[00:03:00] Carol: I'll also need the brand guidelines. Who has those?
[00:03:15] Alice: I'll send them to you after this meeting.
[00:03:30] Dave: One more thing - we decided to use React for the frontend, right?
[00:03:45] Alice: Yes, that's correct. React with TypeScript.
[00:04:00] Bob: I'm concerned about the tight deadline. We might need additional resources.
[00:04:15] Alice: Good point. Let's discuss that with management. I'll set up a meeting.
[00:04:30] Carol: Should I start working on mobile designs too?
[00:04:45] Alice: Let's focus on desktop first, then mobile in phase 2.
[00:05:00] Dave: Sounds good. I'll start setting up the development environment.
[00:05:15] Alice: Perfect. Let's reconvene next Monday to check progress.
[00:05:30] Bob: I'll have an update on the vendor situation by then.
[00:05:45] Alice: Great. Thanks everyone!"""
    
    try:
        print("\nInitializing workflow...")
        print("(This requires valid watsonx.ai credentials)")
        print()
        
        # Initialize the workflow
        workflow = MeetingAnalysisWorkflow()
        
        print("\nRunning complete analysis workflow...")
        print("This will:")
        print("  1. Parse the transcript")
        print("  2. Run parallel analysis (confusion, actions, blockers)")
        print("  3. Calculate meeting health score")
        print("  4. Generate executive summary")
        print()
        
        # Run the complete workflow
        results = workflow.analyze_meeting(
            transcript_data=sample_transcript,
            format_type="txt"
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        # Metadata
        print("\n📋 MEETING METADATA")
        print("-" * 80)
        metadata = results['metadata']
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        # Health Score
        print("\n💊 MEETING HEALTH")
        print("-" * 80)
        health = results['health']
        print(f"  Score: {health['score']}/100")
        print(f"  Status: {health['status']} {health['emoji']}")
        print(f"  Recommendations: {len(health['recommendations'])}")
        for i, rec in enumerate(health['recommendations'][:3], 1):
            print(f"    {i}. {rec}")
        
        # Confusion Analysis
        print("\n😕 CONFUSION ANALYSIS")
        print("-" * 80)
        confusion = results['confusion']
        print(f"  Confusion Score: {confusion.get('confusion_score', 0):.2f}")
        print(f"  Confused Topics: {len(confusion.get('confused_topics', []))}")
        print(f"  Unanswered Questions: {len(confusion.get('unanswered_questions', []))}")
        
        # Action Items
        print("\n✅ ACTION ITEMS")
        print("-" * 80)
        action_items = results['action_items']
        print(f"  Total: {action_items.get('total_action_items', 0)}")
        print(f"  Unassigned: {action_items.get('unassigned_tasks', 0)}")
        for i, item in enumerate(action_items.get('action_items', [])[:3], 1):
            owner = item.get('owner', 'Unassigned')
            action = item.get('action', 'Unknown')
            print(f"    {i}. {action} (Owner: {owner})")
        
        # Blockers
        print("\n🚫 BLOCKERS")
        print("-" * 80)
        blockers = results['blockers']
        print(f"  Total: {blockers.get('total_blockers', 0)}")
        print(f"  Critical: {blockers.get('critical_blockers', 0)}")
        for i, blocker in enumerate(blockers.get('blockers', [])[:3], 1):
            severity = blocker.get('severity', 'unknown')
            description = blocker.get('blocker', 'Unknown')
            print(f"    {i}. [{severity.upper()}] {description}")
        
        # Executive Summary
        print("\n📊 EXECUTIVE SUMMARY")
        print("-" * 80)
        summary = results['summary']
        print(f"\n{summary['executive_summary']}\n")
        
        print("Key Highlights:")
        for i, highlight in enumerate(summary['key_highlights'], 1):
            print(f"  {i}. {highlight}")
        
        print("\nTop Priorities:")
        for i, priority in enumerate(summary['top_priorities'], 1):
            print(f"  {i}. {priority}")
        
        if summary['red_flags']:
            print("\n🔴 Red Flags:")
            for i, flag in enumerate(summary['red_flags'], 1):
                print(f"  {i}. {flag}")
        
        print("\nNext Steps:")
        for i, step in enumerate(summary['next_steps'], 1):
            print(f"  {i}. {step}")
        
        # Performance Metrics
        print("\n⏱️  PERFORMANCE METRICS")
        print("-" * 80)
        print(f"  Total Processing Time: {results['processing_time_seconds']}s")
        stage_times = results['stage_times']
        print(f"  Stage 1 (Parsing): {stage_times['parsing']}s")
        print(f"  Stage 2 (Parallel Analysis): {stage_times['parallel_analysis']}s")
        print(f"  Stage 3 (Health Calculation): {stage_times['health_calculation']}s")
        print(f"  Stage 4 (Summary Generation): {stage_times['summary_generation']}s")
        
        # Save results to file
        output_file = "meeting_analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Full results saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure all required files exist.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: If you see credential errors, make sure you have:")
        print("1. Created a .env file based on .env.example")
        print("2. Added your watsonx.ai credentials")
        print("3. Installed required dependencies: pip install -r requirements.txt")
        import traceback
        traceback.print_exc()


def example_simple_usage():
    """Simple example showing basic workflow usage"""
    print("\n" + "=" * 80)
    print("Simple Usage Example")
    print("=" * 80)
    
    # Minimal transcript
    transcript = """[00:00:00] Manager: Let's discuss the project status.
[00:00:15] Developer: We're blocked by the API issue.
[00:00:30] Manager: I'll follow up with the vendor today."""
    
    try:
        workflow = MeetingAnalysisWorkflow()
        results = workflow.analyze_meeting(transcript, format_type="txt")
        
        print(f"\n✅ Analysis complete!")
        print(f"   Health Score: {results['health']['score']}/100")
        print(f"   Status: {results['health']['status']} {results['health']['emoji']}")
        print(f"   Processing Time: {results['processing_time_seconds']}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run the complete example
    example_complete_workflow()
    
    # Uncomment to run simple example
    # example_simple_usage()

# Made with Bob
