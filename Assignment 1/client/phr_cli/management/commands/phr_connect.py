from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "Initialize connection and retrieve remote parameters"
    args = "<host> <storage_file>"

    def handle(self, *args, **options):
        host, storage_file = unpack_arguments(args, [str, str])

        # Open data file
        storage = DataFile(storage_file)

        try:
            actions.connect(storage_file, host)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")

        # Write output data
        storage.save()
