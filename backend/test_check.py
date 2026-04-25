import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

from django.db import models

# Test to see what attributes UniqueConstraint has for name checking
uc = models.UniqueConstraint(fields=["a"], name="test")
print("Checking max_name_length attribute:")
print(f"  hasattr(uc, 'max_name_length'): {hasattr(uc, 'max_name_length')}")
print(f"  dir: {[x for x in dir(uc) if 'name' in x.lower() or 'check' in x.lower()]}")

# Check what the error is about - Django's check code
import django
from django.db.models import BaseConstraint

print("\nBaseConstraint has max_name_length:", hasattr(BaseConstraint, 'max_name_length'))
