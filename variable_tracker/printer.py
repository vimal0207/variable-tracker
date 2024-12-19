from abc import ABC, abstractmethod
from .models import SettingsData
from tabulate import tabulate

class PrinterAbstract(ABC):
    """
    Abstract base class defining the interface for printing configuration or tracking data.
    Subclasses must implement the print method to define specific printing strategies.
    """
    @abstractmethod
    def print(self, data: dict, func_name: str):
        """
        Abstract method to print data for a specific function.
        
        Args:
            data (dict): A dictionary containing data to be printed
            func_name (str): The name of the function whose data is being printed
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        pass


class TabluerPrinter(PrinterAbstract):
    """
    A printer implementation that displays data in a tabular format using the tabulate library.
    Prints changes to variables in a grid-like table.
    """

    def print(self, data: dict, func_name: str):
        """
        Print the data for a specific function in a tabular grid format.
        
        Args:
            data (dict): A dictionary of function data
            func_name (str): The name of the function being processed
        
        Prints:
            A formatted table showing variable changes using tabulate
        """
        value = data.pop(func_name)
        if value:
            headers = ["Variable", "Change Type", "Value"]
            print(f"\n-----------------Function '{func_name}' data-----------------")
            print(tabulate(value, headers=headers, tablefmt="grid"))


class LifeCyclePrinter(PrinterAbstract):
    """
    A printer implementation that displays the full lifecycle of tracked variables 
    with a detailed, hierarchical print format.
    """

    def print(self, data: dict, func_name: str):
        """
        Print the complete lifecycle of variables for a specific function.
        
        Args:
            data (dict): A dictionary containing variable lifecycle information
            func_name (str): The name of the function being processed
        
        Prints:
            A detailed representation of each variable's changes throughout its lifecycle
        """
        print(f"\n-----------------Function '{func_name}' Variable Lifecycles-----------------")
        value = data.pop(func_name)
        for var_name, lifecycle in value.items():
            print(f"  Variable: {var_name}")
            for change_type, value in lifecycle:
                print(f"    - {change_type}: {value}")


def get_printer(settings: SettingsData) -> PrinterAbstract:
    """
    Factory method to create and return an appropriate Printer instance based on settings.
    
    Args:
        settings (SettingsData): Configuration settings determining the printer type
    
    Returns:
        PrinterAbstract: Either a TabluerPrinter or LifeCyclePrinter 
        based on the print_table setting
    """
    if settings.print_table:
        return TabluerPrinter()
    else:
        return LifeCyclePrinter()