from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.schemes.abenc import abenc_waters09
from charm.core.math.pairing import hashPair

from Crypto.Cipher import AES
from Crypto import Random

from phr_cli.utils import pad_message, unpad_message

import jsonrpclib
import base64
import struct
import zlib
import io

class Protocol(object):
    """
    Wrapper for CP-ABE scheme with support for multiple categories, parties and
    encryption/decryption of unspecified data.

    Encrypt and decrypt use symmetric encryption for the data while the key is
    encrypted with CP-ABE. This is based on http://bit.ly/17PaPfK.
    """

    def __init__(self, categories, parties, mappings):
        """
        Setup a new protocol instance, providing the protocol parameters.

        @param categories List of supported categories
        @param parties List of involved parties
        @param mappings Dictionary of a category to allowed parties
        """

        # Setup scheme
        self.group = PairingGroup("SS512")
        self.scheme = abenc_waters09.CPabe09(self.group)

        # Protocol parameters
        self.parties = parties
        self.categories = categories
        self.mappings = self.clean_mappings(mappings)

    def setup(self):
        """
        For each category, generate a public key and a master key

        @return Tuple of master keys and public keys. Each set of keys is a
            dictionary per category.
        """

        # Generate a public key and master key for each category
        master_keys = {}
        public_keys = {}

        for category in self.categories:
            # Generate keys
            mk, pk = self.scheme.setup()

            # Add to result
            master_keys[category] = mk
            public_keys[category] = pk

        # Done
        return master_keys, public_keys

    def keygen(self, master_keys, public_keys):
        """
        Generate secret keys for the system mappings, given the public keys and
        master keys per category.

        @param master_keys Dictionary of master keys per category
        @param public_keys Dictionary of public keys per category
        @return Dictionary of secret keys per party and category

        @throws KeyRingError if no keys are available for a requested category.
        """

        # Validate parameters
        master_keys = self.clean_keys(master_keys)
        public_keys = self.clean_keys(public_keys)

        # For each party, generate a secret key for a specific category
        result = {}

        for category, parties in self.mappings.iteritems():
            # Unpack keys
            try:
                mk = master_keys[category]
                pk = public_keys[category]
            except LookupError:
                raise KeyRingError("No public key and master key available for category %s" % category)

            # Generate secret keys
            for party in parties:
                # Generate keys for a party.
                sk = self.scheme.keygen(pk, mk, party)

                # Add key to each party for category
                for item in party:
                    if not item in result:
                        result[item] = {}

                    result[item][category] = sk

        # Done
        return result

    def encrypt(self, plain, public_keys, category, parties):
        """
        Encrypt a given plain message of a specific category for given parties.
        The message itself will be encryped with AES, but the session key will
        be encrypted with CP-ABE. The category will be encoded in the cipher.

        @param plain Message to encrypt. Can be text or binary data.
        @param public_keys Dictionary of public keys per category.
        @param category Category of message
        @param parties List of parties allowed to decrypt this message.
        @return Encrypted message with header

        @throws KeyRingError if no public key is available for category
        """

        # Validate parameters
        public_keys = self.clean_keys(public_keys)
        category = self.clean_category(category)
        parties = self.clean_parties(parties)

        # Unpack key
        try:
            pk = public_keys[category]
        except LookupError:
            raise KeyRingError("No public key available for category %s" % category)

        # Create result buffer
        result = io.BytesIO()

        # Initialize AES
        aes_iv = Random.new().read(AES.block_size)
        aes_key_plain = self.group.random(GT)
        aes_key_cipher = self.scheme.encrypt(pk, aes_key_plain, parties)
        aes_key_cipher["category"] = category
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
        return base64.b64encode(result.getvalue())

    def decrypt(self, cipher, secret_keys):
        """
        Decrypt a given cipher message including header. Message category will
        be deduced from cipher.

        @param cipher Message to decrypt
        @param secret_keys Dictionary of secret keys per category
        @return Decrypted message

        @throws DecryptError if data is invalid or if attributes are missing in
            keypairs
        @throws KeyRingError if no public key is available for cipher's category
        """

        # Validate parameters
        secret_keys = self.clean_keys(secret_keys)

        # Create result buffer
        cipher = io.BytesIO(base64.b64decode(cipher))

        # Initialize AES
        try:
            aes_iv = cipher.read(AES.block_size)
            aes_key_size = struct.unpack("<Q", cipher.read(struct.calcsize("Q")))[0]
            aes_key_bytes = cipher.read(aes_key_size)
            aes_key_cipher = bytesToObject(aes_key_bytes, self.group)
        except (TypeError, struct.error, zlib.error) as e:
            raise DecryptError("Decoding cipher failed")

        # Unpack category from cipher
        category = self.clean_category(aes_key_cipher["category"])

        # Unpack key
        try:
            sk = secret_keys[category]
        except LookupError:
            raise KeyRingError("No public key and secret key available for category %s" % category)

        # Decrypt the AES key
        try:
            # For some reason, the decrypt method wants a public key. We don't
            # supply it since it isn't required.
            aes_key_plain = self.scheme.decrypt(None, sk, aes_key_cipher)
        except Exception, e:
            # There is a bug in Charm which requires a fix in the scheme to not
            # crash during execution. See for the idea: http://bit.ly/1e19H7A
            if e.args[0] == "Insufficient attributes":
                raise DecryptError("Missing attributes for decryption")
            else:
                raise e

        aes = AES.new(hashPair(aes_key_plain)[0:32], AES.MODE_CFB, aes_iv)

        # Decrypt data
        plain_padded = aes.decrypt(cipher.read())

        # Done
        return unpad_message(plain_padded)

    def keys_to_base64(self, keys):
        """
        Given a keyring (or similar structure), convert it to Base64, which is
        safe for transport.

        @param keys Keyring (or similar)
        @return Base64 string
        @throws KeyRingError if no keys are serialized
        """

        # Validate keys
        keys = self.clean_keys(keys)

        # Serialize
        return objectToBytes(keys, self.group)

    def base64_to_keys(self, data):
        """
        Given a Base64 string, convert it back to a keyring (or similar).

        @return data Base64 string
        @returns Keyring (or similar)
        @throws KeyRingError if no keys are serialized
        """
        keys = bytesToObject(data, self.group)

        # Validate result
        return self.clean_keys(keys)

    def clean_keys(self, keys):
        """
        Validate length of keys. Private helper.

        @param keypairs Given keys
        @return Validates keys

        @throws KeyRingError if no keys available
        """
        if len(keys) == 0:
            raise KeyRingError("Empty keys")

        # Done
        return keys

    def clean_category(self, category):
        """
        Validate category. Private helper.

        @param category Category to validate
        @return Given keypair

        @throws ParameterError if category is not known to the system
        """
        if not category in self.categories:
            raise ParameterError("Unknown category: %s" % category)

        # Done
        return category

    def clean_mappings(self, mappings):
        """
        Validate mappings. Private helper.

        @param mappings Dictionary of mappings to validate
        @return Given mappings

        @throws ParameterError if a category key does not exist or a given
            party value does not exists
        """

        for category, parties in mappings.iteritems():
            self.clean_category(category)

            new_parties = []

            for party in parties:
                if not isinstance(party, list):
                    party = [party]

                for item in party:
                    if not item in self.parties:
                        raise ParameterError("Unknown party: %s" % items)

                new_parties.append(party)

            mappings[category] = new_parties

        # Return concatination of parties
        return mappings

    def clean_parties(self, parties):
        """
        Validate and clean parties. Private helper.

        Given a list of parties, convert it to a policy known to the CP-ABE
        scheme. For example:

        - [a, b, c] -> (a or b or c)
        - [(a, b), c] -> ((a and b) or c)

        @param parties List of parties to encode
        @return CP-ABE compatible policy

        @throws ParameterError if a given party is not known to the protocol or
            when a (sub)set is empty.
        """

        # Validate each party
        def loop(items):
            if isinstance(items, basestring):
                if not items in self.parties:
                    raise ParameterError("Unknown party: %s" % items)

                return items
            else:
                if len(items) == 0:
                    raise ParameterError("Cannot encode empty parties")

                if isinstance(items, list):
                    return "(" + " or ".join([ loop(x) for x in items ]) + ")"
                elif isinstance(items, tuple):
                    return "(" + " and ".join([ loop(x) for x in items ]) + ")"

        # Return concatination of parties
        return loop(parties)

class Error(Exception):
    """
    Base protocol exception
    """
    pass

class ParameterError(Error):
    """
    Exception for protocol parameters errors
    """
    pass

class KeyRingError(Error):
    """
    Exception for keypairs errors
    """
    pass

class DecryptError(Error):
    """
    Exception for decryption errors
    """
    pass

class EncryptError(Error):
    """
    Exception for encryption errors
    """
    pass