from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Retrieve a remote public key for a given category"
    args = "<storage_file> <category>"

    def handle(self, *args, **options):
        storage_file, category = unpack_arguments(args, [str, str_upper])

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Retrieve key
        try:
            success = actions.retrieve_key(storage, category)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        if success:
            storage.save()
            self.stdout.write("New key imported.\n")
        else:
            self.stderr.write("No keys to import.\n")
