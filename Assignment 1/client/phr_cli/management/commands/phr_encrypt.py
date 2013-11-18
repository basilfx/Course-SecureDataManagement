from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, str_upper_split
from phr_cli.data_file import DataFile

import jsonrpclibs

class Command(BaseCommand):
    help = "Encrypt a message of a given category for certain parties"
    args = "<storage_file> <category> <party1,..,partyN> <message>"

    def handle(self, *args, **options):
        storage_file, category, parties, message = unpack_arguments(
            args, [str, str_upper, str_upper_split, str])

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Encrypt data
        try:
            record_item_id = actions.encrypt(storage, category, parties, message)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        self.stdout.write("Uploaded to record item ID %d" % record_item_id)
