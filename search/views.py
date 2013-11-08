from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from search.models import *
from search.forms import *
from django.contrib.auth import authenticate, login, forms
import json


from django.http import HttpResponse

# Create your views here.
def transaction_index(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        data = []
        for transaction in Transaction.objects.filter(client_bucket=client.client_bucket):
            data.append(model_to_dict(transaction, fields=["id", "data"]))
        data = json.dumps(data, indent=4)
        return render(request,"transaction_index.html",locals())
    else:
        return redirect('search.views.client_login')

def transaction_show(request, transaction_id):
    if request.user.is_authenticated():
        transaction = get_object_or_404(Transaction,id=transaction_id)
        return render(request,"transaction_show.html",locals())
    else:
        return redirect('search.views.client_login')

def transaction_new(request):
    if request.user.is_authenticated():
        user = request.user
        form = TransactionForm()
        form_hidden = HiddenForm(data=request.POST or None)
        if request.method == "POST" and form_hidden.is_valid():
            data = form_hidden.cleaned_data["data"]
            data = json.loads(data)
            instance = Transaction(**data)
            instance.save()     
            return redirect('search.views.transaction_show', transaction_id=instance.id)
        return render(request, "transaction_new.html", locals())
    else:
        return redirect('search.views.client_login')

def transaction_edit(request, transaction_id):
    if request.user.is_authenticated():
        user = request.user
        transaction = get_object_or_404(Transaction,id=transaction_id)
        form = TransactionForm()
        form_hidden = HiddenForm(data=request.POST or None)
        if request.method == "POST" and form_hidden.is_valid():
            data = form_hidden.cleaned_data["data"]
            print data
            data = json.loads(data)
            transaction.data = data["data"]
            transaction.save()
            return redirect('search.views.transaction_show', transaction_id=transaction.id)

        return render(request, "transaction_edit.html", locals())
    else:
        return redirect('search.views.client_login')

def client_index(request):
    data = []
    for client in Client.objects.all():
        data.append(model_to_dict(client, fields=["id", "username", ""]))
    data = json.dumps(data, indent=4)
    return render(request, "client_index.html", locals())

def client_login(request):
    form = forms.AuthenticationForm()
    return render(request, "client_login.html", locals())

def client_authenticate(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            #client = Client.objects.get(user=user), client_bucket=client.client_bucket
            return redirect('search.views.transaction_index')
        else:
            return HttpResponse("Disabled")
    else:
        return HttpResponse("Invalid login")

def client_register(request):
    if request.method =='POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], None, form.cleaned_data['password1'])
            user.save()
            client = Client(user=user,client_bucket=user.id)
            client.save()
            return redirect('search.views.client_login') # Redirect after POST            
    else:
        form = forms.UserCreationForm() # An unbound form
    return render(request, "client_register.html", locals())


def test(request):
    data1 = {
        "abc": [1, 2, 3],
        "deeper": {
            "nested": {
                "is": "cool"
            }
        }
    }

    data2 = []

    for transaction in Transaction.objects.all():
        data2.append(model_to_dict(transaction, fields=["id", "sender", "receiver", "amount"]))

    data1 = json.dumps(data1, indent=4)
    data2 = json.dumps(data2, indent=4)

    form_normal = TransactionForm()
    form_hidden = HiddenForm()

    if request.method == "POST" and form_hidden.is_valid():
        data = form_hidden.cleaned_data["data"]
        print data
        data = json.loads(data)
        print data

        data["bucket"]

        data = {"a": 1, "b": 2}

        Transaction(**data).save()
    return render(request, "test.html", locals())