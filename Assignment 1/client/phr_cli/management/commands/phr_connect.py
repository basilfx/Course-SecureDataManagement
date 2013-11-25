from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, str_upper_split, load_data_file

import jsonrpclib

class Command(BaseCommand):
    help = "Connect to a PHR record on a specific PHR server"
    args = "<data_file> <host>"

    def handle(self, *args, **options):
        storage, host = unpack_arguments(args, [load_data_file(False), str])

        # Ask user to supply key
        key_data = raw_input("Paste the keys data, excluding the BEGIN and END block: ")

        if len(key_data) == 0:
            return

        # Process data
        try:
            record_id = actions.connect(storage, host, key_data)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        storage.save()

        # Done
        self.stdout.write("Connected to record ID %d\n" % record_id)
