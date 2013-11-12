from django.test import TestCase

from phr_cli.protocol import Protocol
from phr_cli.protocol import ProtocolDecryptException, ProtocolKeyException
from phr_cli.utils import pad_message, unpad_message

class ProtocolTest(TestCase):
    def setUp(self):
        self.person = "John Doe"
        self.message = "Hi, this is a test message of a unspecific length"
        self.categories = {
            1: "PERSONAL",
            2: "HEALTH",
            3: "TRAINING"
        }
        self.parties = {
            1: ["DOCTOR", "INSURANCE", "EMPLOYER"],
            2: ["HOSPITAL"],
            3: ["HEALTH_CLUB"]
        }

        self.protocol = Protocol()
        self.keypairs = self.protocol.setup(self.person, self.categories)
        self.secrets = self.protocol.keygen(self.keypairs, self.parties)

    def test_encrypt_decrypt_ok(self):
        cipher_one = self.protocol.encrypt(self.message, self.keypairs, 1, ["DOCTOR", "INSURANCE"])
        cipher_two = self.protocol.encrypt(self.message, self.keypairs, 1, ["EMPLOYER"])

        # Same message with different policies should not have same ciphers
        self.assertNotEqual(cipher_one, cipher_two)

        plain_doctor = self.protocol.decrypt(cipher_one, self.secrets["DOCTOR"], 1)
        plain_insurance = self.protocol.decrypt(cipher_one, self.secrets["INSURANCE"], 1)
        plain_employer = self.protocol.decrypt(cipher_two, self.secrets["EMPLOYER"], 1)

        # Encrypt -> Decrypt should yield the same
        self.assertEqual(self.message, plain_doctor)
        self.assertEqual(self.message, plain_insurance)
        self.assertEqual(self.message, plain_employer)

    def test_encrypt_decrypt_fail(self):
        cipher = self.protocol.encrypt(self.message, self.keypairs, 1, ["DOCTOR", "INSURANCE"])

        # Decryption should fail since it lacks an attribute
        with self.assertRaises(ProtocolDecryptException) as context:
            plain = self.protocol.decrypt(cipher, self.secrets["EMPLOYER"], 1)

    def test_encrypt_missing_keys(self):
        with self.assertRaises(ProtocolKeyException) as context:
            self.protocol.encrypt(self.message, self.keypairs, 5, [])

        with self.assertRaises(ProtocolKeyException) as context:
            self.protocol.decrypt("", [], 5)

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

        # Empty message is at most one block
        self.assertEqual(len(padded_c), block_size)

        unpadded_a = unpad_message(padded_a)
        unpadded_b = unpad_message(padded_b)
        unpadded_c = unpad_message(padded_c)

        # Unpadding should yield original message
        self.assertEqual(message_a, unpadded_a)
        self.assertEqual(message_b, unpadded_b)
        self.assertEqual(message_c, unpadded_c)

