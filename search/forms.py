from django import forms
from search.models import Transaction, Client

class HiddenForm(forms.Form):
    data = forms.CharField()

class TransactionForm(forms.Form):
    amount = forms.CharField()
    sender = forms.CharField()
    receiver = forms.CharField()
    description = forms.CharField()

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name","public_key", "sym_key_client", "sym_key_cons"]

