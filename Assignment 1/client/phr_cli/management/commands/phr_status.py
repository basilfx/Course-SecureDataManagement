from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, load_data_file

class Command(BaseCommand):
    help = "Retrieve a remote public key for a given category"
    args = "<data_file>"

    def handle(self, *args, **options):
        storage, = unpack_arguments(args, [load_data_file()])

        # Open data file
        instance = storage.get_protocol()

        def join(attribute):
            return getattr(storage, attribute, "<not set>")

        def join_attribute(attribute):
            return ", ".join(getattr(storage, attribute, ["<not set>"]))

        def join_attribute_keys(attribute, prefix=" "*13, unfold=False):
            keys = getattr(storage, attribute, False)

            if not keys:
                return "<not set>"

            if unfold:
                return ("\n" + prefix).join([ "%s -> %s" % (x, ", ".join([ str(z) for z in y.iterkeys()])) for x, y in keys.iteritems() ])
            else:
                return ("\n" + prefix).join([ "%s -> %s" % (x, ", ".join([ str(z) for z in y ])) for x, y in keys.iteritems() ])

        # Print statistics
        self.stdout.write("\n".join([
            "Host:        %s" % join("host"),
            "Categories:  %s" % join_attribute("categories"),
            "Parties:     %s" % join_attribute("parties"),
            "Mappings:    %s" % join_attribute_keys("mappings"),
            "",
            "Record ID:   %s" % join("record_id"),
            "Record name: %s" % join("record_name"),
            "Record role: %s" % join("record_role"),
            "",
            "Master keys: %s" % join_attribute("master_keys"),
            "Public keys: %s" % join_attribute("public_keys"),
            "Secret keys: %s" % join_attribute_keys("secret_keys", unfold=True)
        ]))
