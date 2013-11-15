from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper, str_upper_split
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Grant a one or more parties write access by providing the public key"
    args = "<storage_file> <category> <party1,..,partyN>"

    def handle(self, *args, **options):
        storage_file, category, parties = unpack_arguments(
            args, [str, str_upper, str_upper_split])

        # Open data file
        storage = DataFile(storage_file, load=True)
        instance = storage.get_protocol()

        # Encrypt
        key = instance.keys_to_base64(storage.public_keys[category])
        data = instance.encrypt(key, storage.public_keys, category, parties)

        # Upload to server
        api = jsonrpclib.Server(storage.host)
        key_id = api.add_key(storage.record_id, category, data)
