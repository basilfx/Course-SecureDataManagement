from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Transaction(models.Model):
	data = models.CharField(max_length=1024)
	amount_bucket = models.CharField(max_length=1)
	date_bucket = models.CharField(max_length=1)
	client_bucket = models.IntegerField()

class Client(models.Model):
	name = models.CharField(max_length=100)
	public_key = models.CharField(max_length=1024)
	sym_key_client = models.CharField(max_length=100)
	sym_key_cons = models.CharField(max_length=100)
	user = models.OneToOneField(User)
	client_bucket = models.IntegerField()