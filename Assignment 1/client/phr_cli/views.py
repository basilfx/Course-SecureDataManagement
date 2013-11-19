from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from phr_cli import actions
from phr_cli.data_file import DataFile
from phr_cli.forms import SelectDataFileForm, ConnectPHRForm, CreatePHRForm, \
                          EncryptForm, GrantForm

from functools import wraps

import os
import json
import uuid
import base64

def resolve_data_file(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        data_file = request.session.get("data_file", False)

        if not data_file:
            return redirect("phr_cli.views.records_select")

        # Try to load file
        try:
            data_file = os.path.join(settings.ROOT_DIR, "data", data_file)
            data_file = DataFile(data_file, load=True)
        except IOError:
            return redirect("phr_cli.views.records_select")

        # Execute actual function
        return func(request, data_file, *args, **kwargs)

    return _inner

@resolve_data_file
def index(request, data_file):
    return render(request, "index.html", locals())

@resolve_data_file
def records_share(request, data_file):
    secret_keys = []
    instance = data_file.get_protocol()

    for party, keys in data_file.secret_keys.iteritems():
        # Store record ID with the key, so the other knows the record we are
        # talking about
        data = instance.keys_to_base64((data_file.record_id, party, keys))

        secret_keys.append({
            "categories": keys.iterkeys(),
            "party": party,
            "data": data
        })

    return render(request, "records_share.html", locals())

@resolve_data_file
def record_items_create(request, data_file):
    categories = list(getattr(data_file, "public_keys", {}).iterkeys())
    form = EncryptForm(
        categories,
        data_file.parties,
        data=request.POST or None,
        files=request.FILES or None
    )

    if request.method == "POST" and form.is_valid():
        # Convert file to URI
        attachment = form.cleaned_data["attachment"]

        if attachment:
            attachment_size = attachment.size
            attachment_name = attachment.name
            attachment_data = "data:%s;base64,%s" % (
                attachment.content_type,
                base64.b64encode(attachment.read())
            )

        # Simple JSON used as container
        data = json.dumps([
            form.cleaned_data["title"],
            data_file.record_role,
            [attachment_size, attachment_name, attachment_data] if attachment else None,
            form.cleaned_data["message"]
        ])

        # Encrypt the data
        record_item_id = actions.encrypt(
            data_file,
            form.cleaned_data["category"],
            form.cleaned_data["parties"],
            data,
        )

        # Add notification
        if record_item_id:
            messages.info(request, "Record item added with ID %d" % record_item_id)
        else:
            messages.error(request, "Could not add record item")

        # Return to record list overview
        return redirect("phr_cli.views.record_items_list")

    return render(request, "record_items_create.html", locals())

@resolve_data_file
def record_items_list(request, data_file):
    record_item_ids = actions.list_record_items(data_file)
    record_items = actions.get_record_items(data_file, record_item_ids)
    instance = data_file.get_protocol()

    for record_item in record_items:
        data = actions.decrypt(data_file, record_item=record_item)

        if data:
            data = json.loads(data)
            record_item["title"] = data[0]
            record_item["sender"] = data[1]
            record_item["attachment"] = data[2]

    return render(request, "record_items_list.html", locals())

@resolve_data_file
def record_items_show(request, data_file, record_item_id):
    data = actions.decrypt(data_file, record_item_id)

    if data:
        title, sender, attachment, message = json.loads(data)

        if attachment:
            attachment_size, attachment_name, attachment_data = attachment

    return render(request, "record_items_show.html", locals())

@resolve_data_file
def keys_grant(request, data_file):
    categories = list(getattr(data_file, "public_keys", {}).iterkeys())
    form = GrantForm(
        categories,
        data_file.parties,
        data=request.POST or None
    )

    # Handle request
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["access"] == "W":
            key_id = actions.grant(data_file, form.cleaned_data["category"], form.cleaned_data["parties"])

            if key_id:
                messages.info(request, "Granted %s access to %s" % (
                    ", ".join(form.cleaned_data["parties"]),
                    form.cleaned_data["category"]
                ))
            else:
                message.error(request, "Unable to grant access")

            # Return to index page
            return redirect("phr_cli.views.index")
        elif form.cleaned_data["access"] == "R":
            messages.info(request, "Ask the record owner for a secret!")

    # Render template
    return render(request, "keys_grant.html", locals())

@resolve_data_file
def keys_retrieve(request, data_file):
    pass

def records_select(request):
    form = SelectDataFileForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        request.session["data_file"] = form.cleaned_data["data_file"]
        messages.info(request, "Welcome back!")

        return redirect("phr_cli.views.index")

    return render(request, "records_select.html", locals())

def records_create(request):
    form = CreatePHRForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Create a new data file
        new_data_file = "%s.json" % uuid.uuid4().hex
        data_file = os.path.join(settings.ROOT_DIR, "data", new_data_file)

        # Create PHR
        storage = DataFile(data_file)

        try:
            actions.create(storage, form.cleaned_data["host"], form.cleaned_data["record_name"])
        except Exception, e:
            raise e

        storage.save()

        # Done
        request.session["data_file"] = new_data_file
        return redirect("phr_cli.views.index")

    return render(request, "records_create.html", locals())

def records_connect(request):
    form = ConnectPHRForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Create a new data file
        new_data_file = "%s.json" % uuid.uuid4().hex
        data_file = os.path.join(settings.ROOT_DIR, "data", new_data_file)

        # Connect to PHR
        storage = DataFile(data_file)

        try:
            actions.connect(storage, form.cleaned_data["host"], form.cleaned_data["key_data"])
        except Exception, e:
            raise e

        storage.save()

        # Done
        request.session["data_file"] = new_data_file
        return redirect("phr_cli.views.index")

    return render(request, "records_connect.html", locals())

def logout(request):
    # Destroy session
    request.session.flush()

    # Back to select form
    return redirect("phr_cli.views.records_select")