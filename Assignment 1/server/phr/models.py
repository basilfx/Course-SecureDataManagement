from django.db import models
from django.conf import settings

class Record(models.Model):
    person = models.CharField(max_length=128)

class RecordItem(models.Model):
    record = models.ForeignKey("phr.Record")
    category = models.IntegerField(choices=settings.PHR_CATEGORIES)
    data = models.BinaryField()

class Key(models.Model):
    record = models.ForeignKey("phr.Record")
    category = models.IntegerField(choices=settings.PHR_CATEGORIES)
    key = models.BinaryField()