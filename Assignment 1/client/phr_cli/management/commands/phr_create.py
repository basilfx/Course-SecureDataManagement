from django.core.management.base import BaseCommand, CommandError

from phr_cli import actions
from phr_cli.utils import unpack_arguments, load_data_file

import jsonrpclib

class Command(BaseCommand):
    help = "Initialize a new PHR record with a given host and record name"
    args = "<data_file> <host> <record_name>"

    def handle(self, *args, **options):
        storage, host, record_name = unpack_arguments(args, [load_data_file(False), str, str])

        # Connect to remote server
        try:
            secret_keys = actions.create(storage, host, record_name)
        except jsonrpclib.ProtocolError:
            raise CommandError("Unable to communicate to remote server")
        except ValueError, e:
            raise CommandError(e)

        # Print keys
        instance = storage.get_protocol()
        output = []

        for party, keys in storage.secret_keys.iteritems():
            # Store record ID with the key, so the other knows the record we are
            # talking about
            data = instance.keys_to_base64((storage.record_id, party, keys))

            output.append(
                "BEGIN SECRET READ FOR KEYS %s\n%s\nEND SECRET READ KEYS FOR %s" % (
                    party, data, party
                )
            )

        self.stdout.write("\n\n".join(output))

        # Write output data
        storage.save()