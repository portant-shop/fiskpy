from signxml import XMLVerifier
import os


class Verifier(object):
    """
    A class used for verification of reply messages.

    is uses signxml module
    """

    def __init__(self, production=False):
        """
        Initialize.

        Args:
            production (boolean): if False demo fiscalization environment will be used (default),
                if True production fiscalization environment will be used

        The locations of files holding CA cerificates are hardcoded so if you need to add some
        certificate please add it to those files.
        """
        mpath = os.path.dirname(__file__) + '/CAcerts'
        self.CAs = mpath + "/demoCAfile2020.pem"
        prodCAfile = mpath + "/prodCAfile.pem"
        if production:
            self.CAs = prodCAfile

    def verifiyXML(self, xml):
        """
        Verify an xml document.

        Returns (ElementTree): verified xml if it can verify signature of message, or
            None if not
        """
        root = xml
        rvalue = None

        rvalue = WeakXMLVerifier().verify(root, ca_pem_file=self.CAs, validate_schema=False)
        if rvalue.signed_xml is not None:
            rvalue = rvalue.signed_xml
        else:
            rvalue = None
        return rvalue


class WeakXMLVerifier(XMLVerifier):
    def check_signature_alg_expected(self, signature):
        # Override the method to skip the check
        pass
