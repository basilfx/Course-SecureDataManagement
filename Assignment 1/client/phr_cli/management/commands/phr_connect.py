from django.core.management.base import BaseCommand, CommandError

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

        # Retrieve the server data
        api = jsonrpclib.Server(host)

        try:
            storage.categories = api.get_categories()
            storage.parties = api.get_parties()
            storage.mappings = api.get_mappings()
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")

        # Add host
        storage.host = host

        # Write output data
        storage.save()
