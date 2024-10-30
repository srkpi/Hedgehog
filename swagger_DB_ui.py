import requests

URL = ""
KEY = ""
HEADERS = {}


def initialize(BASE_URL:str,DB_KEY:str):
    global URL,KEY, HEADERS
    """Initialize swagger DB connection."""
    URL = BASE_URL
    KEY = DB_KEY
    HEADERS = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }


def fetch_all_events():
    """Fetch all events from the calendar."""
    try:
        response = requests.get(f"{URL}/calendar/event", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception("Error fetching all events") from e


def fetch_event_by_id(event_id):
    """Fetch a specific event by ID from the calendar."""
    try:
        response = requests.get(f"{URL}/calendar/event/{event_id}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception("Error fetching event by ID") from e


def create_event(data):
    """Create a new event in the calendar."""
    required_fields = ["title", "shortDescription", "location", "tag", "startDate", "endDate"]
    if not all(field in data and data[field] for field in required_fields):
        raise ValueError(
            "Missing one or more required fields: title, shortDescription, location, tag, startDate, endDate.")
    try:
        response = requests.post(f"{URL}/calendar/event", json=data, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception("Error creating event") from e


def update_event(event_id, update_data):
    """Update an existing event by ID with a PATCH request."""
    update_data["id"] = event_id
    try:
        response = requests.patch(f"{URL}/calendar/event", json=update_data, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if response.status_code == 404:
            raise Exception("Event with this ID does not exist") from e
        raise Exception("Error updating event") from e


def delete_event(event_id):
    """Delete an event by ID from the calendar."""
    try:
        response = requests.delete(f"{URL}/calendar/event/{event_id}", headers=HEADERS)
        response.raise_for_status()
        return {"status": "deleted", "id": event_id}
    except requests.RequestException as e:
        raise Exception("Error deleting event") from e