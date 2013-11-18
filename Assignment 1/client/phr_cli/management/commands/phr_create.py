from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Initialize a new PHR record with a given host and record name"
    args = "<storage_file> <host> <record_name>"

    def handle(self, *args, **options):
        storage_file, host, record_name = unpack_arguments(args, [str, str, str])

        # Open data file
        storage = DataFile(storage_file, load=True)

        try:
            # Connect
            actions.connect(storage, host)

            # Create
            secret_keys = actions.create(storage, record_name)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError, e:
            raise CommandError(e)

        # Print keys
        self.stdout.write("\n\n".join(output))

        # Write output data
        storage.save()