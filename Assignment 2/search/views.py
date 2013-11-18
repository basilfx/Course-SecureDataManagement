from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from search.models import *
from search.forms import *
from django.contrib.auth import authenticate, login, forms, logout
import json
from django.views.decorators.csrf import csrf_exempt



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

def client_logout(request):
    logout(request)
    return redirect('search.views.client_login')

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

def transaction_search(request, query):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        data = []
        
        amount = []
        date = []
        if query[0:6] == "amount":
            query = query[7:].split(',')
            for number in query:
                print(number)
                amount.append(int(number))
                transactions = Transaction.objects.filter(client_bucket=client.client_bucket,amount_bucket__in=amount)
        else:
            query = query[5:].split(',')
            for number in query:
                date.append(int(number))
                transactions = Transaction.objects.filter(client_bucket=client.client_bucket,miliseconds_bucket__in=date)
        
        for transaction in transactions:
            data.append(model_to_dict(transaction, fields=["id", "data"]))
        data = json.dumps(data, indent=4)
        return render(request,"transaction_search.html",locals())
    else:
        return redirect('search.views.client_login')

def bla(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        transactions = Transaction.objects.filter(client_bucket=client.client_bucket)
        data = []
        for transaction in transactions:
            data.append(model_to_dict(transaction, fields=["id", "data"]))
        data = json.dumps(data, indent=4)

        return HttpResponse(data,mimetype='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,mimetype='application/json')

@csrf_exempt
def blalogin(request):
    username = request.POST.__getitem__('username')
    password = request.POST.__getitem__('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            client = Client.objects.get(user=user) 
            client_bucket = client.client_bucket
            data = {"login_successful": True};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
        else:
            data = {"login_successful": False};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,mimetype='application/json')

@csrf_exempt
def blacreatetransaction(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        client_bucket = client.client_bucket
        id = request.POST.__getitem__('id')
        data = request.POST.__getitem__('data')
        amount_bucket = request.POST.__getitem__('amount_bucket')
        date_bucket = request.POST.__getitem__('date_bucket')
        if (id == "-1"):
            t = Transaction(data=data, amount_bucket=amount_bucket,miliseconds_bucket=date_bucket,client_bucket=client_bucket)
            t.save()
            data = {"message": "Transaction created"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
        else:
            t = Transaction.objects.get(id=int(id), client_bucket=client_bucket)
            t.data = data
            t.amount_bucket = amount_bucket
            t.date_bucket = date_bucket
            t.save()
            data = {"message": "Transaction updated"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,mimetype='application/json')

@csrf_exempt
def bladeletetransaction(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        client_bucket = client.client_bucket
        id = request.POST.__getitem__('id')
        if (id != "-1"):
            t = Transaction.objects.get(id=int(id),client_bucket=client_bucket)
            t.delete()
            data = {"message": "Transaction deleted"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
        else:
            data = {"message": "Transaction not deleted"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,mimetype='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,mimetype='application/json')