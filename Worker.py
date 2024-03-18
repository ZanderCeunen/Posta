import time
import requests
import json
import os


fb_app_id = json.load(open("static/config.json", "r"))["fb_app_id"]
fb_app_secret = json.load(open("static/config.json", "r"))["fb_app_id"]


def vernieuw_token():
    fb_token = json.load(open("static/config.json", "r"))["fb_token"]
    # Controleer de vervaldatum van het token
    url = f"https://graph.facebook.com/debug_token?input_token={fb_token}&access_token={fb_token}"
    response = requests.get(url)
    data = response.json()
    expires_at = data["data"]["expires_at"]
    # Als het token minder dan een dag geldig is, vernieuw het
    if expires_at - time.time() < 86300:
        url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={fb_app_id}&client_secret={fb_app_secret}&fb_exchange_token={fb_token}"
        response = requests.get(url)
        data = response.json()
        fb_token = data["access_token"]
        # Schrijf het vernieuwde token terug naar het config bestand
        filename = 'static/config.json'
        with open(filename, 'r') as f:
            data = json.load(f)
            data['fb_token'] = fb_token
        os.remove(filename)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
