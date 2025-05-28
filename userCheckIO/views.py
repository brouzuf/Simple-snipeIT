from django.shortcuts import render, redirect
from django.urls import reverse # Added for named URL reversal with query params
from django.conf import settings
import requests, json
from .forms import LoginForm

# Replace with your Snipe-IT API URL and token
API_URL = settings.SNIPEIT_API_URL
API_TOKEN = settings.SNIPEIT_API_TOKEN

def login_view(request):
    form = LoginForm() # Instantiate the form
    if request.method == 'POST':
        # For this simplified "login", we'll assume the act of POSTing
        # to this view is an attempt to "log in" using the pre-configured token.
        # We need to verify the token with a test API call.
        # Let's try to fetch user details for the current token holder.
        # (Using /users endpoint as an example, Snipe-IT might have a /me endpoint)
        headers = {
            "Authorization": f"Bearer {settings.SNIPEIT_API_TOKEN}",
            "Accept": "application/json",
        }
        # Attempting to get the first user as a test. A /hardware endpoint or similar could also be used.
        # A /users/me endpoint would be ideal if Snipe-IT has one.
        test_url = f"{settings.SNIPEIT_API_URL.rstrip('/')}/users?limit=1"
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Authentication successful
                request.session['snipeit_authenticated'] = True
                request.session['snipeit_api_token'] = settings.SNIPEIT_API_TOKEN # Store token if needed for other requests
                return redirect('asset_list') # Redirect to a page for authenticated users
            else:
                # Authentication failed
                error_message = f"Snipe-IT API authentication failed. Status: {response.status_code} - {response.text}"
                return render(request, 'login.html', {'form': form, 'error_message': error_message})
        except requests.exceptions.RequestException as e:
            error_message = f"Error connecting to Snipe-IT API: {e}"
            return render(request, 'login.html', {'form': form, 'error_message': error_message})
    
    # For a GET request, just show the login page with the form
    return render(request, 'login.html', {'form': form})

def index(request):
    context = None
    return render(request, 'index.html', context)

def get_assets():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    response = requests.get(f"{API_URL}/assets", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def asset_list(request):
    # Make sure user is authenticated before showing asset list
    if not request.session.get('snipeit_authenticated'):
        # Construct the redirect URL with the 'next' parameter
        login_url_with_next = f"{reverse('login')}?next={request.path}"
        return redirect(login_url_with_next)
    assets = get_assets() # Moved after authentication check
    return render(request, 'asset_list.html', {'assets': assets})

def logout_view(request):
    if 'snipeit_authenticated' in request.session:
        del request.session['snipeit_authenticated']
    if 'snipeit_api_token' in request.session: # Also clear the token if stored
        del request.session['snipeit_api_token']
    # Redirect to a page that doesn't require authentication, e.g., the index or login page.
    return redirect('index')