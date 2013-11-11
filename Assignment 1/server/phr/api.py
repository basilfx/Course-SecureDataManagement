from django.conf import settings

from jsonrpc import jsonrpc_method

from phr.models import Key

@jsonrpc_method("get_attributes")
def get_attributes(request):
    """
    Retrieve all available attributes currently used in the system.

    Returns: list of attributes
    """

    return settings.PHR_ATTRIBUTES

@jsonrpc_method("get_categories")
def get_categories(request):
    """
    Retrieve all available categories currently used in the system.

    Returns: list of (id, category)
    """

    return settings.PHR_CATEGORIES

@jsonrpc_method("get_key")
def get_key(request, record_id, category_id):
    """
    Retrieve an encrypted key for a given record and category. The key is
    encrypted with the attributes specified by the encrypter.

    Parameters:
    record_id -- id of the records
    category_id -- id of category

    Returns: (encrypted) key if matched, else False.
    """

    try:
        return Key.objects.get(record_id=record_id, category_id=category_id)
    except:
        return False