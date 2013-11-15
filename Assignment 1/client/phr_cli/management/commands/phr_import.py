from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper, str_upper_split
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Import a secret key into the given storage"
    args = "<storage_file>"

    def handle(self, *args, **options):
        storage_file, = unpack_arguments(args, [str])

        # Ask user to supply key
        data = raw_input("Paste the keys data, excluding the BEGIN and END block: ")

        if len(data) == 0:
            return

        # Open data file
        storage = DataFile(storage_file, load=True)
        instance = storage.get_protocol()

        # Retrieve the keys
        data = instance.base64_to_keys(data)
        storage.record_id = data[0]
        storage.secret_keys = { 0: data[1] }

        # Done
        storage.save()
