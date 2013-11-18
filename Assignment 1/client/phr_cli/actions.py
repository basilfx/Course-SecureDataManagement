from phr_cli.protocol import DecryptError, KeyRingError

import jsonrpclib

def create(storage, host, record_name):
    # Create a new record on the server
    api = jsonrpclib.Server(host)

    # Retrieve server settings
    storage.categories = api.get_categories()
    storage.parties = api.get_parties()
    storage.mappings = api.get_mappings()
    storage.host = host

    # Add record information
    storage.record_id = api.add_record(record_name)
    storage.record_name = record_name
    storage.record_role = "OWNER"

    if not storage.record_id:
        raise ValueError("Unable to create record")

    # Generate all the required keys
    instance = storage.get_protocol()

    storage.master_keys, storage.public_keys = instance.setup()
    storage.secret_keys = instance.keygen(storage.master_keys, storage.public_keys)

    # Done
    return storage.record_id

def connect(storage, host, key_data):
    # Connect to remote server
    api = jsonrpclib.Server(host)

    # Retrieve server settings
    storage.categories = api.get_categories()
    storage.parties = api.get_parties()
    storage.mappings = api.get_mappings()
    storage.host = host

    # Unpack the key
    instance = storage.get_protocol()
    record_id, record_role, secret_keys = instance.base64_to_keys(key_data)

    # Verify if record exists
    api = jsonrpclib.Server(storage.host)
    record = api.get_record(record_id)

    if not record:
        raise ValueError("Unable to retrieve record from server")

    if not record["id"] == record_id:
        raise ValueError("Record ID mismatch")

    # Record exists, set properties
    storage.record_id = record["id"]
    storage.record_name = record["name"]
    storage.record_role = record_role
    storage.secret_keys = { record_role: secret_keys }

    # Done
    return record["id"]

def decrypt(storage, record_item_id=None, record_item=None):
    instance = storage.get_protocol()

    # Query the server for any keys
    if not record_item_id is None:
        api = jsonrpclib.Server(storage.host)
        record_item = api.get_record_item(storage.record_id, record_item_id)

    # Try to decrypt the key
    success = False

    for party, secret_keys in storage.secret_keys.iteritems():
        try:
            data = instance.decrypt(record_item["data"], secret_keys)
            success = True

            break
        except (DecryptError, KeyRingError):
            # Just ignore
            continue

    # Done
    if success:
        return data
    else:
        return None

def encrypt(storage, category, parties, message):
    instance = storage.get_protocol()

    # Encrypt
    data = instance.encrypt(message, storage.public_keys, category, parties)

    # Upload to server
    api = jsonrpclib.Server(storage.host)
    record_item_id = api.add_record_item(storage.record_id, category, data)

    if not record_item_id:
        raise ValueError("Failed uploading record item")

def grant(storage, category, parties):
    instance = storage.get_protocol()

    # Encrypt
    key = instance.keys_to_base64(storage.public_keys[category])
    data = instance.encrypt(key, storage.public_keys, category, parties)

    # Upload to server
    api = jsonrpclib.Server(storage.host)
    key_id = api.add_key(storage.record_id, category, data)

    # Verify
    if not key_id:
        raise ValueError("Unable to upload key")

    # Done
    return key_id

def retrieve(storage, category):
    instance = storage.get_protocol()

    # Query the server for any keys
    api = jsonrpclib.Server(storage.host)
    key_ids = api.find_keys(storage.record_id, { "category": category })

    if not key_ids:
        return

    # Process each ID
    success = False

    for key_id in key_ids:
        key = api.get_key(storage.record_id, key_id)

        # Try to decrypt the key
        success2 = False

        for secret_keys in storage.secret_keys.itervalues():
            try:
                data = instance.decrypt(key["data"], secret_keys)
                success2 = True

                break
            except DecryptError:
                # Just ignore
                continue

        if not success2:
            continue

        # Store it
        if not hasattr(storage, "public_keys"):
            storage.public_keys = {}

        storage.public_keys[category] = instance.base64_to_keys(data)

        # When success, stop. There can only be one public key for a given
        # category.
        return True

def get_record_items(storage, record_item_ids):
    api = jsonrpclib.Server(storage.host)
    return [ api.get_record_item(storage.record_id, x) for x in record_item_ids ]

def list_record_items(storage, **lookups):
    api = jsonrpclib.Server(storage.host)
    record_item_ids = api.find_record_items(storage.record_id, lookups)
    print record_item_ids

    if record_item_ids == False:
        raise ValueError("Unable to retrieve record from server")

    return record_item_ids