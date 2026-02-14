"""
Model management for Agent.
Handles model selection, switching, and validation.
"""

from typing import Optional, Dict, Any
import toml


class ModelManager:
    """Manages model selection and switching during conversations."""
    
    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize the model manager.
        
        Args:
            config_path: Path to the config.toml file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.current_model = self.config["model"]["name"]
        self.available_models = self.config.get("models", {})
        
        if not self.available_models:
            # Fallback to default models if not in config
            self.available_models = {
                "claude-3-5-sonnet-20241022": {
                    "display_name": "Claude 3.5 Sonnet",
                    "max_tokens": 8000,
                    "description": "Most capable model, best for complex tasks"
                },
                "claude-3-5-haiku-20241022": {
                    "display_name": "Claude 3.5 Haiku",
                    "max_tokens": 8000,
                    "description": "Faster and more cost-effective, good for simpler tasks"
                }
            }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        with open(self.config_path, 'r') as f:
            return toml.load(f)
    
    def get_current_model(self) -> str:
        """Get the currently active model name."""
        return self.current_model
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a model.
        
        Args:
            model_name: The model to get info for. If None, returns info for current model.
            
        Returns:
            Dictionary containing model information.
        """
        model = model_name or self.current_model
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' not found in available models")
        return self.available_models[model]
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get a dictionary of all available models and their info."""
        return self.available_models.copy()
    
    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a different model.
        
        Args:
            new_model: The name of the model to switch to.
            
        Returns:
            True if switch was successful, False otherwise.
        """
        if new_model not in self.available_models:
            return False
        
        self.current_model = new_model
        return True
    
    def validate_model(self, model_name: str) -> bool:
        """
        Check if a model name is valid.
        
        Args:
            model_name: The model name to validate.
            
        Returns:
            True if the model exists, False otherwise.
        """
        return model_name in self.available_models
    
    def get_max_tokens(self, model_name: Optional[str] = None) -> int:
        """
        Get the max tokens for a model.
        
        Args:
            model_name: The model to get max tokens for. If None, uses current model.
            
        Returns:
            The maximum number of tokens for the model.
        """
        model = model_name or self.current_model
        return self.get_model_info(model)["max_tokens"]
    
    def get_temperature(self) -> float:
        """Get the temperature setting from config."""
        return self.config["model"].get("temperature", 1.0)