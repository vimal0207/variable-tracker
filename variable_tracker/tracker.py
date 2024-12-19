from typing import Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from .models import SettingsData
from .function_tracker import FunctionTracker
from .printer import PrinterAbstract

class TrackerAbstract(ABC):
    """
    Abstract base class defining the contract for variable tracking functionality.
    
    This class provides an abstract interface for tracking function calls, 
    extracting class names, and managing the tracing process. Concrete 
    implementations must provide specific tracking mechanisms.

    Attributes:
        No direct attributes defined in the abstract base class.

    Methods:
        _trace_calls: Abstract method to trace function calls and variable changes.
        _get_class_name: Abstract method to extract the class name from a stack frame.
    """

    @abstractmethod
    def _trace_calls(self, frame: Any, event: str, arg: Any) -> Any:
        """
        Abstract method to trace function calls and manage variable tracking.

        This method is called for each function call during tracing and should 
        implement the core logic of tracking variable lifecycles.

        Args:
            frame (Any): The current stack frame being traced.
            event (str): The type of event ('call', 'line', 'return', etc.).
            arg (Any): Additional event-specific argument.

        Returns:
            Any: Typically returns itself to continue tracing, or None to stop.

        Raises:
            NotImplementedError: If not implemented by a concrete subclass.
        """
        pass

    @abstractmethod
    def _get_class_name(self, frame: Any) -> Optional[str]:
        """
        Abstract method to extract the class name from a stack frame.

        Determines the name of the class containing the current method being executed.

        Args:
            frame (Any): The current stack frame.

        Returns:
            Optional[str]: The name of the class, or None if not inside a class method.

        Raises:
            NotImplementedError: If not implemented by a concrete subclass.
        """
        pass


class Tracker(TrackerAbstract):
    """
    Concrete implementation of the variable tracking functionality.

    This tracker provides a comprehensive mechanism for tracking variable 
    lifecycles across different functions and classes, with configurable 
    settings and output mechanisms.

    Attributes:
        settings (SettingsData): Configuration settings for tracking.
        function_tracker (FunctionTracker): Component responsible for tracking function variables.
        printer (PrinterAbstract): Component responsible for printing variable changes.
    """

    def __init__(
        self, 
        settings: SettingsData, 
        function_tracker: FunctionTracker, 
        printer: PrinterAbstract
    ):
        """
        Initialize the Tracker with necessary components.

        Args:
            settings (SettingsData): Configuration settings for variable tracking.
            function_tracker (FunctionTracker): Mechanism to track function variables.
            printer (PrinterAbstract): Mechanism to print variable changes.
        """
        self.settings = settings
        self.function_tracker = function_tracker
        self.printer = printer

    def _get_class_name(self, frame: Any) -> Optional[str]:
        """
        Extract the class name from a stack frame.

        Determines the name of the class containing the current method being executed.
        This method specifically looks for the 'self' parameter in the frame's local variables.

        Args:
            frame (Any): The current stack frame.

        Returns:
            Optional[str]: The name of the class, or None if not inside a class method.
        
        Example:
            If called inside a method of a class 'MyClass', returns 'MyClass'.
            If called in a standalone function, returns None.
        """
        return frame.f_locals.get("self", object).__class__.__name__ if "self" in frame.f_locals else None
    
    def _trace_calls(self, frame: Any, event: str, arg: Any) -> Any:
        """
        Trace function calls and track variable changes.

        This method is called for each function call during tracing. It performs 
        the following key operations:
        1. Checks if the current frame is within the specified module path
        2. Extracts module, function, and class names
        3. Traces function variables
        4. Prints variable changes based on configuration settings

        Args:
            frame (Any): The current stack frame being traced.
            event (str): The type of event ('call', 'line', 'return', etc.).
            arg (Any): Additional event-specific argument.

        Returns:
            Any: Returns itself to continue tracing, enabling recursive tracing.

        Notes:
            - Only tracks functions outside the specified module path
            - Prints variable changes when a function returns
            - Uses different printing methods based on configuration
        """
        # Extract the file name without extension
        file_name = Path(frame.f_code.co_filename).stem

        # Skip tracing if the frame is within the specified module path
        if not self.settings.module_path in frame.f_code.co_filename:
            # Extract context information
            module_name = frame.f_globals.get("__name__", "")
            func_name = frame.f_code.co_name
            class_name = self._get_class_name(frame)

            # Get the fully qualified function name
            full_func_name = self.function_tracker._get_function_full_name(
                module_name, file_name, func_name, class_name
            )
            
            # Process function variables if tracking is enabled
            if full_func_name:
                # Track variables within the function
                self.function_tracker._trace_function_variables(frame, full_func_name, class_name)
                
                # Print variable changes when function returns
                if event == "return":
                    # Choose printing method based on settings
                    if self.settings.print_table:
                        # Print changes in tabular format
                        self.printer.print(
                            self.function_tracker.variable_changes, 
                            full_func_name
                        )
                    else:
                        # Print full variable lifecycle
                        self.printer.print(
                            self.function_tracker.variable_lifecycle, 
                            full_func_name
                        )
        
        # Return self to continue tracing
        return self._trace_calls