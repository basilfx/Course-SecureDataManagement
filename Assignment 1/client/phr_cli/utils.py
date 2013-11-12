from Crypto import Random

import struct
import io

def pad_message(message, block_size):
    """
    Pad a given message such that it is a multiple of a given block size. The
    original length is encoded in the message, so the message can be of any
    type of data. Random data is added as padding.

    @param message Unpadded message
    @param block_size Block size to which it will be aligned
    @returns Padded message
    """

    original_length = len(message)
    new_length = original_length + struct.calcsize("Q")

    result = io.BytesIO()
    result.write(struct.pack("<Q", original_length))
    result.write(message)
    result.write(Random.new().read(block_size - (new_length % block_size)))

    # Done
    return result.getvalue()

def unpad_message(message):
    """
    Given a padded message, unpad it.

    @param message Message to unpad
    @returns Unpadded message
    """
    message = io.BytesIO(message)
    original_length = struct.unpack("<Q", message.read(struct.calcsize("Q")))[0]

    # Done
    return message.read(original_length)