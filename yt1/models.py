from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from moviepy.editor import VideoFileClip
from django.core.validators import FileExtensionValidator
from datetime import timedelta
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Channel(models.Model):
    cid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User,to_field='username' ,on_delete = models.CASCADE)
    channel_name = models.CharField(max_length=60)
    channel_disc = models.CharField(max_length=300)
    channel_image = models.ImageField(upload_to= 'yt1/images')
    slug = models.CharField(max_length = 150)
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.channel_name
      
class Video_uplode(models.Model):
    vid = models.AutoField(primary_key=True)
    cid = models.ForeignKey(Channel,on_delete = models.CASCADE)
    video = models.FileField(upload_to='yt1/videos' , validators=[FileExtensionValidator(allowed_extensions=['.mov', '.avi', '.mp4', '.webm', '.mkv'])])
    video_title = models.CharField(max_length=150)
    video_disc = models.CharField(max_length=500)
    video_thumbnail = models.ImageField(upload_to='yt1/thumbnails')
    video_duration = models.DurationField(null=True)
    slug = models.SlugField(max_length = 100, unique=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    catogery = models.CharField(max_length=150)
    private = models.BooleanField(default=False)

    def __str__(self):
        return  f"{self.vid} by {self.cid.cid}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created, not updated 
            super().save(*args, **kwargs)   #super(Video_uplode,self).save(*args, **kwargs) this is used before python 3

            # Check and use the value of self.vid after the initial save
            if not self.slug and self.vid:
                self.slug = slugify(str(self.vid))
                self.save(update_fields=['slug'])
        
            video_path = self.video.path
            try:
                du_seconds = VideoFileClip(video_path).duration
                du_timedelta = timedelta(seconds=du_seconds)
                self.video_duration = du_timedelta
                self.save(update_fields=['video_duration'])
            except Exception as e:
                print(f"duration problam : {e}")    
        else:
            super().save(*args, **kwargs)

class Phone_numbers(models.Model):
    collage_id = models.ForeignKey(Channel , on_delete=models.CASCADE)
    number = PhoneNumberField(unique=True, blank=False)   

    def __str__(self):
        return f'{self.collage_id} and {self.number}' 

class Verified_users(models.Model):
    uid = models.ForeignKey(User,to_field='username' ,on_delete = models.CASCADE)
    collage_id = models.ForeignKey(Channel , on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.collage_id} and {self.uid}' 
    
class ldtable(models.Model):
    vid = models.ForeignKey(Video_uplode , on_delete = models.CASCADE)
    uid = models.ForeignKey(User,to_field='username' ,on_delete = models.CASCADE) 
    like = models.BooleanField(default=None)
    dislike = models.BooleanField(default=None)

    def __str__(self):
        return f'{self.vid} and {self.uid} and {self.like} , {self.dislike}' 

