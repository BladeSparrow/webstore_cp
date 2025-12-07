import requests

API_URL = "https://api.novaposhta.ua/v2.0/json/"
API_KEY = "c97e3de4186c9e39a5b33aeaad192a59df815c35"

def get_cities():
    data = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getCities",
        "methodProperties": {}
    }
    response = requests.post(API_URL, json=data)
    print(response.status_code)
    print(response.json())
    return response.json().get("data", [])

def get_warehouses(city_ref):
    data = {
        "apiKey": API_KEY,
        "modelName": "AddressGeneral",
        "calledMethod": "getWarehouses",
        "methodProperties": {"CityRef": city_ref}
    }
    response = requests.post(API_URL, json=data)
    return response.json().get("data", [])