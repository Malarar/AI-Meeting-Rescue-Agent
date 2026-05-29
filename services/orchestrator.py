"""
Analysis Orchestrator
Manages parallel execution of analysis skills
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
from config import Config
from services.watsonx_service import WatsonxService
from utils.transcript_parser import TranscriptParser
from skills import (
    ConfusionDetector,
    DecisionExtractor,
    ActionItemParser,
    BlockerIdentifier
)

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """Orchestrates parallel execution of analysis skills"""
    
    def __init__(self):
        """Initialize the orchestrator with all skills"""
        logger.info("Initializing Analysis Orchestrator")
        
        # Initialize watsonx service
        self.watsonx_service = WatsonxService()
        
        # Initialize all skills
        self.skills = {
            'transcript_parser': TranscriptParser(),
            'confusion_detector': ConfusionDetector(),
            'decision_extractor': DecisionExtractor(self.watsonx_service),
            'action_item_parser': ActionItemParser(),
            'blocker_identifier': BlockerIdentifier()
        }
        
        # Configuration
        self.max_workers = Config.MAX_WORKERS
        self.timeout = Config.TIMEOUT_SECONDS
        
        logger.info(f"Orchestrator initialized with {len(self.skills)} skills")
    
    def analyze_all(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute all analysis skills in parallel
        
        Args:
            transcript: Meeting transcript text
            metadata: Optional meeting metadata
            
        Returns:
            Dictionary containing results from all skills
        """
        logger.info("Starting parallel analysis with all skills")
        
        results = {}
        
        # Execute skills in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_skill = {
                executor.submit(skill.analyze, transcript, metadata): skill_name
                for skill_name, skill in self.skills.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_skill, timeout=self.timeout):
                skill_name = future_to_skill[future]
                try:
                    result = future.result()
                    results[skill_name] = result
                    logger.info(f"Completed analysis for skill: {skill_name}")
                except Exception as e:
                    logger.error(f"Error in skill {skill_name}: {str(e)}", exc_info=True)
                    results[skill_name] = {
                        'skill': skill_name,
                        'status': 'error',
                        'error': str(e)
                    }
        
        logger.info("Parallel analysis completed for all skills")
        return results
    
    def analyze_single(self, skill_name: str, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a single analysis skill
        
        Args:
            skill_name: Name of the skill to execute
            transcript: Meeting transcript text
            metadata: Optional meeting metadata
            
        Returns:
            Dictionary containing result from the skill
        """
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")
        
        logger.info(f"Starting single skill analysis: {skill_name}")
        
        skill = self.skills[skill_name]
        result = skill.analyze(transcript, metadata)
        
        logger.info(f"Completed single skill analysis: {skill_name}")
        return result
    
    def analyze_subset(self, skill_names: List[str], transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a subset of analysis skills in parallel
        
        Args:
            skill_names: List of skill names to execute
            transcript: Meeting transcript text
            metadata: Optional meeting metadata
            
        Returns:
            Dictionary containing results from specified skills
        """
        # Validate skill names
        invalid_skills = [name for name in skill_names if name not in self.skills]
        if invalid_skills:
            raise ValueError(f"Unknown skills: {', '.join(invalid_skills)}")
        
        logger.info(f"Starting parallel analysis with {len(skill_names)} skills")
        
        results = {}
        
        # Execute specified skills in parallel
        with ThreadPoolExecutor(max_workers=min(len(skill_names), self.max_workers)) as executor:
            # Submit tasks for specified skills only
            future_to_skill = {
                executor.submit(self.skills[skill_name].analyze, transcript, metadata): skill_name
                for skill_name in skill_names
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_skill, timeout=self.timeout):
                skill_name = future_to_skill[future]
                try:
                    result = future.result()
                    results[skill_name] = result
                    logger.info(f"Completed analysis for skill: {skill_name}")
                except Exception as e:
                    logger.error(f"Error in skill {skill_name}: {str(e)}", exc_info=True)
                    results[skill_name] = {
                        'skill': skill_name,
                        'status': 'error',
                        'error': str(e)
                    }
        
        logger.info(f"Parallel analysis completed for {len(skill_names)} skills")
        return results
    
    def get_available_skills(self) -> List[str]:
        """
        Get list of available skill names
        
        Returns:
            List of skill names
        """
        return list(self.skills.keys())
    
    def test_skills(self) -> Dict[str, bool]:
        """
        Test all skills with a simple transcript
        
        Returns:
            Dictionary mapping skill names to test results (True/False)
        """
        logger.info("Testing all skills")
        
        test_transcript = """
        Alice: We need to decide on the database architecture.
        Bob: I'm confused about whether we should use SQL or NoSQL.
        Charlie: Let's go with PostgreSQL for now.
        Alice: Agreed. Bob, can you set up the initial schema by Friday?
        Bob: Sure, but I'm blocked on getting access to the dev environment.
        """
        
        results = {}
        for skill_name, skill in self.skills.items():
            try:
                result = skill.analyze(test_transcript)
                results[skill_name] = 'error' not in result
                logger.info(f"Skill {skill_name} test: {'PASS' if results[skill_name] else 'FAIL'}")
            except Exception as e:
                logger.error(f"Skill {skill_name} test failed: {str(e)}")
                results[skill_name] = False
        
        return results

# Made with Bob
