from django.shortcuts import render, redirect
from django.conf import settings

from phr_cli import actions
from phr_cli.data_file import DataFile
from phr_cli.forms import SelectDataFileForm, ConnectPHRForm

from functools import wraps

import os

def data_file_required(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        data_file = request.session.get("data_file", False)

        if not data_file:
            return redirect("phr_cli.views.phr_select")

        # Execute actual function
        return func(request, *args, **kwargs)

    return _inner

def resolve_data_file(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        # Data file is ensured via @data_file_required
        data_file = os.path.join(settings.ROOT_DIR, "data", request.session["data_file"])
        data_file = DataFile(data_file, load=True)

        return func(request, data_file, *args, **kwargs)

    return _inner

@data_file_required
def index(request):
    return render(request, "index.html", locals())

def phr_select(request):
    form = SelectDataFileForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        request.session["data_file"] = form.cleaned_data["data_file"]

    return render(request, "select.html", locals())

def phr_connect(request):
    form = ConnectPHRForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Create a new data file
        data_file = form.cleaned_data["data_file"]
        data_file = os.path.join(settings.ROOT_DIR, "data", data_file)

        # Connect to server
        storage = DataFile(data_file)
        actions.connect(storage, form.cleaned_data["host"])
        storage.save()

        # Done
        return redirect("phr_cli.views.phr_select")

    return render(request, "connect.html", locals())

@data_file_required
@resolve_data_file
def phr_create(request, data_file):
    return render(request, "create.html", locals())

@data_file_required
@resolve_data_file
def phr_import(request, data_file):
    form = ImportDataFileForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        pass

    return render(request, "create.html", locals())