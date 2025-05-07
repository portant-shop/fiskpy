from fisk.validator import XMLValidator, XMLValidatorRequired
from lxml import etree as et


class XMLElement(object):
    """
    XMLElement - this is class which knows to represent her self and hers attributes as xml element.

    this is usually used as base calss

    it uses ElementTree for xml generation
    """

    def __init__(self, childrenNames=None, namespace="", text=None, data=None, name=None):
        """
        Create XMLElement object.

        childrenNames (tuple): ((name1, validators1), (name2, validators2), ...)
        namespace (str): xml namespace used for this class element and its sub elements
        text (str): if set and if this class does not hold any attribute that this text is text
            inside xml tag
        data (dict): initial data
        name (str): if for some reason you have to use diferent name for xml tag then class name
        """
        if childrenNames is None:
            childrenNames = ()
        self.__dict__['items'] = dict()
        self.__dict__['order'] = []
        self.__dict__['attributes'] = dict()
        self.__dict__['namespace'] = "{" + namespace + "}"
        self.__dict__['text'] = None
        self.__dict__['textValidators'] = []
        self.__dict__['textRequired'] = []
        self.__dict__['name'] = name
        self.__dict__["validators"] = dict()
        self.__dict__['required'] = dict()

        childNames = list()
        for element in childrenNames:
            key, value = element
            childNames.append(key)
        self.setAvailableChildren(childNames)

        for element in childrenNames:
            name, validators = element
            if isinstance(validators, list):
                for validator in validators:
                    self.addValidator(name, validator)
            else:
                raise TypeError("Validators has to be list of validators")

        if text is not None:
            self.__setattr__("text", text)
        if data is not None:
            for name, value in data.items():
                self.__setattr__(name, value)

    def generate(self):
        """
        Return (ElementTree): xml reprezentation of this class.

        Raises:
            ValueError: This method also checks are all required valuesa (attributes) set.
                If not it will raise this exception
        """
        # generate xml as ElementTree
        xml = et.Element(self.__dict__["namespace"] + self.getName(), self.__dict__['attributes'])
        if self.__dict__['items']:
            for key in self.__dict__['order']:
                # check if it is required
                if key in self.__dict__['required']:
                    validators = self.__dict__['required'][key]
                    for validator in validators:
                        if not validator.validate(self.__dict__['items'][key]):
                            raise ValueError(
                                f"Attribute {key}  of class {self.__class__.__name__} is required!"
                            )
                value = self.__dict__['items'][key]
                if value is not None:
                    if isinstance(value, str):
                        svar = et.SubElement(xml, self.__dict__["namespace"] + key)
                        svar.text = value
                    elif isinstance(value, list):
                        svar = et.SubElement(xml, self.__dict__["namespace"] + key)
                        for subvalue in value:
                            if issubclass(type(subvalue), XMLElement):
                                svar.append(subvalue.generate())
                    elif issubclass(type(value), XMLElement) and key == value.getName():
                        xml.append(value.generate())
                    else:
                        raise TypeError("Generate method in class " +
                                        self.__class__.__name__ + " can not generate supplied type")
        else:
            # check if it text is required
            validators = self.__dict__['textRequired']
            for validator in validators:
                if not validator.validate(self.__dict__['text']):
                    raise ValueError(
                        "Text attribute of class " +
                        self.__class__.__name__ +
                        " is required!"
                    )
            xml.text = self.__dict__["text"]
        return xml

    def __getattr__(self, name):
        if name not in self.items:
            raise NameError(
                "Class " + self.__class__.__name__ +
                " does not have attribute with name " + name
            )
        return self.items[name]

    def __setattr__(self, name, value):
        if name == "items":
            return
        if name == "text":
            if isinstance(value, str):
                if self._validateValue(name, value):
                    self.__dict__['items'] = dict()
                    self.__dict__['text'] = value
                else:
                    raise ValueError(
                        "Value " +
                        value +
                        " (" +
                        type(value).__name__ +
                        ") is not valid as text of " +
                        self.__class__.__name__ +
                        " element"
                    )
            else:
                raise TypeError("text attribute must be string")
        else:
            if name not in self.__dict__['order']:
                raise NameError(
                    "Class " + self.__class__.__name__ +
                    " does not have attribute with name " + name
                )
            if self._validateValue(name, value):
                self.items[name] = value
            else:
                raise ValueError(
                    "Value " + str(value) + " (" + type(value).__name__ +
                    ") is not valid for " + name + " attribute of class " +
                    self.__class__.__name__
                )

    def setAvailableChildren(self, names):
        """Set list of possible sub elements (in context of class possible attributes)."""
        self.__dict__['items'] = dict()
        self.__dict__['order'] = []
        self.__dict__['validators'] = dict()
        self.__dict__['required'] = dict()
        for name in names:
            if name != "text":
                self.__dict__['items'][name] = None
                self.__dict__['order'].append(name)
                self.__dict__['validators'][name] = []
                self.__dict__['required'][name] = []

    def setAttr(self, attrs):
        """
        Reset element attributes.

        attrs - dict with keys as attribute names and values as attribure values
        """
        if isinstance(attrs, dict):
            self.__dict__['attributes'] = attrs

    def setNamespace(self, namespace):
        """Set new namespace for this elementa and all his children."""
        self.__dict__["namespace"] = "{" + namespace + "}"

    def getElementName(self):
        """Return full xml element tag name including namespace as used in ElementTree module."""
        return self.__dict__["namespace"] + self.getName()

    def getName(self):
        name = self.__class__.__name__
        if self.__dict__['name'] is not None:
            name = self.__dict__['name']
        return name

    def addValidator(self, name, validator):
        """
        Add new validator to valirable.

        After adding new validator this function will try to validate element
        """
        if name == "text":
            if isinstance(validator, XMLValidator):
                if isinstance(validator, XMLValidatorRequired):
                    self.__dict__['textRequired'].append(validator)
                else:
                    self.__dict__["textValidators"].append(validator)
                    if not self._validateValue(name, self.__dict__["text"]):
                        raise ValueError(
                            "Value " + self.__dict__["text"] + " (" +
                            type(self.__dict__["text"]).__name__ + ") is not valid for " +
                            name + " attribute of class " + self.__class__.__name__
                        )
        else:
            if name not in self.__dict__["order"]:
                raise NameError("This object does not have attribute with given value")
            if isinstance(validator, XMLValidator):
                # we separate required and value checkers because they are used in different places
                if isinstance(validator, XMLValidatorRequired):
                    if not self.__dict__["required"][name]:
                        self.__dict__["required"][name] = []
                    self.__dict__["required"][name].append(validator)
                else:
                    if not self.__dict__["validators"][name]:
                        self.__dict__["validators"][name] = []
                    self.__dict__["validators"][name].append(validator)

                    if not self._validateValue(name, self.__dict__["items"][name]):
                        raise ValueError(
                            "Value " + self.__dict__["items"][name] + " (" +
                            type(self.__dict__["items"][name]).__name__ + ") is not valid for " +
                            name + " attribute of class " + self.__class__.__name__
                        )
            else:
                raise TypeError(
                    "Validator for " + name + " attribute of " +
                    self.__class__.__name__ +
                    "class has to be instance or subclass of XMLValidator"
                )

    def _validateValue(self, name, value):
        """Validate class attribute with avaliable validators."""
        if name == "text":
            for validator in self.__dict__["textValidators"]:
                if not validator.validate(value):
                    return False
        else:
            if name not in self.__dict__["order"]:
                raise NameError("This object (of class " + self.__class__.__name__ +
                                ") does not have attribute with given value")

            for validator in self.__dict__['validators'][name]:
                if not validator.validate(value):
                    return False
        return True


class FiskXMLElement(XMLElement):
    """Base element for creating fiskla xml messages."""

    def __init__(self, childrenNames=None, text=None, data=None, name=None):
        super().__init__(
            childrenNames,
            "http://www.apis-it.hr/fin/2012/types/f73",
            text,
            data,
            name
        )
