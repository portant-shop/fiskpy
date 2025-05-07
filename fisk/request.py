from datetime import datetime
from fisk import FiskInit, FiskSOAPMessage
from fisk.client import FiskSOAPClientDemo
from fisk.elements import PoslovniProstor, Racun, Zaglavlje
from fisk.signer import Signer
from fisk.validator import XMLValidatorLen, XMLValidatorRequired, XMLValidatorType
from fisk.verifier import Verifier
from fisk.xml import FiskXMLElement
from lxml import etree as et


class FiskXMLRequest(FiskXMLElement):
    """
    Base element for creating fiskal SOAP mesage.

    it knows how to send request to srever using send
    """

    def __init__(self, childrenNames=None, text=None, data=None, name=None):
        super().__init__(childrenNames, text, data)
        self.__dict__['lastRequest'] = None
        self.__dict__['lastResponse'] = None
        self.__dict__['idPoruke'] = None
        self.__dict__['dateTime'] = None
        self.__dict__['lastError'] = None

    def getSOAPMessage(self):
        """Add SOAP elements to xml message."""
        message = FiskSOAPMessage(self)
        return message.getSOAPMessage()

    def send(self):
        """Send SOAP request to server."""
        cl = None
        verifier = None
        signer = None
        signxmlNS = "{http://www.w3.org/2000/09/xmldsig#}"
        apisNS = "{http://www.apis-it.hr/fin/2012/types/f73}"

        if FiskInit.isset:
            cl = FiskInit.environment
            signer = FiskInit.signer
            verifier = FiskInit.verifier
        else:
            cl = FiskSOAPClientDemo()

        self.__dict__['lastRequest'] = self.getSOAPMessage()
        # rememer generated IdPoruke nedded for return message check
        self.__dict__['idPoruke'] = None
        self.__dict__['dateTime'] = None
        try:
            self.__dict__['idPoruke'] = self.Zaglavlje.IdPoruke
            self.__dict__['dateTime'] = datetime.strptime(
                self.Zaglavlje.DatumVrijeme, '%d.%m.%YT%H:%M:%S')
        except NameError:
            pass

        message = et.tostring(self.__dict__['lastRequest'])

        if signer is not None and isinstance(signer, Signer):
            message = signer.signXML(self.__dict__['lastRequest'], self.getElementName())

        reply = cl.send(message)
        print('reply is', et.tostring(reply))
        has_signature = False
        verified_reply = None
        if reply.find(".//" + signxmlNS + "Signature") is not None:
            has_signature = True
        if (has_signature is True):
            if (verifier is not None and isinstance(verifier, Verifier)):
                verified_reply = verifier.verifiyXML(reply)
        else:
            verified_reply = reply

        if self.__dict__['idPoruke'] is not None and verified_reply is not None:
            retIdPoruke = None
            idPorukeE = verified_reply.find(".//" + apisNS + "IdPoruke")
            if idPorukeE is not None:
                retIdPoruke = idPorukeE.text
            if self.__dict__['idPoruke'] != retIdPoruke:
                verified_reply = None
        self.__dict__['lastResponse'] = verified_reply
        return verified_reply

    def get_last_request(self):
        """Return last SOAP message sent to server as ElementTree object."""
        return self.__dict__['lastRequest']

    def get_last_response(self):
        """Return last SOAP message received from server as ElementTree object."""
        return self.__dict__['lastResponse']

    def get_last_error(self):
        """Return last error which was recieved from PU serever."""
        return self.__dict__['lastError']

    def execute(self):
        """
        Return reply from server or False.

        If false you can check what was error with get_last_error method

        In this class this method does nothing as this is base class for other requests
        """
        self.__dict__['lastError'] = list()
        self.__dict__['lastError'].append(
            "Class " + self.__class__.__name__ + "did not implement execute method")
        return False

    def get_id_msg(self):
        """Return last message id if available (Echo request does not have it)."""
        return self.__dict__['idPoruke']

    def get_datetime_msg(self):
        """Return last message datetime if available (Echo request does not have it)."""
        return self.__dict__['dateTime']


class EchoRequest(FiskXMLRequest):
    """
    EchoRequest fiskal element.

    This element is capable to send Echo SOAP message to server
    """

    def __init__(self, text=None):
        """
        Init.

        creates Echo Request with message defined in text. Althought there is no string limit
        defined in specification I have put that text should be between 1-1000 chars
        """
        super().__init__(
            text=text,
            childrenNames=(
                ("text", [XMLValidatorLen(1, 1000), XMLValidatorRequired()]),
            )
        )

    def execute(self):
        """
        Send echo request to server and returns echo reply.

        If error occures returns False. You can get last error with get_last_error method
        """
        self.__dict__['lastError'] = list()
        reply = False

        self.send()
        if isinstance(self.__dict__['lastResponse'], et._Element):
            for relement in self.__dict__['lastResponse'].iter(
                    self.__dict__['namespace'] + "EchoResponse"):
                reply = relement.text

            if reply is False:
                for relement in self.__dict__['lastResponse'].iter(
                        self.__dict__['namespace'] + "PorukaGreske"):
                    self.__dict__['lastError'].append(relement.text)

        return reply


class PoslovniProstorZahtjev(FiskXMLRequest):
    """
    PoslovniProstorZahtjev element.

    This class is capable to sent is self as SOAP message to
    server and veifiey server seply.
    """

    def __init__(self, poslovniProstor):
        super().__init__(
            childrenNames=(
                ("Zaglavlje", [XMLValidatorType(Zaglavlje)]),
                ("PoslovniProstor", [XMLValidatorType(PoslovniProstor), XMLValidatorRequired()])
            ),
            data={"PoslovniProstor": poslovniProstor}
        )
        self.Zaglavlje = Zaglavlje()
        self.setAttr({"Id": "ppz"})
        self.addValidator("Zaglavlje", XMLValidatorRequired())

    def execute(self):
        """
        Send PoslovniProstorZahtjev request to server and returns True if success.

        If error occures returns False. In that case you can check error with get_last_error
        """
        self.__dict__['lastError'] = list()
        reply = False

        self.send()

        if isinstance(self.__dict__['lastResponse'], et._Element):
            for element in self.__dict__['lastResponse'].iter(
                    self.__dict__['namespace'] + "PorukaGreske"):
                self.__dict__['lastError'].append(element.text)
            if len(self.__dict__['lastError']) == 0:
                reply = True

        return reply


class RacunZahtjev(FiskXMLRequest):
    """RacunZahtijev element - has everything needed to send RacunZahtijev to server."""

    def __init__(self, racun):
        super().__init__(
            childrenNames=(
                ("Zaglavlje", [XMLValidatorType(Zaglavlje)]),
                ("Racun", [XMLValidatorType(Racun), XMLValidatorRequired()])
            ),
            data={"Racun": racun}
        )
        self.Zaglavlje = Zaglavlje()
        self.setAttr({"Id": "rac"})
        self.addValidator("Zaglavlje", XMLValidatorRequired())

    def execute(self):
        """
        Send RacunRequest to server.

        If seccessful returns JIR else False
        If returns False you can get errors with get_last_error method
        """
        self.__dict__['lastError'] = list()
        reply = False

        self.send()

        if isinstance(self.__dict__['lastResponse'], et._Element):
            for element in self.__dict__['lastResponse'].iter(self.__dict__['namespace'] + "Jir"):
                reply = element.text

            if reply is False:
                for element in self.__dict__['lastResponse'].iter(
                        self.__dict__['namespace'] + "PorukaGreske"):
                    self.__dict__['lastError'].append(element.text)

        return reply


class ProvjeraZahtjev(FiskXMLRequest):
    """ProvjeraZahtjev element."""

    def __init__(self, racun):
        super().__init__(
            childrenNames=(
                ("Zaglavlje", [XMLValidatorType(Zaglavlje)]),
                ("Racun", [XMLValidatorType(Racun), XMLValidatorRequired()])
            ),
            data={"Racun": racun}
        )
        self.Zaglavlje = Zaglavlje()
        self.setAttr({"Id": "rac"})
        self.addValidator("Zaglavlje", XMLValidatorRequired())

    def execute(self):
        """
        Send ProvjeraZahtjec request to server.

        If returns False if request Racun data is not same as response Racun data,
        otherwise it returns Greske element from respnse so you can check them if they exist.
        """
        self.__dict__['lastError'] = list()
        reply = False

        self.send()

        if isinstance(self.__dict__['lastResponse'], et._Element):
            for element in self.__dict__['lastResponse'].iter(self.__dict__['namespace'] + "Racun"):
                if et.tostring(element) == et.tostring(self.Racun.generate()):
                    reply = True

            if reply is False:
                for element in self.__dict__['lastResponse'].iter(
                        self.__dict__['namespace'] + "Greske"):
                    reply = element

        return reply
