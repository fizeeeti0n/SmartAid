from django.contrib import admin
from .models import StudyGroup, GroupMembership, GroupMessage

# Register your models here.
admin.site.register(StudyGroup)
admin.site.register(GroupMembership)
admin.site.register(GroupMessage)
