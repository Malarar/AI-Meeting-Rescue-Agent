"""
Action Item Parser
Extracts action items from meeting transcripts using Granite LLM
"""
import logging
import os
from typing import Dict, List, Any
from services.granite_client import GraniteClient

logger = logging.getLogger(__name__)


class ActionItemParser:
    """
    Extracts action items from meeting transcripts using Granite LLM
    
    Detects action item phrases:
    - "I'll do"
    - "Can you handle"
    - "[Name] will follow up"
    - Task assignments with deadlines
    
    Extracts: task description, owner, deadline (YYYY-MM-DD), priority, dependencies, timestamp
    """
    
    # Default values if LLM fails
    DEFAULT_OUTPUT = {
        "action_items": [],
        "total_action_items": 0,
        "unassigned_tasks": 0
    }
    
    # LLM parameters
    TEMPERATURE = 0.2
    MAX_TOKENS = 2000
    
    def __init__(self, prompt_template_path: str = "prompts/action_item_prompt.txt"):
        """
        Initialize the action item parser
        
        Args:
            prompt_template_path: Path to the prompt template file
            
        Raises:
            FileNotFoundError: If prompt template file doesn't exist
        """
        self.granite_client = GraniteClient()
        self.prompt_template_path = prompt_template_path
        self.prompt_template = self._load_prompt_template()
        
        logger.info("ActionItemParser initialized successfully")
    
    def _load_prompt_template(self) -> str:
        """
        Load prompt template from file
        
        Returns:
            Prompt template string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If file cannot be read
        """
        try:
            if not os.path.exists(self.prompt_template_path):
                raise FileNotFoundError(
                    f"Prompt template not found: {self.prompt_template_path}"
                )
            
            with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            logger.info(f"Loaded prompt template from {self.prompt_template_path}")
            return template
            
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}", exc_info=True)
            raise
    
    def parse(self, transcript_text: str) -> Dict[str, Any]:
        """
        Run action item parsing on transcript
        
        Args:
            transcript_text: The meeting transcript text to analyze
            
        Returns:
            Dictionary with structure:
            {
                "action_items": [
                    {
                        "id": str,
                        "task": str,
                        "owner": str,
                        "deadline": str (YYYY-MM-DD or "No deadline"),
                        "priority": str (urgent/high/medium/low),
                        "dependencies": [str],
                        "mentioned_at": str
                    }
                ],
                "total_action_items": int,
                "unassigned_tasks": int
            }
        """
        try:
            logger.info("Starting action item parsing")
            
            # Build prompt from template
            prompt = self.prompt_template.format(transcript=transcript_text)
            
            # Generate analysis using Granite LLM
            result = self.granite_client.generate_json(
                prompt=prompt,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Validate and normalize output
            validated_result = self._validate_output(result)
            
            logger.info(
                f"Action item parsing completed. "
                f"Total: {validated_result['total_action_items']}, "
                f"Unassigned: {validated_result['unassigned_tasks']}"
            )
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error in action item parsing: {str(e)}", exc_info=True)
            logger.warning("Returning default values due to error")
            return self.DEFAULT_OUTPUT.copy()
    
    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the LLM output
        
        Args:
            result: Raw result from LLM
            
        Returns:
            Validated and normalized result
        """
        validated = self.DEFAULT_OUTPUT.copy()
        
        # Validate action_items array
        if 'action_items' in result and isinstance(result['action_items'], list):
            validated_items = []
            unassigned_count = 0
            
            for item in result['action_items']:
                if isinstance(item, dict):
                    # Validate priority
                    priority = str(item.get('priority', 'medium')).lower()
                    if priority not in ['urgent', 'high', 'medium', 'low']:
                        priority = 'medium'
                    
                    # Validate dependencies
                    dependencies = item.get('dependencies', [])
                    if not isinstance(dependencies, list):
                        dependencies = []
                    dependencies = [str(d) for d in dependencies]
                    
                    # Validate owner
                    owner = str(item.get('owner', 'Unassigned'))
                    if owner.lower() in ['unassigned', 'unknown', 'tbd', 'to be determined', '']:
                        owner = 'Unassigned'
                        unassigned_count += 1
                    
                    validated_items.append({
                        'id': str(item.get('id', f'AI-{len(validated_items)+1:03d}')),
                        'task': str(item.get('task', 'Unknown task')),
                        'owner': owner,
                        'deadline': str(item.get('deadline', 'No deadline')),
                        'priority': priority,
                        'dependencies': dependencies,
                        'mentioned_at': str(item.get('mentioned_at', 'N/A'))
                    })
            
            validated['action_items'] = validated_items
            validated['total_action_items'] = len(validated_items)
            validated['unassigned_tasks'] = unassigned_count
        
        # Validate total_action_items
        if 'total_action_items' in result and isinstance(result['total_action_items'], int):
            # Ensure it matches the actual count
            validated['total_action_items'] = len(validated['action_items'])
        
        # Validate unassigned_tasks
        if 'unassigned_tasks' in result and isinstance(result['unassigned_tasks'], int):
            # Recalculate to ensure accuracy
            validated['unassigned_tasks'] = sum(
                1 for item in validated['action_items']
                if item['owner'] == 'Unassigned'
            )
        
        return validated
    
    def get_summary(self, parsing_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of action item parsing results
        
        Args:
            parsing_result: Result from parse() method
            
        Returns:
            Summary string
        """
        total = parsing_result['total_action_items']
        unassigned = parsing_result['unassigned_tasks']
        
        if total == 0:
            return "No action items were identified in the meeting."
        
        items = parsing_result['action_items']
        
        # Count by priority
        urgent = sum(1 for item in items if item['priority'] == 'urgent')
        high = sum(1 for item in items if item['priority'] == 'high')
        
        # Count with deadlines
        with_deadline = sum(1 for item in items if item['deadline'] != 'No deadline')
        
        summary_parts = [
            f"Total Action Items: {total}",
            f"Urgent: {urgent}",
            f"High Priority: {high}",
            f"With Deadlines: {with_deadline}"
        ]
        
        if unassigned > 0:
            summary_parts.append(f"⚠️ Unassigned: {unassigned}")
        
        return " | ".join(summary_parts)
    
    def get_by_owner(self, parsing_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group action items by owner
        
        Args:
            parsing_result: Result from parse() method
            
        Returns:
            Dictionary mapping owner names to their action items
        """
        by_owner = {}
        
        for item in parsing_result['action_items']:
            owner = item['owner']
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(item)
        
        return by_owner
    
    def get_by_priority(self, parsing_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group action items by priority
        
        Args:
            parsing_result: Result from parse() method
            
        Returns:
            Dictionary mapping priority levels to their action items
        """
        by_priority = {
            'urgent': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for item in parsing_result['action_items']:
            priority = item['priority']
            if priority in by_priority:
                by_priority[priority].append(item)
        
        return by_priority
    
    def get_urgent_items(self, parsing_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and return only urgent action items
        
        Args:
            parsing_result: Result from parse() method
            
        Returns:
            List of urgent action item dictionaries
        """
        return [
            item for item in parsing_result['action_items']
            if item['priority'] == 'urgent'
        ]
    
    def get_unassigned_items(self, parsing_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and return unassigned action items
        
        Args:
            parsing_result: Result from parse() method
            
        Returns:
            List of unassigned action item dictionaries
        """
        return [
            item for item in parsing_result['action_items']
            if item['owner'] == 'Unassigned'
        ]


# Made with Bob