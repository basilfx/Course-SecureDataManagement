from django.conf import settings

from jsonrpc import jsonrpc_method

from phr.models import Key

@jsonrpc_method("get_attributes")
def get_attributes(request):
    """
    Retrieve all available attributes currently used in the system.

    @returns list of attributes
    """

    return settings.PHR_ATTRIBUTES

@jsonrpc_method("get_categories")
def get_categories(request):
    """
    Retrieve all available categories currently used in the system.

    @returns list of (id, category)
    """

    return settings.PHR_CATEGORIES

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