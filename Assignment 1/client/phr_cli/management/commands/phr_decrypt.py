from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper
from phr_cli.data_file import DataFile

class Command(BaseCommand):
    help = "Decrypt a given record item"
    args = "<storage_file> <record_item_id"

    def handle(self, *args, **options):
        storage_file, record_item_id = unpack_arguments(args, [str, int])

        # Open data file
        storage = DataFile(storage_file, load=True)

        # Decrypt it
        data = actions.decrypt(storage, record_item_id)

        # Output
        if data:
            self.stdout.write("Record item content:\n\n%s" % data)
        else:
            self.stdout.write("Cannot decrypt record item\n")