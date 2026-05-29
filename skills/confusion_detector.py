"""
Confusion Detector
Detects confusion signals in meeting transcripts using Granite LLM
"""
import logging
import os
from typing import Dict, List, Any
from services.granite_client import GraniteClient

logger = logging.getLogger(__name__)


class ConfusionDetector:
    """
    Detects confusion signals in meeting transcripts using Granite LLM
    
    Identifies:
    - Confusion phrases: "I'm lost", "wait what?", "can you clarify?", "I don't understand"
    - Topics discussed multiple times without resolution
    - Unanswered questions
    - Calculates confusion score (0.0 = clear, 1.0 = very confusing)
    """
    
    # Default values if LLM fails
    DEFAULT_OUTPUT = {
        "confusion_score": 0.0,
        "confused_topics": [],
        "unanswered_questions": [],
        "confusion_signals": []
    }
    
    # LLM parameters
    TEMPERATURE = 0.3
    MAX_TOKENS = 1500
    
    def __init__(self, prompt_template_path: str = "prompts/confusion_prompt.txt"):
        """
        Initialize the confusion detector
        
        Args:
            prompt_template_path: Path to the prompt template file
            
        Raises:
            FileNotFoundError: If prompt template file doesn't exist
        """
        self.granite_client = GraniteClient()
        self.prompt_template_path = prompt_template_path
        self.prompt_template = self._load_prompt_template()
        
        logger.info("ConfusionDetector initialized successfully")
    
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
    
    def detect(self, transcript_text: str) -> Dict[str, Any]:
        """
        Run confusion detection on transcript
        
        Args:
            transcript_text: The meeting transcript text to analyze
            
        Returns:
            Dictionary with structure:
            {
                "confusion_score": float (0.0-1.0),
                "confused_topics": [
                    {
                        "topic": str,
                        "timestamp": str,
                        "indicators": [str]
                    }
                ],
                "unanswered_questions": [str],
                "confusion_signals": [
                    {
                        "timestamp": str,
                        "speaker": str,
                        "signal": str
                    }
                ]
            }
        """
        try:
            logger.info("Starting confusion detection")
            
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
                f"Confusion detection completed. Score: {validated_result['confusion_score']:.2f}, "
                f"Signals: {len(validated_result['confusion_signals'])}, "
                f"Confused topics: {len(validated_result['confused_topics'])}"
            )
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error in confusion detection: {str(e)}", exc_info=True)
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
        
        # Validate confusion_score
        if 'confusion_score' in result:
            score = result['confusion_score']
            if isinstance(score, (int, float)):
                validated['confusion_score'] = max(0.0, min(1.0, float(score)))
            else:
                logger.warning(f"Invalid confusion_score type: {type(score)}")
        
        # Validate confused_topics
        if 'confused_topics' in result and isinstance(result['confused_topics'], list):
            validated_topics = []
            for topic in result['confused_topics']:
                if isinstance(topic, dict):
                    validated_topics.append({
                        'topic': str(topic.get('topic', 'Unknown')),
                        'timestamp': str(topic.get('timestamp', 'N/A')),
                        'indicators': [str(i) for i in topic.get('indicators', [])]
                    })
            validated['confused_topics'] = validated_topics
        
        # Validate unanswered_questions
        if 'unanswered_questions' in result and isinstance(result['unanswered_questions'], list):
            validated['unanswered_questions'] = [
                str(q) for q in result['unanswered_questions']
            ]
        
        # Validate confusion_signals
        if 'confusion_signals' in result and isinstance(result['confusion_signals'], list):
            validated_signals = []
            for signal in result['confusion_signals']:
                if isinstance(signal, dict):
                    validated_signals.append({
                        'timestamp': str(signal.get('timestamp', 'N/A')),
                        'speaker': str(signal.get('speaker', 'Unknown')),
                        'signal': str(signal.get('signal', ''))
                    })
            validated['confusion_signals'] = validated_signals
        
        return validated
    
    def get_summary(self, detection_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of confusion detection results
        
        Args:
            detection_result: Result from detect() method
            
        Returns:
            Summary string
        """
        score = detection_result['confusion_score']
        num_signals = len(detection_result['confusion_signals'])
        num_topics = len(detection_result['confused_topics'])
        num_questions = len(detection_result['unanswered_questions'])
        
        # Determine clarity level
        if score < 0.2:
            clarity = "very clear"
        elif score < 0.4:
            clarity = "mostly clear"
        elif score < 0.6:
            clarity = "somewhat confusing"
        elif score < 0.8:
            clarity = "confusing"
        else:
            clarity = "very confusing"
        
        summary_parts = [
            f"Confusion Score: {score:.2f} ({clarity})",
            f"Confusion Signals: {num_signals}",
            f"Confused Topics: {num_topics}",
            f"Unanswered Questions: {num_questions}"
        ]
        
        return " | ".join(summary_parts)


# Made with Bob