"""
Meeting Analysis Workflow
Orchestrates the complete meeting analysis pipeline with parallel processing
"""
import logging
import time
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.transcript_parser import TranscriptParser
from skills.confusion_detector import ConfusionDetector
from skills.action_item_parser import ActionItemParser
from skills.blocker_identifier import BlockerIdentifier
from skills.summary_generator import SummaryGenerator
from utils.health_calculator import HealthCalculator

logger = logging.getLogger(__name__)


class MeetingAnalysisWorkflow:
    """
    Orchestrates the complete meeting analysis workflow
    
    Workflow stages:
    1. Parse transcript (sequential)
    2. Run 4 analysis skills in parallel (confusion, decisions, actions, blockers)
    3. Calculate health score (sequential, depends on step 2)
    4. Generate summary (sequential, depends on all previous steps)
    
    Uses ThreadPoolExecutor for parallel processing of independent analysis tasks.
    """
    
    def __init__(self):
        """
        Initialize all skill instances
        
        Raises:
            Exception: If any skill initialization fails
        """
        try:
            logger.info("Initializing MeetingAnalysisWorkflow")
            
            # Initialize transcript parser
            self.transcript_parser = TranscriptParser()
            logger.info("✓ TranscriptParser initialized")
            
            # Initialize analysis skills
            self.confusion_detector = ConfusionDetector()
            logger.info("✓ ConfusionDetector initialized")
            
            self.action_item_parser = ActionItemParser()
            logger.info("✓ ActionItemParser initialized")
            
            self.blocker_identifier = BlockerIdentifier()
            logger.info("✓ BlockerIdentifier initialized")
            
            # Initialize summary generator
            self.summary_generator = SummaryGenerator()
            logger.info("✓ SummaryGenerator initialized")
            
            # Health calculator is static, no initialization needed
            self.health_calculator = HealthCalculator
            logger.info("✓ HealthCalculator ready")
            
            logger.info("MeetingAnalysisWorkflow initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize MeetingAnalysisWorkflow: {str(e)}", exc_info=True)
            raise
    
    def analyze_meeting(
        self,
        transcript_data: str,
        format_type: str = "txt"
    ) -> Dict[str, Any]:
        """
        Run complete meeting analysis workflow
        
        Args:
            transcript_data: Raw transcript data as string
            format_type: Format type ('json' or 'txt')
            
        Returns:
            Dictionary containing:
            - metadata: Meeting metadata
            - transcript: Parsed transcript text
            - confusion: Confusion analysis results
            - decisions: Decision extraction results (placeholder)
            - action_items: Action items analysis
            - blockers: Blockers identification
            - health: Meeting health score and status
            - summary: Executive summary
            - processing_time_seconds: Total processing time
            
        Raises:
            ValueError: If transcript data or format is invalid
            Exception: If workflow execution fails
        """
        start_time = time.time()
        
        try:
            logger.info("=" * 80)
            logger.info("Starting Meeting Analysis Workflow")
            logger.info("=" * 80)
            
            # Stage 1: Parse transcript (sequential)
            print("\n[1/4] Parsing transcript...")
            logger.info("Stage 1: Parsing transcript")
            stage1_start = time.time()
            
            parsed_data = self.transcript_parser.parse(transcript_data, format_type)
            metadata = parsed_data.get('metadata', {})
            parsed_transcript = parsed_data.get('parsed_transcript', [])
            
            # Convert parsed transcript to text for analysis
            transcript_text = self._format_transcript_for_analysis(parsed_transcript)
            
            stage1_time = time.time() - stage1_start
            logger.info(f"✓ Transcript parsed in {stage1_time:.2f}s")
            print(f"   ✓ Parsed {len(parsed_transcript)} messages in {stage1_time:.2f}s")
            
            # Stage 2: Run analysis skills in parallel
            print("\n[2/4] Running parallel analysis (confusion, actions, blockers)...")
            logger.info("Stage 2: Running parallel analysis")
            stage2_start = time.time()
            
            analysis_results = self._run_parallel_analysis(transcript_text)
            
            stage2_time = time.time() - stage2_start
            logger.info(f"✓ Parallel analysis completed in {stage2_time:.2f}s")
            print(f"   ✓ Analysis completed in {stage2_time:.2f}s")
            
            # Stage 3: Calculate health score (sequential, depends on stage 2)
            print("\n[3/4] Calculating meeting health score...")
            logger.info("Stage 3: Calculating health score")
            stage3_start = time.time()
            
            health = self._calculate_health(analysis_results)
            
            stage3_time = time.time() - stage3_start
            logger.info(f"✓ Health score calculated in {stage3_time:.2f}s")
            print(f"   ✓ Health: {health['score']}/100 ({health['status']}) {health['emoji']}")
            
            # Stage 4: Generate summary (sequential, depends on all previous)
            print("\n[4/4] Generating executive summary...")
            logger.info("Stage 4: Generating executive summary")
            stage4_start = time.time()
            
            summary = self.summary_generator.generate(
                metadata=metadata,
                confusion=analysis_results['confusion'],
                decisions=analysis_results['decisions'],
                action_items=analysis_results['action_items']['action_items'],
                blockers=analysis_results['blockers']['blockers'],
                health=health
            )
            
            stage4_time = time.time() - stage4_start
            logger.info(f"✓ Summary generated in {stage4_time:.2f}s")
            print(f"   ✓ Summary generated in {stage4_time:.2f}s")
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Build comprehensive results
            results = {
                'metadata': metadata,
                'transcript': transcript_text,
                'confusion': analysis_results['confusion'],
                'decisions': analysis_results['decisions'],
                'action_items': analysis_results['action_items'],
                'blockers': analysis_results['blockers'],
                'health': health,
                'summary': summary,
                'processing_time_seconds': round(total_time, 2),
                'stage_times': {
                    'parsing': round(stage1_time, 2),
                    'parallel_analysis': round(stage2_time, 2),
                    'health_calculation': round(stage3_time, 2),
                    'summary_generation': round(stage4_time, 2)
                }
            }
            
            logger.info("=" * 80)
            logger.info(f"Meeting Analysis Workflow Complete - Total time: {total_time:.2f}s")
            logger.info("=" * 80)
            
            print(f"\n{'=' * 80}")
            print(f"✅ Analysis Complete - Total time: {total_time:.2f}s")
            print(f"{'=' * 80}\n")
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            raise
    
    def _format_transcript_for_analysis(self, parsed_transcript: List[Dict[str, Any]]) -> str:
        """
        Format parsed transcript into text for analysis
        
        Args:
            parsed_transcript: List of message dictionaries
            
        Returns:
            Formatted transcript text
        """
        if not parsed_transcript:
            return ""
        
        lines = []
        for msg in parsed_transcript:
            timestamp = msg.get('timestamp', '')
            speaker = msg.get('speaker', 'Unknown')
            text = msg.get('text', '')
            
            if timestamp:
                lines.append(f"[{timestamp}] {speaker}: {text}")
            else:
                lines.append(f"{speaker}: {text}")
        
        return '\n'.join(lines)
    
    def _run_parallel_analysis(self, transcript_text: str) -> Dict[str, Any]:
        """
        Run analysis skills in parallel using ThreadPoolExecutor
        
        Args:
            transcript_text: Formatted transcript text
            
        Returns:
            Dictionary with results from all analysis skills
        """
        results = {
            'confusion': None,
            'decisions': None,
            'action_items': None,
            'blockers': None
        }
        
        # Define analysis tasks
        tasks = {
            'confusion': lambda: self.confusion_detector.detect(transcript_text),
            'action_items': lambda: self.action_item_parser.parse(transcript_text),
            'blockers': lambda: self.blocker_identifier.identify(transcript_text)
        }
        
        # Note: DecisionExtractor v2 doesn't exist yet, so we'll use a placeholder
        # When it's implemented, add it to the tasks dict
        
        # Execute tasks in parallel with max 4 workers
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(task_func): task_name
                for task_name, task_func in tasks.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result()
                    results[task_name] = result
                    logger.info(f"   ✓ {task_name} analysis completed")
                    print(f"   ✓ {task_name.capitalize()} analysis completed")
                except Exception as e:
                    logger.error(f"   ✗ {task_name} analysis failed: {str(e)}")
                    print(f"   ✗ {task_name.capitalize()} analysis failed")
                    # Use default values on failure
                    if task_name == 'confusion':
                        results[task_name] = ConfusionDetector.DEFAULT_OUTPUT
                    elif task_name == 'action_items':
                        results[task_name] = ActionItemParser.DEFAULT_OUTPUT
                    elif task_name == 'blockers':
                        results[task_name] = BlockerIdentifier.DEFAULT_OUTPUT
        
        # Add placeholder for decisions (until DecisionExtractor v2 is implemented)
        results['decisions'] = []
        
        return results
    
    def _calculate_health(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate meeting health score based on analysis results
        
        Args:
            analysis_results: Results from parallel analysis
            
        Returns:
            Health score dictionary
        """
        # Extract metrics from analysis results
        confusion_score = analysis_results['confusion'].get('confusion_score', 0.0)
        decisions_count = len(analysis_results['decisions'])
        
        action_items_data = analysis_results['action_items']
        action_items_count = action_items_data.get('total_action_items', 0)
        unassigned_tasks = action_items_data.get('unassigned_tasks', 0)
        
        blockers_data = analysis_results['blockers']
        blockers_count = blockers_data.get('total_blockers', 0)
        
        # Calculate health score
        health = self.health_calculator.calculate(
            confusion_score=confusion_score,
            decisions_count=decisions_count,
            action_items_count=action_items_count,
            blockers_count=blockers_count,
            unassigned_tasks=unassigned_tasks
        )
        
        return health


# Made with Bob