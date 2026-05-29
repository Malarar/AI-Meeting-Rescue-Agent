"""
IBM watsonx.ai Granite LLM Client
Provides interface for text generation and JSON-structured output
"""
import json
import logging
import re
from typing import Dict, Any, Optional, List
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from config import Config

logger = logging.getLogger(__name__)


class GraniteClient:
    """Client for interfacing with IBM watsonx.ai Granite LLM"""
    
    def __init__(self):
        """
        Initialize the Granite client with credentials from config
        
        Raises:
            ValueError: If required configuration is missing
            Exception: If client initialization fails
        """
        # Load configuration
        self.api_key = Config.WATSONX_API_KEY
        self.project_id = Config.WATSONX_PROJECT_ID
        self.url = Config.WATSONX_URL
        self.model_id = Config.GRANITE_MODEL_ID
        
        # Validate required configuration
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY is required")
        if not self.project_id:
            raise ValueError("WATSONX_PROJECT_ID is required")
        
        # Default model parameters
        self.default_params = {
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
        """
        Initialize the watsonx.ai client and model
        
        Raises:
            Exception: If initialization fails
        """
        try:
            logger.info("Initializing Granite LLM client")
            
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
                params=self.default_params
            )
            
            logger.info(f"Successfully initialized Granite client with model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Granite client: {str(e)}", exc_info=True)
            raise
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text response from Granite LLM
        
        Args:
            prompt: The input prompt for the model
            temperature: Sampling temperature (0.0 to 1.0). Higher values make output more random.
            max_tokens: Maximum number of tokens to generate
            stop_sequences: List of sequences where generation should stop
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Generated text response from the model
            
        Raises:
            Exception: If text generation fails
        """
        try:
            # Build parameters
            params = self.default_params.copy()
            
            if temperature is not None:
                params['temperature'] = temperature
            if max_tokens is not None:
                params['max_new_tokens'] = max_tokens
            if stop_sequences is not None:
                params['stop_sequences'] = stop_sequences
            
            # Add any additional parameters
            params.update(kwargs)
            
            logger.debug(f"Generating text with prompt length: {len(prompt)}")
            logger.debug(f"Parameters: {params}")
            
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
    
    def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response from Granite LLM
        
        This method handles markdown code blocks (```json ... ```) and extracts
        valid JSON from the response.
        
        Args:
            prompt: The input prompt for the model (should request JSON output)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stop_sequences: List of sequences where generation should stop
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Parsed JSON response as a dictionary
            
        Raises:
            ValueError: If response cannot be parsed as JSON
            Exception: If text generation fails
        """
        try:
            # Generate text response
            response = self.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=stop_sequences,
                **kwargs
            )
            
            logger.debug(f"Raw response for JSON parsing: {response[:200]}...")
            
            # Parse JSON from response
            parsed_json = self._extract_json(response)
            
            logger.debug(f"Successfully parsed JSON with {len(parsed_json)} keys")
            
            return parsed_json
            
        except ValueError as e:
            logger.error(f"JSON parsing error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error generating JSON: {str(e)}", exc_info=True)
            raise
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from text, handling markdown code blocks
        
        Args:
            text: Text containing JSON (possibly in markdown code blocks)
            
        Returns:
            Parsed JSON as a dictionary
            
        Raises:
            ValueError: If no valid JSON is found
        """
        # Try to extract JSON from markdown code blocks first
        # Pattern: ```json ... ``` or ```\n...\n```
        code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            # Try each code block
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # If no code blocks or parsing failed, try to find JSON in the text
        # Look for content between { } or [ ]
        json_pattern = r'(\{.*\}|\[.*\])'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Try each potential JSON string
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # Last resort: try to parse the entire text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Could not extract valid JSON from response. "
                f"Error: {str(e)}. Response: {text[:200]}..."
            )
    
    def test_connection(self) -> bool:
        """
        Test the connection to watsonx.ai
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing Granite client connection")
            
            test_prompt = "Hello, this is a test. Please respond with 'OK'."
            response = self.generate(test_prompt, max_tokens=10)
            
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
            'project_id': self.project_id,
            'default_parameters': self.default_params
        }


# Made with Bob