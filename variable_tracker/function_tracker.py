from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .models import SettingsData


class FunctionTrackerAbstract(ABC):
    """
    Abstract base class for a function tracker, ensuring that all subclasses
    implement the required methods for handling function tracking.
    """
    
    @abstractmethod
    def _get_function_full_name(self, module_name: str, file_name: str, 
                                func_name: str, class_name: Optional[str]) -> str:
        """
        Generate the full name of a function for tracking purposes.

        Args:
            module_name: The name of the module containing the function.
            file_name: The name of the file containing the function.
            func_name: The name of the function.
            class_name: The name of the class if the function belongs to a class.

        Returns:
            The fully qualified name of the function or a matching tracking key.
        """
        pass


class FunctionTracker(FunctionTrackerAbstract):
    """
    Concrete implementation of a function tracker that tracks function calls
    and variable lifecycles based on provided settings.
    """

    def __init__(self, settings: SettingsData):
        """
        Initialize the FunctionTracker with user-defined settings.

        Args:
            settings: An instance of SettingsData containing tracking configurations.
        """
        self.settings = settings
        # To store the lifecycle of tracked variables per function
        self.variable_lifecycle: Dict[str, Dict[str, List[tuple]]] = {}
        # To store all changes to variables per function
        self.variable_changes: Dict[str, Dict[str, List[tuple]]] = {}

    def _get_function_full_name(self, module_name: str, file_name: str, 
                                func_name: str, class_name: Optional[str]) -> str:
        """
        Generate the fully qualified function name or find a match for tracking.

        Args:
            module_name: The name of the module containing the function.
            file_name: The name of the file containing the function.
            func_name: The name of the function.
            class_name: The class name, if the function is a method.

        Returns:
            A matching key for tracking or an empty string if no match is found.
        """
        # Skip tracking if settings explicitly do not track classes or functions
        if (class_name and not self.settings.track_classes) or not self.settings.track_functions:
            return func_name

        # Generate all possible key variations for matching
        possible_keys = [
            f"{module_name}.{file_name}.{func_name}",
            f"{module_name}.{file_name}.{class_name}.{func_name}",
            f"{file_name}.{func_name}",
            f"{file_name}.{class_name}.{func_name}",
            f"{class_name}.{func_name}",
            func_name
        ]

        # Check if any of the keys match the configured tracking keys
        for key in possible_keys:
            if key in self.settings.track_functions or key in self.settings.track_classes:
                return key

        return ""

    def _trace_function_variables(self, frame: Any, full_func_name: str, class_name: Optional[str]) -> None:
        """
        Trace local and class-level variables in a function or method.

        Args:
            frame: The current execution frame of the function being tracked.
            full_func_name: The fully qualified name of the function.
            class_name: The name of the class, if the function is a method.
        """
        # Snapshot of local variables within the function
        locals_snapshot = frame.f_locals

        # Initialize storage for variable lifecycle and changes if not already present
        if full_func_name not in self.variable_lifecycle:
            self.variable_lifecycle[full_func_name] = {}

        if full_func_name not in self.variable_changes:
            self.variable_changes[full_func_name] = []

        # Extract class-level variables if the function is a method
        class_vars = {}
        if class_name and "self" in locals_snapshot:
            try:
                class_vars = vars(locals_snapshot["self"])
            except TypeError:
                # Handle cases where `self` may not be a standard class-like object
                pass

        # Merge local and class-level variables for tracking
        variables_to_track = {**locals_snapshot, **class_vars}

        for var_name, value in variables_to_track.items():
            # Check if the variable should be tracked
            if self._should_track_variable(full_func_name, class_name, var_name) and isinstance(
                value, (int, float, str, list, dict, tuple, set, complex, bool, bytes, bytearray, memoryview)
            ):
                # Track the lifecycle of the variable
                var_lifecycle = self.variable_lifecycle[full_func_name].setdefault(var_name, [])

                # Log variable initialization or changes
                if not var_lifecycle or var_lifecycle[-1][1] != value:
                    change_type = "Initialized" if not var_lifecycle else "Changed"
                    var_lifecycle.append((change_type, value))
                    self.variable_changes[full_func_name].append((var_name, change_type, value))

    def _should_track_variable(self, full_func_name: str, class_name: Optional[str], var_name: str) -> bool:
        """
        Determine if a specific variable should be tracked.

        Args:
            full_func_name: The fully qualified name of the function.
            class_name: The name of the class, if applicable.
            var_name: The name of the variable.

        Returns:
            True if the variable should be tracked; otherwise, False.
        """
        # Helper function to check wildcard or key-specific inclusion
        def is_wildcard_or_contains(target_dict, key):
            return key in target_dict and (target_dict[key] == "*" or var_name in target_dict[key])

        # Check if the variable meets the tracking conditions
        return (
            is_wildcard_or_contains(self.settings.track_functions, full_func_name) or
            is_wildcard_or_contains(self.settings.track_classes, class_name) or
            (class_name and not self.settings.track_classes) or 
            not self.settings.track_functions
        ) and not var_name.startswith("_")  # Skip private variables (prefixed with `_`)
