import cloudinary.models
from django.db import models
from django.db import models
from django.contrib.auth.models import User
import cloudinary


# Create your models here.
class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # photo = cloudinary.models.CloudinaryField("image", blank=True, null=True)
    photo = cloudinary.models.CloudinaryField("image", blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    latitude = models.FloatField(null=True, blank=True)  # Store latitude
    longitude = models.FloatField(null=True, blank=True)
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def __str__(self):
        return self.name

    def followers_count(self):
        return self.followers.count()  # Count the number of followers

    def following_count(self):
        return self.following.count()

    def __str__(self):
        return self.name


# Create your models here.


class Posts(models.Model):
    caption = models.CharField(max_length=100)
    post_image = cloudinary.models.CloudinaryField("image", blank=True, null=True)
    author = models.ForeignKey(User_profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption


class Comments(models.Model):
    name = models.ForeignKey(User_profile, on_delete=models.CASCADE)  # Fix this
    post_name = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment_body = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.post_name}"


class Likes(models.Model):
    user = models.ForeignKey(User_profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.post}"


class saved_posts(models.Model):
    user = models.ForeignKey(User_profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} saved {self.post}"
