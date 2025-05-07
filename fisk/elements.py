from datetime import datetime
from uuid import uuid4
from fisk import FiskInit, FiskInitError
from fisk.utils import zastitni_kod
from fisk.validator import (
    XMLValidatorEnum, XMLValidatorLen, XMLValidatorListType, XMLValidatorRegEx,
    XMLValidatorRequired, XMLValidatorType
)
from fisk.xml import FiskXMLElement


class Zaglavlje(FiskXMLElement):
    """
    Zaglavlje fiskal element.

    it automaticly generates Idporuke and DateTime

    IdPoruke is regenerated on message creation so you should check this value after element
    generation not before

    Ususaly you will not use this element as it is used internaly by this library
    """

    def __init__(self):
        super().__init__(
            childrenNames=(
                (
                    "IdPoruke",
                    [XMLValidatorRegEx(
                        "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
                    )]
                ),
                (
                    "DatumVrijeme", [XMLValidatorRegEx(
                        "^[0-9]{2}.[0-9]{2}.[1-2][0-9]{3}T[0-9]{2}:[0-9]{2}:[0-9]{2}$"
                    )]
                )
            )
        )
        self.IdPoruke = str(uuid4())
        self.DatumVrijeme = datetime.now().strftime('%d.%m.%YT%H:%M:%S')
        self.addValidator("IdPoruke", XMLValidatorRequired())
        self.addValidator("DatumVrijeme", XMLValidatorRequired())

    def generate(self):  # overide because need new ID and time for every message we sent to porezna
        self.IdPoruke = str(uuid4())
        self.DatumVrijeme = datetime.now().strftime('%d.%m.%YT%H:%M:%S')
        return FiskXMLElement.generate(self)


class Adresa(FiskXMLElement):
    """Adresa fiskal element."""

    def __init__(self, data=None):
        string35Val = XMLValidatorLen(1, 35)
        super().__init__(
            childrenNames=(
                ("Ulica", [XMLValidatorLen(1, 100)]),
                ("KucniBroj", [XMLValidatorRegEx("^\\d{1,4}$")]),
                ("KucniBrojDodatak", [XMLValidatorLen(1, 4)]),
                ("BrojPoste", [XMLValidatorRegEx("^\\d{1,12}$")]),
                ("Naselje", [string35Val]),
                ("Opcina", [string35Val])
            ),
            data=data
        )


class AdresniPodatak(FiskXMLElement):
    """
    AdresniPodatak fiskal element.

    can hold Addres type element or OstaliTipoviPP. this is determend in constructor
    and it is not ment to be changed later
    """

    def __init__(self, adresa):
        super().__init__()
        if isinstance(adresa, Adresa):
            self.setAvailableChildren(["Adresa"])
            self.addValidator("Adresa", XMLValidatorType(Adresa))
            self.Adresa = adresa
        else:
            self.setAvailableChildren(["OstaliTipoviPP"])
            self.addValidator("OstaliTipoviPP", XMLValidatorLen(1, 100))
            self.OstaliTipoviPP = adresa


class PoslovniProstor(FiskXMLElement):
    """PoslovniProstor element."""

    def __init__(self, data=None):
        string1000Val = XMLValidatorLen(1, 1000)
        super().__init__(
            childrenNames=(
                ("Oib", [XMLValidatorRegEx("^\\d{11}$"), XMLValidatorRequired()]),
                (
                    "OznPoslProstora",
                    [XMLValidatorRegEx("^[0-9a-zA-Z]{1,20}$"), XMLValidatorRequired()]
                ),
                ("AdresniPodatak", [XMLValidatorType(AdresniPodatak), XMLValidatorRequired()]),
                ("RadnoVrijeme", [string1000Val, XMLValidatorRequired()]),
                (
                    "DatumPocetkaPrimjene",
                    [
                        XMLValidatorRegEx("^[0-9]{2}.[0-9]{2}.[1-2][0-9]{3}$"),
                        XMLValidatorRequired()
                    ]
                ),
                ("OznakaZatvaranja", [XMLValidatorEnum(["Z"])]),
                ("SpecNamj", [string1000Val])
            ),
            data=data
        )


class BrRac(FiskXMLElement):
    """BrojRacuna element."""

    def __init__(self, data=None):
        regexVal = XMLValidatorRegEx("^\\d{1,20}$")
        FiskXMLElement.__init__(
            self,
            childrenNames=(
                ("BrOznRac", [regexVal, XMLValidatorRequired()]),
                ("OznPosPr", [XMLValidatorRegEx("^[0-9a-zA-Z]{1,20}$"), XMLValidatorRequired()]),
                ("OznNapUr", [regexVal, XMLValidatorRequired()])
            ),
            data=data
        )


class Porez(FiskXMLElement):
    """Porez element."""

    def __init__(self, data=None):
        regexVal = XMLValidatorRegEx("^([+-]?)[0-9]{1,15}\\.[0-9]{2}$")
        super().__init__(
            childrenNames=(
                (
                    "Stopa",
                    [XMLValidatorRegEx("^([+-]?)[0-9]{1,3}\\.[0-9]{2}$"), XMLValidatorRequired()]
                ),
                ("Osnovica", [regexVal, XMLValidatorRequired()]),
                ("Iznos", [regexVal, XMLValidatorRequired()])
            ),
            data=data
        )


class OstPorez(FiskXMLElement):
    """Porez element which is cuhiled od OstaliPor elemt."""

    def __init__(self, data=None):
        regexVal = XMLValidatorRegEx("^([+-]?)[0-9]{1,15}\\.[0-9]{2}$")
        super().__init__(
            childrenNames=(
                ("Naziv", [XMLValidatorLen(1, 100), XMLValidatorRequired()]),
                (
                    "Stopa",
                    [XMLValidatorRegEx("^([+-]?)[0-9]{1,3}\\.[0-9]{2}$"), XMLValidatorRequired()]
                ),
                ("Osnovica", [regexVal, XMLValidatorRequired()]),
                ("Iznos", [regexVal, XMLValidatorRequired()])
            ),
            data=data,
            name="Porez"
        )


class Naknada(FiskXMLElement):
    """Naknada element."""

    def __init__(self, data=None):
        super().__init__(
            childrenNames=(
                ("NazivN", [XMLValidatorLen(1, 100), XMLValidatorRequired()]),
                (
                    "IznosN",
                    [XMLValidatorRegEx("^([+-]?)[0-9]{1,15}\\.[0-9]{2}$"), XMLValidatorRequired()]
                )
            ),
            data=data
        )


class Racun(FiskXMLElement):
    """
    Racun element.

    it is not possible to set ZastKod as this class calculate it each time
        you change one of varibales from it is calcualted
    """

    def __init__(self, data, key_file=None, key_password=None):
        """
        Initialize.

        data - dict - initial data
        key_file - string - ful path of filename which holds private key needed for
            creation of ZastKod
        key_password - key password
        """
        if (key_file is None and key_password is None):
            if (not FiskInit.isset):
                raise FiskInitError(
                    "Needed members not set or fiskpy was not initalized (see FiskInit)")
            else:
                key_file = FiskInit.key_file
                key_password = FiskInit.password

        porezListVal = XMLValidatorListType(Porez)
        iznosVal = XMLValidatorRegEx("^([+-]?)[0-9]{1,15}\\.[0-9]{2}$")
        oibVal = XMLValidatorRegEx("^\\d{11}$")
        boolVal = XMLValidatorEnum(["true", "false"])
        super().__init__(
            childrenNames=(
                ("Oib", [oibVal, XMLValidatorRequired()]),
                ("USustPdv", [boolVal, XMLValidatorRequired()]),
                ("DatVrijeme", [
                    XMLValidatorRegEx(
                        "^[0-9]{2}.[0-9]{2}.[1-2][0-9]{3}T[0-9]{2}:[0-9]{2}:[0-9]{2}$"),
                    XMLValidatorRequired()
                ]),
                ("OznSlijed", [XMLValidatorEnum(["P", "N"]), XMLValidatorRequired()]),
                ("BrRac", [XMLValidatorType(BrRac), XMLValidatorRequired()]),
                ("Pdv", [porezListVal]),
                ("Pnp", [porezListVal]),
                ("OstaliPor", [XMLValidatorListType(OstPorez)]),
                ("IznosOslobPdv", [iznosVal]),
                ("IznosMarza", [iznosVal]),
                ("IznosNePodlOpor", [iznosVal]),
                ("Naknade", [XMLValidatorListType(Naknada)]),
                ("IznosUkupno", [iznosVal, XMLValidatorRequired()]),
                ("NacinPlac", [
                    XMLValidatorEnum(["G", "K", "C", "T", "O"]), XMLValidatorRequired()
                ]),
                ("OibOper", [oibVal, XMLValidatorRequired()]),
                ("ZastKod", [XMLValidatorRegEx("^[a-f0-9]{32}$")]),
                ("NakDost", [boolVal, XMLValidatorRequired()]),
                ("ParagonBrRac", [XMLValidatorLen(1, 100)]),
                ("SpecNamj", [XMLValidatorLen(1, 1000)])
            ),
            data=data
        )
        self.__dict__["key"] = key_file
        self.__dict__["key_pass"] = key_password
        self.__dict__["items"]["ZastKod"] = zastitni_kod(
            self.Oib,
            self.DatVrijeme,
            self.BrRac.BrOznRac,
            self.BrRac.OznPosPr,
            self.BrRac.OznNapUr,
            self.IznosUkupno,
            self.__dict__["key"],
            self.__dict__["key_pass"]
        )

    def __setattr__(self, name, value):
        """
        Overiden so that it is not possible to set ZastKod and to update.

        ZastKod is some of variables which are used to generate Zastkode are changed

        wanted to raise exception if someone want to set ZastKod but it is not possible
        because of constructor
        """
        if name != "ZastKod":
            FiskXMLElement.__setattr__(self, name, value)
            if name in ["Oib", "DatVrijeme", "BrRac", "IznosUkupno"]:
                if (
                    self.Oib is not None and
                    self.DatVrijeme is not None and
                    self.BrRac is not None and
                    self.IznosUkupno is not None and ("key" in self.__dict__)
                ):
                    self.__dict__["items"]["ZastKod"] = zastitni_kod(
                        self.Oib,
                        self.DatVrijeme,
                        self.BrRac.BrOznRac,
                        self.BrRac.OznPosPr,
                        self.BrRac.OznNapUr,
                        self.IznosUkupno,
                        self.__dict__["key"],
                        self.__dict__["key_pass"]
                    )
