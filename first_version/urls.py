from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.login_view, name="login_view"),
    path("signup/", views.register, name="register"),
    path("DashBoard_view/", views.DashBoard_view, name="DashBoard_view"),
    path("create_post/", views.post_create_view, name="post_create_view"),
    path("nearby_coders/", views.show_nearby_coders, name="show_nearby_coders"),
    path("notification/", views.notification, name="notification"),
    path("show_saved_posts/", views.show_saved_posts, name="show_saved_posts"),
    path("logout/", views.Logout_view, name="Logout_view"),
    path("<str:user_id>/profile/", views.show_profile, name="show_profile"),
    path("<str:user_id>/edit/", views.edit_profile, name="edit_profile"),
    path(
        "<str:user_id>/follow_unfollow/", views.follow_unfollow, name="follow_unfollow"
    ),
    path("<int:post_id>/edit_post/", views.edit_post, name="edit_post"),
    path("<int:post_id>/delete_post/", views.delete_post, name="delete_post"),
    path("<int:post_id>/post_comment/", views.add_comment, name="add_comment"),
    path("<int:post_id>/add_like/", views.add_like, name="add_like"),
    path("<int:post_id>/save_post/", views.save_post, name="save_post"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
