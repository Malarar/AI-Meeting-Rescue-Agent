# AI Meeting Rescue Agent - API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, no authentication is required. In production, implement API key authentication.

---

## Endpoints

### 1. Home Page

**GET /**

Returns the web interface home page.

**Response:**
- HTML page with API documentation and features

---

### 2. Health Check

**GET /api/health**

Check if the service is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Meeting Rescue Agent",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 3. Analyze Transcript (JSON)

**POST /api/analyze**

Analyze a meeting transcript provided in the request body.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "transcript": "Meeting transcript text here",
  "format": "txt"
}
```

**Parameters:**
- `transcript` (string, required): The meeting transcript text
- `format` (string, optional): Format type - "txt" or "json" (default: "txt")

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "[00:00:00] Alice: Let'\''s start the meeting.\n[00:00:15] Bob: We'\''re blocked by the API issue.",
    "format": "txt"
  }'
```

**Response:**
```json
{
  "metadata": {
    "title": "Meeting",
    "date": "2024-01-15",
    "duration": "30 minutes",
    "participants": ["Alice", "Bob"]
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
    "action_items": [
      {
        "action": "Follow up with vendor",
        "owner": "Bob",
        "deadline": "2024-01-20",
        "priority": "high"
      }
    ],
    "total_action_items": 1,
    "unassigned_tasks": 0
  },
  "blockers": {
    "blockers": [
      {
        "blocker": "API documentation incomplete",
        "severity": "high",
        "impact": "Cannot proceed with integration"
      }
    ],
    "total_blockers": 1,
    "critical_blockers": 1
  },
  "health": {
    "score": 68.5,
    "status": "at-risk",
    "emoji": "⚠️",
    "recommendations": [
      "High confusion detected. Schedule follow-up meeting.",
      "1 blocker(s) identified. Assign owners and deadlines."
    ]
  },
  "summary": {
    "executive_summary": "Meeting focused on project status with one critical blocker identified.",
    "key_highlights": [
      "API integration blocked by vendor",
      "Team needs additional resources"
    ],
    "top_priorities": [
      "Resolve API documentation blocker",
      "Follow up with vendor",
      "Request additional resources"
    ],
    "red_flags": [
      "Critical blocker preventing progress"
    ],
    "next_steps": [
      "Bob to contact vendor by EOD",
      "Schedule follow-up meeting for Friday"
    ]
  },
  "processing_time_seconds": 12.45,
  "stage_times": {
    "parsing": 0.15,
    "parallel_analysis": 8.30,
    "health_calculation": 0.02,
    "summary_generation": 3.98
  },
  "api_metadata": {
    "request_timestamp": "2024-01-15T10:30:00.000Z",
    "response_timestamp": "2024-01-15T10:30:12.450Z",
    "format": "txt"
  }
}
```

**Status Codes:**
- `200 OK` - Analysis completed successfully
- `400 Bad Request` - Invalid input (missing transcript, invalid format)
- `500 Internal Server Error` - Processing failed

**Error Response:**
```json
{
  "error": "Invalid input",
  "message": "Request must include 'transcript' field"
}
```

---

### 4. Analyze Transcript (File Upload)

**POST /api/analyze/file**

Analyze a meeting transcript from an uploaded file.

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (TXT or JSON file)

**Supported File Formats:**
- `.txt` - Plain text transcript
- `.json` - JSON formatted transcript

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/analyze/file \
  -F "file=@meeting_transcript.txt"
```

**Response:**
Same structure as `/api/analyze` endpoint, with additional `filename` in `api_metadata`:

```json
{
  "metadata": {...},
  "transcript": "...",
  "confusion": {...},
  "action_items": {...},
  "blockers": {...},
  "health": {...},
  "summary": {...},
  "processing_time_seconds": 12.45,
  "api_metadata": {
    "request_timestamp": "2024-01-15T10:30:00.000Z",
    "response_timestamp": "2024-01-15T10:30:12.450Z",
    "filename": "meeting_transcript.txt",
    "format": "txt"
  }
}
```

**Status Codes:**
- `200 OK` - Analysis completed successfully
- `400 Bad Request` - Missing file, invalid format, empty file, encoding error
- `500 Internal Server Error` - Processing failed

**Error Responses:**
```json
{
  "error": "Missing file",
  "message": "Request must include a file upload"
}
```

```json
{
  "error": "Invalid file format",
  "message": "File must be one of: txt, json"
}
```

```json
{
  "error": "Invalid file encoding",
  "message": "File must be UTF-8 encoded"
}
```

---

## Transcript Formats

### TXT Format
Plain text with timestamps and speakers:

```
[00:00:00] Alice: Let's start the meeting.
[00:00:15] Bob: We're blocked by the API issue.
[00:00:30] Alice: I'll follow up with the vendor.
```

### JSON Format
Structured JSON with messages array:

```json
{
  "meeting_title": "Q4 Planning Meeting",
  "date": "2024-01-15",
  "participants": ["Alice", "Bob"],
  "messages": [
    {
      "timestamp": "00:00:00",
      "speaker": "Alice",
      "text": "Let's start the meeting."
    },
    {
      "timestamp": "00:00:15",
      "speaker": "Bob",
      "text": "We're blocked by the API issue."
    }
  ]
}
```

---

## Response Schema

### Metadata
```typescript
{
  title: string,
  date: string,
  duration: string,
  participants: string[]
}
```

### Confusion Analysis
```typescript
{
  confusion_score: number,        // 0.0 to 1.0
  confused_topics: Array<{
    topic: string,
    timestamp: string,
    indicators: string[]
  }>,
  unanswered_questions: string[],
  confusion_signals: Array<{
    timestamp: string,
    speaker: string,
    signal: string
  }>
}
```

### Action Items
```typescript
{
  action_items: Array<{
    action: string,
    owner: string,
    deadline: string,           // YYYY-MM-DD
    priority: string,           // low, medium, high
    dependencies: string[],
    timestamp: string
  }>,
  total_action_items: number,
  unassigned_tasks: number
}
```

### Blockers
```typescript
{
  blockers: Array<{
    blocker: string,
    type: string,               // technical, resource, dependency
    severity: string,           // low, medium, high, critical
    blocking_entity: string,
    owner: string,
    impact: string,
    timestamp: string
  }>,
  total_blockers: number,
  critical_blockers: number
}
```

### Health Score
```typescript
{
  score: number,                // 0 to 100
  status: string,               // healthy, at-risk, critical
  emoji: string,                // ✅, ⚠️, 🔴
  recommendations: string[]
}
```

### Summary
```typescript
{
  executive_summary: string,
  key_highlights: string[],     // 3-5 items
  top_priorities: string[],     // 3 items
  red_flags: string[],          // 0+ items
  next_steps: string[]          // 3+ items
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Common Error Types

**400 Bad Request**
- Missing required fields
- Invalid format
- Invalid file type
- Empty content

**404 Not Found**
- Endpoint doesn't exist

**500 Internal Server Error**
- LLM processing failed
- Unexpected server error

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- Rate limiting per IP address
- API key-based quotas
- Request throttling

---

## Best Practices

1. **Transcript Length**: Optimal length is 500-2000 words
2. **Format**: Use TXT format for better parsing reliability
3. **Error Handling**: Always check status codes and handle errors
4. **Timeouts**: Set appropriate timeouts (30-60 seconds recommended)
5. **Retries**: Implement exponential backoff for failed requests

---

## Examples

### Python Example
```python
import requests

url = "http://localhost:5000/api/analyze"
data = {
    "transcript": "[00:00:00] Alice: Let's discuss the project.",
    "format": "txt"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Health Score: {result['health']['score']}/100")
print(f"Status: {result['health']['status']}")
```

### JavaScript Example
```javascript
const response = await fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    transcript: '[00:00:00] Alice: Let\'s discuss the project.',
    format: 'txt'
  })
});

const result = await response.json();
console.log(`Health Score: ${result.health.score}/100`);
```

---

## Support

For issues or questions:
- Check logs in `logs/app.log`
- Verify watsonx.ai credentials in `.env`
- Review `WORKFLOW_GUIDE.md` for detailed workflow information

---

Made with Bob 🤖