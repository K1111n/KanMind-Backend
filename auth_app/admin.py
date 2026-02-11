from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.site_header = "KanMind Admin"
