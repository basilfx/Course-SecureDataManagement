from django.core.management.base import BaseCommand, CommandError

from phr_cli.utils import unpack_arguments, str_upper
from phr_cli.data_file import DataFile

import jsonrpclib

class Command(BaseCommand):
    help = "List all record items for a given category"
    args = "<storage_file> <category>"

    def handle(self, *args, **options):
        storage_file, category = unpack_arguments(args, [str, str_upper])

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Download list of record items
        api = jsonrpclib.Server(storage.host)
        record_item_ids = api.find_record_items(storage.record_id, { "category": category })

        # Process each one
        for record_item_id in record_item_ids:
            self.stdout.write("Record item ID %d\n" % record_item_id)