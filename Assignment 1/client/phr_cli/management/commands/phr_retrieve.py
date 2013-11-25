from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, load_data_file

import jsonrpclib

class Command(BaseCommand):
    help = "Retrieve a remote public key for a given category"
    args = "<data_file> <category>"

    def handle(self, *args, **options):
        storage, category = unpack_arguments(args, [load_data_file(), str_upper])

        # Retrieve key
        try:
            keys = actions.retrieve(storage, category=category)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError:
            raise CommandError(e)

        # Done
        if len(keys) > 0:
            storage.save()
            self.stdout.write("Key(s) imported for %s.\n" % ", ".join(keys))
        else:
            self.stdout.write("No new key(s) imported.\n")
