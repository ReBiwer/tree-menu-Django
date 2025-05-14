from django.contrib import admin
from .models import Menu, MenuItem

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'order')
    list_filter = ('menu',)
    search_fields = ('title',)
    ordering = ('menu', 'parent', 'order')

class MenuAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
