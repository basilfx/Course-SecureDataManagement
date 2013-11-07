from django.db import models

# Create your models here.

class Transaction(models.Model):
	data = models.CharField(max_length=1024)
	amount_bucket = models.IntegerField()
	miliseconds_bucket = models.IntegerField()

class Client(models.Model):
	name = models.CharField(max_length=100)
	public_key = models.CharField(max_length=1024)
	sym_key_client = models.CharField(max_length=100)
	sym_key_cons = models.CharField(max_length=100)