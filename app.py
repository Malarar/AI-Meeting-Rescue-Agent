"""
AI Meeting Rescue Agent - Flask REST API
Analyzes meeting transcripts using IBM watsonx.ai Granite LLM with complete workflow
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from services.meeting_analysis_workflow import MeetingAnalysisWorkflow
from utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Setup logging
logger = setup_logger(__name__)

# Validate configuration on startup
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

# Initialize workflow
try:
    workflow = MeetingAnalysisWorkflow()
    logger.info("MeetingAnalysisWorkflow initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize workflow: {e}")
    raise

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'json'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    """Home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.warning(f"Template not found, returning JSON: {e}")
        return jsonify({
            'service': 'AI Meeting Rescue Agent',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'analyze': '/api/analyze',
                'analyze_file': '/api/analyze/file'
            }
        }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Meeting Rescue Agent',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_transcript():
    """
    Analyze meeting transcript from JSON body
    
    Request body:
    {
        "transcript": "meeting transcript text",
        "format": "txt" or "json"
    }
    
    Returns:
    Complete analysis results including metadata, confusion, decisions,
    action items, blockers, health score, and executive summary
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid input',
                'message': 'Request body must be JSON'
            }), 400
        
        # Validate transcript
        transcript = data.get('transcript')
        if not transcript:
            return jsonify({
                'error': 'Missing transcript',
                'message': 'Request must include "transcript" field'
            }), 400
        
        # Get format (default to txt)
        format_type = data.get('format', 'txt').lower()
        if format_type not in ['txt', 'json']:
            return jsonify({
                'error': 'Invalid format',
                'message': 'Format must be "txt" or "json"'
            }), 400
        
        logger.info(f"Starting analysis for transcript (format: {format_type})")
        
        # Run complete workflow
        start_time = datetime.utcnow()
        results = workflow.analyze_meeting(transcript, format_type)
        end_time = datetime.utcnow()
        
        # Add API metadata
        results['api_metadata'] = {
            'request_timestamp': start_time.isoformat() + 'Z',
            'response_timestamp': end_time.isoformat() + 'Z',
            'format': format_type
        }
        
        logger.info(f"Analysis completed in {results['processing_time_seconds']}s")
        
        return jsonify(results), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'Invalid input',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


@app.route('/api/analyze/file', methods=['POST'])
def analyze_file():
    """
    Analyze meeting transcript from uploaded file
    
    Form data:
    - file: Transcript file (TXT or JSON)
    
    Auto-detects format from file extension.
    
    Returns:
    Complete analysis results
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'Missing file',
                'message': 'Request must include a file upload'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file format',
                'message': f'File must be one of: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get file extension to determine format
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        format_type = file_ext  # 'txt' or 'json'
        
        # Read file content
        try:
            transcript = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({
                'error': 'Invalid file encoding',
                'message': 'File must be UTF-8 encoded'
            }), 400
        
        if not transcript.strip():
            return jsonify({
                'error': 'Empty file',
                'message': 'Uploaded file is empty'
            }), 400
        
        logger.info(f"Starting analysis for uploaded file: {filename} (format: {format_type})")
        
        # Run complete workflow
        start_time = datetime.utcnow()
        results = workflow.analyze_meeting(transcript, format_type)
        end_time = datetime.utcnow()
        
        # Add API metadata
        results['api_metadata'] = {
            'request_timestamp': start_time.isoformat() + 'Z',
            'response_timestamp': end_time.isoformat() + 'Z',
            'filename': filename,
            'format': format_type
        }
        
        logger.info(f"Analysis completed for {filename} in {results['processing_time_seconds']}s")
        
        return jsonify(results), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'Invalid input',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Run the application
    logger.info(f"Starting AI Meeting Rescue Agent on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )


# Made with Bob
