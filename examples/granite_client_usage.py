"""
Example usage of GraniteClient for IBM watsonx.ai Granite LLM
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.granite_client import GraniteClient
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


def example_text_generation():
    """Example: Basic text generation"""
    print("\n=== Example 1: Basic Text Generation ===")
    
    try:
        # Initialize client
        client = GraniteClient()
        
        # Generate text
        prompt = "Explain what a meeting action item is in one sentence."
        response = client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error in text generation: {e}")


def example_json_generation():
    """Example: JSON-structured output"""
    print("\n=== Example 2: JSON Generation ===")
    
    try:
        # Initialize client
        client = GraniteClient()
        
        # Generate JSON
        prompt = """
        Extract action items from this meeting transcript and return as JSON.
        
        Transcript: "John will prepare the quarterly report by Friday. Sarah needs to schedule a follow-up meeting with the client."
        
        Return a JSON object with this structure:
        {
            "action_items": [
                {"assignee": "person name", "task": "task description", "deadline": "deadline if mentioned"}
            ]
        }
        """
        
        response = client.generate_json(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        print(f"Prompt: {prompt[:100]}...")
        print(f"JSON Response: {response}")
        print(f"Number of action items: {len(response.get('action_items', []))}")
        
    except Exception as e:
        logger.error(f"Error in JSON generation: {e}")


def example_with_stop_sequences():
    """Example: Using stop sequences"""
    print("\n=== Example 3: Generation with Stop Sequences ===")
    
    try:
        # Initialize client
        client = GraniteClient()
        
        # Generate with stop sequences
        prompt = "List three benefits of AI in meetings:\n1."
        response = client.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            stop_sequences=["\n4.", "Conclusion"]
        )
        
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error with stop sequences: {e}")


def example_markdown_json_handling():
    """Example: Handling JSON in markdown code blocks"""
    print("\n=== Example 4: Markdown JSON Handling ===")
    
    try:
        # Initialize client
        client = GraniteClient()
        
        # This prompt might return JSON wrapped in markdown
        prompt = """
        Create a JSON object representing a meeting summary with these fields:
        - title: "Weekly Team Sync"
        - date: "2024-01-15"
        - participants: ["Alice", "Bob", "Charlie"]
        - duration_minutes: 45
        
        Return only the JSON object.
        """
        
        response = client.generate_json(
            prompt=prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        print(f"Successfully parsed JSON from response")
        print(f"Meeting title: {response.get('title')}")
        print(f"Participants: {response.get('participants')}")
        
    except Exception as e:
        logger.error(f"Error handling markdown JSON: {e}")


def example_connection_test():
    """Example: Test connection"""
    print("\n=== Example 5: Connection Test ===")
    
    try:
        # Initialize client
        client = GraniteClient()
        
        # Test connection
        is_connected = client.test_connection()
        
        if is_connected:
            print("✓ Connection successful")
            
            # Get model info
            info = client.get_model_info()
            print(f"Model ID: {info['model_id']}")
            print(f"URL: {info['url']}")
            print(f"Project ID: {info['project_id']}")
        else:
            print("✗ Connection failed")
        
    except Exception as e:
        logger.error(f"Error testing connection: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("GraniteClient Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_text_generation()
    example_json_generation()
    example_with_stop_sequences()
    example_markdown_json_handling()
    example_connection_test()
    
    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()


# Made with Bob