from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from financial_app.models import UserProfile, Budget, Operation

admin.site.register(UserProfile)
admin.site.register(Budget, MPTTModelAdmin)
admin.site.register(Operation)
