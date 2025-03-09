from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User_profile, Posts, Comments, Likes, saved_posts
from math import radians, cos, sin, asin, sqrt
from django.db.models import Count


# Create your views here.
def register(request):
    # print(
    #     "hello i ma registration modeule----------------------------------------------------------------------------------------------------------------------------"
    # )
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        username = request.POST["username"]
        latitude = request.POST["latitude"]
        longitude = request.POST["longitude"]
        user_data_error = False
        if User.objects.filter(username=username).exists():
            messages = "username already exists"
            user_data_error = True
        if User.objects.filter(email=email).exists():
            messages = "Email already exists"
            user_data_error = True
        if user_data_error:
            return render(request, "register.html", {"messages": messages})

        if not user_data_error:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            messages = f"Sucessfully registered {first_name}"
            new_profile = User_profile.objects.create(
                name=first_name,
                user=new_user,
                email=email,
                latitude=latitude,
                longitude=longitude,
            )
            new_profile.save()
            return redirect("login_view")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("DashBoard_view")
        else:
            messages = "Invalid Login Credentials"
            return render(request, "login.html", {"messages": messages})

    return render(request, "login.html")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return R * c


def find_coders_nearby(lat, lon, radius_km=10000, current_user=None):
    nearby_coders = []

    # Exclude current user
    coders = (
        User_profile.objects.exclude(user=current_user)
        .exclude(latitude=None)
        .exclude(longitude=None)
    )

    for coder in coders:
        distance = haversine(lat, lon, coder.latitude, coder.longitude)

        if distance <= radius_km:
            nearby_coders.append((coder, int(distance)))

    nearby_coders.sort(key=lambda x: x[1])
    return nearby_coders


@login_required
def DashBoard_view(request):

    profile = User_profile.objects.filter(user=request.user).first()
    user = request.user
    # Avoid crash
    if not profile:
        return render(request, "dashboard.html", {"error": "Profile not found."})

    latitude = profile.latitude
    longitude = profile.longitude
    nearby_coders = find_coders_nearby(latitude, longitude, current_user=request.user)
    posts = (
        Posts.objects.annotate(
            like_count=Count("likes"), comment_count=Count("comments")
        )
        .prefetch_related("comments_set")
        .order_by("-created_at")
    )

    liked_posts = []
    comments_dict = {}
    for post in posts:
        post.likes_counting = Likes.objects.filter(post=post).count()
        post.comments = Comments.objects.filter(post_name=post)
        if Likes.objects.filter(post=post, user=profile).exists():
            liked_posts.append(post.id)
    saved_post = saved_posts.objects.filter(user=profile)

    saved_posti = []
    for post in saved_post:
        saved_posti.append(post.post.id)

    return render(
        request,
        "DashBoard.html",
        {
            "user_profile": profile,
            "nearby_coders": nearby_coders,
            "posts": posts,
            "liked_posts": liked_posts,
            "comments_dict": comments_dict,
            "saved_posts": saved_posti,
        },
    )


@login_required
def post_create_view(request):
    if request.method == "POST":
        caption = request.POST["caption"]
        post_image = request.FILES["post_image"]
        user = User_profile.objects.filter(user=request.user).first()
        new_post = Posts.objects.create(
            caption=caption, post_image=post_image, author=user
        )
        new_post.save()
        return redirect("DashBoard_view")


@login_required
def show_nearby_coders(request):
    profile = User_profile.objects.filter(user=request.user).first()
    user = request.user
    # Avoid crash
    if not profile:
        return render(request, "dashboard.html", {"error": "Profile not found."})

    latitude = profile.latitude
    longitude = profile.longitude
    nearby_coders = find_coders_nearby(latitude, longitude, current_user=request.user)
    comments = Comments.objects.all()
    likes = Likes.objects.all()

    return render(
        request,
        "show_nearby_coders.html",
        {"nearby_coders": nearby_coders, "comments": comments, "likes": likes},
    )


@login_required
def show_profile(request, user_id):
    profile = get_object_or_404(User_profile, pk=user_id)
    # profile = User_profile.objects.filter(user).first()
    posts = Posts.objects.filter(author=profile)
    return render(
        request, "profile_show.html", {"user_profile": profile, "posts": posts}
    )


@login_required
def edit_profile(request, user_id):
    profile = get_object_or_404(User_profile, pk=user_id, user=request.user)
    if request.method == "POST":
        profile.name = request.POST["name"]
        profile.email = request.POST["email"]
        profile.latitude = request.POST["latitude"]
        profile.longitude = request.POST["longitude"]
        if "photo" in request.FILES:
            profile.photo = request.FILES["photo"]
        profile.save()
        return redirect("show_profile", user_id=user_id)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.method == "POST":
        post.caption = request.POST.get("caption", post.caption)
        if "post_image" in request.FILES:
            post.post_image = request.FILES["post_image"]
        post.save()
        return redirect("DashBoard_view")  # Redirect back after editing


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("DashBoard_view")


@login_required
def add_comment(request, post_id):
    if request.htmx:
        print("got a htmx request.......................................")
        post = get_object_or_404(Posts, id=post_id)
        profile = get_object_or_404(User_profile, user=request.user)

        comment = request.POST.get("comment")
        new_comment = Comments.objects.create(
            comment_body=comment, post_name=post, name=profile
        )
        new_comment.save()
        post.comments = Comments.objects.filter(post_name=post)
        post.comments_counting = Comments.objects.filter(post_name=post).count()
        return render(request, "snippets/comment_section.html", {"post": post})

    return redirect("DashBoard_view")


# @login_required
# def add_like(request, post_id):
#     liked_posts = []
#     posts = get_object_or_404(Posts, id=post_id)
#     profile = get_object_or_404(User_profile, user=request.user)
#     for post in posts:

#         if Likes.objects.filter(post=post, user=profile).exists():
#             liked_posts.append(post.id)
#     if request.htmx:
#         post = get_object_or_404(Posts, id=post_id)
#         profile = get_object_or_404(User_profile, user=request.user)
#         new_like, created = Likes.objects.get_or_create(user=profile, post=post)
#         if not created:
#             new_like.delete()
#         print("hello world...........................................................")
#         render(request, "snippets/like_section.html", {"liked_posts": liked_posts})

#     return redirect("DashBoard_view")


@login_required
def add_like(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    profile = get_object_or_404(User_profile, user=request.user)

    like, created = Likes.objects.get_or_create(user=profile, post=post)

    if not created:
        like.delete()  # Unlike the post if already liked

    if request.htmx:
        liked_posts = Likes.objects.filter(user=profile).values_list(
            "post_id", flat=True
        )
        like_count = Likes.objects.filter(post=post).count()
        return render(
            request,
            "snippets/like_section.html",
            {"post": post, "liked_posts": liked_posts, "like_count": like_count},
        )

    return redirect("DashBoard_view")


@login_required
def notification(request):
    comments = Comments.objects.all()
    likes = Likes.objects.all()
    return render(request, "notification.html", {"comments": comments, "likes": likes})


@login_required
def follow_unfollow(request, user_id):
    current_user = get_object_or_404(User_profile, user=request.user)
    user_to_follow = get_object_or_404(User_profile, pk=user_id)

    if user_to_follow in current_user.following.all():
        current_user.following.remove(user_to_follow)
    else:
        current_user.following.add(user_to_follow)

    return redirect("DashBoard_view")


@login_required
def show_saved_posts(request):
    current_user = get_object_or_404(User_profile, user=request.user)
    saved_post = saved_posts.objects.filter(user=current_user)

    return render(request, "saved_posts.html", {"saved_posts": saved_post})


def Logout_view(request):
    logout(request)
    return redirect("login_view")


def save_post(request, post_id):
    if request.htmx:
        post = get_object_or_404(Posts, id=post_id)
        current_user = get_object_or_404(User_profile, user=request.user)
        saved_postu = saved_posts.objects.filter(user=current_user)

        if saved_posts.objects.filter(user=current_user).filter(post=post).exists():
            saved_posts.objects.filter(user=current_user).filter(post=post).delete()
        else:
            saved_poste = saved_posts.objects.create(post=post, user=current_user)
            saved_poste.save()
        saved_posti = []
        for saved_postss in saved_postu:
            saved_posti.append(saved_postss.post.id)
        return render(
            request,
            "snippets/savepost_section.html",
            {"saved_posts": saved_posti, "post": post},
        )
        # return render(request, "snippets/savepost_section.html")
    return redirect("DashBoard_view")


# @login_required
# def save_post(request, post_id):
#     if request.htmx:
#         post = get_object_or_404(Posts, id=post_id)
#         current_user = get_object_or_404(User_profile, user=request.user)

#         # Check if the post is already saved
#         if saved_posts.objects.filter(user=current_user, post=post).exists():
#             saved_posts.objects.filter(user=current_user, post=post).delete()
#         else:
#             saved_posts.objects.create(post=post, user=current_user)

#         # Get the updated saved posts
#         saved_post_ids = saved_posts.objects.filter(user=current_user).values_list(
#             "post_id", flat=True
#         )

#         return render(
#             request,
#             "snippets/savepost_section.html",
#             {"saved_posts": saved_post_ids, "post": post},
#         )

#     return redirect("DashBoard_view")
