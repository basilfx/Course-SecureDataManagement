from phr_cli.protocol import DecryptError, KeyRingError

import jsonrpclib

"""
Helper methods to bridge the gap between the PHR server and our local storage.
Methods in this module are shared between the command line commands and the web
interface.
"""

def create(storage, host, record_name):
    """
    Create a new PHR record on the server.

    This method modifies the storage, but does not save the changes.

    @param storage Data file to work with.
    @param host Remote PHR server to connect with
    @param record_name User identifier to represent the record.
    @return ID of the newly created record

    @throws ValueError if record could not be created on the remote server.
    """

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

    # Server may fail.
    if not storage.record_id:
        raise ValueError("Unable to create record")

    # Generate all the required keys
    instance = storage.get_protocol()

    storage.master_keys, storage.public_keys = instance.setup()
    storage.secret_keys = instance.keygen(storage.master_keys, storage.public_keys)

    # Done
    return storage.record_id

def connect(storage, host, key_data):
    """
    Connect to an existing PHR record on a given server via a user specified
    key.

    This method modifies the storage, but does not save the changes.

    @param storage Data file to work with.
    @param host Remote PHR server to connect with.
    @param key_data Base64 encoded key data, supplied by the record owner.
    @return ID of the record connected with.

    @throws ValueError if record does not exist on remote server or if ID
        embedded in the key does not match the ID of the remote record.
    """
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

def encrypt(storage, category, parties, message):
    """
    Given a message, a category and parties (receivers), encrypt a message and
    upload it to the PHR server as a new record item.

    @param storage Data file to work with.
    @param category Category of message. Determines the right encryption key.
    @param parties Receiving parties.
    @param message Arbtrary message. Can be binary.
    @return The record item

    @throws ValueError if message cannot be uploaded.
    """
    instance = storage.get_protocol()

    # Encrypt
    data = instance.encrypt(message, storage.public_keys, category, parties)

    # Upload to server
    api = jsonrpclib.Server(storage.host)
    record_item_id = api.add_record_item(storage.record_id, category, data)

    if not record_item_id:
        raise ValueError("Failed uploading record item")

    # Done
    return record_item_id

def decrypt(storage, record_item_id=None, record_item=None):
    """
    Decrypt a message. Message can be given or an ID can be specified. In the
    latter case, the message will be downloaded from the server first. The
    decryption is oppertunistic and will try each key in the key chain until it
    succeeds.

    @param storage Data file to work with.
    @param record_item_id ID of the (remote) record
    @param record_item Pre downloaded message
    @return Decrypted message

    @throws ValueError if message could not be downloaded
    """
    instance = storage.get_protocol()

    # Query the server for any keys
    if not record_item_id is None:
        api = jsonrpclib.Server(storage.host)
        record_item = api.get_record_item(storage.record_id, record_item_id)

        if not record_item:
            raise ValueError("Downloading record item failed")

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

def grant(storage, category, parties):
    """
    Encrypt and store a specific key on the server to be decrypted by another
    party. The sender should already have a decrypt key for the same category.

    @param storage Data file to work with.
    @param category The category of the key to store.
    @param parties List of parties allowed to decrypt the key.
    @return ID of the remote key

    @throws ValueError if key cannot be uploaded
    """
    instance = storage.get_protocol()

    # Encrypt
    key = instance.keys_to_base64((category, storage.public_keys[category]))
    data = instance.encrypt(key, storage.public_keys, category, parties)

    # Upload to server
    api = jsonrpclib.Server(storage.host)
    key_id = api.add_key(storage.record_id, category, data)

    # Verify
    if key_id == False:
        raise ValueError("Unable to upload key")

    # Done
    return key_id

def retrieve(storage, **lookups):
    """
    Naive method to import all remote keys available which can be decrypted.
    Extra lookups can be specified to filter remote keys

    @param storage Data file to work with.
    @param lookups Django ORM style lookups.
    @return List of categories where keys have been imported for

    @throws ValueError if search or retrieve failed.
    """
    instance = storage.get_protocol()

    # Query the server for any keys
    api = jsonrpclib.Server(storage.host)
    key_ids = api.find_keys(storage.record_id, lookups)

    if key_ids == False:
        raise ValueError("Could not search for remote keys")

    # Process each ID
    new_categories = []

    for key_id in key_ids:
        key = api.get_key(storage.record_id, key_id)

        # Try to decrypt the key
        success = False

        for secret_keys in storage.secret_keys.itervalues():
            try:
                data = instance.decrypt(key["data"], secret_keys)
                success = True

                break
            except (DecryptError, KeyRingError):
                # Just ignore, since this is a naive implementation just trying
                # to decrypt a key.
                continue

        if not success:
            continue

        # Store it
        if not hasattr(storage, "public_keys"):
            storage.public_keys = {}

        category, key = instance.base64_to_keys(data)
        storage.public_keys[category] = key

        # For stats
        new_categories.append(category)

    # Return number of imported keys
    return new_categories

def get_record_items(storage, record_item_ids):
    """
    Resolve a list of record items IDs from the remote server.

    @param storage Data file to work with.
    @param record_item_ids List of IDs to resolve.
    @return List of resolved record items.
    """

    api = jsonrpclib.Server(storage.host)
    return [ api.get_record_item(storage.record_id, x) for x in record_item_ids ]

def list_record_items(storage, **lookups):
    """

    @param lookups Django ORM style lookups.
    @param storage Data file to work with.
    @return List of IDs satisfying the lookup.

    @throws ValueError if search or retrieve failed.
    """

    api = jsonrpclib.Server(storage.host)
    record_item_ids = api.find_record_items(storage.record_id, lookups)

    if record_item_ids == False:
        raise ValueError("Unable to retrieve record from server")

    return record_item_ids