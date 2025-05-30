from django.shortcuts import render, redirect
from django.urls import reverse # Added for named URL reversal with query params
from django.conf import settings
import requests, json
from django.http import HttpResponse # Added for potential intermediate use
from django.contrib import messages # Added for Django messaging framework
from .forms import LoginForm, EmployeeNumberForm, AssignAssetForm, UnassignAssetForm

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
            "Authorization": f"Bearer {API_TOKEN}",
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
                request.session['snipeit_api_token'] = API_TOKEN # Store token if needed for other requests
                messages.success(request, "Login successful.") # Optional: Add a success message
                return redirect('index') # Redirect to the main index page
            else:
                # Authentication failed
                # error_message = f"Snipe-IT API authentication failed. Status: {response.status_code} - {response.text}"
                # Using Django messages for error feedback on login page itself.
                messages.error(request, f"Snipe-IT API authentication failed. Status: {response.status_code} - {response.text}")
                return render(request, 'login.html', {'form': form}) # Re-render login form with error
        except requests.exceptions.RequestException as e:
            # error_message = f"Error connecting to Snipe-IT API: {e}"
            messages.error(request, f"Error connecting to Snipe-IT API: {e}")
            return render(request, 'login.html', {'form': form}) # Re-render login form with error
    
    # For a GET request, just show the login page with the form
    # Make sure login.html can display messages.
    return render(request, 'login.html', {'form': form})

def index(request):
    # Messages are now handled by Django's messaging framework
    # and displayed in the template. No specific context needed here for them.
    form = EmployeeNumberForm()
    return render(request, 'index.html', {'form': form})

def get_user_by_employee_number(employee_number_str):
    """
    Fetches a user from Snipe-IT API by their employee number.
    Returns the user dictionary if an exact match is found, otherwise None.
    """
    if not employee_number_str:
        return None

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    search_url = f"{API_URL}users?employee_num={employee_number_str}"

    try:
        response = requests.get(search_url, headers=headers, timeout=100)
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            for user in rows:
                # Ensure case-insensitive or exact match as per Snipe-IT's behavior if necessary
                # Assuming employee_number field in Snipe-IT is reliable for exact match.
                if user.get('employee_num') == employee_number_str:
                    return user # Return the first exact match
            return None # No exact match found
        else:
            # Log error or handle specific status codes if needed
            print(f"Error fetching user: API returned status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"RequestException while fetching user: {e}")
        return None


def get_assets():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    response = requests.get(f"{API_URL}assets", headers=headers)
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

def user_asset_view(request):
    employee_number = request.GET.get('employee_number')
    if not employee_number:
        messages.error(request, 'Please provide an employee number.')
        return redirect('index')

    user = get_user_by_employee_number(employee_number)

    if user and 'id' in user:
        user_id = user['id']
        assets_data = []
        categories_data = []
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json",
        }

        # Fetch assets for this user
        user_assets_url = f"{API_URL}users/{user_id}/assets"
        try:
            response = requests.get(user_assets_url, headers=headers, timeout=10)
            if response.status_code == 200:
                assets_data = response.json().get('rows', [])
            else:
                error_msg_api = f"Error fetching assets for user {user_id}: API returned status {response.status_code} - {response.text}"
                print(error_msg_api)
                messages.error(request, f'Could not retrieve assets from Snipe-IT. Details: {error_msg_api}')
        except requests.exceptions.RequestException as e:
            print(f"RequestException while fetching assets for user {user_id}: {e}")
            messages.error(request, f'Could not retrieve assets from Snipe-IT due to a network error: {e}')

        # Fetch categories
        categories_url = f"{API_URL}categories"
        try:
            response = requests.get(categories_url, headers=headers, timeout=10)
            if response.status_code == 200:
                categories_data = response.json().get('rows', [])
            else:
                error_msg_api_cat = f"Error fetching categories: API returned status {response.status_code} - {response.text}"
                print(error_msg_api_cat)
                messages.error(request, f'Could not retrieve asset categories from Snipe-IT. Details: {error_msg_api_cat}')
        except requests.exceptions.RequestException as e:
            print(f"RequestException while fetching categories: {e}")
            messages.error(request, f'Could not retrieve asset categories from Snipe-IT due to a network error: {e}')

        selected_category_id_str = request.GET.get('category_id')
        filtered_assets = assets_data
        selected_category_id = None # Ensure it's defined

        if selected_category_id_str and selected_category_id_str.isdigit():
            selected_category_id = int(selected_category_id_str)
            filtered_assets = [
                asset for asset in assets_data 
                if asset.get('category') and asset['category'].get('id') == selected_category_id
            ]
        
        context = {
            'user': user,
            'assets': filtered_assets,
            'categories': categories_data,
            'selected_category_id': selected_category_id,
            'employee_number': employee_number, # For displaying in template or pre-filling form
        }
        return render(request, 'asset_list.html', context)
    else:
        messages.error(request, f"Employee number '{employee_number}' not found.")
        return redirect('index')

def logout_view(request):
    if 'snipeit_authenticated' in request.session:
        del request.session['snipeit_authenticated']
    if 'snipeit_api_token' in request.session: # Also clear the token if stored
        del request.session['snipeit_api_token']
    # Redirect to a page that doesn't require authentication, e.g., the index or login page.
    return redirect('index')

def assign_asset_to_user_view(request, user_id):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json", # Keep for POST
    }
    
    # Fetch user details for display
    user_to_assign_data = None
    user_url = f"{API_URL}users/{user_id}"
    try:
        user_response = requests.get(user_url, headers=headers, timeout=10)
        if user_response.status_code == 200:
            user_to_assign_data = user_response.json()
        else:
            messages.error(request, f"User with ID {user_id} not found. API Status: {user_response.status_code}")
            return redirect('index') # Or a more appropriate error page/redirect
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching user details for ID {user_id}: {e}")
        return redirect('index')

    form = AssignAssetForm(request.POST or None) # Instantiate form for GET and POST

    if request.method == 'POST':
        if form.is_valid():
            asset_tag_to_find = form.cleaned_data['asset_tag']

            # Fetch asset by tag from Snipe-IT
            # Assuming /hardware/bytag/{asset_tag} is the endpoint.
            # If it's /hardware?search={asset_tag}, response handling might need adjustment
            # to pick the correct asset from a list or handle multiple matches.
            asset_by_tag_url = f"{API_URL}hardware/bytag/{asset_tag_to_find}"
            # Remove Content-Type for GET request to fetch asset by tag
            get_headers = {k: v for k, v in headers.items() if k != "Content-Type"}

            asset_id_to_assign = None
            try:
                asset_response = requests.get(asset_by_tag_url, headers=get_headers, timeout=10)
                if asset_response.status_code == 200:
                    asset_data = asset_response.json()
                    # Check if the response is a direct asset object or a list (like from a search)
                    if isinstance(asset_data, dict) and 'id' in asset_data: # Direct object
                        asset_id_to_assign = asset_data.get('id')
                    elif isinstance(asset_data, dict) and 'rows' in asset_data and len(asset_data['rows']) == 1: # Search result with one match
                        asset_id_to_assign = asset_data['rows'][0].get('id')
                    elif isinstance(asset_data, dict) and 'total' in asset_data and asset_data['total'] == 1 and 'rows' in asset_data and len(asset_data['rows']) == 1: # Another common search result pattern
                        asset_id_to_assign = asset_data['rows'][0].get('id')
                    else:
                        # Handle cases: not found, or multiple assets found if API behaves that way
                        # For /hardware/bytag/, ideally it's specific. If it can return multiple, error here.
                        # If using a search endpoint, this logic is crucial.
                        if isinstance(asset_data, dict) and asset_data.get('total', 0) > 1:
                             messages.error(request, f"Multiple assets found for tag '{asset_tag_to_find}'. Please use a unique tag.")
                        else:
                             messages.error(request, f"Asset with tag '{asset_tag_to_find}' not found or API response format unclear.")

                elif asset_response.status_code == 404:
                     messages.error(request, f"Asset with tag '{asset_tag_to_find}' not found (404).")
                else:
                    messages.error(request, f"Error fetching asset by tag '{asset_tag_to_find}'. API Status: {asset_response.status_code} - {asset_response.text}")

            except requests.exceptions.RequestException as e:
                messages.error(request, f"Network error fetching asset by tag '{asset_tag_to_find}': {e}")

            if asset_id_to_assign:
                checkout_url = f"{API_URL}hardware/{asset_id_to_assign}/checkout"
                payload = {
                    "checkout_to_type": "user",
                    "assigned_user": user_id, # This is the user_id passed to the view
                    "note": "Assigned via asset management app (by tag)."
                }
                try:
                    # Use original headers with Content-Type for POST
                    response = requests.post(checkout_url, headers=headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get('status') == 'success':
                            messages.success(request, f"Asset tag '{asset_tag_to_find}' (ID: {asset_id_to_assign}) assigned successfully to user {user_to_assign_data.get('name', user_id)}.")
                            employee_number = user_to_assign_data.get('employee_number')
                            if employee_number:
                                return redirect(reverse('user_asset_view') + f'?employee_number={employee_number}')
                            return redirect('index') # Fallback
                        else:
                            api_message = response_data.get('messages', 'Unknown error from Snipe-IT API.')
                            messages.error(request, f"Failed to assign asset: {api_message}")
                    else:
                        messages.error(request, f"Failed to assign asset. Snipe-IT API returned status {response.status_code}. Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    messages.error(request, f"Error during asset assignment: {e}")
            # If asset_id_to_assign is None (due to error or not found), the user will stay on the page
            # and see the error message. The form will be re-rendered below.

        # else: form is invalid, it will be re-rendered with errors by the GET part / context below

    # GET request or if POST had form errors or asset lookup failed:
    context = {
        'form': form, # Pass the form instance (empty or with POST data and errors)
        'user_to_assign': user_to_assign_data,
        'user_id': user_id,
    }
    return render(request, 'assign_asset.html', context)

def unassign_asset_from_user_view(request, asset_id):
    if not request.session.get('snipeit_authenticated'):
        return redirect(f"{reverse('admin_login')}?next={request.get_full_path()}")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # First, get asset details to find the assigned user's employee_number for redirection
    employee_number = None
    original_user_id = None
    asset_details_url = f"{API_URL}hardware/{asset_id}"
    try:
        asset_response = requests.get(asset_details_url, headers=headers, timeout=10)
        if asset_response.status_code == 200:
            asset_data = asset_response.json()
            if asset_data.get('assigned_to') and isinstance(asset_data['assigned_to'], dict):
                employee_number = asset_data['assigned_to'].get('employee_number')
                original_user_id = asset_data['assigned_to'].get('id') # Store user_id too
                # If employee_number is null but we have user_id, we could fetch user details
                # For now, this should cover most cases if employee_number is populated in Snipe-IT
                if not employee_number and original_user_id: # Attempt to get user details for employee_number
                    user_url = f"{API_URL}users/{original_user_id}"
                    user_resp = requests.get(user_url, headers=headers, timeout=5)
                    if user_resp.status_code == 200:
                        employee_number = user_resp.json().get('employee_number')
        else:
            messages.error(request, f"Could not retrieve details for asset ID {asset_id}. API Status: {asset_response.status_code}")
            return redirect('index')
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching asset details for ID {asset_id}: {e}")
        return redirect('index')

    # Proceed with check-in (unassignment)
    checkin_url = f"{API_URL}hardware/{asset_id}/checkin"
    payload = {"note": "Unassigned via asset management app."}

    try:
        response = requests.post(checkin_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                messages.success(request, "Asset unassigned successfully.")
                if employee_number:
                    return redirect(reverse('user_asset_view') + f'?employee_number={employee_number}')
                return redirect('index') # Fallback if employee_number not found
            else:
                api_message = response_data.get('messages', 'Unknown error from API.')
                messages.error(request, f"Failed to unassign asset: {api_message}")
        else:
            messages.error(request, f"Failed to unassign asset. Snipe-IT API returned status {response.status_code}. Response: {response.text}")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error during asset unassignment: {e}")

    # If any error occurred during POST, redirect to appropriate page with message
    if employee_number:
        # The error message would have been set above, redirect to user's asset page
        return redirect(reverse('user_asset_view') + f'?employee_number={employee_number}')
    # Fallback redirect to index if employee_number could not be determined
    return redirect('index')

def unassign_asset_by_tag_view(request, user_id):
    if not request.session.get('snipeit_authenticated'):
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        # Content-Type will be added for POST requests specifically
    }

    # Fetch user details for display and redirection context
    user_context_data = None
    user_url = f"{API_URL}users/{user_id}"
    try:
        # Use headers without Content-Type for this GET request
        get_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
        user_response = requests.get(user_url, headers=get_headers, timeout=10)
        if user_response.status_code == 200:
            user_context_data = user_response.json()
        else:
            messages.error(request, f"User with ID {user_id} (for context) not found. API Status: {user_response.status_code}")
            return redirect('index') # Or a more appropriate error page
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching user details for ID {user_id}: {e}")
        return redirect('index')

    form = UnassignAssetForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            asset_tag_to_unassign = form.cleaned_data['asset_tag']

            asset_id_to_unassign = None
            # Fetch asset by tag from Snipe-IT to get its ID
            asset_by_tag_url = f"{API_URL}hardware/bytag/{asset_tag_to_unassign}"
            get_headers = {k: v for k, v in headers.items() if k != "Content-Type"} # Ensure no content-type for GET

            try:
                asset_response = requests.get(asset_by_tag_url, headers=get_headers, timeout=10)
                if asset_response.status_code == 200:
                    asset_data = asset_response.json()
                    if isinstance(asset_data, dict) and 'id' in asset_data:
                        asset_id_to_unassign = asset_data.get('id')
                        # Optional: Check if asset is assigned to the user_context_data.id if needed
                        # current_assignee_id = asset_data.get('assigned_to', {}).get('id')
                        # if current_assignee_id != user_id:
                        #    messages.warning(request, f"Asset {asset_tag_to_unassign} is not assigned to {user_context_data.get('name', 'this user')}.")
                            # Decide if to proceed or stop
                    elif isinstance(asset_data, dict) and 'rows' in asset_data and len(asset_data['rows']) == 1:
                        asset_id_to_unassign = asset_data['rows'][0].get('id')
                    elif isinstance(asset_data, dict) and 'total' in asset_data and asset_data['total'] == 1 and 'rows' in asset_data and len(asset_data['rows']) == 1:
                        asset_id_to_unassign = asset_data['rows'][0].get('id')
                    else:
                        if isinstance(asset_data, dict) and asset_data.get('total', 0) > 1:
                            messages.error(request, f"Multiple assets found for tag '{asset_tag_to_unassign}'. Please use a unique tag.")
                        else:
                            messages.error(request, f"Asset with tag '{asset_tag_to_unassign}' not found or API response format unclear.")
                elif asset_response.status_code == 404:
                    messages.error(request, f"Asset with tag '{asset_tag_to_unassign}' not found (404).")
                else:
                    messages.error(request, f"Error fetching asset by tag '{asset_tag_to_unassign}'. API Status: {asset_response.status_code} - {asset_response.text}")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Network error fetching asset by tag '{asset_tag_to_unassign}': {e}")

            if asset_id_to_unassign:
                # Proceed with check-in (unassignment)
                checkin_url = f"{API_URL}hardware/{asset_id_to_unassign}/checkin"
                payload = {"note": "Unassigned via asset management app (by tag)."}
                post_headers = {**headers, "Content-Type": "application/json"}

                try:
                    response = requests.post(checkin_url, headers=post_headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get('status') == 'success':
                            messages.success(request, f"Asset tag '{asset_tag_to_unassign}' (ID: {asset_id_to_unassign}) unassigned successfully.")
                            employee_number = user_context_data.get('employee_number')
                            if employee_number:
                                return redirect(reverse('user_asset_view') + f'?employee_number={employee_number}')
                            # If user_context_data didn't have employee_number, redirect to index or user_asset_view with user_id if that's an option
                            return redirect('index') # Fallback
                        else:
                            api_message = response_data.get('messages', 'Unknown error from Snipe-IT API.')
                            messages.error(request, f"Failed to unassign asset: {api_message}")
                    else:
                        messages.error(request, f"Failed to unassign asset. Snipe-IT API returned status {response.status_code}. Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    messages.error(request, f"Error during asset unassignment: {e}")
            # If asset_id_to_unassign is None, error messages are already set. Re-render form.

    # GET request or if POST had form errors or asset lookup/unassignment failed:
    context = {
        'form': form,
        'user_context': user_context_data, # User for whom the unassignment is being initiated
        'user_id': user_id, # Pass user_id for form action URL and other links
    }
    return render(request, 'unassign_asset_by_tag.html', context)