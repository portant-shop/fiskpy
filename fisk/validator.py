import re


class XMLValidator:
    """Base validator class."""

    def validate(self, value):
        """Override this method in derived classes."""
        return True


class XMLValidatorLen(XMLValidator):
    """Validator which checks string length."""

    def __init__(self, min_len, max_len):
        """
        Init XMLValidatorLen.

        Args:
            min_len (int): Minimum length
            max_len (int): Maximum length
        """
        self.min = min_len
        self.max = max_len

    def validate(self, value):
        if value is None:
            return True
        if (isinstance(value, str)):
            lenght = len(value)
            if lenght >= self.min and lenght <= self.max:
                return True
        return False


class XMLValidatorRegEx(XMLValidator):
    """regex validator. Returns True if regex is matched or false if it is not."""

    def __init__(self, regex):
        """
        Init.

        Args:
            regex (str): is regular expression
        """
        self.regex = re.compile(regex)

    def validate(self, value):
        if value is None:
            return True
        if (isinstance(value, str)):
            if self.regex.match(value) is not None:
                return True
        return False


class XMLValidatorEnum(XMLValidator):
    """validator which checks is value in values list.

    Returns
    True if value is found in list and flase if value is ot in the list
    """

    def __init__(self, values):
        """
        Init.

        Args:
            values (list): list of possible values
        """
        self.values = values

    def validate(self, value):
        if value is None:
            return True
        if isinstance(value, str):
            if value in self.values:
                return True
        return False


class XMLValidatorType(XMLValidator):
    """type cheking validator."""

    def __init__(self, typeC):
        """
        Init.

        Args:
            typeC: is object of which type value should be checked.
        """
        self.type = typeC

    def validate(self, value):
        """
        Validate.

        Returns: True if value is not set or if value is of selected
            type otherwise returns False
        """
        if value is None:
            return True
        if isinstance(value, self.type):
            return True
        return False


class XMLValidatorListType(XMLValidator):
    """
    validator which checks are all object in list of defined type.

    Returns True if they are False if they are not.
    """

    def __init__(self, typeC):
        """
        Init.

        Args:
            typeC: tpye for which list itmes will be checked
        """
        self.type = typeC

    def validate(self, value):
        if value is None:
            return True
        if isinstance(value, list):
            ret = True
            for val in value:
                if not isinstance(val, self.type):
                    ret = False
                    break
            return ret
        return False


class XMLValidatorRequired(XMLValidator):
    """Check if value is None or not."""

    def validate(self, value):
        """
        Validate.

        Returns: True if value is not None or False
            if value is None
        """
        if value is None:
            return False
        return True
