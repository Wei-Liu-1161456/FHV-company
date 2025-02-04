import tkinter as tk
from tkinter import ttk

class ValidatedSpinbox(ttk.Spinbox):
    def __init__(self, *args, from_=1, to=100, **kwargs):
        """
        Initialize the Spinbox with validation. Supports integer and float modes.
        """
        super().__init__(*args, from_=from_, to=to, **kwargs)
        
        # Default properties
        self._model = 'float'  # Mode: 'int' for positive integers, 'float' for up to one decimal place
        self.max_value = to    # Maximum value, can be dynamically set on initialization
        self.int_min = from_   # Minimum value for integer mode
        self.float_min = 0.1   # Minimum value for float mode
        self.default_value = from_  # Initial value defaults to starting value

        # Configure validation command
        self.configure(validate='key', validatecommand=(self.register(self._validate_input), '%P'))

    @property
    def model(self):
        """Get the current mode ('int' or 'float')"""
        return self._model

    @model.setter
    def model(self, value):
        """Set the mode ('int' or 'float') and reset to default value when switching modes"""
        if value in ['int', 'float']:
            self._model = value
            if value == 'int':
                self.configure(from_=self.int_min, increment=1)
                self.set(self.int_min)  # Reset to minimum value in integer mode
            elif value == 'float':
                self.configure(from_=self.float_min, increment=0.1)
                self.set(self.default_value)  # Reset to default value in float mode
        else:
            raise ValueError("The model attribute must be 'int' or 'float'")
    
    def _validate_input(self, value_if_allowed):
        """
        Validate input based on the current mode, adjust automatically to max value if exceeded.
        """
        if value_if_allowed == "":
            return True

        # Integer mode validation
        if self._model == 'int':
            if value_if_allowed.isdigit():  # Only allow digits
                int_value = int(value_if_allowed)
                if int_value > self.max_value:
                    self.set(self.max_value)
                return int_value >= self.int_min

        # Float mode validation
        elif self._model == 'float':
            try:
                # Check float format, limit decimal places to 1
                if value_if_allowed.count('.') <= 1 and all(c.isdigit() or c == '.' for c in value_if_allowed):
                    if '.' in value_if_allowed:
                        decimal_part = value_if_allowed.split('.')[1]
                        # Limit decimal part to only 1 digit
                        if len(decimal_part) > 1:
                            return False
                    float_value = float(value_if_allowed)
                    if float_value > self.max_value:
                        self.set(f"{self.max_value:.1f}")
                    return float_value >= self.float_min
            except ValueError:
                return False
        return False