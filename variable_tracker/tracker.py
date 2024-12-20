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
    Concrete implementation of the TrackerAbstract class for tracking function calls 
    and managing variable lifecycles within the code. It leverages the settings, 
    function tracking, and printer to provide optimized trace functionality.

    Attributes:
        settings (SettingsData): Configuration for the tracker behavior.
        function_tracker (FunctionTracker): Responsible for tracking function-related data.
        printer (PrinterAbstract): Handles printing the tracked data.
        skip_paths (list): Paths to skip during tracing (e.g., Django and other frameworks).
    
    Methods:
        _should_skip_frame: Determines if the current stack frame should be skipped.
        _get_class_name: Extracts the class name from the given stack frame.
        _trace_calls: Main method to trace function calls and variable changes.
    """
    
    def __init__(
        self, 
        settings: SettingsData, 
        function_tracker: FunctionTracker, 
        printer: PrinterAbstract
    ):
        """
        Initialize the Tracker instance.

        Args:
            settings (SettingsData): Configuration for the tracker behavior.
            function_tracker (FunctionTracker): Function tracking object.
            printer (PrinterAbstract): Printer object to display data.
        """
        self.settings = settings
        self.function_tracker = function_tracker
        self.printer = printer
        # Paths to skip when tracing, such as Django and third-party libraries
        self.skip_paths = [
            'django',
            'asgiref',
            'urllib',
            'socketserver',
            'concurrent',
            'multiprocessing',
            'wsgiref',
            'site-packages',
            'lib/python',
            '/usr/lib/python'
        ]

    def _should_skip_frame(self, filename: str) -> bool:
        """
        Determine if the current frame should be skipped based on its filename.

        Args:
            filename (str): The filename from the frame.
        
        Returns:
            bool: True if the frame should be skipped, otherwise False.
        """
        # Skip if the filename is outside the module's path
        if not self.settings.module_path in filename:
            return True
            
        # Skip framework-related files such as Django or third-party libraries
        return any(path in filename for path in self.skip_paths)

    def _get_class_name(self, frame: Any) -> Optional[str]:
        """Extract the class name from a stack frame."""
        if "self" not in frame.f_locals:
            return None
            
        try:
            return frame.f_locals["self"].__class__.__name__
        except (AttributeError, KeyError):
            return None
    
    def _trace_calls(self, frame: Any, event: str, arg: Any) -> Any:
        """
        Trace function calls with Django-specific optimizations. It is the main 
        function that processes the function call events and tracks the variables.

        Args:
            frame (Any): The current stack frame being traced.
            event (str): The type of event ('call', 'line', 'return', etc.).
            arg (Any): Additional event-specific argument.
        
        Returns:
            Any: Returns self to continue tracing the next frame.
        """
        try:
            # Get filename from the stack frame
            filename = frame.f_code.co_filename

            # Skip processing if the frame should be skipped
            if self._should_skip_frame(filename):
                return self._trace_calls

            # Extract context information like function, class, and module name
            file_name = Path(filename).stem
            module_name = frame.f_globals.get("__name__", "")
            func_name = frame.f_code.co_name
            class_name = self._get_class_name(frame)

            # Skip Django internal methods related to dispatching, middleware, or response
            if any(name in func_name for name in ['dispatch', 'middleware', 'get_response']):
                return self._trace_calls

            # Get the fully qualified function name using function tracker
            full_func_name = self.function_tracker._get_function_full_name(
                module_name, file_name, func_name, class_name
            )
            
            if full_func_name:
                # Track the variables within the function call
                self.function_tracker._trace_function_variables(frame, full_func_name, class_name)
                
                # Print the changes in the function's variables when it returns
                if event == "return":
                    if self.settings.print_table:
                        self.printer.print(
                            self.function_tracker.variable_changes, 
                            full_func_name
                        )
                    else:
                        self.printer.print(
                            self.function_tracker.variable_lifecycle, 
                            full_func_name
                        )
        
        except Exception as e:
            # Catch any exceptions that occur during tracing
            print(f"Error in variable tracking: {str(e)}")
            
        # Return self to continue tracing further frames
        return self._trace_calls
