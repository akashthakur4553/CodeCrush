from django.contrib import admin
from .models import User_profile, Posts, Comments, Likes, saved_posts

# Register your models here.
admin.site.register(User_profile)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(Likes)
admin.site.register(saved_posts)
