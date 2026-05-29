"""
Decision Extractor Skill
Extracts key decisions made during meeting discussions
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DecisionExtractor:
    """Extracts and categorizes decisions from meeting transcripts"""
    
    def __init__(self, watsonx_service):
        """
        Initialize the decision extractor
        
        Args:
            watsonx_service: Instance of WatsonxService for LLM interactions
        """
        self.watsonx_service = watsonx_service
        self.skill_name = "decision_extractor"
    
    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract decisions from the meeting transcript
        
        Args:
            transcript: Raw meeting transcript text
            metadata: Optional metadata about the meeting
            
        Returns:
            Dictionary containing extracted decisions
        """
        try:
            logger.info(f"Starting {self.skill_name} analysis")
            
            # Build prompt for Granite LLM
            prompt = self._build_prompt(transcript)
            
            # Get analysis from Granite LLM
            response = self.watsonx_service.generate(prompt)
            
            # Parse and structure the response
            result = self._parse_response(response)
            
            logger.info(f"{self.skill_name} analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.skill_name}: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'skill': self.skill_name
            }
    
    def _build_prompt(self, transcript: str) -> str:
        """Build the prompt for Granite LLM"""
        
        prompt = f"""You are an expert at extracting key decisions from meeting discussions. Analyze the following meeting transcript and identify all decisions made.

Meeting Transcript:
{transcript}

Extract all decisions including:
1. Explicit decisions (e.g., "Let's go with...", "We've decided to...", "Agreed")
2. Implicit agreements or consensus
3. Approved proposals or plans
4. Rejected alternatives
5. Deferred decisions

For each decision, provide:
- Decision statement (what was decided)
- Decision maker(s) or who agreed
- Context/reasoning behind the decision
- Impact level (low, medium, high)
- Category (technical, business, process, resource, other)
- Related action items (if any)
- Quote from transcript

Format your response as a JSON object with:
- decisions: array of decision objects
- total_count: number of decisions
- by_category: count of decisions by category
- by_impact: count of decisions by impact level
- deferred_decisions: array of decisions that were postponed

Provide only the JSON response, no additional text."""
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        import json
        
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            
            decisions = parsed.get('decisions', [])
            
            return {
                'skill': self.skill_name,
                'status': 'success',
                'data': {
                    'decisions': decisions,
                    'total_count': parsed.get('total_count', len(decisions)),
                    'by_category': parsed.get('by_category', {}),
                    'by_impact': parsed.get('by_impact', {}),
                    'deferred_decisions': parsed.get('deferred_decisions', []),
                    'summary': self._generate_summary(parsed),
                    'high_impact_decisions': self._filter_high_impact(decisions)
                }
            }
        except json.JSONDecodeError:
            # If not valid JSON, return raw response
            logger.warning("Response is not valid JSON, returning raw response")
            return {
                'skill': self.skill_name,
                'status': 'partial',
                'data': {
                    'raw_response': response
                }
            }
    
    def _generate_summary(self, parsed_data: Dict[str, Any]) -> str:
        """Generate a summary of decisions"""
        total = parsed_data.get('total_count', 0)
        deferred = len(parsed_data.get('deferred_decisions', []))
        
        if total == 0:
            return "No explicit decisions were identified in the meeting."
        
        by_impact = parsed_data.get('by_impact', {})
        high_impact = by_impact.get('high', 0)
        
        summary = f"Identified {total} decisions"
        
        if high_impact > 0:
            summary += f", including {high_impact} high-impact decisions"
        
        if deferred > 0:
            summary += f". {deferred} decisions were deferred for later"
        
        return summary + "."
    
    def _filter_high_impact(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and return only high-impact decisions"""
        return [
            decision for decision in decisions
            if decision.get('impact_level', '').lower() == 'high'
        ]

# Made with Bob
