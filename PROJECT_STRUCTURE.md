# AI Meeting Rescue Agent - Project Structure

## Directory Tree

```
ai-meeting-rescue-agent/
├── app.py                          # Main Flask application with API routes
├── run.py                          # Quick start script
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── example_usage.py                # API usage examples
├── PROJECT_STRUCTURE.md            # This file
│
├── skills/                         # Modular analysis skills
│   ├── __init__.py
│   ├── transcript_parser.py       # Parses and structures transcripts
│   ├── confusion_detector.py      # Identifies confusion points
│   ├── decision_extractor.py      # Extracts key decisions
│   ├── action_item_parser.py      # Identifies action items
│   └── blocker_identifier.py      # Detects blockers
│
├── services/                       # Core services
│   ├── __init__.py
│   ├── watsonx_service.py         # IBM watsonx.ai integration
│   └── orchestrator.py            # Parallel processing orchestrator
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── logger.py                  # Logging configuration
│   └── validators.py              # Input validation
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   └── test_skills.py             # Skills unit tests
│
└── logs/                           # Application logs (created at runtime)
    └── app.log
```

## File Descriptions

### Root Level Files

- **app.py**: Main Flask application containing all API endpoints
  - `/health` - Health check endpoint
  - `/api/analyze` - Full transcript analysis
  - `/api/analyze/<skill_name>` - Single skill analysis
  - `/api/skills` - List available skills

- **run.py**: Convenience script to start the application

- **config.py**: Centralized configuration management
  - Environment variable loading
  - Configuration classes (Development, Production, Testing)
  - Validation of required settings

- **requirements.txt**: All Python dependencies with versions

- **.env.example**: Template for environment variables

- **example_usage.py**: Demonstrates API usage with sample requests

### Skills Package

Each skill is a self-contained module that:
- Accepts a transcript and optional metadata
- Generates a specialized prompt for Granite LLM
- Processes the LLM response
- Returns structured JSON results

**Available Skills:**
1. **transcript_parser.py**: Structures raw transcripts
2. **confusion_detector.py**: Identifies confusion points
3. **decision_extractor.py**: Extracts decisions
4. **action_item_parser.py**: Identifies action items
5. **blocker_identifier.py**: Detects blockers

### Services Package

- **watsonx_service.py**: Handles all IBM watsonx.ai interactions
  - Client initialization
  - Granite LLM text generation
  - Batch processing support
  - Connection testing

- **orchestrator.py**: Manages parallel skill execution
  - ThreadPoolExecutor for concurrent processing
  - Result aggregation
  - Error handling
  - Single and batch skill execution

### Utils Package

- **logger.py**: Structured logging setup
  - Console and file handlers
  - JSON formatting for logs
  - Rotating file handler

- **validators.py**: Input validation functions
  - Transcript validation
  - Skill name validation
  - Meeting ID validation

### Tests Package

- **test_skills.py**: Unit tests for all skills
  - Mock watsonx service
  - Test fixtures
  - Skill initialization tests
  - Analysis method tests

## Key Features

### 1. Modular Architecture
Each skill is independent and can be:
- Executed individually
- Run in parallel with other skills
- Tested in isolation
- Extended or modified without affecting others

### 2. Parallel Processing
The orchestrator uses ThreadPoolExecutor to:
- Run multiple skills concurrently
- Reduce total processing time
- Handle errors gracefully
- Aggregate results efficiently

### 3. Configuration Management
Centralized configuration with:
- Environment-specific settings
- Validation of required variables
- Easy deployment across environments
- Secure credential management

### 4. Comprehensive Logging
Structured logging provides:
- Console output for development
- JSON logs for production
- Rotating file handlers
- Different log levels per environment

### 5. REST API
Flask-based API with:
- Health check endpoint
- Full analysis endpoint
- Individual skill endpoints
- Skill listing endpoint
- CORS support
- Error handling

## Data Flow

```
1. Client Request
   ↓
2. Flask API (app.py)
   ↓
3. Input Validation (utils/validators.py)
   ↓
4. Orchestrator (services/orchestrator.py)
   ↓
5. Parallel Skill Execution
   ├── Skill 1 → watsonx_service → Granite LLM
   ├── Skill 2 → watsonx_service → Granite LLM
   ├── Skill 3 → watsonx_service → Granite LLM
   ├── Skill 4 → watsonx_service → Granite LLM
   └── Skill 5 → watsonx_service → Granite LLM
   ↓
6. Result Aggregation
   ↓
7. JSON Response to Client
```

## Environment Variables

Required:
- `WATSONX_API_KEY`: IBM watsonx.ai API key
- `WATSONX_PROJECT_ID`: watsonx.ai project ID

Optional:
- `WATSONX_URL`: API endpoint (default: us-south)
- `GRANITE_MODEL_ID`: Model identifier
- `GRANITE_MAX_TOKENS`: Max response tokens
- `GRANITE_TEMPERATURE`: LLM temperature
- `MAX_WORKERS`: Parallel processing workers
- `LOG_LEVEL`: Logging level

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the Application**
   ```bash
   python app.py
   # or
   python run.py
   ```

4. **Test the API**
   ```bash
   python example_usage.py
   ```

## Extension Points

### Adding New Skills

1. Create new skill file in `skills/` directory
2. Implement skill class with `analyze()` method
3. Add to `skills/__init__.py`
4. Register in `orchestrator.py`
5. Add tests in `tests/test_skills.py`

### Adding New Endpoints

1. Add route handler in `app.py`
2. Implement validation if needed
3. Update API documentation in README.md

### Custom Configuration

1. Add new config variables in `config.py`
2. Update `.env.example`
3. Document in README.md

## Best Practices

1. **Always validate input** before processing
2. **Use structured logging** for debugging
3. **Handle errors gracefully** with try-except blocks
4. **Test skills individually** before integration
5. **Keep skills focused** on single responsibility
6. **Document API changes** in README.md
7. **Use environment variables** for sensitive data
8. **Follow Python naming conventions**

## Performance Considerations

- Parallel processing reduces total analysis time
- ThreadPoolExecutor manages concurrent requests
- Configurable worker count for resource management
- Timeout settings prevent hanging requests
- Rotating logs prevent disk space issues

## Security Notes

- Never commit `.env` file
- Use environment variables for credentials
- Validate all user input
- Implement rate limiting in production
- Use HTTPS in production
- Keep dependencies updated