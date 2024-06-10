from django.contrib import admin
from .models import Channel, Video_uplode ,Phone_numbers,Verified_users, ldtable

# Register your models here.
class VideoUplodeAdmin(admin.ModelAdmin):
    list_display = ['upload_time'] 
admin.site.register(Channel)
admin.site.register(Video_uplode , VideoUplodeAdmin)
admin.site.register(Phone_numbers)
admin.site.register(Verified_users)
admin.site.register(ldtable)