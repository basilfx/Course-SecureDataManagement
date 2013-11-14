from django.conf import settings

from jsonrpc import jsonrpc_method

from phr.models import Key

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

    @returns List of attributes
    """

    return settings.PHR_PARTIES

@jsonrpc_method("get_mappings")
def get_mappings(request):
    """
    Retrieve all mappings between a category and parties.

    @returns Dictionary of mappings
    """

    return settings.PHR_MAPPINGS

@jsonrpc_method("get_key")
def get_key(request, record_id, category_id):
    """
    Retrieve an encrypted key for a given record and category. The key is
    encrypted with the attributes specified by the encrypter.

    @param record_id ID of the records
    @param category_id -- ID of category
    @returns (encrypted) key if matched, else False.
    """

    try:
        return Key.objects.get(record_id=record_id, category_id=category_id)
    except:
        return False

@jsonrpc_method("create_record")
def create_record(request):
    """
    """

    pass