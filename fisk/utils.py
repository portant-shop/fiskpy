from OpenSSL import crypto
from hashlib import md5
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def zastitni_kod(
    oib,
    datumVrijeme,
    brRacuna,
    ozPoslovnogP,
    ozUredaja,
    ukupnoIznos,
    key_filename,
    key_password
):
    """
    Generate Zastitni kod.

    it is defined as member as it is likely that you would need to call it to generate this
    code without need to create all elements for sending to server
    """
    forsigning = oib + datumVrijeme + brRacuna + ozPoslovnogP + ozUredaja + ukupnoIznos

    with open(key_filename, 'rb') as f:
        key = crypto.load_privatekey(
            crypto.FILETYPE_PEM,
            f.read(),
            key_password.encode('utf-8')
        )
    private_key = key.to_cryptography_key()
    signature = private_key.sign(
        forsigning.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    signature = md5(signature).hexdigest()
    return signature
