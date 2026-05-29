"""
Example usage of the HealthCalculator class.

This demonstrates how to calculate meeting health scores based on various metrics.
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import directly to avoid dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "health_calculator",
    os.path.join(os.path.dirname(__file__), '..', 'utils', 'health_calculator.py')
)
health_calc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_calc_module)
HealthCalculator = health_calc_module.HealthCalculator


def example_healthy_meeting():
    """Example of a healthy meeting."""
    print("=" * 60)
    print("Example 1: Healthy Meeting")
    print("=" * 60)
    
    result = HealthCalculator.calculate(
        confusion_score=0.1,      # Low confusion
        decisions_count=5,        # Good number of decisions
        action_items_count=5,     # Reasonable action items
        blockers_count=0,         # No blockers
        unassigned_tasks=0        # All tasks assigned
    )
    
    print(f"Score: {result['score']}")
    print(f"Status: {result['status']} {result['emoji']}")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()


def example_at_risk_meeting():
    """Example of an at-risk meeting."""
    print("=" * 60)
    print("Example 2: At-Risk Meeting")
    print("=" * 60)
    
    result = HealthCalculator.calculate(
        confusion_score=0.4,      # Moderate confusion
        decisions_count=1,        # Few decisions
        action_items_count=8,     # Decent action items
        blockers_count=2,         # Some blockers
        unassigned_tasks=1        # One unassigned task
    )
    
    print(f"Score: {result['score']}")
    print(f"Status: {result['status']} {result['emoji']}")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()


def example_critical_meeting():
    """Example of a critical meeting."""
    print("=" * 60)
    print("Example 3: Critical Meeting")
    print("=" * 60)
    
    result = HealthCalculator.calculate(
        confusion_score=0.8,      # High confusion
        decisions_count=0,        # No decisions
        action_items_count=0,     # No action items
        blockers_count=4,         # Many blockers
        unassigned_tasks=3        # Multiple unassigned tasks
    )
    
    print(f"Score: {result['score']}")
    print(f"Status: {result['status']} {result['emoji']}")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()


def example_too_many_action_items():
    """Example of a meeting with too many action items."""
    print("=" * 60)
    print("Example 4: Meeting with Too Many Action Items")
    print("=" * 60)
    
    result = HealthCalculator.calculate(
        confusion_score=0.2,      # Low confusion
        decisions_count=3,        # Some decisions
        action_items_count=15,    # Too many action items
        blockers_count=1,         # One blocker
        unassigned_tasks=2        # Some unassigned tasks
    )
    
    print(f"Score: {result['score']}")
    print(f"Status: {result['status']} {result['emoji']}")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()


if __name__ == "__main__":
    example_healthy_meeting()
    example_at_risk_meeting()
    example_critical_meeting()
    example_too_many_action_items()

# Made with Bob
