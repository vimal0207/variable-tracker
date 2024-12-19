from abc import ABC, abstractmethod
import json
from typing import Dict, Any
from .models import SettingsData

class SettingsLoader(ABC):
    """
    Abstract base class defining the contract for loading configuration settings.

    This class provides a standardized interface for loading configuration settings 
    from various sources. Concrete implementations will define specific loading 
    mechanisms for different configuration formats or sources.

    Attributes:
        No direct attributes defined in the abstract base class.

    Methods:
        load_settings: Abstract method to load configuration settings.
    """

    @abstractmethod
    def load_settings(self) -> Dict[str, Any]:
        """
        Abstract method to load configuration settings from a source.

        This method must be implemented by subclasses to provide a mechanism 
        for loading configuration settings. The method should handle different 
        loading scenarios, including potential errors and default configurations.

        Returns:
            Dict[str, Any]: A dictionary containing configuration settings.

        Raises:
            NotImplementedError: If not implemented by a concrete subclass.
        """
        pass


class JsonSettingsLoader(SettingsLoader):
    """
    Concrete implementation of settings loader for JSON configuration files.

    This loader provides a robust mechanism for loading settings from JSON files, 
    with built-in validation, error handling, and default configuration support.

    Attributes:
        settings_file (str): Path to the JSON configuration file.

    Methods:
        load_settings: Load and validate settings from a JSON file.
        _validate_settings: Validate and sanitize loaded settings.
        _default_settings: Provide default settings if loading fails.
    """

    def __init__(self, settings_file: str):
        """
        Initialize the JSON settings loader with the path to the settings file.

        Args:
            settings_file (str): Absolute or relative path to the JSON settings file.

        Example:
            loader = JsonSettingsLoader("config/settings.json")
        """
        self.settings_file = settings_file

    def load_settings(self) -> SettingsData:
        """
        Load settings from the specified JSON file and convert to SettingsData.

        This method performs the following key operations:
        1. Attempt to read and parse the JSON file
        2. Validate the loaded settings
        3. Provide default settings if loading or parsing fails
        4. Convert the settings to a SettingsData object

        Returns:
            SettingsData: A structured configuration object with validated settings.

        Raises:
            json.JSONDecodeError: If the JSON file is malformed.
            FileNotFoundError: If the settings file cannot be found.

        Notes:
            - Prints error messages for loading/parsing failures
            - Fallback to default settings if an error occurs
        """
        try:
            # Attempt to read and parse the JSON file
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
                
                # Validate and sanitize the loaded settings
                data = self._validate_settings(settings)
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Handle potential loading or parsing errors
            print(f"Error loading settings from {self.settings_file}: {e}")
            
            # Fallback to default settings
            data = self._default_settings()
        
        # Create and return a SettingsData object
        return SettingsData(**data)

    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize the loaded settings dictionary.

        This method performs the following validations:
        - Ensures all expected keys are present
        - Provides default values for missing keys
        - Allows for potential additional validation logic

        Args:
            settings (Dict[str, Any]): Raw settings dictionary loaded from JSON.

        Returns:
            Dict[str, Any]: Validated and sanitized settings dictionary.

        Example:
            Input: {'module_path': 'my_module'}
            Output: {
                'module_path': 'my_module',
                'track_functions': {},
                'track_classes': {},
                'print_table': False,
                'print_lifecycle': True
            }
        """
        return {
            # Use get() to provide default values, ensuring all keys exist
            'module_path': settings.get('module_path', 'python'),
            'track_functions': settings.get('track_functions', {}),
            'track_classes': settings.get('track_classes', {}),
            'print_table': settings.get('print_table', False),
            'print_lifecycle': settings.get('print_lifecycle', True)
        }

    def _default_settings(self) -> Dict[str, Any]:
        """
        Generate a dictionary of default configuration settings.

        Provides a fallback configuration when loading from a file fails.
        Ensures that the application can run with minimal configuration.

        Returns:
            Dict[str, Any]: A dictionary of default configuration settings.

        Notes:
            - Offers a safe, minimal configuration
            - Prevents application failure due to missing settings
        """
        return {
            'module_path': 'python',  # Default module tracking path
            'track_functions': {},    # No functions tracked by default
            'track_classes': {},      # No classes tracked by default
            'print_table': False,     # Disable tabular output by default
            'print_lifecycle': True   # Enable lifecycle printing by default
        }