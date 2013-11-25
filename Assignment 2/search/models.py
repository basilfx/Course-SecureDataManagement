from django.db import models

class Transaction(models.Model):
	data = models.CharField(max_length=1024)
	amount_bucket = models.CharField(max_length=1)
	date_bucket = models.CharField(max_length=1)
	client_bucket = models.IntegerField()

class Client(models.Model):
	name = models.CharField(max_length=100)
	sym_key_cons = models.CharField(max_length=1024)
	user = models.OneToOneField('auth.User')
	client_bucket = models.IntegerField()
	consultant = models.ForeignKey('Consultant', null=True)

class Consultant(models.Model):
	name = models.CharField(max_length=100)
	public_exp = models.CharField(max_length=1024)
	public_mod = models.CharField(max_length=100)
	user = models.OneToOneField('auth.User')
