from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from charm.toolbox.pairinggroup import PairingGroup
from charm.core.engine.util import objectToBytes
from charm.schemes.abenc import abenc_lsw08

import jsonrpclib
import json
import os

class Command(BaseCommand):
    args = "<host> <data_file>"
    help = "Initialize connection"

    def handle(self, *args, **options):
        host, data_file = self.parse_args(args)

        # Connect to server
        api = jsonrpclib.Server(host)
        attributes = api.system.get_attributes()
        categories = api.system.get_categories()

        # Make data
        data = {
            "connection": {
                "host": host,
                "attributes": attributes,
                "categories": categories
            }
        }

        # Save to file
        json.dump(data, open(data_file, "w"))

        # Done
        self.stdout.write("Written data to '%s'\n" % data_file)

        return

        # Instantize encryption
        group = PairingGroup("MNT224")
        abe = abenc_lsw08.KPabe(group)

        # Generate public key and master key
        pk, mk = abe.setup()

        # Dump to JSON
        pk = objectToBytes(pk, group)
        mk = objectToBytes(mk, group)

        self.stdout.write("PK = %s\nMK = %s" % (pk, mk))

    def parse_args(self, args):
        # Check if host is given
        try:
            host = args[0]
        except:
            raise CommandError("Missing host")

        # Check if file is given
        try:
            data_file = args[1]
        except:
            raise CommandError("Missing data file")

        # Done
        return host, data_file

