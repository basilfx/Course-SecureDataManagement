from django import forms
from django.conf import settings

from phr_cli.data_file import DataFile

import os
import glob

def list_data_files():
    data_files = glob.glob(os.path.join(settings.ROOT_DIR, "data", "*.json"))
    result = []

    for data_file in data_files:
        instance = DataFile(data_file, load=True)

        if hasattr(instance, "record_id"):
            result.append((
                data_file,
                "%d - %s (%s)" % (
                    instance.record_id,
                    instance.record_name,
                    instance.record_role
                )
            ))

    return result

class SelectDataFileForm(forms.Form):
    data_file = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(SelectDataFileForm, self).__init__(*args, **kwargs)
        self.fields["data_file"].choices = list_data_files()

class ConnectPHRForm(forms.Form):
    host = forms.URLField()
    key_data = forms.CharField(max_length=1024*1024)

    data_file = forms.CharField(max_length=128)

class CreatePHRForm(forms.Form):
    host = forms.URLField()
    record_name = forms.CharField(max_length=128)

    data_file = forms.CharField(max_length=128)

class EncryptForm(forms.Form):
    category = forms.ChoiceField()
    parties = forms.MultipleChoiceField()

    title = forms.CharField(max_length=128)
    message = forms.CharField(max_length=1024*1024)

    def __init__(self, categories, parties, *args, **kwargs):
        super(EncryptForm, self).__init__(*args, **kwargs)

        self.fields["category"].choices = zip(categories, categories)
        self.fields["parties"].choices = zip(parties, parties)

class GrantForm(forms.Form):
    category = forms.ChoiceField()
    parties = forms.MultipleChoiceField()
    access = forms.ChoiceField(choices=(("R", "READ"), ("W", "WRITE")))

    def __init__(self, categories, parties, *args, **kwargs):
        super(GrantForm, self).__init__(*args, **kwargs)

        self.fields["category"].choices = zip(categories, categories)
        self.fields["parties"].choices = zip(parties, parties)