from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, str_upper_split, load_data_file

import jsonrpclib

class Command(BaseCommand):
    help = "Encrypt a message of a given category for certain parties"
    args = "<data_file> <category> <party1,..,partyN> <message>"

    def handle(self, *args, **options):
        storage, category, parties, message = unpack_arguments(args,
            [load_data_file(), str_upper, str_upper_split, str])

        # Encrypt data
        try:
            record_item_id = actions.encrypt(storage, category, parties, message)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        self.stdout.write("Uploaded to record item ID %d" % record_item_id)
