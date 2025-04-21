import logging

# Local logger
logger = logging.getLogger(__name__)

class Validator():
    """
    Base class for settings validator
    """

    def __init__(self):
        pass

    def validate(self, value):
        raise NotImplementedError(f"{self.__class__} must implement self.validate(value).")

    @property
    def allowed_values_as_string(self):
        raise NotImplementedError(f"{self.__class__} must implement self.allowed_values_as_string.")

class ListValidator(Validator):
    """
    Validates a value to be a list item
    """
    def __init__(self, allowed_values):
        self._allowed_values = allowed_values

    def validate(self, value):
        for val in self._allowed_values:
            if value.lower() == val:
                return val
        return None

    @property
    def allowed_values_as_string(self):
        return str(self._allowed_values)

class IntegerRangeValidator(Validator):
    """
    Validates a value to be within a range
    """

    def __init__(self, min, max):
        self._min = minimum
        self._max = maximum

    def validate(self, value):
        return value if value >= self._min and value <= self._max else None

    @property
    def allowed_values_as_string(self):
        return f"{self._min} to {self._max}"

class BooleanValidator(Validator):
    """
    Validates a value to a boolean
    """
    def validate(self, value):
        value = str(value).lower()
        return True if value == 'true' else False if value == 'false' else None

    @property
    def allowed_values_as_string(self):
        return "'true' or 'false'"

