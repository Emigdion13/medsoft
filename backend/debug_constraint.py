import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

from django.db import models

# Let's trace through the error by looking at Django source
# The error is: if len(index.name) > index.max_name_length:
# This happens in _check_indexes which is called on models

class TestModel(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='very_long_constraint_name_that_might_exceed_postgres_limit',
            )
        ]

# Check if the model has a max_name_length
print("Checking TestModel:")
for constraint in TestModel._meta.constraints:
    print(f"  Constraint: {constraint}")
    print(f"  hasattr(max_name_length): {hasattr(constraint, 'max_name_length')}")
    print(f"  type: {type(constraint)}")
    
# Now let's see what Django check code expects
from django.core import checks

# The error comes from _check_indexes in base.py
import inspect
print("\nDjango version:", models.__file__)
