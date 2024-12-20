# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-12-20
### Added
- Added support for Django middleware integration.
- New feature: Ability to track model methods in Django apps.

### Changed
- Improved lifecycle logging for variable changes.
- Enhanced settings configuration for better flexibility.

### Fixed
- Resolved an issue where tracker would not stop correctly in some scenarios.

## [0.1.0] - 2024-12-19
### Initial Release
- First official release of the library to PyPI.
- Supported tracking of variable lifecycles in Python scripts.
- Features included tracking function and class variable changes during runtime.
- Configuration via JSON settings file for Python scripts.
- Output formats: Tabular and lifecycle views.