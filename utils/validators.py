"""
Input validation utilities for AI Meeting Rescue Agent
"""
from typing import Dict, Any, Tuple


def validate_transcript_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate transcript input data
    
    Args:
        data: Input data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if data exists
    if not data:
        return False, "Request body is empty"
    
    # Check if transcript field exists
    if 'transcript' not in data:
        return False, "Missing required field: 'transcript'"
    
    # Check if transcript is a string
    transcript = data.get('transcript')
    if not isinstance(transcript, str):
        return False, "Field 'transcript' must be a string"
    
    # Check if transcript is not empty
    if not transcript.strip():
        return False, "Field 'transcript' cannot be empty"
    
    # Check transcript length (minimum)
    if len(transcript.strip()) < 10:
        return False, "Transcript is too short (minimum 10 characters)"
    
    # Check transcript length (maximum - 100KB)
    max_length = 100 * 1024  # 100KB
    if len(transcript) > max_length:
        return False, f"Transcript is too long (maximum {max_length} characters)"
    
    # Validate metadata if provided
    if 'metadata' in data:
        metadata = data.get('metadata')
        if not isinstance(metadata, dict):
            return False, "Field 'metadata' must be a dictionary"
        
        # Validate participants if provided
        if 'participants' in metadata:
            participants = metadata.get('participants')
            if not isinstance(participants, list):
                return False, "Field 'metadata.participants' must be a list"
            
            # Check if all participants are strings
            if not all(isinstance(p, str) for p in participants):
                return False, "All participants must be strings"
    
    # All validations passed
    return True, ""


def validate_skill_name(skill_name: str) -> Tuple[bool, str]:
    """
    Validate skill name
    
    Args:
        skill_name: Name of the skill
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_skills = [
        'transcript_parser',
        'confusion_detector',
        'decision_extractor',
        'action_item_parser',
        'blocker_identifier'
    ]
    
    if not skill_name:
        return False, "Skill name is required"
    
    if skill_name not in valid_skills:
        return False, f"Invalid skill name. Must be one of: {', '.join(valid_skills)}"
    
    return True, ""


def validate_meeting_id(meeting_id: str) -> Tuple[bool, str]:
    """
    Validate meeting ID format
    
    Args:
        meeting_id: Meeting identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not meeting_id:
        return False, "Meeting ID is required"
    
    if not isinstance(meeting_id, str):
        return False, "Meeting ID must be a string"
    
    if len(meeting_id) > 255:
        return False, "Meeting ID is too long (maximum 255 characters)"
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', meeting_id):
        return False, "Meeting ID can only contain alphanumeric characters, hyphens, and underscores"
    
    return True, ""

# Made with Bob
