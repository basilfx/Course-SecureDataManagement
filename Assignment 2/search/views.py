from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, forms, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

from search.models import *
from search.decorators import json_response

import json

"""
data = {"login_successful": False};
data = json.dumps(data, indent=4)
return HttpResponse(data,content_type='application/json')
"""

def index(request):
    return render(request, "index.html", locals())

def client_index(request):
    data = []
    for client in Client.objects.all():
        data.append(model_to_dict(client, fields=["id", "username", ""]))
    data = json.dumps(data, indent=4)
    return render(request, "client_index.html", locals())

@require_POST
@json_response
def client_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    client = Client.objects.get(user=user)
    if user is not None:
        if user.is_active:
            login(request, user)
            return {"login_successful": True, "client_id": client.id};

    return {"login_successful": False};

@require_POST
@json_response
def consultant_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    consultant = Consultant.objects.get(user=user)
    client = Client.objects.filter(consultant=consultant)[0]

    if user is not None:
        if user.is_active:
            login(request, user)
            return {"login_successful": True, "client_id": client.id, "client_name": client.name, "client_key": client.sym_key_cons }

    return {"login_successful" : False}

@json_response
def client_logout(request):
    logout(request)
    return {"logout_successful": True}

@require_POST
@json_response
def client_register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    consultant_id = request.POST.get('consultant_id')
    consultant = Consultant.objects.get(id = consultant_id)
    key = request.POST.get('key')
    print(key)
    user = User.objects.create_user(username, None, password)
    user.save()
    client_bucket = user.id - user.id % 3
    client = Client(user=user,name=username,client_bucket=client_bucket,consultant=consultant, sym_key_cons=key)
    client.save()

    return {"registered_successful": True};

@json_response
def consultant_register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    public_exp = request.POST.get('public_exp')
    public_mod = request.POST.get('public_mod')
    print(public_mod)
    user = User.objects.create_user(username, None, password)
    user.save()
    consultant = Consultant(user=user,name=username,public_exp=public_exp,public_mod=public_mod)
    consultant.save()
    print(consultant.public_mod)

    return {"registered_successful": True};

@login_required
@json_response
def transactions(request):
    user = request.user
    client_id = request.GET.get('client_id')
    client = Client.objects.get(id=client_id)
    transactions = Transaction.objects.filter(client_bucket=client.client_bucket)
    data = []
    for transaction in transactions:
        data.append(model_to_dict(transaction, fields=["id", "data"]))

    return data

@json_response
def consultants(request):
    consultants = Consultant.objects.all()
    data = []
    for consultant in consultants:
        data.append(model_to_dict(consultant, fields=["id", "name", "public_exp", "public_mod"]))

    return data

@login_required
@json_response
def client_list(request):
    user = request.user
    consultant = Consultant.objects.get(user=user)
    clients = Client.objects.filter(consultant_id=consultant.id)
    data = []

    for client in clients:
        data.append(model_to_dict(client, fields=["id", "name", "sym_key_cons"]))

    return data

@require_POST
@login_required
@json_response
def transactions_create(request):
    user = request.user
    client_id=request.POST.get('client_id')
    client = Client.objects.get(id=client_id)
    client_bucket = client.client_bucket
    id = request.POST.get('id')
    data = request.POST.get('data')
    amount_bucket = request.POST.get('amount_bucket')
    date_bucket = request.POST.get('date_bucket')

    if id == "-1" or id == "undefined":
        t = Transaction(data=data, amount_bucket=amount_bucket,date_bucket=date_bucket,client_bucket=client_bucket)
        t.save()

        return {"message": "Transaction created", "id": t.id};
    else:
        t = Transaction.objects.get(id=int(id), client_bucket=client_bucket)
        t.data = data
        t.amount_bucket = amount_bucket
        t.date_bucket = date_bucket
        t.save()

        return {"message": "Transaction updated", "id": t.id};

@require_POST
@login_required
@json_response
def transactions_delete(request):
    user = request.user
    client_id=request.POST.get('client_id')
    client = Client.objects.get(id=client_id)
    client_bucket = client.client_bucket
    id = request.POST.get('id')

    if id != "-1" or id == "undefined":
        t = Transaction.objects.get(id=int(id),client_bucket=client_bucket)
        t.delete()
        return {"message": "Transaction deleted"};
    else:
        return {"message": "Transaction not deleted"};

@login_required
@json_response
def search_amount_date(request):
    amounts = request.GET.get("amount", False)
    dates = request.GET.get("date", False)
    print(amounts)

    if not amounts and not dates:
        return Http404()

    user = request.user
    client_id=request.GET.get('client_id')
    client = Client.objects.get(id=client_id)

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

    return data