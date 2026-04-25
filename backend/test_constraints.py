import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

from django.db import models

# Test UniqueConstraint in Django 5.1
uc = models.UniqueConstraint(fields=["a"], name="test")
print("UniqueConstraint attributes:", dir(uc))
print("\n__init__ signature:")
import inspect
sig = inspect.signature(models.UniqueConstraint.__init__)
print(sig)
