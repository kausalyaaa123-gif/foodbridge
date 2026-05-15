from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .utils import calculate_distance # Ensure you have this utility function


from datetime import timedelta
from django.utils import timezone
from httpx import request
from .utils import calculate_distance
from .models import Donation

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard') # We will create the dashboard next!
        else:
            messages.error(request, "Invalid username or password")
            
    return render(request, 'foodapp/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    # This is the page with Donate and Claim buttons
    return render(request, 'foodapp/dashboard.html')

@login_required(login_url='login')
def donate_view(request):
    if request.method == "POST":
        name = request.POST.get('food_name')
        qty = request.POST.get('quantity')
        img = request.FILES.get('food_image')
        
        # FIX: Use '0.0' as a default if the input is empty
        lat = request.POST.get('lat') or '0.0'
        lon = request.POST.get('lon') or '0.0'

        new_donation = Donation(
            donor=request.user,
            food_name=name,
            quantity=float(qty), # Convert qty to float
            food_image=img,
            latitude=float(lat), # Convert lat to float
            longitude=float(lon) # Convert lon to float
        )
        new_donation.save()
        messages.success(request, "Donation successful!")
        return redirect('dashboard')
        
    return render(request, 'foodapp/donate.html')
def claim_feed(request):
    # 1. Capture whatever comes from the URL
    lat_raw = request.GET.get('lat')
    lon_raw = request.GET.get('lon')

    # 2. Grab EVERY donation that is active (No time filter for now!)
    donations = Donation.objects.filter(is_active=True)
    
    # 3. Just for the UI: Show the distance as "Checking..." if GPS is missing
    for d in donations:
        if lat_raw and lon_raw:
            dist = calculate_distance(float(lat_raw), float(lon_raw), d.latitude, d.longitude)
            d.distance = round(dist, 2)
        else:
            d.distance = "Unknown"

    return render(request, 'foodapp/claim.html', {'donations': donations})
@login_required(login_url='login')
@require_http_methods(["POST"])
def process_claim(request, donation_id):
    if request.method == "POST":
        claimed_qty = float(request.POST.get('claimed_quantity', 0))
        donation = Donation.objects.get(id=donation_id)

        if claimed_qty > 0 and claimed_qty <= donation.quantity:
            # 1. Update the quantity in database
            donation.quantity -= claimed_qty
            
            # 2. If no food left, mark as inactive
            if donation.quantity <= 0:
                donation.is_active = False
            donation.save()

            # 3. Carbon Calculation Algorithm
            # Formula: 1kg saved = 2.5kg CO2 prevented
            carbon_saved = round(claimed_qty * 2.5, 2)

            messages.success(request, f"Successfully claimed {claimed_qty}kg! You saved {carbon_saved}kg of CO2 emissions.")
        else:
            messages.error(request, "Invalid quantity requested.")
            
    return redirect('claim')

def signup_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        # Check if user already exists
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken")
        else:
            # Create the user
            user = User.objects.create_user(username=u, password=p)
            login(request, user)
            messages.success(request, f"Welcome to FoodBridge, {u}!")
            return redirect('dashboard')
            
    return render(request, 'foodapp/signup.html')

def claim_feed(request):
    # 1. Spoilage Filter (6-hour window)
    safety_window = timezone.now() - timedelta(hours=6)
    all_donations = Donation.objects.filter(is_active=True, created_at__gte=safety_window)
    
    # 2. Get User's Current Location from the URL (sent via JavaScript)
    lat_raw = request.GET.get('lat')
    lon_raw = request.GET.get('lon')

    nearby_donations = []

    if lat_raw and lon_raw:
        user_lat = float(lat_raw)
        user_lon = float(lon_raw)

        for d in all_donations:
            # Calculate distance using your Haversine function
            dist = calculate_distance(user_lat, user_lon, d.latitude, d.longitude)
            
            # STRICT FILTER: Only 5km or less
            if dist <= 5.0:
                d.distance = round(dist, 2)
                nearby_donations.append(d)
    
    # If no GPS yet, we send an empty list or a message 
    # so the user knows they need to enable location.
    return render(request, 'foodapp/claim.html', {'donations': nearby_donations})
from django.contrib.auth.models import User
from django.contrib.auth import login

def signup_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Validation: Ensure fields aren't empty (Fixes your previous ValueError)
        if not u or not p:
            messages.error(request, "Both username and password are required.")
            return render(request, 'foodapp/signup.html')

        # Check if user already exists
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken. Please choose another.")
        else:
            # Create the user and log them in immediately
            user = User.objects.create_user(username=u, password=p)
            login(request, user)
            messages.success(request, f"Welcome to FoodBridge, {u}!")
            return redirect('dashboard') # Redirect to choice page
            
    return render(request, 'foodapp/signup.html')


# --- LOGIN VIEW ---
def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Authenticate against the database
        user = authenticate(username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'foodapp/login.html')


# --- LOGOUT VIEW ---
def logout_view(request):
    logout(request)
    return redirect('login')
