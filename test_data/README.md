# Test Data - Meeting Transcripts

This directory contains realistic Microsoft Teams meeting transcript files in JSON format for testing the AI Meeting Rescue Agent.

## Files

### 1. healthy_meeting.json
**Meeting:** Sprint Planning - Week 15  
**Duration:** 6 minutes  
**Participants:** 3 (Alice Chen, Bob Smith, Carol Davis)  
**Messages:** 10

**Characteristics:**
- ✅ Clear decisions (2 decisions made)
- ✅ Well-assigned action items (3 tasks with owners and deadlines)
- ✅ No blockers
- ✅ Low confusion
- ✅ Organized and productive

**Expected Analysis Results:**
- Health Score: ~95-100 (Healthy ✅)
- Confusion Score: ~0.0-0.1
- Decisions: 2
- Action Items: 3 (all assigned)
- Blockers: 0

**Use Case:** Testing optimal meeting analysis, baseline for healthy meetings

---

### 2. chaotic_meeting.json
**Meeting:** Architecture Discussion  
**Duration:** 26 minutes  
**Participants:** 4 (Dave Johnson, Eve Martinez, Frank Wilson, Grace Lee)  
**Messages:** 20

**Characteristics:**
- ❌ High confusion (multiple "I'm lost", "wait what?", "can you clarify?")
- ❌ No clear decisions made
- ❌ Multiple unresolved topics (architecture, database, vendors)
- ❌ Many unanswered questions
- ❌ Multiple blockers (infrastructure, HR, security)
- ❌ No assigned action items

**Expected Analysis Results:**
- Health Score: ~10-30 (Critical 🔴)
- Confusion Score: ~0.7-0.9
- Decisions: 0
- Action Items: 0-1 (unassigned)
- Blockers: 3-4 (infrastructure, HR, security)

**Use Case:** Testing worst-case scenario, stress testing confusion detection

---

### 3. at_risk_meeting.json
**Meeting:** Product Launch Planning  
**Duration:** 22 minutes  
**Participants:** 3 (Henry Park, Iris Thompson, Jack Robinson)  
**Messages:** 17

**Characteristics:**
- ⚠️ Tentative decisions (1-2 decisions with conditions)
- ⚠️ Some assigned action items (2-3 tasks)
- ⚠️ 1 unassigned task (customer support training)
- ⚠️ External blocker (legal approval)
- ⚠️ Moderate confusion about pricing strategy

**Expected Analysis Results:**
- Health Score: ~50-70 (At-Risk ⚠️)
- Confusion Score: ~0.3-0.4
- Decisions: 1-2 (tentative)
- Action Items: 3-4 (1 unassigned)
- Blockers: 1-2 (legal approval, training coordination)

**Use Case:** Testing mid-range scenarios, realistic business meetings

---

## JSON Format

All files follow this structure:

```json
{
  "meeting_title": "Meeting Title",
  "date": "YYYY-MM-DD",
  "duration": "X minutes",
  "participants": ["Name 1", "Name 2", "Name 3"],
  "messages": [
    {
      "timestamp": "HH:MM:SS",
      "speaker": "Speaker Name",
      "text": "Message content"
    }
  ]
}
```

## Usage

### With Python
```python
import json

# Load test data
with open('test_data/healthy_meeting.json', 'r') as f:
    meeting_data = json.load(f)

# Use with workflow
from services.meeting_analysis_workflow import MeetingAnalysisWorkflow

workflow = MeetingAnalysisWorkflow()
results = workflow.analyze_meeting(
    transcript_data=json.dumps(meeting_data),
    format_type='json'
)
```

### With API
```bash
# Analyze healthy meeting
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d @test_data/healthy_meeting.json

# Or upload as file
curl -X POST http://localhost:5000/api/analyze/file \
  -F "file=@test_data/chaotic_meeting.json"
```

## Testing Scenarios

### Scenario 1: Baseline Testing
Use `healthy_meeting.json` to verify:
- Correct decision extraction
- Accurate action item parsing
- Proper owner assignment
- High health score calculation

### Scenario 2: Edge Case Testing
Use `chaotic_meeting.json` to verify:
- Confusion detection accuracy
- Handling of no decisions
- Blocker identification
- Low health score calculation
- Recommendation generation for critical meetings

### Scenario 3: Real-World Testing
Use `at_risk_meeting.json` to verify:
- Tentative decision handling
- Mixed action item assignment
- External blocker detection
- Moderate health score calculation
- Balanced recommendations

## Adding New Test Data

When creating new test transcripts:

1. **Use realistic conversations** - Natural language, not scripted
2. **Include timestamps** - Format: HH:MM:SS
3. **Vary message length** - Mix short and long messages
4. **Add context** - Include meeting metadata
5. **Test specific features** - Target particular analysis aspects

## Validation

To validate test data structure:

```python
import json

def validate_transcript(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    required_fields = ['meeting_title', 'date', 'participants', 'messages']
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    for msg in data['messages']:
        assert 'timestamp' in msg
        assert 'speaker' in msg
        assert 'text' in msg
    
    print(f"✓ {filepath} is valid")

# Validate all test files
validate_transcript('test_data/healthy_meeting.json')
validate_transcript('test_data/chaotic_meeting.json')
validate_transcript('test_data/at_risk_meeting.json')
```

---

Made with Bob 🤖