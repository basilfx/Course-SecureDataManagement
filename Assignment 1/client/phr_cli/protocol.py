from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.schemes.abenc import abenc_waters09
from charm.core.math.pairing import hashPair

from Crypto.Cipher import AES
from Crypto import Random

from phr_cli.utils import pad_message, unpad_message

import jsonrpclib
import io
import struct

class ProtocolException(Exception):
    pass

class ProtocolKeyException(ProtocolException):
    pass

class ProtocolDecryptException(ProtocolException):
    pass

class Protocol(object):
    """
    Encrypt and decrypt functions are based on http://bit.ly/17PaPfK.
    """

    def __init__(self):
        # Setup scheme
        self.group = PairingGroup("SS512")
        self.scheme = abenc_waters09.CPabe09(self.group)

    def connect(self, host):
        # Retrieve the server data
        api = jsonrpclib.Server(host)

        try:
            attributes = api.get_attributes()
            categories = api.get_categories()
        except jsonrpclib.ProtocolError:
            raise ProtocolException("Unable to connect to remote server")

        # Validate response
        if not type(attributes) == list or not type(categories) == list:
            raise ProtocolException("Remote server returned invalid data")

        # Done
        return attributes, categories

    def setup(self, person, categories):
        # Generate a public key and master key for each category
        result = {}

        for key, name in categories.iteritems():
            # Generate keys
            mk, pk = self.scheme.setup()

            # Add to result
            result[key] = (pk, mk)

        # Done
        return result

    def keygen(self, keypairs, parties):
        # For each party, generate a secret key for a specific category
        result = {}

        for category, parties in parties.iteritems():
            # Unpack keys
            try:
                pk, mk = keypairs[category]
            except LookupError:
                raise ProtocolKeyException("No public key and master key available for category %s" % category)

            # Generate secret keys
            for party in parties:
                # Make sure dictionary exists in result
                if not party in result:
                    result[party] = {}

                # A party may specify multiple attributes
                if isinstance(party, list):
                    attributes = party
                else:
                    attributes = [party]

                # Generate keys for a party.
                result[party][category] = (pk, self.scheme.keygen(pk, mk, attributes))

        # Done
        return result

    def encrypt(self, plain, keypairs, category, parties):
        # Unpack keys
        try:
            pk, _ = keypairs[category]
        except LookupError:
            raise ProtocolKeyException("No public key available for category %s" % category)

        # Policy is a OR concatination of parties
        policy = " or ".join(parties)

        # Create result buffer
        result = io.BytesIO()

        # Initialize AES
        aes_iv = Random.new().read(AES.block_size)
        aes_key_plain = self.group.random(GT)
        aes_key_cipher = self.scheme.encrypt(pk, aes_key_plain, policy)
        aes_key_bytes = objectToBytes(aes_key_cipher, self.group)
        aes_key_size = len(aes_key_bytes)

        aes = AES.new(hashPair(aes_key_plain)[0:32], AES.MODE_CFB, aes_iv)

        # Write header
        result.write(bytes(aes_iv))
        result.write(struct.pack("<Q", aes_key_size))
        result.write(aes_key_bytes)

        # Encrypt data
        plain_padded = pad_message(plain, AES.block_size)
        result.write(aes.encrypt(plain_padded))

        # Done
        return result.getvalue()

    def decrypt(self, cipher, keypairs, category):
        # Unpack keys
        try:
            pk, sk = keypairs[category]
        except LookupError:
            raise ProtocolKeyException("No public key and secret key available for category %s" % category)

        # Create result buffer
        cipher = io.BytesIO(cipher)

        # Initialize AES
        aes_iv = cipher.read(AES.block_size)
        aes_key_size = struct.unpack("<Q", cipher.read(struct.calcsize("Q")))[0]
        aes_key_bytes = cipher.read(aes_key_size)
        aes_key_cipher = bytesToObject(aes_key_bytes, self.group)

        try:
            aes_key_plain = self.scheme.decrypt(pk, sk, aes_key_cipher)
        except Exception, e:
            # There is a bug in Charm which requires a fix in the scheme to not
            # crash during execution. See for the idea: http://bit.ly/1e19H7A
            if e.args[0] == "Insufficient attributes":
                raise ProtocolDecryptException("Missing attributes for decryption")
            else:
                raise e

        aes = AES.new(hashPair(aes_key_plain)[0:32], AES.MODE_CFB, aes_iv)

        # Decrypt data
        plain_padded = aes.decrypt(cipher.read())

        # Done
        return unpad_message(plain_padded)