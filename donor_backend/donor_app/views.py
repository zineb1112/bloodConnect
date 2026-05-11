from django.shortcuts import render , redirect
from .models import DonorUser, Donor
from django.contrib.auth import authenticate , login
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Donor
import json, urllib.parse, urllib.request
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required



# Create your views here.

def index(request):
    return render(request, 'donor/index.html')

def about(request):
    return render(request, 'donor/about.html')

@login_required(login_url="loginView")
def profile(request):
    donor = Donor.objects.get(user=request.user)
    return render(request, 'donor/profile.html', {'donor': donor})

def register_view(request):
    return render(request, 'authentif/register.html')

def login_view(request):
    return render(request, 'authentif/login.html')

def reset_password_view(request):
    return render(request, 'authentif/reset.html')

def new_password_view(request):
    return render(request, 'authentif/newpassword.html')

def edit_view(request):
    return render(request, 'donor/edite_donor.html')


@login_required(login_url="loginView")
def donor_view(request): # include a subfolder if you put it inside 'donor'
    donor = Donor.objects.get(user=request.user)
    return render(request, 'donor/donor.html', {'donor': donor})  # include a subfolder if you put it inside 'donor'



#   ** API Views for Donor Registration and Login
def donor_register(request):
    print("donor_register called")

    if request.method == "POST":
        print("POST request received")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")
        print(f"Received: email={email}, username={username}, full_name={full_name}")

        if not all([email, username, password, full_name]):
            print("Missing required fields!")
            return render(request, "authentif/register.html", {
                "error": "Please fill all required fields"
            })
        
        # CHECK EMAIL
        if DonorUser.objects.filter(email=email).exists():
            return render(request, "authentif/register.html", {
                "error": "This email is already registered"
            })

        # CHECK USERNAME
        if DonorUser.objects.filter(username=username).exists():
            return render(request, "authentif/register.html", {
                "error": "This username is already taken"
            })

        # Optional fields (convert empty strings to None)
        birth_date = request.POST.get("birth_date") or None
        last_donation_date = request.POST.get("last_donation_date") or None
        phone_number = request.POST.get("phone_number") or None
        gender = request.POST.get("gender") or None
        blood_type = request.POST.get("blood_type") or None
        region = request.POST.get("region") or None
        city = request.POST.get("city") or None
        weight = request.POST.get("weight")
        weight = int(weight) if weight else None
        image_url = request.POST.get("image_url") or None
        availability = request.POST.get("availability", "on") == "on"
        print(f"Optional fields: birth_date={birth_date}, city={city}, availability={availability}")

        # Create user
        user = DonorUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"User created: {user}")

        # Create donor profile
        donor = Donor.objects.create(
            user=user,
            full_name=full_name,
            birth_date=birth_date,
            phone_number=phone_number,
            gender=gender,
            blood_type=blood_type,
            region=region,
            city=city,
            weight=weight,
            image_url=image_url,
            availability=availability,
            last_donation_date=last_donation_date
        )
        print(f"Donor profile created: {donor}")

        print("Redirecting to donor page...")

        login(request, user)
        return redirect("donor")

    print("GET request → rendering registration form")
    return render(request, "authentif/register.html")

def donor_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "authentif/login.html", {
                "error": "Please enter both email and password"
            })

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)  # Log in the user
            # Redirect to donor dashboard or homepage
            return redirect("donor")  
        else:
            return render(request, "authentif/login.html", {
                "error": "Invalid email or password"
            })

    # GET request → render login form
    return render(request, "authentif/login.html")


@require_GET
def internal_donors_api(request):
    """
    INTERNAL JSON API (no auth yet)
    URL:
      /api/donors/internal/donors/

    Query params (optional):
      blood_type=O+
      region=Souss-Massa
      city=Agadir
      available_only=1 (default) or 0
    """
    blood_type = (request.GET.get("blood_type") or "").strip()
    region = (request.GET.get("region") or "").strip()
    city = (request.GET.get("city") or "").strip()
    available_only = (request.GET.get("available_only") or "1").strip()

    qs = Donor.objects.select_related("user").all()

    if available_only == "1":
        qs = qs.filter(availability=True)

    if blood_type:
        qs = qs.filter(blood_type__iexact=blood_type)
    if region:
        qs = qs.filter(region__icontains=region)
    if city:
        qs = qs.filter(city__icontains=city)

    qs = qs.order_by("-updated_at")[:200]

    donors = []
    for d in qs:
        donors.append({
            "id": d.id,
            "full_name": d.full_name,
            "blood_type": d.blood_type,
            "region": d.region,
            "city": d.city,
            "phone_number": d.phone_number,
            "last_donation_date": d.last_donation_date.isoformat() if d.last_donation_date else None,
            "availability": bool(d.availability),
        })

    return JsonResponse({"count": len(donors), "donors": donors})


@login_required(login_url="loginView")
def donor_dashboard(request):
    """
    Donor dashboard page:
    - loads donor profile
    - fetches blood requests from Hospital internal API
    - supports filters via query params:
      /donor/?blood_type=A+&city=Agadir&status=open
    """

    donor = Donor.objects.select_related("user").filter(user=request.user).first()
    if not donor:
        messages.error(request, "No donor profile is linked to this account.")
        return redirect("loginView")

    blood_type = (request.GET.get("blood_type") or "").strip()
    city = (request.GET.get("city") or "").strip()
    status_ = (request.GET.get("status") or "").strip()

    filters = {"blood_type": blood_type, "city": city, "status": status_}

    hospital_base = getattr(settings, "HOSPITAL_SERVICE_BASE_URL", "http://hospital:8000")
    endpoint = "/api/internal/blood-requests/"
    query = {k: v for k, v in filters.items() if v}
    # default behavior: active_only=1
    query["active_only"] = "1"

    url = hospital_base.rstrip("/") + endpoint + "?" + urllib.parse.urlencode(query)

    requests_list = []
    error = None

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode())
            requests_list = payload.get("requests", [])
    except Exception:
        error = "Unable to load blood requests right now."

    return render(request, "donor/donor.html", {
        "donor": donor,
        "requests": requests_list,
        "filters": filters,
        "error": error,
    })

def donor_logout(request):
    logout(request) 
    return redirect("index") 

@login_required
def edit_donor(request):
    donor = Donor.objects.get(user=request.user)

    if request.method == "POST":
        donor.full_name = request.POST.get("full_name")
        donor.phone_number = request.POST.get("phone_number")
        donor.gender = request.POST.get("gender")
        donor.blood_type = request.POST.get("blood_type")
        donor.region = request.POST.get("region")
        donor.city = request.POST.get("city")

        weight = request.POST.get("weight")
        donor.weight = int(weight) if weight else None

        donor.availability = request.POST.get("availability") == "on"
        donor.last_donation_date = request.POST.get("last_donation_date") or None

        donor.save()

        return redirect("donor")

    return render(request, "donor/edit_donor.html", {
        "donor": donor
    })

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("new_password1")
        password2 = request.POST.get("new_password2")

        if not email or not password1 or not password2:
            return render(request, "authentif/newpassword.html", {
                "error": "All fields are required"
            })

        if password1 != password2:
            return render(request, "authentif/newpassword.html", {
                "error": "Passwords do not match"
            })

        try:
            user = DonorUser.objects.get(email=email)
            user.set_password(password1)
            user.save()
            return redirect("loginView")

        except DonorUser.DoesNotExist:
            return render(request, "authentif/newpassword.html", {
                "error": "No account found with this email"
            })

    return render(request, "authentif/newpassword.html")
