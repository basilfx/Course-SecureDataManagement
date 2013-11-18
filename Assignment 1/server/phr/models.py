from django.db import models
from django.conf import settings

# Django wants (short, long) choices.
PHR_CATEGORIES = zip(settings.PHR_CATEGORIES, settings.PHR_CATEGORIES)

class Record(models.Model):
    name = models.CharField(max_length=128)

class RecordItem(models.Model):
    record = models.ForeignKey("phr.Record")
    category = models.CharField(max_length=32, choices=PHR_CATEGORIES)
    data = models.BinaryField()

class Key(models.Model):
    record = models.ForeignKey("phr.Record")
    category = models.CharField(max_length=32, choices=PHR_CATEGORIES)
    data = models.BinaryField()