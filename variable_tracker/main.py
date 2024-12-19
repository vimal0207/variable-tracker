import sys

from abc import ABC, abstractmethod
from .settings_loader import JsonSettingsLoader
from .function_tracker import FunctionTracker
from .printer import get_printer
from .tracker import Tracker

class SetupAbstract(ABC):
    """
    Abstract base class defining the interface for initializing and managing a tracking system.
    
    Defines the contract for setup and teardown operations in a tracking mechanism.
    Subclasses must implement start() and stop() methods to define specific 
    initialization and cleanup behaviors.
    """

    @abstractmethod
    def start(self):
        """
        Abstract method to initialize the tracking system.
        
        Subclasses must implement the logic for starting tracking,
        setting up necessary components, and preparing the system.
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Abstract method to stop the tracking system and perform cleanup.
        
        Subclasses must implement the logic for stopping tracking,
        releasing resources, and performing any necessary teardown operations.
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        pass


class Setup(SetupAbstract):
    """
    Concrete implementation of the tracking system setup.
    
    Manages the initialization, configuration, and lifecycle of a tracking mechanism
    using a settings loader, function tracker, and custom printer.
    """

    def __init__(self, settings_path : str):
        """
        Initialize the tracking setup with optional custom settings loader.
        
        Args:
            settings_loader (object, optional): A settings loader instance. 
                If not provided, defaults to JsonSettingsLoader with 'settings.json'.
                Allows for flexible configuration and dependency injection.
        
        Attributes:
            settings_loader (object): The configured settings loader
            settings (dict): Loaded configuration settings
        """
        self.settings_loader =  JsonSettingsLoader(settings_path)
        self.settings = {}

    def start(self):
        """
        Initialize and start the tracking system.
        
        Performs the following steps:
        1. Load configuration settings
        2. Create a function tracker based on the settings
        3. Create a printer for displaying tracking information
        4. Create a main tracker instance
        5. Set up system-wide call tracing
        
        Raises:
            Exception: If any error occurs during tracker initialization
        """
        try:
            # Load configuration settings
            self.settings = self.settings_loader.load_settings()
            print("Tracker started with settings:", self.settings)
            
            # Create tracking components
            function_tracker = FunctionTracker(self.settings)
            printer = get_printer(self.settings)
            tracker = Tracker(self.settings, function_tracker, printer)
            
            # Set up system-wide call tracing
            sys.settrace(tracker._trace_calls)
        except Exception as e:
            print(f"Error starting tracker: {e}")
            raise

    def stop(self):
        """
        Stop the tracking system and disable call tracing.
        
        Disables the system-wide trace function, effectively stopping 
        the tracking of function calls and related activities.
        """
        print("Tracker stopped.")
        sys.settrace(None)