from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from search.models import *
from search.forms import *
from django.contrib.auth import authenticate, login, forms, logout
import json
from django.views.decorators.csrf import csrf_exempt



from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, "index.html", locals())

def client_index(request):
    data = []
    for client in Client.objects.all():
        data.append(model_to_dict(client, fields=["id", "username", ""]))
    data = json.dumps(data, indent=4)
    return render(request, "client_index.html", locals())

def client_logout(request):
    logout(request)
    return redirect('search.views.index')

def transactions(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        transactions = Transaction.objects.filter(client_bucket=client.client_bucket)
        data = []
        for transaction in transactions:
            data.append(model_to_dict(transaction, fields=["id", "data"]))
        data = json.dumps(data, indent=4)

        return HttpResponse(data,content_type='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,content_type='application/json')

@csrf_exempt
def do_login(request):
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
            return HttpResponse(data,content_type='application/json')
        else:
            data = {"login_successful": False};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,content_type='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,content_type='application/json')

@csrf_exempt
def createTransaction(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        client_bucket = client.client_bucket
        id = request.POST.__getitem__('id')
        data = request.POST.__getitem__('data')
        amount_bucket = request.POST.__getitem__('amount_bucket')
        date_bucket = request.POST.__getitem__('date_bucket')
        if id == "-1" or id == "undefined":
            t = Transaction(data=data, amount_bucket=amount_bucket,date_bucket=date_bucket,client_bucket=client_bucket)
            t.save()
            data = {"message": "Transaction created"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,content_type='application/json')
        else:
            t = Transaction.objects.get(id=int(id), client_bucket=client_bucket)
            t.data = data
            t.amount_bucket = amount_bucket
            t.date_bucket = date_bucket
            t.save()
            data = {"message": "Transaction updated"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,content_type='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,content_type='application/json')

@csrf_exempt
def deleteTransaction(request):
    if request.user.is_authenticated():
        user = request.user
        client = Client.objects.get(user=user)
        client_bucket = client.client_bucket
        id = request.POST.__getitem__('id')
        if id != "-1" or id == "undefined":
            t = Transaction.objects.get(id=int(id),client_bucket=client_bucket)
            t.delete()
            data = {"message": "Transaction deleted"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,content_type='application/json')
        else:
            data = {"message": "Transaction not deleted"};
            data = json.dumps(data, indent=4)
            return HttpResponse(data,content_type='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,content_type='application/json')

@csrf_exempt
def register(request):
    username = request.POST.__getitem__('username')
    password = request.POST.__getitem__('password')
    print request.POST
    user = User.objects.create_user(username, None, password)
    user.save()
    client_bucket = user.id - user.id % 3
    client = Client(user=user,client_bucket=client_bucket)
    client.save()
    data = {"registered_successful": True};
    data = json.dumps(data, indent=4)
    return HttpResponse(data,content_type='application/json')

def search_amount_date(request):
    if request.user.is_authenticated():

        amounts = request.GET.get("amount", False)
        dates = request.GET.get("date", False)
        print amounts

        if not amounts and not dates:
            return

        user = request.user
        client = Client.objects.get(user=user)

        if amounts and dates:
            query = amounts.split(',')
            amount_list = []
            for number in query:
                amount_list.append(number)
            query = dates.split(',')
            date_list = []
            for number in query:
                date_list.append(number)
            transactions = Transaction.objects.filter(client_bucket=client.client_bucket,amount_bucket__in=amount_list, date_bucket__in=date_list)
        elif amounts:
            query = amounts.split(',')
            amount_list = []
            for number in query:
                amount_list.append(number)
            transactions = Transaction.objects.filter(client_bucket=client.client_bucket,amount_bucket__in=amount_list)
        else:
            query = dates.split(',')
            date_list = []
            for number in query:
                date_list.append(number)
            transactions = Transaction.objects.filter(client_bucket=client.client_bucket,date_bucket__in=date_list)

        data = []
        for transaction in transactions:
            data.append(model_to_dict(transaction, fields=["id", "data"]))
        data = json.dumps(data, indent=4)

        return HttpResponse(data,content_type='application/json')
    else:
        data = {"login_successful": False};
        data = json.dumps(data, indent=4)
        return HttpResponse(data,content_type='application/json')