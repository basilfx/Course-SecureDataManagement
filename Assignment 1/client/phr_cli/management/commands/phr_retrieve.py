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
            count = actions.retrieve(storage, { "category": category })
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        if count:
            storage.save()
            self.stdout.write("%d new keys imported.\n" % count)
        else:
            self.stout.write("No new keys imported.\n")
