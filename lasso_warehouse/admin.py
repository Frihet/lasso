from django.db import models
from django.contrib import admin
from lasso.lasso_warehandling.models import *
from lasso.lasso_warehouse.models import *

admin.site.register(Warehouse)
admin.site.register(Row)

class EmptyPalletSpaceAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(EmptyPalletSpaceAdmin, self).queryset(request)
        return qs.filter(entry_row__isnull=True)

class FilledPalletSpaceAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(FilledPalletSpaceAdmin, self).queryset(request)
        return qs.filter(entry_row__isnull=False)

class EmptyPalletSpace(PalletSpace):
    class Meta:
        proxy = True

class FilledPalletSpace(PalletSpace):
    class Meta:
        proxy = True


admin.site.register(EmptyPalletSpace, EmptyPalletSpaceAdmin)
admin.site.register(FilledPalletSpace, FilledPalletSpaceAdmin)
