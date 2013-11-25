from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, str_upper_split, load_data_file

import jsonrpclib

class Command(BaseCommand):
    help = "Grant a one or more parties write access by providing the public key"
    args = "<data_file> <category> <party1,..,partyN>"

    def handle(self, *args, **options):
        storage, category, parties = unpack_arguments(
            args, [load_data_file(), str_upper, str_upper_split])

        # Send key
        try:
            key_id = actions.grant(storage, category, parties)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        self.stdout.write("Granted key for category %s with key ID %d" % (category, key_id))