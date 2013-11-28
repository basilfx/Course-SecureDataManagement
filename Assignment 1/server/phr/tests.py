from django.test import TestCase
from django.test.client import RequestFactory
from django.conf import settings

from phr.models import Record, RecordItem, Key

from phr import api

import json

def to_from_json(obj):
    """
    The JSON RPC server converts data to JSON and the JSON PRC client converts
    it back to Python. This method simulates this behaviour since the test
    runner cannot simulate a JSON RPC server.
    """
    return json.loads(json.dumps(obj))

class ApiTest(TestCase):

    def setUp(self):
        # Create some objects
        self.record = Record(name="Test Record")
        self.record.save()

        # Request factory
        self.factory = RequestFactory()

    def test_get_categories(self):
        request = self.factory.get("/")

        categories = to_from_json(api.get_categories(request))

        self.assertEqual(categories, settings.PHR_CATEGORIES)

    def test_get_parties(self):
        request = self.factory.get("/")

        parties = to_from_json(api.get_parties(request))

        self.assertEqual(parties, settings.PHR_PARTIES)

    def test_get_mappings(self):
        request = self.factory.get("/")

        mappings = to_from_json(api.get_mappings(request))

        self.assertEqual(mappings, settings.PHR_MAPPINGS)

    def test_add_get_record(self):
        request = self.factory.get("/")

        record_id = to_from_json(api.add_record(request, "Test 2"))
        record = to_from_json(api.get_record(request, record_id))

        self.assertEqual(record_id, record["id"])
        self.assertEqual("Test 2", record["name"])

    def test_add_get_record_item(self):
        request = self.factory.get("/")

        record_item_id = to_from_json(api.add_record_item(request, self.record.id, "PERSONAL", "Data"))
        record_item = to_from_json(api.get_record_item(request, self.record.id, record_item_id))

        self.assertEqual(record_item_id, record_item["id"])
        self.assertEqual("PERSONAL", record_item["category"])
        self.assertEqual("Data", record_item["data"])

    def test_add_get_key(self):
        request = self.factory.get("/")

        key_id = to_from_json(api.add_record_item(request, self.record.id, "HEALTH", "Key data"))
        key = to_from_json(api.get_record_item(request, self.record.id, key_id))

        self.assertEqual(key_id, key["id"])
        self.assertEqual("HEALTH", key["category"])
        self.assertEqual("Key data", key["data"])

    def test_find_record_items(self):
        request = self.factory.get("/")

        record_item_ids_one = to_from_json(api.find_record_items(request, self.record.id, {}))

        record_item_id_one = to_from_json(api.add_record_item(request, self.record.id, "HEALTH", "Key data 1"))
        record_item_id_two = to_from_json(api.add_record_item(request, self.record.id, "HEALTH", "Key data 2"))
        record_item_id_three = to_from_json(api.add_record_item(request, self.record.id, "HEALTH", "Key data 3"))

        record_item_ids_two = to_from_json(api.find_record_items(request, self.record.id, {}))

        self.assertEqual(record_item_ids_one, [])
        self.assertEqual(record_item_ids_two, [record_item_id_one, record_item_id_two, record_item_id_three])

    def test_find_keys(self):
        request = self.factory.get("/")

        key_ids_one = to_from_json(api.find_keys(request, self.record.id, {}))

        key_id_one = to_from_json(api.add_key(request, self.record.id, "HEALTH", "Key data 1"))
        key_id_two = to_from_json(api.add_key(request, self.record.id, "HEALTH", "Key data 2"))
        key_id_three = to_from_json(api.add_key(request, self.record.id, "HEALTH", "Key data 3"))

        key_ids_two = to_from_json(api.find_keys(request, self.record.id, {}))

        self.assertEqual(key_ids_one, [])
        self.assertEqual(key_ids_two, [key_id_one, key_id_two, key_id_three])
