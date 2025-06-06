import logging
import requests
from django.conf import settings


def validate_credentials():
    """Validate FatSecret credentials are properly configured"""
    if not settings.FATSECRET_CLIENT_ID or not settings.FATSECRET_CLIENT_SECRET:
        raise ValueError(
            "FatSecret credentials are missing. "
            "Please check your .env file and make sure FATSECRET_CLIENT_ID "
            "and FATSECRET_CLIENT_SECRET are set correctly."
        )


def get_fatsecret_token():
    """Get an access token from FatSecret API"""
    validate_credentials()

    url = "https://oauth.fatsecret.com/connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "basic",
        "client_id": settings.FATSECRET_CLIENT_ID,
        "client_secret": settings.FATSECRET_CLIENT_SECRET,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        if 'access_token' not in token_data:
            raise ValueError("No access token in response")

        return token_data['access_token']

    except requests.exceptions.RequestException as e:
        error_content = getattr(e.response, 'text', 'No error content')
        logging.error(f"FatSecret API error: {str(e)}\nResponse: {error_content}")
        if e.response.status_code == 400:
            logging.error("Invalid client error - please check your FatSecret credentials")
        raise Exception("Failed to get FatSecret token. Check your credentials and try again.")


def search_food(query):
    """Search for foods using FatSecret API"""
    if not query:
        return {'foods': {'food': []}}

    token = get_fatsecret_token()
    url = "https://platform.fatsecret.com/rest/server.api"

    params = {
        "method": "foods.search",
        "search_expression": query,
        "format": "json",
        "max_results": 20  # Add this to ensure we get results
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Log the raw response for debugging
        logging.info(f"FatSecret search response: {response.text}")

        data = response.json()

        # Check if we have valid results
        if 'foods' not in data:
            logging.error(f"Unexpected API response format: {data}")
            return {'foods': {'food': []}}

        foods = data['foods']

        # Handle different response formats
        if 'food' not in foods:
            logging.info(f"No foods found for query: {query}")
            return {'foods': {'food': []}}

        food_items = foods['food']

        # If single result, wrap it in a list
        if isinstance(food_items, dict):
            food_items = [food_items]
        print(food_items)
        return {'foods': {'food': food_items}}

    except Exception as e:
        logging.error(f"FatSecret search error: {str(e)}")
        if hasattr(e, 'response'):
            logging.error(f"Response content: {e.response.text}")
        return {'foods': {'food': []}}