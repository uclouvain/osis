from django.contrib import admin

# Register your models here.
from rules_management.models import FieldReference, FieldReferenceAdmin

admin.site.register(FieldReference, FieldReferenceAdmin)
