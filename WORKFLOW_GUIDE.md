# Meeting Analysis Workflow Guide

## Overview

The `MeetingAnalysisWorkflow` class orchestrates a complete meeting analysis pipeline that processes meeting transcripts through multiple AI-powered analysis stages, running independent tasks in parallel for optimal performance.

## Architecture

### Workflow Stages

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Parse Transcript (Sequential)                      │
│ - TranscriptParser extracts metadata and messages           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Parallel Analysis (ThreadPoolExecutor, 4 workers)  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Confusion   │ │ Action      │ │ Blockers    │           │
│ │ Detection   │ │ Items       │ │ Identifier  │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 3: Calculate Health Score (Sequential)                │
│ - HealthCalculator computes meeting health (0-100)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 4: Generate Summary (Sequential)                      │
│ - SummaryGenerator creates executive summary                │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. TranscriptParser
- **Purpose**: Parse raw transcript data into structured format
- **Input**: Raw transcript (JSON or TXT format)
- **Output**: Parsed messages with metadata
- **Processing**: Sequential (required for all subsequent stages)

### 2. ConfusionDetector
- **Purpose**: Identify confusion signals and unclear topics
- **Input**: Formatted transcript text
- **Output**: Confusion score (0-1), confused topics, unanswered questions
- **Processing**: Parallel (independent of other analyses)

### 3. ActionItemParser
- **Purpose**: Extract action items and task assignments
- **Input**: Formatted transcript text
- **Output**: Action items with owners, deadlines, priorities
- **Processing**: Parallel (independent of other analyses)

### 4. BlockerIdentifier
- **Purpose**: Identify blockers and risks
- **Input**: Formatted transcript text
- **Output**: Blockers with severity levels and impacts
- **Processing**: Parallel (independent of other analyses)

### 5. HealthCalculator
- **Purpose**: Calculate overall meeting health score
- **Input**: Results from all analysis skills
- **Output**: Health score (0-100), status, recommendations
- **Processing**: Sequential (depends on Stage 2 results)

### 6. SummaryGenerator
- **Purpose**: Generate executive summary using LLM
- **Input**: All analysis results and metadata
- **Output**: Executive summary, highlights, priorities, red flags, next steps
- **Processing**: Sequential (depends on all previous stages)

## Usage

### Basic Usage

```python
from services.meeting_analysis_workflow import MeetingAnalysisWorkflow

# Initialize workflow
workflow = MeetingAnalysisWorkflow()

# Analyze meeting
transcript = """[00:00:00] Alice: Let's discuss the project.
[00:00:15] Bob: We're blocked by the API issue."""

results = workflow.analyze_meeting(
    transcript_data=transcript,
    format_type="txt"
)

# Access results
print(f"Health Score: {results['health']['score']}/100")
print(f"Status: {results['health']['status']}")
print(f"Processing Time: {results['processing_time_seconds']}s")
```

### Advanced Usage

```python
# Access detailed results
metadata = results['metadata']
confusion = results['confusion']
action_items = results['action_items']
blockers = results['blockers']
health = results['health']
summary = results['summary']

# Performance metrics
stage_times = results['stage_times']
print(f"Parsing: {stage_times['parsing']}s")
print(f"Analysis: {stage_times['parallel_analysis']}s")
print(f"Health: {stage_times['health_calculation']}s")
print(f"Summary: {stage_times['summary_generation']}s")
```

## Output Schema

```json
{
  "metadata": {
    "title": "Meeting Title",
    "date": "2024-01-15",
    "duration": "45 minutes",
    "participants": ["Alice", "Bob", "Carol"]
  },
  "transcript": "Formatted transcript text...",
  "confusion": {
    "confusion_score": 0.3,
    "confused_topics": [...],
    "unanswered_questions": [...],
    "confusion_signals": [...]
  },
  "decisions": [],
  "action_items": {
    "action_items": [...],
    "total_action_items": 5,
    "unassigned_tasks": 1
  },
  "blockers": {
    "blockers": [...],
    "total_blockers": 2,
    "critical_blockers": 1
  },
  "health": {
    "score": 68.5,
    "status": "at-risk",
    "emoji": "⚠️",
    "recommendations": [...]
  },
  "summary": {
    "executive_summary": "...",
    "key_highlights": [...],
    "top_priorities": [...],
    "red_flags": [...],
    "next_steps": [...]
  },
  "processing_time_seconds": 12.45,
  "stage_times": {
    "parsing": 0.15,
    "parallel_analysis": 8.30,
    "health_calculation": 0.02,
    "summary_generation": 3.98
  }
}
```

## Performance Optimization

### Parallel Processing
The workflow uses `ThreadPoolExecutor` with 4 workers to run independent analysis tasks concurrently:

- **Confusion Detection**: ~3-5 seconds
- **Action Item Parsing**: ~3-5 seconds  
- **Blocker Identification**: ~3-5 seconds

**Sequential execution**: ~9-15 seconds
**Parallel execution**: ~3-5 seconds (3x faster!)

### Error Handling
Each parallel task has independent error handling:
- If one analysis fails, others continue
- Failed tasks return default values
- Workflow completes successfully even with partial failures

## Requirements

### Dependencies
```
ibm-watsonx-ai>=0.2.0
python-dotenv>=1.0.0
```

### Environment Variables
```bash
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

## Examples

See `examples/meeting_analysis_workflow_usage.py` for complete examples:
- Complete workflow with detailed output
- Simple usage example
- Error handling examples

## Logging

The workflow provides detailed logging at each stage:
```
INFO: Stage 1: Parsing transcript
INFO: ✓ Transcript parsed in 0.15s
INFO: Stage 2: Running parallel analysis
INFO:    ✓ confusion analysis completed
INFO:    ✓ action_items analysis completed
INFO:    ✓ blockers analysis completed
INFO: ✓ Parallel analysis completed in 8.30s
INFO: Stage 3: Calculating health score
INFO: ✓ Health score calculated in 0.02s
INFO: Stage 4: Generating executive summary
INFO: ✓ Summary generated in 3.98s
INFO: Meeting Analysis Workflow Complete - Total time: 12.45s
```

## Best Practices

1. **Transcript Format**: Use TXT format for better parsing reliability
2. **Transcript Length**: Optimal length is 500-2000 words
3. **Error Handling**: Always wrap workflow calls in try-except blocks
4. **Results Storage**: Save results to JSON for later analysis
5. **Performance**: Parallel processing is most effective with longer transcripts

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'ibm_watsonx_ai'`
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `ValueError: WATSONX_API_KEY is required`
**Solution**: Create `.env` file with valid credentials

**Issue**: Slow performance
**Solution**: Check network connection to watsonx.ai service

**Issue**: Analysis returns default values
**Solution**: Check logs for LLM errors, verify credentials

## Future Enhancements

- [ ] Add DecisionExtractor v2 for parallel decision analysis
- [ ] Support for more transcript formats (VTT, SRT)
- [ ] Real-time streaming analysis
- [ ] Batch processing for multiple meetings
- [ ] Custom skill plugins
- [ ] Performance caching for repeated analyses

## License

Made with Bob - AI Meeting Rescue Agent