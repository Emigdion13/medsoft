# Django 5.1 Bug: max_name_length missing from Constraint classes

## Problem
The `_check_indexes` method in `django.db.models.base.Model` tries to access `index.max_name_length`, but this attribute is not defined on the `Constraint` class or its subclasses like `UniqueConstraint`.

## Root Cause
In Django 5.1, the check code at line 2086 of base.py does:
```python
if len(index.name) > index.max_name_length:
```

But the Constraint class doesn't have a `max_name_length` attribute.

## Solution Options

### Option 1: Patch Django in Docker container
Add a monkey-patch to the startup script that adds the missing attribute.

### Option 2: Use a different Django version
Use Django 4.2 LTS which doesn't have this check or has it implemented differently.

### Option 3: Wait for Django 5.1.x patch
The bug will be fixed in Django 5.1.2+ (released June 2024).

## Current Approach
Since we need to get the application running, let's use Option 1 - monkey-patch Django at startup.
