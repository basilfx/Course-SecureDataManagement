from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.schemes.abenc import abenc_waters09
from charm.core.math.pairing import hashPair

from Crypto.Cipher import AES
from Crypto import Random

from phr_cli.utils import pad_message, unpad_message

import jsonrpclib
import itertools
import base64
import struct
import zlib
import io

def Party(name, *sub_parties):
    """
    Small helper to model a party.

    @param name Name of the party
    @param sub_parties Optional sub parties
    @return Tuple object
    """
    return (name, sub_parties)

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
        self.categories = categories
        self.parties, self.attributes = self.clean_parties_unfold(parties)
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
                raise KeyRingError("No public key and master key available for category: %s" % category)

            # Generate secret keys
            for party, attributes in parties.iteritems():
                # Generate keys for a party.
                sk = self.scheme.keygen(pk, mk, attributes)

                # Ensure key exist
                if not party in result:
                    result[party] = {}

                # Add key to each party for category
                result[party][category] = sk

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
        @return Base64 string representing the keyring (or similar)

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

    def unfold_party(self, party):
        """
        Convert string notation to tuple. For example, PARTY+A+B+C will be
        converted to (PARTY, (A, B, C)). This is to work around the fact that
        JSON has no native support for tuples.

        @param party Party to unfold.
        @return If party can be unfolded, then it will return a tuple. If this
            is not possible, return party.
        """

        if isinstance(party, basestring):
            parts = party.split("+")

            if len(parts) > 1:
                return Party(parts[0], *parts[1:])

        return party

    def parties_to_dict(self, sub_parties_only=False):
        """
        Convert the parties dictionary to a flat dictionary with the key
        representing the name of the (sub) party. If a specific party does not
        have sub parties, it is always added while if a specific party does have
        sub parties, it is only added if sub_parties_only is False.

        @param sub_parties_only Include party if party has sub parties.
        @return Dictionary object with keys representing the (sub) party name
            and the value all the attributes.
        """
        result = {}

        for party, sub_parties in self.parties.iteritems():
            if len(sub_parties) > 0:
                if not sub_parties_only:
                    result[party] = party

                for sub_party in sub_parties:
                    result["%s-%s" % (party, sub_party)] = (party, sub_party)
            else:
                result[party] = party

        return result

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

        new_mappings = {}

        for category, parties in mappings.iteritems():
            category = self.clean_category(category)
            new_mappings[category] = {}

            for party in parties:
                # Convert PARTY+A+B into (PARTY, (A, B)) if possible
                party = self.unfold_party(party)

                if isinstance(party, basestring):
                    if not party in self.parties:
                        raise ParameterError("Unknown party: %s" % party)

                    sub_parties = self.parties[party]

                    if len(sub_parties) > 1:
                        for sub_party in sub_parties:
                            new_party = "%s-%s" % (party, sub_party)
                            new_mappings[category][new_party] = [party, sub_party]
                    else:
                        new_mappings[category][party] = [party]
                elif isinstance(party, tuple):
                    party, sub_parties = party

                    for sub_party in sub_parties:
                        new_party = "%s-%s" % (party, sub_party)
                        new_mappings[category][new_party] = [party, sub_party]
                elif isinstance(party, list):
                    new_parties = []
                    all_attributes = []

                    # Unfold each item
                    for item in party:
                        # Convert PARTY+A+B into (PARTY, (A, B)) if possible
                        item = self.unfold_party(item)

                        if isinstance(item, tuple):
                            attributes = list(item[1])
                            all_attributes += attributes + [item[0]]

                            for attribute in attributes:
                                new_parties += ["%s-%s" % (item[0], attribute)]
                        if isinstance(item, basestring):
                            if not item in self.parties:
                                raise ParameterError("Unknown party: %s" % party)

                            attributes = self.parties[item]
                            all_attributes += attributes + [item]

                            if len(attributes) > 1:
                                for attribute in attributes:
                                    new_parties += ["%s-%s" % (item, attribute)]
                            else:
                                new_parties += [item]

                    # Remove duplicates, the easy way
                    all_attributes = list(set(all_attributes))

                    # Append to the list
                    for item in new_parties:
                        new_mappings[category][item] = all_attributes

        # Verify each attribute for its existence
        for category, parties in new_mappings.iteritems():
            for party, attributes in parties.iteritems():
                for attribute in attributes:
                    if attribute not in self.attributes:
                        raise ParameterError("Unknown attribute: %s" % attribute)

        # Return new mappings
        return new_mappings

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
                if not items in self.attributes:
                    raise ParameterError("Unknown party or sub party: %s" % items)

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

    def clean_parties_unfold(self, parties):
        """
        Validate, clean and unfold parties. Private helper.

        """

        result = {}
        attributes = []

        for party in parties:
            # Convert PARTY+A+B into (PARTY, (A, B)) if possible
            party = self.unfold_party(party)

            if isinstance(party, tuple):
                party, sub_parties = party

                result[party] = []
                attributes.append(party)

                for sub_party in sub_parties:
                    if sub_party in result:
                        raise ParameterError("A sub party cannot have the same name as a party")

                    result[party].append(sub_party)
                    attributes.append(sub_party)
            else:
                result[party] = []
                attributes.append(party)

        return result, attributes

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