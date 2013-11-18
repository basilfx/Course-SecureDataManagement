from django.conf import settings

from jsonrpc import jsonrpc_method

from phr.models import Key, RecordItem, Record

@jsonrpc_method("get_categories")
def get_categories(request):
    """
    Retrieve all available categories currently used in the system.

    @returns List of categories
    """

    return settings.PHR_CATEGORIES

@jsonrpc_method("get_parties")
def get_parties(request):
    """
    Retrieve all available parties currently used in the system.

    @returns List of parties
    """

    return settings.PHR_PARTIES

@jsonrpc_method("get_mappings")
def get_mappings(request):
    """
    Retrieve all mappings between a category and parties.

    @returns Dictionary of mappings
    """

    return settings.PHR_MAPPINGS

@jsonrpc_method("add_record")
def add_record(request, name):
    """
    Add a new record to the database with a given name.

    @param name Name of record
    @returns Record ID
    """

    instance = Record(name=name)
    instance.save()

    return instance.pk

@jsonrpc_method("add_record_item")
def add_record_item(request, record_id, category, data):
    """
    Add a new record item to the database for a given category

    @param record_id ID of record where item is child of
    @param category Category of record item
    @param data Record item data
    @returns Record item ID
    """

    instance = RecordItem(record_id=record_id, category=category, data=data)
    instance.save()

    return instance.pk

@jsonrpc_method("add_key")
def add_key(request, record_id, category, data):
    """
    Add a new key to the database for a given category

    @param record_id ID of record where item is child of
    @param category Category of record item
    @param data Key data
    @returns Record item ID
    """

    instance = Key(record_id=record_id, category=category, data=data)
    instance.save()

    return instance.pk

@jsonrpc_method("get_key")
def get_key(request, record_id, key_id):
    """
    Retrieve an (encrypted) key for a given record and category.

    @param record_id ID of the record
    @param key_id ID of the key
    @return (Encrypted) key if matched, else False
    """

    try:
        instance = Key.objects.get(pk=key_id, record_id=record_id)

        return {
            "id": instance.pk,
            "category": instance.category,
            "data": instance.data
        }
    except Key.DoesNotExist:
        return False

@jsonrpc_method("get_record")
def get_record(request, record_id):
    """
    Retrieve a specific record from the database.

    @param record_id ID of the record
    @return Record if matched, else False
    """

    try:
        instance = Record.objects.get(pk=record_id)

        return {
            "id": instance.pk,
            "name": instance.name
        }
    except Record.DoesNotExist:
        return False

@jsonrpc_method("get_record_item")
def get_record_item(request, record_id, record_item_id):
    """
    Retrieve a specific record item from the database

    @param record_id ID of the record
    @param record_item_id ID of the record item
    @return Record item if matched, else False
    """

    try:
        instance = RecordItem.objects.get(pk=record_item_id, record_id=record_id)

        return {
            "id": instance.pk,
            "category": instance.category,
            "data": instance.data
        }
    except RecordItem.DoesNotExist:
        return False

@jsonrpc_method("find_keys")
def find_keys(request, record_id, lookups):
    """
    Lookup ID of keys for a given record. Lookup can be a Django-like object.

    @param record_id ID of the record
    @param lookups Dictionary of lookups
    @return List of IDs of keys
    """

    items = Key.objects.filter(record_id=record_id) \
                       .filter(**lookups) \
                       .values_list("pk", flat=True)
    return list(items)

@jsonrpc_method("find_record_items")
def find_record_items(request, record_id, lookups):
    """
    Lookup ID of record items for a given record. Lookup can be a Django-like
    object.

    @param record_id ID of the record
    @param lookups Dictionary of lookups
    @return List of IDs of record items
    """

    items = RecordItem.objects.filter(record_id=record_id) \
                              .filter(**lookups) \
                              .values_list("pk", flat=True)
    return list(items)
