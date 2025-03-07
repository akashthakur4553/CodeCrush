from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import profile
from math import radians, cos, sin, asin, sqrt


# Create your views here.
def home(request):
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
            return render(request, "home.html", {"messages": messages})

        if not user_data_error:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            messages = f"Sucessfully registered {first_name}"
            new_profile = profile.objects.create(
                name=first_name, latitude=latitude, longitude=longitude
            )
            new_profile.save()
            login(request, new_user)
            return redirect("dashboard_view")

    return render(request, "home.html")


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


def find_coders_nearby(lat, lon, radius_km=1000):
    user_location = (lat, lon)
    nearby_coders = []

    for coder in profile.objects.all():
        if coder.latitude and coder.longitude:  # Ensure location is set
            coder_lat, coder_lon = (
                coder.latitude,
                coder.longitude,
            )  # (latitude, longitude)
            distance = haversine(lat, lon, coder_lat, coder_lon)

            if distance <= radius_km:
                nearby_coders.append((coder, int(distance)))

    nearby_coders.sort(key=lambda x: x[1])
    return nearby_coders


def dashboard_view(request):
    user = request.user
    myprofile = profile.objects.filter(name=user.first_name).first()  # Avoid crash
    if not myprofile:
        return render(request, "dashboard.html", {"error": "Profile not found."})

    latitude = myprofile.latitude
    longitude = myprofile.longitude
    nearby_coders = find_coders_nearby(latitude, longitude)

    return render(request, "dashboard.html", {"nearby_coders": nearby_coders})
