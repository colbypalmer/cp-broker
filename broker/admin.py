from django.contrib import admin
from models import Service, Connection, FacebookProfile


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ['name', 'url']


class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'username', 'uid', 'token')
    list_filter = ['provider']
    search_fields = ['username', 'uid', 'token']


class FacebookProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook_name', 'facebook_id')


admin.site.register(Service, ServiceAdmin)
admin.site.register(Connection, ConnectionAdmin)
admin.site.register(FacebookProfile)