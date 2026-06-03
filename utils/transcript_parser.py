"""
Transcript Parser Utility
Parses Microsoft Teams meeting transcripts from JSON or TXT format
"""
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class TranscriptParser:
    """
    Parses Microsoft Teams meeting transcripts from JSON or TXT format
    
    Supported formats:
    - JSON: {"meeting_title": "...", "messages": [{"timestamp": "HH:MM:SS", "speaker": "...", "text": "..."}]}
    - TXT: [HH:MM:SS] Speaker: Text
    """
    
    # Regex pattern for TXT format: [HH:MM:SS] Speaker: Text
    TXT_PATTERN = r'\[(\d{2}:\d{2}:\d{2})\]\s+([^:]+):\s+(.+)'
    
    def __init__(self):
        """Initialize the transcript parser"""
        self.supported_formats = ['json', 'txt']
    
    def parse(self, transcript_data: str, format_type: str) -> Dict[str, Any]:
        """
        Main parsing method for transcript data
        
        Args:
            transcript_data: Raw transcript data as string
            format_type: Format type ('json' or 'txt')
            
        Returns:
            Dictionary containing:
                - parsed_transcript: List of message dictionaries
                - metadata: Dictionary with meeting metadata
                
        Raises:
            ValueError: If format_type is not supported or data is invalid
        """
        format_type = format_type.lower()
        
        if format_type not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        try:
            logger.info(f"Parsing transcript in {format_type.upper()} format")
            
            if format_type == 'json':
                parsed_transcript = self._parse_json(transcript_data)
            else:  # txt
                parsed_transcript = self._parse_txt(transcript_data)
            
            # Extract metadata
            metadata = self._extract_metadata(parsed_transcript)
            
            logger.info(
                f"Successfully parsed transcript: {len(parsed_transcript)} messages, "
                f"{metadata['total_speakers']} speakers"
            )
            
            return {
                'parsed_transcript': parsed_transcript,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error parsing transcript: {str(e)}", exc_info=True)
            raise
    
    def _parse_json(self, transcript_data: str) -> List[Dict[str, Any]]:
        """
        Parse JSON format transcript
        
        Expected structure:
        {
            "meeting_title": "..." or "title": "...",
            "date": "YYYY-MM-DD" (optional),
            "messages": [...] or "transcript": [...]
        }
        
        Each message/transcript item should have:
        {
            "timestamp": "HH:MM:SS",
            "speaker": "...",
            "text": "..."
        }
        
        Args:
            transcript_data: JSON string
            
        Returns:
            List of parsed message dictionaries
            
        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(transcript_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object/dictionary")
        
        # Check for either 'messages' or 'transcript' field
        if 'messages' in data:
            messages = data['messages']
        elif 'transcript' in data:
            messages = data['transcript']
        else:
            raise ValueError("JSON must contain either 'messages' or 'transcript' field")
        
        if not isinstance(messages, list):
            raise ValueError("'messages' or 'transcript' must be an array")
        
        parsed_messages = []
        
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                logger.warning(f"Skipping invalid message at index {i}: not a dictionary")
                continue
            
            # Validate required fields
            if 'timestamp' not in msg or 'speaker' not in msg or 'text' not in msg:
                logger.warning(f"Skipping message at index {i}: missing required fields")
                continue
            
            # Parse timestamp
            timestamp_obj = self._parse_timestamp(msg['timestamp'])
            
            # Get meeting title from either 'meeting_title' or 'title' field
            meeting_title = data.get('meeting_title') or data.get('title', 'Untitled Meeting')
            
            parsed_messages.append({
                'timestamp': msg['timestamp'],
                'timestamp_obj': timestamp_obj,
                'speaker': msg['speaker'].strip(),
                'text': msg['text'].strip(),
                'meeting_title': meeting_title,
                'date': data.get('date', None)
            })
        
        if not parsed_messages:
            raise ValueError("No valid messages found in transcript")
        
        return parsed_messages
    
    def _parse_txt(self, transcript_data: str) -> List[Dict[str, Any]]:
        """
        Parse TXT format transcript using regex
        
        Expected pattern: [HH:MM:SS] Speaker: Text
        
        Args:
            transcript_data: Plain text string
            
        Returns:
            List of parsed message dictionaries
            
        Raises:
            ValueError: If no valid messages found
        """
        lines = transcript_data.strip().split('\n')
        parsed_messages = []
        
        # Try to extract meeting title from first line if it doesn't match pattern
        meeting_title = "Untitled Meeting"
        start_index = 0
        
        if lines and not re.match(self.TXT_PATTERN, lines[0]):
            meeting_title = lines[0].strip()
            start_index = 1
        
        for i, line in enumerate(lines[start_index:], start=start_index):
            line = line.strip()
            if not line:
                continue
            
            match = re.match(self.TXT_PATTERN, line)
            if match:
                timestamp_str, speaker, text = match.groups()
                
                # Parse timestamp
                timestamp_obj = self._parse_timestamp(timestamp_str)
                
                parsed_messages.append({
                    'timestamp': timestamp_str,
                    'timestamp_obj': timestamp_obj,
                    'speaker': speaker.strip(),
                    'text': text.strip(),
                    'meeting_title': meeting_title,
                    'date': None
                })
            else:
                logger.debug(f"Line {i} doesn't match pattern: {line[:50]}...")
        
        if not parsed_messages:
            raise ValueError(
                "No valid messages found in transcript. "
                "Expected format: [HH:MM:SS] Speaker: Text"
            )
        
        return parsed_messages
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Convert timestamp string to datetime object
        
        Args:
            timestamp_str: Timestamp in format "HH:MM:SS"
            
        Returns:
            datetime object (date set to today, time from timestamp)
            
        Raises:
            ValueError: If timestamp format is invalid
        """
        try:
            # Parse time components
            time_obj = datetime.strptime(timestamp_str, "%H:%M:%S").time()
            
            # Create datetime with today's date
            return datetime.combine(datetime.today().date(), time_obj)
            
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format '{timestamp_str}': {str(e)}")
    
    def _extract_metadata(self, parsed_transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract metadata from parsed transcript
        
        Args:
            parsed_transcript: List of parsed message dictionaries
            
        Returns:
            Dictionary containing:
                - meeting_title: Title of the meeting
                - total_speakers: Number of unique speakers
                - speaker_list: List of unique speaker names
                - duration_minutes: Meeting duration in minutes
                - total_messages: Total number of messages
                - date: Meeting date (if available)
                - start_time: First message timestamp
                - end_time: Last message timestamp
        """
        if not parsed_transcript:
            return {
                'meeting_title': 'Untitled Meeting',
                'total_speakers': 0,
                'speaker_list': [],
                'duration_minutes': 0,
                'total_messages': 0,
                'date': None,
                'start_time': None,
                'end_time': None
            }
        
        # Extract unique speakers
        speakers = set(msg['speaker'] for msg in parsed_transcript)
        speaker_list = sorted(list(speakers))
        
        # Get meeting title (from first message)
        meeting_title = parsed_transcript[0].get('meeting_title', 'Untitled Meeting')
        
        # Get date (from first message if available)
        date = parsed_transcript[0].get('date', None)
        
        # Calculate duration
        first_timestamp = parsed_transcript[0]['timestamp_obj']
        last_timestamp = parsed_transcript[-1]['timestamp_obj']
        
        # Handle case where meeting crosses midnight
        if last_timestamp < first_timestamp:
            last_timestamp += timedelta(days=1)
        
        duration = last_timestamp - first_timestamp
        duration_minutes = int(duration.total_seconds() / 60)
        
        return {
            'meeting_title': meeting_title,
            'total_speakers': len(speakers),
            'speaker_list': speaker_list,
            'duration_minutes': duration_minutes,
            'total_messages': len(parsed_transcript),
            'date': date,
            'start_time': parsed_transcript[0]['timestamp'],
            'end_time': parsed_transcript[-1]['timestamp']
        }
    
    def format_for_llm(self, parsed_data: Dict[str, Any]) -> str:
        """
        Format parsed transcript for LLM consumption
        
        Args:
            parsed_data: Dictionary from parse() method containing
                        parsed_transcript and metadata
            
        Returns:
            Formatted string with one message per line: [HH:MM:SS] Speaker: Text
        """
        parsed_transcript = parsed_data['parsed_transcript']
        metadata = parsed_data['metadata']
        
        # Build header
        lines = []
        lines.append(f"Meeting: {metadata['meeting_title']}")
        
        if metadata['date']:
            lines.append(f"Date: {metadata['date']}")
        
        lines.append(f"Duration: {metadata['duration_minutes']} minutes")
        lines.append(f"Participants: {', '.join(metadata['speaker_list'])}")
        lines.append(f"Total Messages: {metadata['total_messages']}")
        lines.append("")
        lines.append("Transcript:")
        lines.append("-" * 80)
        
        # Format messages
        for msg in parsed_transcript:
            lines.append(f"[{msg['timestamp']}] {msg['speaker']}: {msg['text']}")
        
        return "\n".join(lines)


# Made with Bob