from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper, str_upper_split
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Encrypt a message of a given category for certain parties"
    args = "<storage_file> <category> <party1,..,partyN> <message>"

    def handle(self, *args, **options):
        storage_file, category, parties, message = unpack_arguments(
            args, [str, str_upper, str_upper_split, str])

        # Open data file
        storage = DataFile(storage_file, load=True)
        instance = storage.get_protocol()

        # Encrypt
        data = instance.encrypt(message, storage.public_keys, category, parties)

        # Upload to server
        api = jsonrpclib.Server(storage.host)
        record_item_id = api.add_record_item(storage.record_id, category, data)

        if not record_item_id:
            self.stdout.write("Failed uploading record item")
            return

        # Done
        self.stdout.write("Uploaded to record item ID %d" % record_item_id)
