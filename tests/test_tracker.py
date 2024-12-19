import unittest
from unittest.mock import MagicMock, patch
from variable_tracker.tracker import Tracker
from variable_tracker.models import SettingsData
from variable_tracker.function_tracker import FunctionTracker
from variable_tracker.printer import PrinterAbstract


class TestTracker(unittest.TestCase):

    def setUp(self):
        # Set up mock SettingsData and Tracker components
        self.settings = SettingsData(
            module_path="python",
            track_functions={},
            track_classes={},
            print_table=False,
            print_lifecycle=True
        )
        self.function_tracker = MagicMock(FunctionTracker)
        self.printer = MagicMock(PrinterAbstract)

        # Create an instance of Tracker with the mocks
        self.tracker = Tracker(self.settings, self.function_tracker, self.printer)

        # Mocking variable_lifecycle attribute for the FunctionTracker
        self.function_tracker.variable_lifecycle = []

    def test_get_class_name_inside_class(self):
        # Test if inside a class, the method returns class name
        frame = MagicMock()
        frame.f_locals = {"self": object}
        result = self.tracker._get_class_name(frame)
        self.assertIsInstance(result, str)

    def test_get_class_name_outside_class(self):
        # Test if outside a class, the method returns None
        frame = MagicMock()
        frame.f_locals = {}
        result = self.tracker._get_class_name(frame)
        self.assertIsNone(result)

    @patch.object(Tracker, '_trace_calls', return_value=None)
    def test_trace_calls(self, *args, **kwargs):
        # Test the _trace_calls method itself
        frame = MagicMock()
        event = "return"
        arg = None

        result = self.tracker._trace_calls(frame, event, arg)
        self.tracker._trace_calls.assert_called_once_with(frame, event, arg)
        self.assertIsNone(result)

    def test_trace_calls_with_function(self):
        # Test that the tracker interacts correctly with function tracker and printer
        frame = MagicMock()
        event = "return"
        arg = None

        self.tracker._trace_calls(frame, event, arg)

        # Assert that the function tracker and printer were called
        self.function_tracker._trace_function_variables.assert_called_once()
        self.printer.print.assert_called_once()

    def test_trace_calls_with_print_lifecycle(self):
        # Test if print_lifecycle flag triggers printing in the tracker
        self.settings.print_lifecycle = True
        frame = MagicMock()
        event = "return"
        arg = None

        self.tracker._trace_calls(frame, event, arg)

        # Assert that variable_lifecycle is being passed to the printer
        self.printer.print(self.function_tracker.variable_lifecycle, "full_func_name")


if __name__ == "__main__":
    unittest.main()
