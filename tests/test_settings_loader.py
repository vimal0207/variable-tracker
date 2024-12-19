import unittest
from unittest.mock import patch, mock_open
import json
from variable_tracker.settings_loader import JsonSettingsLoader
from variable_tracker.models import SettingsData


class TestJsonSettingsLoader(unittest.TestCase):

    @patch("builtins.open", mock_open(read_data=json.dumps({
        "module_path": "python",
        "track_functions": {"func1": "arg1"},
        "track_classes": {"class1": "arg1"},
        "print_table": True,
        "print_lifecycle": False
    })))
    def test_load_settings_success(self):
        loader = JsonSettingsLoader("config/settings.json")
        settings_data = loader.load_settings()

        self.assertIsInstance(settings_data, SettingsData)
        self.assertEqual(settings_data.module_path, "python")
        self.assertEqual(settings_data.track_functions, {"func1": "arg1"})
        self.assertTrue(settings_data.print_table)

    @patch("builtins.open", mock_open(read_data=json.dumps({
        "module_path": "python"
    })))
    def test_load_settings_with_missing_keys(self):
        loader = JsonSettingsLoader("config/settings.json")
        settings_data = loader.load_settings()

        self.assertEqual(settings_data.module_path, "python")
        self.assertEqual(settings_data.track_functions, {})
        self.assertEqual(settings_data.track_classes, {})
        self.assertFalse(settings_data.print_table)
        self.assertTrue(settings_data.print_lifecycle)

    @patch("builtins.open", mock_open())
    @patch("json.load", side_effect=json.JSONDecodeError("Error", "", 0))
    def test_load_settings_json_decode_error(self, mock_json):
        loader = JsonSettingsLoader("config/settings.json")
        settings_data = loader.load_settings()

        self.assertEqual(settings_data.module_path, "python")  # Default setting is used
        self.assertEqual(settings_data.track_functions, {})
        self.assertEqual(settings_data.track_classes, {})
        self.assertFalse(settings_data.print_table)
        self.assertTrue(settings_data.print_lifecycle)

    @patch("builtins.open", mock_open())
    def test_load_settings_file_not_found(self):
        loader = JsonSettingsLoader("config/settings.json")
        settings_data = loader.load_settings()

        self.assertEqual(settings_data.module_path, "python")  # Default setting is used
        self.assertEqual(settings_data.track_functions, {})
        self.assertEqual(settings_data.track_classes, {})
        self.assertFalse(settings_data.print_table)
        self.assertTrue(settings_data.print_lifecycle)


if __name__ == "__main__":
    unittest.main()
