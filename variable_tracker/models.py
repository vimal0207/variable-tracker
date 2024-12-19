from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class SettingsData:
    """
    Represents configuration settings for variable lifecycle tracking.
    
    Attributes:
        module_path: Path to the module being tracked
        track_functions: Functions to track
        track_classes: Classes to track
        print_table: Whether to print changes in a table format
        print_lifecycle: Whether to print full variable lifecycle
    """
    module_path: str = 'python'
    track_functions: Dict[str, Any] = None
    track_classes: Dict[str, Any] = None
    print_table: bool = False
    print_lifecycle: bool = True

    def __post_init__(self):
        """
        Initialize mutable default values.
        
        Since dataclasses can't have mutable default values in the class definition,
        we use __post_init__ to set them.
        """
        if self.track_functions is None:
            self.track_functions = {}
        if self.track_classes is None:
            self.track_classes = {}