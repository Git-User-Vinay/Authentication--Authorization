from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
import requests
from django.conf import settings


# This URL is the OAuth2 authentication URL provided by Discord
auth_url = settings.AUTH_URL


# This view redirects the user to Discord's OAuth2 login page
def discord_login(request):
    # Redirect to the Discord login URL to start the OAuth2 flow
    return redirect(auth_url)


# This view is the callback URL after the user is redirected back from Discord
def discord_login_redirect(request):
    # Retrieve the 'code' parameter from the query string
    code = request.GET.get('code')
    print(code)
    # Use the code to exchange it for user data (via OAuth2)
    user = exchange_code(code)
    # Return a JsonResponse with the user data received from Discord
    return JsonResponse({"user" : user})


# This function exchanges the code received from Discord for an access token
def exchange_code(code):
    # Prepare the data to be sent in the token exchange request
    data = settings.DISCORD_DATA
    data["code"] = code  # Add the 'code' to the data dictionary

    # Set the request headers for content type
    headers = {
        "Content-Type" : 'application/x-www-form-urlencoded' 
    }

    # Send a POST request to Discord's token endpoint to exchange the code for an access token
    response = requests.post("https://discord.com/api/oauth2/token", data = data, headers=headers)
    print(response)

     # Parse the response JSON to get the access token
    credentials = response.json()
    access_token = credentials['access_token']  # Extract the access token

     # Send a GET request to Discord's API to fetch the user info
    res = requests.get("https://discord.com/api/v6/users/@me", headers={
        'Authorization': 'Bearer %s' % access_token}) # Use the access token for authorization
    print(res)

    # Parse and return the user data from the response
    user = res.json()
    print(user)
    return user