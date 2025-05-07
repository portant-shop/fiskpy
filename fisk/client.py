from lxml import etree as et
import requests
import os


class FiskSOAPClientError(Exception):
    """Exception used in FiskSOAPClient (and derived classes) class as indicator of some error."""

    def __init__(self, message):
        Exception.__init__(self, message)


class FiskSOAPClient(object):
    """Very very simple SOAP Client implementation."""

    def __init__(self, host, port, url, verify=None):
        """
        Construct client with service arguments (host, port, url, verify).

        verifiy - path to pem file with CA certificates for response verification
        """
        self.host = host
        self.port = port
        self.url = url
        self.verify = verify

    def send(self, message, raw=False):
        """
        Send message (as xml string) to server.

        returns ElementTree object with server response message

        if raw is True then returns raw xml
        """
        xml = message

        r = requests.post(r"https://" + self.host + r":" + self.port + self.url, headers={
            "Host": self.host,
            "Content-Type": "text/xml; charset=UTF-8",
            # "Content-Length": len(xml),
            "SOAPAction": self.url
        }, data=xml, verify=self.verify)

        response = None
        if r.status_code == requests.codes.ok:
            response = r.text
        else:
            if (r.headers['Content-Type'] == "text/xml"):
                response = r.text
            else:
                raise FiskSOAPClientError(str(r.status_code) + ": " + r.reason)
        responseXML = et.fromstring(response.encode('utf-8'))
        for relement in responseXML.iter():
            if relement.tag.find("faultstring") != -1:
                raise FiskSOAPClientError(relement.text)
        if not raw:
            response = responseXML
        return response


class FiskSOAPClientDemo(FiskSOAPClient):
    """Same class as FiskSOAPClient but with demo PU server parameters set by default."""

    def __init__(self):
        mpath = os.path.dirname(__file__)
        cafile = mpath + "/CAcerts/demoCAfile.pem"
        super().__init__(
            host=r"cistest.apis-it.hr",
            port=r"8449",
            url=r"/FiskalizacijaServiceTest",
            verify=cafile
        )


class FiskSOAPClientProduction(FiskSOAPClient):
    """Same class as FiskSOAPClient but with procudtion PU server parameters set by default."""

    def __init__(self):
        mpath = os.path.dirname(__file__)
        cafile = mpath + "/CAcerts/prodCAfile.pem"
        super().__init__(
            host=r"cis.porezna-uprava.hr",
            port=r"8449",
            url=r"/FiskalizacijaService",
            verify=cafile
        )
