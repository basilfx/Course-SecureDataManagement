from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

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

    # Form layout
    helper = FormHelper()
    helper.form_class = "form-group"
    helper.layout = Layout(
        Field("data_file"),

        FormActions(
            Submit("submit", "Select", css_class="btn-primary"),
        )
    )

    def __init__(self, *args, **kwargs):
        super(SelectDataFileForm, self).__init__(*args, **kwargs)
        self.fields["data_file"].choices = list_data_files()

class ConnectPHRForm(forms.Form):
    host = forms.URLField()
    key_data = forms.CharField(max_length=1024*1024, widget=forms.Textarea())

    # Form layout
    helper = FormHelper()
    helper.form_class = "form-group"
    helper.layout = Layout(
        Field("host"),
        Field("key_data"),
        Field("data_file"),

        FormActions(
            Submit("submit", "Connect", css_class="btn-primary"),
        )
    )

class CreatePHRForm(forms.Form):
    host = forms.URLField()
    record_name = forms.CharField(max_length=128)

    # Form layout
    helper = FormHelper()
    helper.form_class = "form-group"
    helper.layout = Layout(
        Field("host"),
        Field("record_name"),
        Field("data_file"),

        FormActions(
            Submit("submit", "Create", css_class="btn-primary"),
        )
    )

class CategoryPartiesForm(forms.Form):
    category = forms.ChoiceField()
    parties = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, storage, sub_parties_only, *args, **kwargs):
        super(CategoryPartiesForm, self).__init__(*args, **kwargs)

        categories = list(getattr(storage, "public_keys", {}).iterkeys())
        parties = storage.get_protocol().parties_to_list(sub_parties_only)

        self.fields["category"].choices = zip(*([categories] * 2))
        self.fields["parties"].choices = zip(*([parties] * 2))

class EncryptForm(CategoryPartiesForm):
    title = forms.CharField(max_length=128)
    attachment = forms.FileField(required=False)
    message = forms.CharField(max_length=1024*1024*10, widget=forms.Textarea())

    # Form layout
    helper = FormHelper()
    helper.form_class = "form-group"
    helper.layout = Layout(
        Field("category"),
        Field("parties"),
        Field("title"),
        Field("attachment"),
        Field("message"),

        FormActions(
            Submit("submit", "Create", css_class="btn-primary"),
        )
    )

    def __init__(self, storage, *args, **kwargs):
        super(EncryptForm, self).__init__(storage, False, *args, **kwargs)

class GrantForm(CategoryPartiesForm):
    category = forms.ChoiceField()
    parties = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple)
    access = forms.ChoiceField(choices=(("W", "WRITE"), ("R", "READ")))

    # Form Layout
    helper = FormHelper()
    helper.form_class = "form-group"
    helper.layout = Layout(
        Field("category"),
        Field("parties"),
        Field("access"),

        FormActions(
            Submit("submit", "Create", css_class="btn-primary"),
        )
    )

    def __init__(self, storage, *args, **kwargs):
        super(GrantForm, self).__init__(storage, True, *args, **kwargs)