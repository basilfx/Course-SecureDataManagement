from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Initialize connection and retrieve remote parameters"
    args = "<storage_file> <name>"

    def handle(self, *args, **options):
        storage_file, name = unpack_arguments(args, [str, str])

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Create a new record on the server
        api = jsonrpclib.Server(storage.host)
        storage.record_id = api.add_record(name)

        if not storage.record_id:
            sys.stderr.write("Unable to create record")
            return

        # Generate all the required keys
        instance = storage.get_protocol()

        storage.master_keys, storage.public_keys = instance.setup()
        storage.secret_keys = instance.keygen(storage.master_keys, storage.public_keys)

        # Write secret keys to screen
        output = []

        for party, keys in storage.secret_keys.iteritems():
            # Store record ID with the key, so the other knows the record we are
            # talking about
            data = instance.keys_to_base64((storage.record_id, keys))

            output.append(
                "BEGIN SECRET READ FOR KEYS %s\n%s\nEND SECRET READ KEYS FOR %s" % (
                    party, data, party
                )
            )

        self.stdout.write("\n\n".join(output))

        # Write output data
        storage.save()