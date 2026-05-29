# AI Meeting Rescue Agent

An intelligent system that analyzes Microsoft Teams meeting transcripts using IBM watsonx Orchestrate and Granite LLM to extract actionable insights, identify confusion points, detect decisions, parse action items, and identify blockers.

## Features

- **Transcript Parser**: Processes and structures meeting transcripts
- **Confusion Detector**: Identifies points of confusion or misunderstanding
- **Decision Extractor**: Extracts key decisions made during meetings
- **Action Item Parser**: Identifies and categorizes action items
- **Blocker Identifier**: Detects potential blockers and impediments
- **Parallel Processing**: Efficient concurrent analysis of multiple skills
- **REST API**: Flask-based API for easy integration

## Architecture

```
ai-meeting-rescue-agent/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── skills/                    # Modular skills architecture
│   ├── __init__.py
│   ├── transcript_parser.py
│   ├── confusion_detector.py
│   ├── decision_extractor.py
│   ├── action_item_parser.py
│   └── blocker_identifier.py
├── services/                  # Core services
│   ├── __init__.py
│   ├── watsonx_service.py    # IBM watsonx.ai integration
│   └── orchestrator.py       # Parallel processing orchestrator
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── logger.py
│   └── validators.py
├── logs/                      # Application logs
└── tests/                     # Unit tests
    ├── __init__.py
    └── test_skills.py
```

## Prerequisites

- Python 3.9 or higher
- IBM watsonx.ai account with API access
- IBM Cloud API key
- watsonx.ai Project ID

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-meeting-rescue-agent
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# IBM watsonx.ai Configuration
WATSONX_API_KEY=your-actual-api-key
WATSONX_PROJECT_ID=your-actual-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Flask Configuration
SECRET_KEY=generate-a-secure-random-key
DEBUG=True
PORT=5000
```

### 5. Create Logs Directory

```bash
mkdir logs
```

## Getting IBM watsonx.ai Credentials

1. **Sign up for IBM Cloud**: Visit [IBM Cloud](https://cloud.ibm.com/)
2. **Create watsonx.ai instance**: Navigate to the watsonx.ai service
3. **Get API Key**: 
   - Go to IBM Cloud Dashboard
   - Navigate to "Manage" → "Access (IAM)" → "API keys"
   - Create a new API key
4. **Get Project ID**:
   - Open your watsonx.ai project
   - Copy the Project ID from the project settings

## Usage

### Starting the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 1. Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-28T18:40:00Z"
}
```

#### 2. Analyze Meeting Transcript

```bash
POST /api/analyze
Content-Type: application/json

{
  "transcript": "Meeting transcript text here...",
  "meeting_id": "optional-meeting-id",
  "metadata": {
    "date": "2026-05-28",
    "participants": ["Alice", "Bob", "Charlie"]
  }
}
```

Response:
```json
{
  "meeting_id": "optional-meeting-id",
  "analysis": {
    "transcript_structure": {...},
    "confusion_points": [...],
    "decisions": [...],
    "action_items": [...],
    "blockers": [...]
  },
  "processing_time": 2.34,
  "timestamp": "2026-05-28T18:40:00Z"
}
```

#### 3. Analyze Specific Skill

```bash
POST /api/analyze/<skill_name>
Content-Type: application/json

{
  "transcript": "Meeting transcript text here..."
}
```

Available skills:
- `transcript_parser`
- `confusion_detector`
- `decision_extractor`
- `action_item_parser`
- `blocker_identifier`

### Example Request

```python
import requests

url = "http://localhost:5000/api/analyze"
payload = {
    "transcript": """
    Alice: We need to decide on the database architecture.
    Bob: I'm confused about whether we should use SQL or NoSQL.
    Charlie: Let's go with PostgreSQL for now.
    Alice: Agreed. Bob, can you set up the initial schema by Friday?
    Bob: Sure, but I'm blocked on getting access to the dev environment.
    """,
    "meeting_id": "team-sync-2026-05-28",
    "metadata": {
        "date": "2026-05-28",
        "participants": ["Alice", "Bob", "Charlie"]
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WATSONX_API_KEY` | IBM watsonx.ai API key | Required |
| `WATSONX_PROJECT_ID` | watsonx.ai Project ID | Required |
| `WATSONX_URL` | watsonx.ai API endpoint | `https://us-south.ml.cloud.ibm.com` |
| `GRANITE_MODEL_ID` | Granite LLM model identifier | `ibm/granite-13b-chat-v2` |
| `GRANITE_MAX_TOKENS` | Maximum tokens for LLM response | `2000` |
| `GRANITE_TEMPERATURE` | LLM temperature (creativity) | `0.7` |
| `MAX_WORKERS` | Parallel processing workers | `5` |
| `TIMEOUT_SECONDS` | Request timeout | `300` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Granite LLM Models

Available Granite models:
- `ibm/granite-13b-chat-v2` (recommended)
- `ibm/granite-13b-instruct-v2`
- `ibm/granite-20b-multilingual`

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

### Project Structure Details

- **`app.py`**: Main Flask application with API routes
- **`config.py`**: Centralized configuration management
- **`skills/`**: Modular analysis skills (each skill is independent)
- **`services/`**: Core services for watsonx.ai integration and orchestration
- **`utils/`**: Helper functions for logging and validation
- **`tests/`**: Unit and integration tests

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your `WATSONX_API_KEY` is correct
   - Ensure your API key has access to watsonx.ai

2. **Project Not Found**
   - Confirm your `WATSONX_PROJECT_ID` is correct
   - Check that the project exists in your watsonx.ai account

3. **Timeout Errors**
   - Increase `TIMEOUT_SECONDS` in `.env`
   - Check your network connection

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify you're using Python 3.9+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check IBM watsonx.ai documentation: [IBM watsonx.ai Docs](https://www.ibm.com/docs/en/watsonx-as-a-service)

## Acknowledgments

- Built with IBM watsonx.ai and Granite LLM
- Powered by Flask framework
- Designed for Microsoft Teams transcript analysis