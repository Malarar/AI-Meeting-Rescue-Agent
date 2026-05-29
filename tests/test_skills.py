"""
Unit tests for analysis skills
"""
import pytest
from unittest.mock import Mock, MagicMock
from utils.transcript_parser import TranscriptParser
from skills.confusion_detector import ConfusionDetector
from skills.decision_extractor import DecisionExtractor
from skills.action_item_parser import ActionItemParser
from skills.blocker_identifier import BlockerIdentifier


@pytest.fixture
def mock_watsonx_service():
    """Create a mock watsonx service"""
    service = Mock()
    service.generate = MagicMock(return_value='{"test": "response"}')
    return service


@pytest.fixture
def sample_transcript():
    """Sample meeting transcript for testing"""
    return """
    Alice: We need to decide on the database architecture.
    Bob: I'm confused about whether we should use SQL or NoSQL.
    Charlie: Let's go with PostgreSQL for now.
    Alice: Agreed. Bob, can you set up the initial schema by Friday?
    Bob: Sure, but I'm blocked on getting access to the dev environment.
    """


class TestTranscriptParser:
    """Tests for TranscriptParser skill"""
    
    def test_initialization(self, mock_watsonx_service):
        """Test skill initialization"""
        parser = TranscriptParser(mock_watsonx_service)
        assert parser.skill_name == "transcript_parser"
        assert parser.watsonx_service is not None
    
    def test_analyze(self, mock_watsonx_service, sample_transcript):
        """Test analyze method"""
        parser = TranscriptParser(mock_watsonx_service)
        result = parser.analyze(sample_transcript)
        
        assert 'skill' in result
        assert result['skill'] == 'transcript_parser'
        mock_watsonx_service.generate.assert_called_once()


class TestConfusionDetector:
    """Tests for ConfusionDetector skill"""
    
    def test_initialization(self, mock_watsonx_service):
        """Test skill initialization"""
        detector = ConfusionDetector(mock_watsonx_service)
        assert detector.skill_name == "confusion_detector"
        assert detector.watsonx_service is not None
    
    def test_analyze(self, mock_watsonx_service, sample_transcript):
        """Test analyze method"""
        detector = ConfusionDetector(mock_watsonx_service)
        result = detector.analyze(sample_transcript)
        
        assert 'skill' in result
        assert result['skill'] == 'confusion_detector'
        mock_watsonx_service.generate.assert_called_once()


class TestDecisionExtractor:
    """Tests for DecisionExtractor skill"""
    
    def test_initialization(self, mock_watsonx_service):
        """Test skill initialization"""
        extractor = DecisionExtractor(mock_watsonx_service)
        assert extractor.skill_name == "decision_extractor"
        assert extractor.watsonx_service is not None
    
    def test_analyze(self, mock_watsonx_service, sample_transcript):
        """Test analyze method"""
        extractor = DecisionExtractor(mock_watsonx_service)
        result = extractor.analyze(sample_transcript)
        
        assert 'skill' in result
        assert result['skill'] == 'decision_extractor'
        mock_watsonx_service.generate.assert_called_once()


class TestActionItemParser:
    """Tests for ActionItemParser skill"""
    
    def test_initialization(self, mock_watsonx_service):
        """Test skill initialization"""
        parser = ActionItemParser(mock_watsonx_service)
        assert parser.skill_name == "action_item_parser"
        assert parser.watsonx_service is not None
    
    def test_analyze(self, mock_watsonx_service, sample_transcript):
        """Test analyze method"""
        parser = ActionItemParser(mock_watsonx_service)
        result = parser.analyze(sample_transcript)
        
        assert 'skill' in result
        assert result['skill'] == 'action_item_parser'
        mock_watsonx_service.generate.assert_called_once()


class TestBlockerIdentifier:
    """Tests for BlockerIdentifier skill"""
    
    def test_initialization(self, mock_watsonx_service):
        """Test skill initialization"""
        identifier = BlockerIdentifier(mock_watsonx_service)
        assert identifier.skill_name == "blocker_identifier"
        assert identifier.watsonx_service is not None
    
    def test_analyze(self, mock_watsonx_service, sample_transcript):
        """Test analyze method"""
        identifier = BlockerIdentifier(mock_watsonx_service)
        result = identifier.analyze(sample_transcript)
        
        assert 'skill' in result
        assert result['skill'] == 'blocker_identifier'
        mock_watsonx_service.generate.assert_called_once()

# Made with Bob
