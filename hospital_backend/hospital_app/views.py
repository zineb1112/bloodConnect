from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from hospital_app.forms import HospitalSignUpForm
from hospital_app.models import HospitalUser, Hospital, BloodRequest
import grpc
import json, urllib.parse, urllib.request

# Import the generated stubs from the grpc directory
# NOTE: The import path depends on your exact project structure.
# This assumes the grpc folder is directly importable from the project root.
from hospital_project.grpc import ai_pb2
from hospital_project.grpc import ai_pb2_grpc
from hospital_project.grpc import forecasting_pb2
from hospital_project.grpc import forecasting_pb2_grpc
from .models import Hospital

def test_ai_connection(request):
    """
    Attempts to connect to the AI Service via gRPC and calls HealthCheck.
    """
    target = settings.AI_SERVICE_TARGET # This should be 'ai_service:50051' in Docker
    
    try:
        # Create an insecure channel to the AI service
        with grpc.insecure_channel(target) as channel:
            # Create a stub (client)
            stub = ai_pb2_grpc.PredictionServiceStub(channel)
            
            # Call the HealthCheck method
            response = stub.HealthCheck(ai_pb2.TestRequest(ping="Hospital ping"))
            
            return JsonResponse({
                'status': 'SUCCESS',
                'grpc_target': target,
                'ai_service_response': response.status
            })

    except grpc.RpcError as e:
        return JsonResponse({
            'status': 'FAILURE',
            'grpc_target': target,
            'error_code': e.code().name,
            'error_details': e.details()
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'FATAL_ERROR',
            'error': str(e)
        }, status=500)

def login_view(request):
    """
    Handle user login for hospitals only.
    GET: Display the login form
    POST: Authenticate and log in the user (hospital only)
    """
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'donor')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if user selected hospital account type
        if user_type != 'hospital':
            return render(request, 'hospital_app/autentif/login.html', {
                'error': 'Hospital login only. Please select Hospital account type.'
            })
        
        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'hospital_app/autentif/login.html', {
                'error': 'Invalid email or password'
            })
    
    return render(request, 'hospital_app/autentif/login.html')

def reset_password_page(request):
    """
    Handle password reset request.
    GET: Display the reset password form
    POST: Verify email and store in session, redirect to newpassword page
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the email exists in the database
        try:
            user = HospitalUser.objects.get(email=email)
            # Store email in session for verification
            request.session['reset_email'] = email
            return redirect('newpassword')
        except HospitalUser.DoesNotExist:
            return render(request, 'hospital_app/autentif/reset.html', {
                'error': 'Email not found in our system'
            })
    
    return render(request, 'hospital_app/autentif/reset.html')

def newpassword_page(request):
    """
    Handle setting new password.
    GET: Display the new password form
    POST: Validate passwords and update user password
    """
    # Check if email is in session (user came from reset page)
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('reset')
    
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Validate passwords match
        if new_password1 != new_password2:
            return render(request, 'hospital_app/autentif/newpassword.html', {
                'error': 'Passwords do not match'
            })
        
        # Validate password is not empty
        if not new_password1 or len(new_password1) < 6:
            return render(request, 'hospital_app/autentif/newpassword.html', {
                'error': 'Password must be at least 6 characters long'
            })
        
        try:
            # Get the user and update password
            user = HospitalUser.objects.get(email=reset_email)
            user.set_password(new_password1)
            user.save()
            
            # Clear session
            del request.session['reset_email']
            
            # Redirect to login with success message
            return render(request, 'hospital_app/autentif/login.html', {
                'success': 'Password reset successfully. Please log in with your new password.'
            })
        except HospitalUser.DoesNotExist:
            return redirect('reset')
    
    return render(request, 'hospital_app/autentif/newpassword.html')

@login_required(login_url="login")
def dashboard(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "No hospital profile associated with this account.")
        return redirect("login")

    # Count requests for this hospital (adjust status if you want different meaning)
    pending_requests_count = BloodRequest.objects.filter(
        hospital=hospital,
        status="open"
    ).count()

    return render(request, "hospital_app/hospital/dashboard.html", {
        "hospital": hospital,
        "pending_requests_count": pending_requests_count,
    })

def logout_view(request):
    """
    Handle user logout.
    Logs out the user and redirects to the login page.
    """
    logout(request)
    return redirect('login')

def signup_page(request):
    """
    Handle hospital signup.
    GET: Display the signup form
    POST: Process signup and create hospital account, then redirect to login
    """
    if request.method == 'POST':
        form = HospitalSignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            hospital_name = form.cleaned_data.get('hospital_name')
            hospital_phone = form.cleaned_data.get('hospital_phone')
            hospital_region = form.cleaned_data.get('hospital_region')
            hospital_city = form.cleaned_data.get('hospital_city')
            hospital_address = form.cleaned_data.get('hospital_address')
            
            # Create the HospitalUser
            user = HospitalUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create hospital profile
            Hospital.objects.create(
                user=user,
                name=hospital_name,
                phone=hospital_phone,
                region=hospital_region,
                city=hospital_city,
                address=hospital_address
            )
            
            # Redirect to login page without auto-login
            return redirect('login')
        else:
            return render(request, 'hospital_app/autentif/signup.html', {'form': form, 'errors': form.errors})
    else:
        form = HospitalSignUpForm()
    
    return render(request, 'hospital_app/autentif/signup.html', {'form': form})

#H: passes the forcasting data to the html interface
def forcast_interface(request):
    # Get hospital information if user is logged in
    from django.utils.safestring import mark_safe
    import json
    
    hospital_info = None
    hospital_info_json = 'null'
    if request.user.is_authenticated:
        try:
            hospital = Hospital.objects.get(user=request.user)
            hospital_info = {
                'name': hospital.name or '',
                'city': hospital.city or '',
                'region': hospital.region or ''
            }
            hospital_info_json = mark_safe(json.dumps(hospital_info))
        except Hospital.DoesNotExist:
            pass
    
    return render(request, 'hospital_app/hospital/forcast.html', {
        'hospital_info': hospital_info,
        'hospital_info_json': hospital_info_json
    })


#H: forcasting the blood types needed 
@require_http_methods(["GET", "POST"])
def get_forecast(request):
    """
    API endpoint to get blood demand forecast predictions.
    If user is logged in, uses their hospital's city/region.
    Otherwise, accepts city and region as POST parameters.
    """
    target = settings.AI_SERVICE_TARGET
    
    # Try to get city and region from logged-in user's hospital
    city = None
    region = None
    
    if request.user.is_authenticated:
        try:
            hospital = Hospital.objects.get(user=request.user)
            city = hospital.city
            region = hospital.region
        except Hospital.DoesNotExist:
            pass
    
    # If not available from user, try to get from request parameters
    if not city or not region:
        if request.method == 'POST':
            city = request.POST.get('city')
            region = request.POST.get('region')
        else:
            city = request.GET.get('city')
            region = request.GET.get('region')
    
    if not city or not region:
        return JsonResponse({
            'status': 'ERROR',
            'message': 'City and region are required. Please provide them or ensure your hospital profile is complete.'
        }, status=400)
    
    try:
        # Create an insecure channel to the AI service
        with grpc.insecure_channel(target) as channel:
            # Create a stub (client) for forecasting service
            stub = forecasting_pb2_grpc.ForecastingServiceStub(channel)
            
            # Create the request
            forecast_request = forecasting_pb2.ForecastRequest(
                city=city,
                region=region
            )
            
            # Call the PredictNextMonth method
            response = stub.PredictNextMonth(forecast_request, timeout=10)
            
            # Format the response
            forecasts = []
            for forecast in response.forecasts:
                forecasts.append({
                    'blood_type': forecast.blood_type,
                    'predicted_quantity': round(forecast.predicted_quantity, 2),
                    'confidence': round(forecast.confidence, 2)
                })
            
            # Sort by predicted quantity (descending)
            forecasts.sort(key=lambda x: x['predicted_quantity'], reverse=True)
            
            return JsonResponse({
                'status': 'SUCCESS',
                'city': response.city,
                'region': response.region,
                'month': response.month,
                'forecasts': forecasts
            })
    
    except grpc.RpcError as e:
        return JsonResponse({
            'status': 'FAILURE',
            'error_code': e.code().name,
            'error_details': e.details(),
            'message': f'Failed to get forecast: {e.details()}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'FATAL_ERROR',
            'error': str(e),
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=500)


@login_required(login_url="login")
def post_request_page(request):
    """
    Create/view blood requests for the logged-in hospital.

    Logic:
    - Deadline defaults to today + DEFAULT_DEADLINE_DAYS if not provided.
    - Deadline cannot be in the past.
    - Auto-expire open requests whose deadline has passed.
    - Cleanup: delete fulfilled/expired requests older than RETENTION_DAYS (set to 0 for instant delete).
    - Keeps form_values aligned with post_request.html (date must be YYYY-MM-DD string).
    """

    # ---- Policy knobs (adjust freely) ----
    DEFAULT_DEADLINE_DAYS = 7
    MAX_DEADLINE_DAYS = 90
    RETENTION_DAYS = 30  # set to 0 to delete expired/fulfilled immediately; set None to disable deletion
    # --------------------------------------

    today = timezone.localdate()

    # Get hospital profile
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "No hospital profile associated with this account.")
        return redirect("dashboard")

    # 1) Auto-expire any open requests past deadline
    BloodRequest.objects.filter(
        hospital=hospital,
        status="open",
        deadline__isnull=False,
        deadline__lt=today
    ).update(status="expired")

    # 2) Cleanup old fulfilled/expired requests (safe retention)
    if RETENTION_DAYS is not None:
        cutoff = today - timedelta(days=RETENTION_DAYS)

        BloodRequest.objects.filter(hospital=hospital).filter(
            Q(status__in=["fulfilled", "expired"]) &
            (
                Q(deadline__lt=cutoff) |
                Q(deadline__isnull=True, request_date__date__lt=cutoff)
            )
        ).delete()

    # For repopulating the form after validation errors
    form_values = {}

    if request.method == "POST":
        blood_type = (request.POST.get("blood_type") or "").strip()
        quantity_raw = (request.POST.get("quantity_needed") or "").strip()
        deadline_value = (request.POST.get("deadline") or "").strip()
        description = (request.POST.get("description") or "").strip()

        # Preserve user input for re-render
        form_values = {
            "blood_type": blood_type,
            "quantity_needed": quantity_raw,
            "deadline": deadline_value,  # keep string for <input type="date">
            "description": description,
        }

        errors = []

        # Validate blood_type
        if not blood_type:
            errors.append("Blood type is required.")

        # Validate quantity
        try:
            quantity_needed = int(quantity_raw)
            if quantity_needed <= 0:
                errors.append("Number of units must be a positive number.")
        except (TypeError, ValueError):
            quantity_needed = None
            errors.append("Number of units must be a valid number.")

        # Deadline rules
        # - If blank: set default today + DEFAULT_DEADLINE_DAYS
        # - Else parse & validate
        if deadline_value:
            try:
                deadline = datetime.strptime(deadline_value, "%Y-%m-%d").date()
            except ValueError:
                deadline = None
                errors.append("Deadline must be a valid date (YYYY-MM-DD).")
        else:
            deadline = today + timedelta(days=DEFAULT_DEADLINE_DAYS)
            # update form_values so UI shows the defaulted date
            form_values["deadline"] = deadline.strftime("%Y-%m-%d")

        if deadline:
            if deadline < today:
                errors.append("Deadline cannot be in the past.")
            if deadline > today + timedelta(days=MAX_DEADLINE_DAYS):
                errors.append(f"Deadline cannot be more than {MAX_DEADLINE_DAYS} days from today.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            BloodRequest.objects.create(
                hospital=hospital,
                blood_type=blood_type,
                quantity_needed=quantity_needed,
                deadline=deadline,
                description=description or None,
                status="open"
            )
            messages.success(request, "Blood request submitted successfully!")
            form_values = {}

    # Show latest requests (after cleanup & possible insert)
    requests_list = BloodRequest.objects.filter(hospital=hospital).order_by("-request_date")

    return render(
        request,
        "hospital_app/hospital/post_request.html",
        {
            "requests": requests_list,
            "form_values": form_values,
            "today": today,  # template can use this for min=... if desired
        }
    )

def campaign_page(request):
    return render(request, 'hospital_app/hospital/campaign.html')


@login_required(login_url="login")
def profile_page(request):
    """
    View + update hospital profile.
    Updates Hospital fields and optionally HospitalUser password.
    """
    try:
        hospital = Hospital.objects.select_related("user").get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "No hospital profile associated with this account.")
        return redirect("dashboard")

    if request.method == "POST":
        hospital_name = (request.POST.get("hospital_name") or "").strip()
        address = (request.POST.get("address") or "").strip()
        region = (request.POST.get("region") or "").strip()
        new_password = (request.POST.get("password") or "").strip()

        errors = []

        if not hospital_name:
            errors.append("Hospital name is required.")
        if not address:
            errors.append("Address is required.")
        if not region:
            errors.append("Region is required.")

        # If password provided, validate it (simple rule; you can strengthen later)
        if new_password and len(new_password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if errors:
            for err in errors:
                messages.error(request, err)
        else:
            # Update Hospital fields
            hospital.name = hospital_name
            hospital.address = address
            hospital.region = region
            hospital.save()

            # Update password if requested
            if new_password:
                hospital.user.set_password(new_password)
                hospital.user.save()

                # Important: changing password invalidates the session in many setups.
                # Easiest behavior: force re-login for security.
                logout(request)
                messages.success(request, "Profile updated. Please log in again with your new password.")
                return redirect("login")

            messages.success(request, "Profile updated successfully!")
            return redirect("profile")

    return render(request, "hospital_app/hospital/profile.html", {
        "hospital": hospital
    })


@login_required(login_url="login")
def donors_page(request):
    """
    Hospital donors page:
    fetch donors from Donor Service internal endpoint.
    """
    # filters from query params
    blood_type = (request.GET.get("blood_type") or "").strip()
    region = (request.GET.get("region") or "").strip()
    city = (request.GET.get("city") or "").strip()
    BLOOD_TYPES = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
    
    filters = {"blood_type": blood_type, "region": region, "city": city, "available_only": "1"}
    query = {k: v for k, v in filters.items() if v}

    donor_base = getattr(settings, "DONOR_SERVICE_BASE_URL", "http://donor:8000")
    url = donor_base.rstrip("/") + "/api/donors/internal/donors/"
    if query:
        url += "?" + urllib.parse.urlencode(query)

    donors = []
    error = None

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode())
            donors = payload.get("donors", [])
    except Exception as e:
        error = "Unable to load donors right now."

    return render(request, "hospital_app/hospital/donors.html", {
        "donors": donors,
        "filters": filters,
        "error": error,
        "blood_types": BLOOD_TYPES,
    })


@require_GET
def internal_blood_requests_api(request):
    """
    INTERNAL JSON API for Donor Service (no auth for now)
    URL:
      /api/internal/blood-requests/

    Query params (optional):
      - blood_type=A+
      - city=Agadir
      - region=Souss-Massa
      - status=open|fulfilled|expired
      - active_only=1 (default) -> returns only open + not expired by deadline
    """

    blood_type = (request.GET.get("blood_type") or "").strip()
    city = (request.GET.get("city") or "").strip()
    region = (request.GET.get("region") or "").strip()
    status_ = (request.GET.get("status") or "").strip()
    active_only = (request.GET.get("active_only") or "1").strip()

    qs = BloodRequest.objects.select_related("hospital").all()

    if blood_type:
        qs = qs.filter(blood_type__iexact=blood_type)
    if city:
        qs = qs.filter(hospital__city__icontains=city)
    if region:
        qs = qs.filter(hospital__region__icontains=region)
    if status_:
        qs = qs.filter(status__iexact=status_)

    # Default: only active open requests (not expired by deadline)
    if active_only == "1":
        today = timezone.localdate()
        qs = qs.filter(status="open").exclude(deadline__lt=today)

    qs = qs.order_by("-request_date")[:200]

    requests_payload = []
    for r in qs:
        requests_payload.append({
            "id": r.id,
            "blood_type": r.blood_type,
            "quantity_needed": r.quantity_needed,
            "status": r.status,
            "deadline": r.deadline.isoformat() if r.deadline else None,
            "request_date": r.request_date.isoformat() if getattr(r, "request_date", None) else None,
            "description": r.description,
            "hospital": {
                "name": r.hospital.name,
                "city": r.hospital.city,
                "region": r.hospital.region,
                "phone": r.hospital.phone,
                "address": getattr(r.hospital, "address", None),
            }
        })

    return JsonResponse({"count": len(requests_payload), "requests": requests_payload})

