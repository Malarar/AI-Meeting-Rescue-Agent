"""
Summary Generator
Generates executive meeting summaries using Granite LLM
"""
import logging
import json
import os
from typing import Dict, List, Any, Optional
from services.granite_client import GraniteClient

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Generates executive meeting summaries using Granite LLM
    
    Creates structured summaries including:
    - Executive summary (2-3 sentences)
    - Key highlights (3-5 bullets)
    - Top 3 priorities
    - Red flags
    - Next steps
    """
    
    # Default values if LLM fails
    DEFAULT_OUTPUT = {
        "executive_summary": "Meeting summary unavailable due to processing error.",
        "key_highlights": [
            "Unable to generate highlights"
        ],
        "top_priorities": [
            "Review meeting recording for details"
        ],
        "red_flags": [
            "Summary generation failed - manual review required"
        ],
        "next_steps": [
            "Manually review meeting notes and create action items"
        ]
    }
    
    # LLM parameters
    TEMPERATURE = 0.4
    MAX_TOKENS = 2000
    
    def __init__(self, prompt_template_path: str = "prompts/summary_prompt.txt"):
        """
        Initialize the summary generator
        
        Args:
            prompt_template_path: Path to the prompt template file
            
        Raises:
            FileNotFoundError: If prompt template file doesn't exist
        """
        self.granite_client = GraniteClient()
        self.prompt_template_path = prompt_template_path
        self.prompt_template = self._load_prompt_template()
        
        logger.info("SummaryGenerator initialized successfully")
    
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from file
        
        Returns:
            The prompt template as a string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        if not os.path.exists(self.prompt_template_path):
            raise FileNotFoundError(
                f"Prompt template not found: {self.prompt_template_path}"
            )
        
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        logger.debug(f"Loaded prompt template from {self.prompt_template_path}")
        return template
    
    def generate(
        self,
        metadata: Dict[str, Any],
        confusion: Dict[str, Any],
        decisions: List[Dict[str, Any]],
        action_items: List[Dict[str, Any]],
        blockers: List[Dict[str, Any]],
        health: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate executive meeting summary
        
        Args:
            metadata: Meeting metadata (title, date, participants, etc.)
            confusion: Confusion analysis results
            decisions: List of decisions made
            action_items: List of action items
            blockers: List of blockers identified
            health: Meeting health score and status
            
        Returns:
            Dictionary containing:
            - executive_summary: str
            - key_highlights: List[str]
            - top_priorities: List[str]
            - red_flags: List[str]
            - next_steps: List[str]
        """
        try:
            logger.info("Generating executive meeting summary")
            
            # Format inputs for the prompt
            formatted_metadata = self._format_metadata(metadata)
            formatted_confusion = self._format_confusion(confusion)
            formatted_decisions = self._format_decisions(decisions)
            formatted_action_items = self._format_action_items(action_items)
            formatted_blockers = self._format_blockers(blockers)
            formatted_health = self._format_health(health)
            
            # Build the prompt
            prompt = self.prompt_template.format(
                metadata=formatted_metadata,
                confusion=formatted_confusion,
                decisions=formatted_decisions,
                action_items=formatted_action_items,
                blockers=formatted_blockers,
                health=formatted_health
            )
            
            logger.debug(f"Generated prompt length: {len(prompt)}")
            
            # Generate summary using Granite LLM
            result = self.granite_client.generate_json(
                prompt=prompt,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Validate and clean the result
            validated_result = self._validate_output(result)
            
            logger.info("Successfully generated executive summary")
            return validated_result
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            logger.warning("Returning default summary due to error")
            return self.DEFAULT_OUTPUT.copy()
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format meeting metadata for the prompt"""
        if not metadata:
            return "No metadata available"
        
        formatted = []
        if 'title' in metadata:
            formatted.append(f"Title: {metadata['title']}")
        if 'date' in metadata:
            formatted.append(f"Date: {metadata['date']}")
        if 'duration' in metadata:
            formatted.append(f"Duration: {metadata['duration']}")
        if 'participants' in metadata:
            participants = metadata['participants']
            if isinstance(participants, list):
                formatted.append(f"Participants: {', '.join(participants)}")
            else:
                formatted.append(f"Participants: {participants}")
        
        return '\n'.join(formatted) if formatted else "No metadata available"
    
    def _format_confusion(self, confusion: Dict[str, Any]) -> str:
        """Format confusion analysis for the prompt"""
        if not confusion:
            return "No confusion analysis available"
        
        score = confusion.get('confusion_score', 0.0)
        confused_topics = confusion.get('confused_topics', [])
        unanswered = confusion.get('unanswered_questions', [])
        
        formatted = [f"Confusion Score: {score:.2f}"]
        
        if confused_topics:
            formatted.append(f"Confused Topics: {len(confused_topics)}")
            for topic in confused_topics[:3]:  # Limit to top 3
                if isinstance(topic, dict):
                    formatted.append(f"  - {topic.get('topic', 'Unknown')}")
        
        if unanswered:
            formatted.append(f"Unanswered Questions: {len(unanswered)}")
            for q in unanswered[:3]:  # Limit to top 3
                formatted.append(f"  - {q}")
        
        return '\n'.join(formatted)
    
    def _format_decisions(self, decisions: List[Dict[str, Any]]) -> str:
        """Format decisions for the prompt"""
        if not decisions:
            return "No decisions made"
        
        formatted = [f"Total Decisions: {len(decisions)}"]
        for i, decision in enumerate(decisions[:5], 1):  # Limit to top 5
            if isinstance(decision, dict):
                desc = decision.get('decision', decision.get('description', 'Unknown'))
                formatted.append(f"{i}. {desc}")
        
        return '\n'.join(formatted)
    
    def _format_action_items(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items for the prompt"""
        if not action_items:
            return "No action items identified"
        
        formatted = [f"Total Action Items: {len(action_items)}"]
        for i, item in enumerate(action_items[:5], 1):  # Limit to top 5
            if isinstance(item, dict):
                desc = item.get('action', item.get('description', 'Unknown'))
                owner = item.get('owner', 'Unassigned')
                formatted.append(f"{i}. {desc} (Owner: {owner})")
        
        return '\n'.join(formatted)
    
    def _format_blockers(self, blockers: List[Dict[str, Any]]) -> str:
        """Format blockers for the prompt"""
        if not blockers:
            return "No blockers identified"
        
        formatted = [f"Total Blockers: {len(blockers)}"]
        for i, blocker in enumerate(blockers, 1):
            if isinstance(blocker, dict):
                desc = blocker.get('blocker', blocker.get('description', 'Unknown'))
                severity = blocker.get('severity', 'Unknown')
                formatted.append(f"{i}. [{severity}] {desc}")
        
        return '\n'.join(formatted)
    
    def _format_health(self, health: Dict[str, Any]) -> str:
        """Format health score for the prompt"""
        if not health:
            return "No health score available"
        
        score = health.get('score', 0)
        status = health.get('status', 'unknown')
        emoji = health.get('emoji', '')
        
        formatted = [
            f"Score: {score}/100",
            f"Status: {status} {emoji}"
        ]
        
        recommendations = health.get('recommendations', [])
        if recommendations:
            formatted.append(f"Key Recommendations: {len(recommendations)}")
            for rec in recommendations[:3]:  # Limit to top 3
                formatted.append(f"  - {rec}")
        
        return '\n'.join(formatted)
    
    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the LLM output
        
        Args:
            result: Raw output from LLM
            
        Returns:
            Validated and cleaned output
        """
        validated = {}
        
        # Validate executive_summary
        validated['executive_summary'] = str(
            result.get('executive_summary', self.DEFAULT_OUTPUT['executive_summary'])
        ).strip()
        
        # Validate key_highlights (must be list of strings)
        highlights = result.get('key_highlights', [])
        if isinstance(highlights, list):
            validated['key_highlights'] = [
                str(h).strip() for h in highlights if h
            ][:5]  # Max 5
        else:
            validated['key_highlights'] = self.DEFAULT_OUTPUT['key_highlights']
        
        if not validated['key_highlights']:
            validated['key_highlights'] = self.DEFAULT_OUTPUT['key_highlights']
        
        # Validate top_priorities (must be list of strings, exactly 3)
        priorities = result.get('top_priorities', [])
        if isinstance(priorities, list):
            validated['top_priorities'] = [
                str(p).strip() for p in priorities if p
            ][:3]  # Max 3
        else:
            validated['top_priorities'] = self.DEFAULT_OUTPUT['top_priorities']
        
        if not validated['top_priorities']:
            validated['top_priorities'] = self.DEFAULT_OUTPUT['top_priorities']
        
        # Validate red_flags (must be list of strings, can be empty)
        red_flags = result.get('red_flags', [])
        if isinstance(red_flags, list):
            validated['red_flags'] = [
                str(f).strip() for f in red_flags if f
            ]
        else:
            validated['red_flags'] = []
        
        # Validate next_steps (must be list of strings)
        next_steps = result.get('next_steps', [])
        if isinstance(next_steps, list):
            validated['next_steps'] = [
                str(s).strip() for s in next_steps if s
            ]
        else:
            validated['next_steps'] = self.DEFAULT_OUTPUT['next_steps']
        
        if not validated['next_steps']:
            validated['next_steps'] = self.DEFAULT_OUTPUT['next_steps']
        
        return validated


# Made with Bob