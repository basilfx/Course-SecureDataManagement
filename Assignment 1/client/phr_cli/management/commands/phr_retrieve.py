from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper
from phr_cli.data_file import DataFile
from phr_cli.protocol import DecryptError

import jsonrpclib

class Command(BaseCommand):
    help = "Retrieve a remote public key for a given category"
    args = "<storage_file> <category>"

    def handle(self, *args, **options):
        storage_file, category = unpack_arguments(args, [str, str_upper])

        # Open data file
        storage = DataFile(storage_file, load=True)
        instance = storage.get_protocol()

        # Query the server for any keys
        api = jsonrpclib.Server(storage.host)
        key_ids = api.find_keys(storage.record_id, { "category": category })

        if not key_ids:
            self.stderr.write("No key available to retrieve\n")
            return

        # Process each ID
        success = False

        for key_id in key_ids:
            key = api.get_key(storage.record_id, key_id)

            # Try to decrypt the key
            try:
                data = instance.decrypt(key["data"], storage.secret_keys)
            except DecryptError:
                # Just ignore
                continue

            # Store it
            if not hasattr(storage, "public_keys"):
                storage.public_keys = {}

            storage.public_keys[category] = instance.base64_to_keys(data)

            # When success, stop. There can only be one public key for a given
            # category.
            success = True
            break

        # Done
        if success:
            storage.save()
            self.stdout.write("Imported key\n")
        else:
            self.stdout.write("Unable to import key.")
