from lxml import etree as et
from signxml import XMLSigner, SignatureMethod, DigestAlgorithm


class FiskXMLEleSignerError(Exception):
    """Exception used in FiskXMLsec class as indicator of some error."""

    def __init__(self, message):
        super().__init__(message)


class Signer:
    """
    A class which implements signing of fiskal SOAP messages.

    It uses signxml library for that purpose.
    """

    def __init__(self, key, password, cert):
        """
        Initialize.

        Args:
        key (str): path to file holding your key. This file should be in pem format
        passwrod (str): password for key file
        cert (str): path to certificate file. This file should be in pem format
        trustcerts (str): path to file vhere are CA certificates in.pem format
        """
        self.init_error = []
        self.key = open(key).read()
        self.password = password
        self.certificate = open(cert).read()

    def signXML(self, fiskXML, elementToSign):
        """
        Sign xml template acording to XML Signature Syntax and Processing.

        returns signed xml

        fiskXMLTemplate - Element (from ElementTree) xml template to sign
        elementToSign - string - name tag of element to sign inside xml template
        """
        if self.init_error:
            raise FiskXMLEleSignerError(self.init_error)

        root = fiskXML
        # print(et.tostring(root))
        RequestElement = None

        for child in root.iter(elementToSign):
            if child.tag == elementToSign:
                RequestElement = child
                break

        if RequestElement is None:
            raise FiskXMLEleSignerError("Coudl not find element to sign")

        # dodavanje Signature taga
        namespace = "{http://www.w3.org/2000/09/xmldsig#}"
        et.SubElement(RequestElement, namespace + "Signature", {'Id': 'placeholder'})

        signed_root = XMLSigner(
            signature_algorithm=SignatureMethod.RSA_SHA256,
            digest_algorithm=DigestAlgorithm.SHA256,
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        ).sign(
            root,
            key=self.key,
            passphrase=self.password.encode('utf-8'),
            cert=self.certificate,
            reference_uri="#" + RequestElement.get("Id")
        )

        return et.tostring(signed_root)
