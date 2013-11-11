from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.schemes.abenc import abenc_waters09
from charm.core.math.pairing import hashPair

from Crypto.Cipher import AES
from Crypto import Random

import jsonrpclib
import xmlrpclib
import pprint
import io
import struct

# Taken from http://bit.ly/ToTsKP
BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0: - ord(s[-1])]

def connect(host):
    # Retrieve the server data
    api = jsonrpclib.Server(host)

    try:
        attributes = api.get_attributes()
        categories = api.get_categories()
    except xmlrpclib.ProtocolError:
        raise Exception("Unable to connect to remote server")

    # Validate response
    if not type(attributes) == list or not type(categories) == list:
        raise Exception("Remote server returned invalid data")

    # Done
    return attributes, categories

def setup(person, categories):
    # Setup scheme
    group = PairingGroup("SS512")
    scheme = abenc_waters09.CPabe09(group)

    # Generate a public key and master key for each category
    result = {}

    for key, name in categories.iteritems():
        # Generate keys
        mk, pk = scheme.setup()

        # Add to result
        result[key] = (pk, mk)

    # Done
    return result

def keygen(keypairs, parties):
    # Setup scheme
    group = PairingGroup("SS512")
    scheme = abenc_waters09.CPabe09(group)

    # For each party, generate a secret key for a specific category
    result = {}

    for category, parties in parties.iteritems():
        # Unpack public and master key
        pk, mk = keypairs[category]

        for party in parties:
            # Make sure dictionary exists in result
            if not party in result:
                result[party] = {}

            # Generate secret key for a party.
            attributes = party if isinstance(party, list) else [party]
            result[party][category] = scheme.keygen(pk, mk, attributes)

    # Done
    return result

def encrypt(plain, keypairs, category, parties):
    """
    Based on http://bit.ly/17PaPfK
    """

    # Setup scheme
    group = PairingGroup("SS512")
    scheme = abenc_waters09.CPabe09(group)

    # Unpack public key and generate policy
    pk, _ = keypairs[category]
    policy = " or ".join(parties)

    # Initialize AES
    aes_iv = Random.new().read(AES.block_size)
    aes_key_plain = group.random(GT)
    aes_key_cipher = scheme.encrypt(pk, aes_key_plain, policy)
    aes_key_bytes = objectToBytes(aes_key_cipher, group)
    aes_key_size = len(aes_key_bytes)

    aes = AES.new(hashPair(aes_key_plain)[0:32], AES.MODE_CFB, aes_iv)

    # Create result buffer
    result = io.BytesIO()

    # Write header to file
    result.write(bytes(aes_iv))
    result.write(struct.pack("<Q", aes_key_size))
    result.write(aes_key_bytes)
    # TODO CRC checksum -- allows server to reject 'random' data

    # Encrypt data
    result.write(aes.encrypt(pad(plain)))
    result.flush()

    # Done
    return result.getvalue()

def decrypt(cipher, keypairs, secret, category):
    """
    Based on http://bit.ly/17PaPfK
    """

    # Setup scheme
    group = PairingGroup("SS512")
    scheme = abenc_waters09.CPabe09(group)

    pk, _ = keypairs[category]
    sk = secret[category]

    # Create result buffer
    cipher = io.BytesIO(cipher)

    # Initialize AES
    aes_iv = cipher.read(AES.block_size)
    aes_key_size = struct.unpack("<Q", cipher.read(struct.calcsize("Q")))[0]
    aes_key_bytes = cipher.read(aes_key_size)
    aes_key_cipher = bytesToObject(aes_key_bytes, group)
    aes_key_plain = scheme.decrypt(pk, sk, aes_key_cipher)

    aes = AES.new(hashPair(aes_key_plain)[0:32], AES.MODE_CFB, aes_iv)

    # Decrypt data
    return unpad(aes.decrypt(cipher.read()))

def test():
    person = "Bas Stottelaar"
    categories = {
        1: "PERSONAL",
        2: "HEALTH",
        3: "TRAINING"
    }
    parties = {
        1: ["DOCTOR", "INSURANCE", "EMPLOYER"],
        2: ["HOSPITAL"],
        3: ["HEALTH_CLUB"]
    }
    plain = "Hi, this is a sample encrypted text!!!!"

    keypairs = setup(person, categories)
    #pprint.pprint(keypairs)
    secrets = keygen(keypairs, parties)

    cipher = encrypt(plain, keypairs, 1, ["DOCTOR", "INSURANCE"])
    new_plain = decrypt(cipher, keypairs, secrets["EMPLOYER"], 1)

    assert plain == new_plain

if __name__ == "__main__":
    test()

