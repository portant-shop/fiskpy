from fisk.client import FiskSOAPClientDemo, FiskSOAPClientProduction
from fisk.signer import Signer
from fisk.verifier import Verifier
from lxml import etree as et


class FiskInitError(Exception):
    """Use as an exception in FiskInit class as indicator of some error."""

    def __init__(self, message):
        Exception.__init__(self, message)


class FiskInit():
    """
    Serve as fisk.py initalizator.

    Mainly it should contain all info about environment and credentials
    """

    key_file = None
    password = None
    environment = None
    isset = False
    signer = None
    verifier = None

    @staticmethod
    def init(
        key_file, password, cert_file, production=False, demo_skip_signature_verification=False
    ):
        """
        Set default fiscalization environment DEMO or PRODUCTION.

        Args:
            key_file (str): path to fiscalization user key file in pem format
            password (str): password for key
            cert_file (str): path to fiscalization user certificate in pem fromat
            production (boolean): True if you need fiscalization production environment,
                for demo False. Default is False
            demo_skip_signature_verification (boolean): True if you want to skip signature in demo
        """
        FiskInit.key_file = key_file
        FiskInit.password = password
        if not production and demo_skip_signature_verification:
            FiskInit.verifier = None
        elif demo_skip_signature_verification:
            FiskInit.verifier = Verifier(production)
        FiskInit.environment = FiskSOAPClientDemo()
        if (production):
            FiskInit.environment = FiskSOAPClientProduction()
        FiskInit.signer = Signer(key_file, password, cert_file)
        FiskInit.isset = True

    @staticmethod
    def deinit():
        FiskInit.key_file = None
        FiskInit.password = None
        FiskInit.environment = None
        FiskInit.signer = None
        FiskInit.verifier = None
        FiskInit.isset = False


class FiskSOAPMessage():
    """
    SOAP Envelope element.

    Sets SOAP elements around content.
    """

    def __init__(self, content=None):
        """
        Initialize.

        Args:
            content (ElementTree): content what will be put in SOAPMessage
        """
        namespace = "{http://schemas.xmlsoap.org/soap/envelope/}"
        self.message = et.Element(namespace + "Envelope")
        self.body = et.SubElement(self.message, namespace + "Body")
        if content is not None:
            self.body.append(content.generate())

    def setBodyContent(self, content):
        """
        Set new SOAP message body content.

        Args:
            content (ElementTree): content what will be put in SOAPMessage
        """
        self.body.clear()
        self.body.append(content.generate())

    def getSOAPMessage(self):
        """Return (ElementTree): reprezentation of SOAPMEssage."""
        return self.message
