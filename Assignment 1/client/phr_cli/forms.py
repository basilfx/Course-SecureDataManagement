from django import forms
from django.conf import settings

from phr_cli.data_file import DataFile

import os
import glob

def list_data_files():
    data_files = glob.glob(os.path.join(settings.ROOT_DIR, "data", "*.json"))
    result = []

    for data_file in data_files:
        instance = DataFile(data_file)

        if hasattr(instance, "record_id"):
            result.append((
                data_file,
                getattr(instance, "record_name", instance.record_id)
            ))

    return result

class SelectDataFileForm(forms.Form):
    data_file = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(SelectDataFileForm, self).__init__(*args, **kwargs)

        # Set choices
        self.fields["data_file"].choices = list_data_files()

class ConnectPHRForm(forms.Form):
    host = forms.URLField(required=True)
    data_file = forms.CharField(max_length=128)