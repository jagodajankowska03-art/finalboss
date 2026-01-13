from flask import Flask, render_template_string, request
import googlemaps
from itertools import islice

app = Flask(__name__)

# Twój klucz API Google Maps
GMAPS_API_KEY = "AIzaSyD2MbzX1UhM7-TeEc13hyuyNO7d9p7OWqg"
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# Punkt startowy
START_ADDRESS = "ul. Ekologiczna 12, 05-080 Klaudyn"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Planowanie tras</title>
</head>
<body>
    <h2>Planowanie tras dla kierowców</h2>
    <form method="POST">
        Adresy (po jednym w linii):<br>
        <textarea name="addresses" rows="10" cols="40">{{ addresses }}</textarea><br><br>
        Liczba kierowców: <input type="number" name="drivers" min="1" value="{{ drivers }}"><br><br>
        <input type="submit" value="Generuj trasy">
    </form>
    {% if routes %}
        <h3>Wygenerowane trasy:</h3>
        {% for i, route in enumerate(routes) %}
            <p><b>Kierowca {{ i+1 }}:</b> {{ route|join(' → ') }}</p>
            <iframe
                width="600"
                height="450"
                style="border:0"
                loading="lazy"
                allowfullscreen
                src="https://www.google.com/maps/embed/v1/directions?key={{ api_key }}&origin={{ route[0] | urlencode }}&destination={{ route[-1] | urlencode }}&waypoints={{ route[1:-1] | join('|') | urlencode }}">
            </iframe>
            <hr>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def split_addresses(addresses_list, num_drivers):
    avg = len(addresses_list) // num_drivers
    remainder = len(addresses_list) % num_drivers
    result = []
    start = 0
    for i in range(num_drivers):
        end = start + avg + (1 if i < remainder else 0)
        result.append([START_ADDRESS] + addresses_list[start:end])
        start = end
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    addresses_text = ""
    num_drivers = 1
    routes = []
    if request.method == "POST":
        addresses_text = request.form.get("addresses", "")
        num_drivers = int(request.form.get("drivers", "1"))
        addresses_list = [addr.strip() for addr in addresses_text.splitlines() if addr.strip()]
        if addresses_list:
            routes = split_addresses(addresses_list, num_drivers)
    return render_template_string(HTML_TEMPLATE, addresses=addresses_text, drivers=num_drivers, routes=routes, api_key=GMAPS_API_KEY)

if __name__ == "__main__":
    app.run(debug=True)
