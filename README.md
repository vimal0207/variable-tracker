# Variable Lifecycle Tracker

A Python library for tracking and analyzing variable lifecycles within functions and classes during runtime. This tool helps developers understand how variables change throughout program execution, making it easier to debug and optimize code.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration Guide](#configuration-guide)
- [Output Formats](#output-formats)
- [Best Practices](#best-practices)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- Track variable value changes throughout function execution
- Monitor class methods and their variable changes
- Multiple output formats (tabular and lifecycle)
- Configurable tracking settings via JSON
- Flexible function and class naming conventions for precise tracking
- Non-intrusive implementation using Python's sys.settrace
- Easy setup and integration with existing projects

## 💻 Installation

```bash
pip install variable-tracker
```

## 🚀 Quick Start

1. **Create a settings file (`settings.json`):**

```json
{
    "module_path": "python",
    "track_functions": {
        "calculate_total": "*"
    },
    "track_classes": {},
    "print_table": true,
    "print_lifecycle": false
}
```

The settings file defines how the `variable-lifecycle-tracker` operates. Below is an explanation of each field:

| **Field**          | **Type**        | **Description**                                                                                  | **Example**                                |
|---------------------|-----------------|--------------------------------------------------------------------------------------------------|--------------------------------------------|
| `module_path`       | `string`        | Specifies the root module or package path for tracking. It helps exclude external libraries by limiting tracking to your project's code, specifically with the module path to trace. | `"variable_tracker"`                                 |
| `track_functions`   | `object` / `[]` | Defines the functions to be tracked. Keys represent function names (with optional paths), and values determine variables to track. Use an empty array `[]` to track all functions. | `{"calculate_total": "*"}`                |
| `track_classes`     | `object` / `[]` | Defines the classes to be tracked. Keys represent class names (with optional paths), and values specify methods and variables to track. Use an empty array `[]` to track all classes. | `{}`                                      |
| `print_table`       | `boolean`       | If `true`, prints the tracked variable data in a tabular format.                                  | `true`                                     |
| `print_lifecycle`   | `boolean`       | If `true`, prints a lifecycle view of each tracked variable.                                      | `false`                                    |


2. **Use the tracker in your code:**

### For Python Scripts:

```python
from variable_tracker import Setup

settings_file_path = "settings.json"
# Initialize the tracker
tracker = Setup(settings_file_path)

try:
    # Start tracking
    tracker.start()

    # Your code here
    def calculate_total(items):
        total = 0
        for item in items:
            total += item.price
        return total

    # Run your code
    items = [Item(price=10), Item(price=20)]
    result = calculate_total(items)

finally:
    # Stop tracking
    tracker.stop()
```

### For Django (Using Middleware):
```python
# your_project/middleware.py
from variable_tracker import Setup

class VariableTrackerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize the tracker
        self.tracker = Setup("settings.json")

    def __call__(self, request):
        try:
            # Start tracking
            self.tracker.start()

            # Process the request
            response = self.get_response(request)
            return response
        finally:
            # Stop tracking
            self.tracker.stop()

# Add to settings.py
MIDDLEWARE = [
    'your_project.middleware.VariableTrackerMiddleware',
    # ... other middleware
]
```

## ⚙️ Configuration Guide

### Naming Conventions

#### Functions
- Full path: `module_name.file_name.function_name`
- File path: `file_name.function_name`
- Direct name: `function_name`

#### Classes
- Full path: `module_name.file_name.class_name`
- File path: `file_name.class_name`
- Direct name: `class_name`

#### Class Methods
- Full path: `module_name.file_name.class_name.method_name`
- File path: `file_name.class_name.method_name`
- Direct name: `class_name.method_name`

### Configuration Examples

#### 1. Track Specific Function
```json
{
    "module_path": "python",
    "track_functions": {
        "sample_function" : "*",
        "sample_file.sample_function": ["var1", "var2"],
        "sample_module.sample_file.sample_function": ["var1", "var2"],
        },
    "track_classes": {},
    "print_table": true,
    "print_lifecycle": false
}
```

#### 2. Track Class With Specific Variable
```json
{
    "module_path": "python",
    "track_classes": {
        "SampleClass": ["key", "value"],
        "sample_file.SampleClass": "*",
        "sample_module.sample_file.SampleClass": "*",
    },
    "track_functions": {},
    "print_table": true,
    "print_lifecycle": false
}
```

#### 3. Track All Classes And Function
```json
{
    "module_path": "python",
    "track_classes": {},
    "track_functions": {},
    "print_table": true,
    "print_lifecycle": false
}
```

#### 4. Track ClassMethod, Function
```json
{
    "module_path": "python",
    "track_classes": {},
    "track_functions": {
        "SampleClass.sample_method": "*",
        "sample_file.SampleClass.sample_method": ["var1"],
        "sample_module.sample_file.SampleClass.sample_method": ["var1"],
        "sample_function": "*"
    },
    "print_table": true,
    "print_lifecycle": false
}
```

## 📊 Output Formats

### Tabular Output (`print_table: true`)
```
-----------------Function 'calculate_total' data-----------------
+----------+--------------+-------+
| Variable | Change Type  | Value |
+----------+--------------+-------+
| total    | initialized  | 0     |
| total    | modified     | 10    |
| total    | modified     | 30    |
| total    | returned     | 30    |
+----------+--------------+-------+
```

### Lifecycle Output (`print_lifecycle: true`)
```
-----------------Function 'calculate_total' Variable Lifecycles-----------------
  Variable: total
    - initialized: 0
    - modified: 10
    - modified: 30
    - returned: 30
```

## 📝 Variable Selection

- Use `"*"` to track all variables
- Use array for specific variables: `["var1", "var2"]`

## 💡 Best Practices

1. **Always use try-finally blocks:**
```python
tracker = Setup()
try:
    tracker.start()
    # Your code here
finally:
    tracker.stop()
```

2. **Use specific naming patterns:**
   - Use full paths for precise targeting
   - Use file paths for file-level tracking
   - Use direct names for project-wide tracking

3. **Choose appropriate output format:**
   - Tabular output for overview
   - Lifecycle output for detailed analysis

4. **Optimize performance:**
   - Track specific variables instead of using "*"
   - Use precise function/class naming
   - Track only necessary functions and methods

## ⚠️ Limitations

- Recommended for use in development environments only
- Not suitable for production servers
- Performance impact varies based on tracking scope
- Cannot track C extensions or built-in functions

## 🤝 Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## ❤️ Support 

If you enjoy using this project or want to help improve it, your support means the world! You can:

- ⭐ Star the repository
- 🗨️ Share feedback
- ☕ [Buy Me a Coffee](https://buymeacoffee.com/vimal0207)

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%23FFDD00.svg?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/vimal0207)


## 📄 License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.