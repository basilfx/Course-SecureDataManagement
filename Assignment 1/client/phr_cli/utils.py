from django.core.management.base import CommandError

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

def unpack_arguments(args, formats):
    """
    Unpack a list of arguments and format them according to formats. Formats is
    a list of functions which will be applied to that argument. Both args and
    format need to be of the same length.

    Helper method to use with Django management commands.

    @param args List of arguments to format
    @param format List of formatting functions
    @return List of formatted arguments
    @throws CommandError if len(args) != len(formats) or if data cannot be
            formatted.
    """

    # Verify number of arguments
    expected, given = len(formats), len(args)

    if expected != given:
        raise CommandError("Expected %d arguments (%d given)" % (expected, given))

    # Parse arguments
    result = []

    for arg, format in zip(args, formats):
        try:
            result.append(format(arg))
        except:
            raise CommandError("Unable to parse argument %d" % (len(result) + 1))

    # Done
    return result

def str_upper(data):
    """
    Given some data, convert it to string and uppercase.

    @param data Any data that can be stringified
    @return String representation in uppercase of data
    """

    return str(data).upper()

def str_upper_split(data, delimeter=","):
    """
    Given some data, convert it to string and uppercase and split it by a
    delimeter.

    @param data Any data that can be stringified
    @param delimeter Optional delimeter to split string
    @return List of string representations in uppercase of data
    """

    return str(data).upper().split(delimeter)

def encode_with_tuples(data):
    pass

def decode_with_tuples(data):
    pass