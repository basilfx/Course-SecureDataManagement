from django.test import TestCase

from phr_cli import protocol
from phr_cli.utils import pad_message, unpad_message

class ProtocolTest(TestCase):
    def setUp(self):
        self.person = "John Doe"
        self.message = "Hi, this is a test message of a unspecific length"
        self.categories = [
            "PERSONAL",
            "HEALTH",
            "TRAINING",

            # For testing only
            "TEST1",
            "TEST2"
        ]
        self.parties = [
            "DOCTOR",
            "INSURANCE",
            "EMPLOYER",
            "HOSPITAL",
            "HEALTHCLUB"
        ]
        self.mappings = {
            "PERSONAL": ["DOCTOR", "INSURANCE", "EMPLOYER"],
            "HEALTH":   ["HOSPITAL"],
            "TRAINING": ["HEALTHCLUB"],

            # For testing only
            "TEST1":   [["DOCTOR", "INSURANCE"], "EMPLOYER", "HOSPITAL", "HEALTHCLUB"]
        }

        self.protocol = protocol.Protocol(self.categories, self.parties, self.mappings)
        self.master_keys, self.public_keys = self.protocol.setup()
        self.secret_keys = self.protocol.keygen(self.master_keys, self.public_keys)

    def test_encrypt_decrypt_ok(self):
        cipher_one = self.protocol.encrypt(self.message, self.public_keys, "PERSONAL", ["DOCTOR", "INSURANCE"])
        cipher_two = self.protocol.encrypt(self.message, self.public_keys, "PERSONAL", ["EMPLOYER"])

        # Same message with different policies should not have same ciphers
        self.assertNotEqual(cipher_one, cipher_two)

        plain_doctor = self.protocol.decrypt(cipher_one, self.secret_keys["DOCTOR"])
        plain_insurance = self.protocol.decrypt(cipher_one, self.secret_keys["INSURANCE"])
        plain_employer = self.protocol.decrypt(cipher_two, self.secret_keys["EMPLOYER"])

        # Encrypt -> Decrypt should yield the same
        self.assertEqual(self.message, plain_doctor)
        self.assertEqual(self.message, plain_insurance)
        self.assertEqual(self.message, plain_employer)

    def test_encrypt_decrypt_shared(self):
        cipher = self.protocol.encrypt(self.message, self.public_keys, "TEST1", [("DOCTOR", "INSURANCE"), "EMPLOYER"])

        plain_doctor = self.protocol.decrypt(cipher, self.secret_keys["DOCTOR"])
        plain_insurance = self.protocol.decrypt(cipher, self.secret_keys["INSURANCE"])
        plain_employer = self.protocol.decrypt(cipher, self.secret_keys["EMPLOYER"])

        # Hospital has no shared attribute
        with self.assertRaises(protocol.DecryptError) as context:
            self.protocol.decrypt(cipher, self.secret_keys["HOSPITAL"])

        # Encrypt -> Decrypt should yield the same
        self.assertEqual(self.message, plain_doctor)
        self.assertEqual(self.message, plain_insurance)
        self.assertEqual(self.message, plain_employer)

    def test_encrypt_decrypt_fail(self):
        cipher = self.protocol.encrypt(self.message, self.public_keys, "HEALTH", ["DOCTOR", "INSURANCE"])

        # Decryption should fail since it lacks an attribute
        with self.assertRaises(protocol.KeyRingError) as context:
            plain = self.protocol.decrypt(cipher, self.secret_keys["EMPLOYER"])

    def test_decrypt_malformed(self):
        cipher = "ABC123" * 16

        # No data
        with self.assertRaises(protocol.DecryptError) as context:
            self.protocol.decrypt("", self.secret_keys["EMPLOYER"])

        # Malformed data
        with self.assertRaises(protocol.DecryptError) as context:
            self.protocol.decrypt(cipher, self.secret_keys["EMPLOYER"])

    def test_missing_party(self):
        with self.assertRaises(protocol.ParameterError) as context:
            cipher = self.protocol.encrypt(self.message, self.public_keys, "HEALTH", [])

    def test_encrypt_missing_keys(self):
        # Non-exisiting party
        with self.assertRaises(protocol.ParameterError) as context:
            self.protocol.encrypt(self.message, self.public_keys, "NOT_EXISTING", [])

        # No keyring
        with self.assertRaises(protocol.KeyRingError) as context:
            self.protocol.decrypt("", [])

class UtilsTest(TestCase):
    def test_pad_unpad(self):
        block_size = 16

        message_a = "A" * 14 * 5
        message_b = "B" * block_size * 5
        message_c = "C" * 0 # Empty

        padded_a = pad_message(message_a, block_size)
        padded_b = pad_message(message_b, block_size)
        padded_c = pad_message(message_c, block_size)

        # Lengths are multiples of block_size
        self.assertEqual(len(padded_a) % block_size, 0)
        self.assertEqual(len(padded_b) % block_size, 0)
        self.assertEqual(len(padded_c) % block_size, 0)

        # Aligned message will one block longer due to overhead
        self.assertEqual(len(padded_b), len(message_b) + block_size)

        # Empty message is at most one block
        self.assertEqual(len(padded_c), block_size)

        unpadded_a = unpad_message(padded_a)
        unpadded_b = unpad_message(padded_b)
        unpadded_c = unpad_message(padded_c)

        # Unpadding should yield original message
        self.assertEqual(message_a, unpadded_a)
        self.assertEqual(message_b, unpadded_b)
        self.assertEqual(message_c, unpadded_c)

