from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, str_upper_split
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Import a secret key into a given storage"
    args = "<storage_file>"

    def handle(self, *args, **options):
        storage_file, = unpack_arguments(args, [str])

        # Ask user to supply key
        data = raw_input("Paste the keys data, excluding the BEGIN and END block: ")

        if len(data) == 0:
            return

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Process data
        try:
            record_id = actions.import_key(storage, data)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        storage.save()

        # Done
        self.stdout.write("Key imported for record ID %d\n" % record_id)
