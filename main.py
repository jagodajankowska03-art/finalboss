from flask import Flask, render_template_string, request
import googlemaps
from itertools import islice

app = Flask(__name__)

# Twój Google Maps API key
GMAPS_API_KEY = "AIzaSyD2MbzX1UhM7-TeEc13hyuyNO7d9p7OWqg"
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Optymalizacja Tras</title>
</head>
<body>
    <h1>Optymalizacja Tras dla Kierowców</h1>
    <form method="post">
        <label>Adresy (po jednym w linii):</label><br>
        <textarea name="addresses" rows="10" cols="50">{{ addresses }}</textarea><br><br>
        <label>Liczba kierowców:</label>
        <input type="number" name="drivers" min="1" value="{{ drivers }}"><br><br>
        <label>Adres startowy:</label>
        <input type="text" name="start_address" value="{{ start_address }}"><br><br>
        <input type="submit" value="Generuj trasy">
    </form>

    {% if routes %}
        <h2>Trasy:</h2>
        {% for i, route in enumerate(routes, start=1) %}
            <h3>Kierowca {{ i }}</h3>
            <ul>
                {% for addr in route %}
                    <li>{{ addr }}</li>
                {% endfor %}
            </ul>
            <iframe
                width="600"
                height="400"
                style="border:0"
                loading="lazy"
                allowfullscreen
                src="https://www.google.com/maps/embed/v1/directions?key={{ gmaps_key }}&origin={{ start_address | urlencode }}&destination={{ route[-1] | urlencode }}&waypoints={{ route[:-1] | join('|') | urlencode }}">
            </iframe>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def split_addresses(addresses, n):
    """Podziel listę adresów na n części"""
    avg = len(addresses) // n
    out = []
    start = 0
    for i in range(n):
        end = start + avg + (1 if i < len(addresses) % n else 0)
        out.append(addresses[start:end])
        start = end
    return out

@app.route("/", methods=["GET", "POST"])
def index():
    routes = None
    addresses_text = ""
    drivers = 1
    start_address = "ul. Ekologiczna 12, 05-080 Klaudyn"

    if request.method == "POST":
        addresses_text = request.form.get("addresses", "")
        drivers = max(1, int(request.form.get("drivers", 1)))
        start_address = request.form.get("start_address", start_address)

        addresses = [line.strip() for line in addresses_text.splitlines() if line.strip()]
        if addresses:
            routes = split_addresses(addresses, drivers)

    return render_template_string(
        HTML_TEMPLATE,
        routes=routes,
        addresses=addresses_text,
        drivers=drivers,
        start_address=start_address,
        gmaps_key=GMAPS_API_KEY
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
