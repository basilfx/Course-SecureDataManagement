from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper
from phr_cli.data_file import DataFile
from phr_cli.protocol import DecryptError, KeyRingError

import jsonrpclib

class Command(BaseCommand):
    help = "Decrypt a given record item"
    args = "<storage_file> <record_item_id"

    def handle(self, *args, **options):
        storage_file, record_item_id = unpack_arguments(args, [str, int])

        # Open data file
        storage = DataFile(storage_file, load=True)
        instance = storage.get_protocol()

        # Query the server for any keys
        api = jsonrpclib.Server(storage.host)
        record_item = api.get_record_item(storage.record_id, record_item_id)

        # Try to decrypt the key
        success = False

        for party, secret_keys in storage.secret_keys.iteritems():
            try:
                data = instance.decrypt(record_item["data"], secret_keys)
                success = True

                break
            except (DecryptError, KeyRingError):
                # Just ignore
                continue

        # It succeeded
        if success:
            self.stdout.write("Record content:\n\n%s" % data)
        else:
            self.stderr.write("Cannot decrypt record\n")