"""
Services package for AI Meeting Rescue Agent
Contains core services for watsonx.ai integration and orchestration
"""
from .watsonx_service import WatsonxService
from .granite_client import GraniteClient
from .orchestrator import AnalysisOrchestrator
from .meeting_analysis_workflow import MeetingAnalysisWorkflow
from .jira_integration import JiraIntegration
from .outlook_integration import OutlookIntegration

__all__ = [
    'WatsonxService',
    'GraniteClient',
    'AnalysisOrchestrator',
    'MeetingAnalysisWorkflow',
    'JiraIntegration',
    'OutlookIntegration'
]

# Made with Bob
