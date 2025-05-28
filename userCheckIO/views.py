from django.shortcuts import render
import requests, json

# Replace with your Snipe-IT API URL and token
API_URL = "https://your-snipeit-instance/api/v1/"
API_TOKEN = "YOUR_API_TOKEN"

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
    assets = get_assets()
    return render(request, 'asset_list.html', {'assets': assets})