from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, str_upper, load_data_file

class Command(BaseCommand):
    help = "Decrypt a given record item"
    args = "<data_file> <record_item_id"

    def handle(self, *args, **options):
        storage, record_item_id = unpack_arguments(args, [load_data_file(), int])

        # Decrypt it
        data = actions.decrypt(storage, record_item_id)

        # Output
        if data:
            self.stdout.write("Record item content:\n\n%s" % data)
        else:
            self.stdout.write("Cannot decrypt record item\n")