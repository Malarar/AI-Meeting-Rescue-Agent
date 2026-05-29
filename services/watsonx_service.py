"""
IBM watsonx.ai Service
Handles integration with IBM watsonx.ai and Granite LLM
"""
import logging
from typing import Dict, Any, Optional
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from config import Config

logger = logging.getLogger(__name__)


class WatsonxService:
    """Service for interacting with IBM watsonx.ai Granite LLM"""
    
    def __init__(self):
        """Initialize the watsonx.ai service"""
        self.api_key = Config.WATSONX_API_KEY
        self.project_id = Config.WATSONX_PROJECT_ID
        self.url = Config.WATSONX_URL
        self.model_id = Config.GRANITE_MODEL_ID
        
        # Model parameters
        self.parameters = {
            'max_new_tokens': Config.GRANITE_MAX_TOKENS,
            'temperature': Config.GRANITE_TEMPERATURE,
            'top_p': Config.GRANITE_TOP_P,
            'top_k': Config.GRANITE_TOP_K,
            'repetition_penalty': 1.0
        }
        
        # Initialize client
        self.client = None
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the watsonx.ai client and model"""
        try:
            logger.info("Initializing watsonx.ai client")
            
            # Create credentials
            credentials = Credentials(
                api_key=self.api_key,
                url=self.url
            )
            
            # Create API client
            self.client = APIClient(credentials)
            
            # Initialize model inference
            self.model = ModelInference(
                model_id=self.model_id,
                api_client=self.client,
                project_id=self.project_id,
                params=self.parameters
            )
            
            logger.info(f"Successfully initialized watsonx.ai with model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize watsonx.ai client: {str(e)}", exc_info=True)
            raise
    
    def generate(self, prompt: str, custom_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text using Granite LLM
        
        Args:
            prompt: The input prompt for the model
            custom_params: Optional custom parameters to override defaults
            
        Returns:
            Generated text response from the model
        """
        try:
            # Use custom parameters if provided, otherwise use defaults
            params = self.parameters.copy()
            if custom_params:
                params.update(custom_params)
            
            logger.debug(f"Generating response with prompt length: {len(prompt)}")
            
            # Generate response
            response = self.model.generate_text(
                prompt=prompt,
                params=params
            )
            
            logger.debug(f"Generated response length: {len(response)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}", exc_info=True)
            raise
    
    def generate_batch(self, prompts: list, custom_params: Optional[Dict[str, Any]] = None) -> list:
        """
        Generate text for multiple prompts
        
        Args:
            prompts: List of input prompts
            custom_params: Optional custom parameters to override defaults
            
        Returns:
            List of generated text responses
        """
        try:
            logger.info(f"Generating batch responses for {len(prompts)} prompts")
            
            responses = []
            for i, prompt in enumerate(prompts):
                logger.debug(f"Processing prompt {i+1}/{len(prompts)}")
                response = self.generate(prompt, custom_params)
                responses.append(response)
            
            logger.info(f"Successfully generated {len(responses)} responses")
            return responses
            
        except Exception as e:
            logger.error(f"Error in batch generation: {str(e)}", exc_info=True)
            raise
    
    def test_connection(self) -> bool:
        """
        Test the connection to watsonx.ai
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing watsonx.ai connection")
            
            test_prompt = "Hello, this is a test."
            response = self.generate(test_prompt)
            
            if response:
                logger.info("Connection test successful")
                return True
            else:
                logger.warning("Connection test returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}", exc_info=True)
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration
        
        Returns:
            Dictionary containing model information
        """
        return {
            'model_id': self.model_id,
            'url': self.url,
            'parameters': self.parameters,
            'project_id': self.project_id
        }

# Made with Bob
