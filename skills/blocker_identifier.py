"""
Blocker Identifier
Identifies blockers and risks from meeting transcripts using Granite LLM
"""
import logging
import os
from typing import Dict, List, Any
from services.granite_client import GraniteClient

logger = logging.getLogger(__name__)


class BlockerIdentifier:
    """
    Identifies blockers and risks from meeting transcripts using Granite LLM
    
    Detects blocker phrases:
    - "Blocked by"
    - "Waiting on"
    - "Can't proceed until"
    - "Risk that"
    - "Concern about"
    - "Dependency on"
    
    Extracts: description, type, severity, blocking entity, owner, impact, timestamp
    """
    
    # Default values if LLM fails
    DEFAULT_OUTPUT = {
        "blockers": [],
        "total_blockers": 0,
        "critical_blockers": 0
    }
    
    # LLM parameters
    TEMPERATURE = 0.2
    MAX_TOKENS = 2000
    
    def __init__(self, prompt_template_path: str = "prompts/blocker_prompt.txt"):
        """
        Initialize the blocker identifier
        
        Args:
            prompt_template_path: Path to the prompt template file
            
        Raises:
            FileNotFoundError: If prompt template file doesn't exist
        """
        self.granite_client = GraniteClient()
        self.prompt_template_path = prompt_template_path
        self.prompt_template = self._load_prompt_template()
        
        logger.info("BlockerIdentifier initialized successfully")
    
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
    
    def identify(self, transcript_text: str) -> Dict[str, Any]:
        """
        Run blocker identification on transcript
        
        Args:
            transcript_text: The meeting transcript text to analyze
            
        Returns:
            Dictionary with structure:
            {
                "blockers": [
                    {
                        "id": str,
                        "description": str,
                        "type": str (technical/resource/dependency/external/approval),
                        "severity": str (critical/high/medium/low),
                        "blocking": str,
                        "owner": str,
                        "impact": str,
                        "mentioned_at": str
                    }
                ],
                "total_blockers": int,
                "critical_blockers": int
            }
        """
        try:
            logger.info("Starting blocker identification")
            
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
                f"Blocker identification completed. "
                f"Total: {validated_result['total_blockers']}, "
                f"Critical: {validated_result['critical_blockers']}"
            )
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error in blocker identification: {str(e)}", exc_info=True)
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
        
        # Validate blockers array
        if 'blockers' in result and isinstance(result['blockers'], list):
            validated_blockers = []
            critical_count = 0
            
            for blocker in result['blockers']:
                if isinstance(blocker, dict):
                    # Validate type
                    blocker_type = str(blocker.get('type', 'dependency')).lower()
                    if blocker_type not in ['technical', 'resource', 'dependency', 'external', 'approval']:
                        blocker_type = 'dependency'
                    
                    # Validate severity
                    severity = str(blocker.get('severity', 'medium')).lower()
                    if severity not in ['critical', 'high', 'medium', 'low']:
                        severity = 'medium'
                    
                    if severity == 'critical':
                        critical_count += 1
                    
                    validated_blockers.append({
                        'id': str(blocker.get('id', f'BLK-{len(validated_blockers)+1:03d}')),
                        'description': str(blocker.get('description', 'Unknown blocker')),
                        'type': blocker_type,
                        'severity': severity,
                        'blocking': str(blocker.get('blocking', 'Unknown')),
                        'owner': str(blocker.get('owner', 'Unassigned')),
                        'impact': str(blocker.get('impact', 'Unknown impact')),
                        'mentioned_at': str(blocker.get('mentioned_at', 'N/A'))
                    })
            
            validated['blockers'] = validated_blockers
            validated['total_blockers'] = len(validated_blockers)
            validated['critical_blockers'] = critical_count
        
        # Validate total_blockers
        if 'total_blockers' in result and isinstance(result['total_blockers'], int):
            # Ensure it matches the actual count
            validated['total_blockers'] = len(validated['blockers'])
        
        # Validate critical_blockers
        if 'critical_blockers' in result and isinstance(result['critical_blockers'], int):
            # Recalculate to ensure accuracy
            validated['critical_blockers'] = sum(
                1 for blocker in validated['blockers']
                if blocker['severity'] == 'critical'
            )
        
        return validated
    
    def get_summary(self, identification_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of blocker identification results
        
        Args:
            identification_result: Result from identify() method
            
        Returns:
            Summary string
        """
        total = identification_result['total_blockers']
        critical = identification_result['critical_blockers']
        
        if total == 0:
            return "No blockers were identified in the meeting."
        
        blockers = identification_result['blockers']
        
        # Count by severity
        high = sum(1 for b in blockers if b['severity'] == 'high')
        medium = sum(1 for b in blockers if b['severity'] == 'medium')
        low = sum(1 for b in blockers if b['severity'] == 'low')
        
        # Count by type
        technical = sum(1 for b in blockers if b['type'] == 'technical')
        resource = sum(1 for b in blockers if b['type'] == 'resource')
        dependency = sum(1 for b in blockers if b['type'] == 'dependency')
        
        summary_parts = [
            f"Total Blockers: {total}",
            f"Critical: {critical}",
            f"High: {high}",
            f"Medium: {medium}",
            f"Low: {low}"
        ]
        
        if critical > 0:
            summary_parts.append(f"⚠️ {critical} CRITICAL blocker(s) need immediate attention!")
        
        return " | ".join(summary_parts)
    
    def get_by_type(self, identification_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group blockers by type
        
        Args:
            identification_result: Result from identify() method
            
        Returns:
            Dictionary mapping blocker types to their blockers
        """
        by_type = {
            'technical': [],
            'resource': [],
            'dependency': [],
            'external': [],
            'approval': []
        }
        
        for blocker in identification_result['blockers']:
            blocker_type = blocker['type']
            if blocker_type in by_type:
                by_type[blocker_type].append(blocker)
        
        return by_type
    
    def get_by_severity(self, identification_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group blockers by severity
        
        Args:
            identification_result: Result from identify() method
            
        Returns:
            Dictionary mapping severity levels to their blockers
        """
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for blocker in identification_result['blockers']:
            severity = blocker['severity']
            if severity in by_severity:
                by_severity[severity].append(blocker)
        
        return by_severity
    
    def get_critical_blockers(self, identification_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and return only critical blockers
        
        Args:
            identification_result: Result from identify() method
            
        Returns:
            List of critical blocker dictionaries
        """
        return [
            blocker for blocker in identification_result['blockers']
            if blocker['severity'] == 'critical'
        ]
    
    def get_unassigned_blockers(self, identification_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and return blockers without assigned owners
        
        Args:
            identification_result: Result from identify() method
            
        Returns:
            List of unassigned blocker dictionaries
        """
        return [
            blocker for blocker in identification_result['blockers']
            if blocker['owner'] == 'Unassigned'
        ]


# Made with Bob