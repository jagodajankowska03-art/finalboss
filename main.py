from flask import Flask, render_template_string, request
import googlemaps

# Twój klucz API Google Maps
GMAPS_API_KEY = "AIzaSyD2MbzX1UhM7-TeEc13hyuyNO7d9p7OWqg"
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

app = Flask(__name__)

# Punkt startowy
START_ADDRESS = "ul. Ekologiczna 12, 05-080 Klaudyn"

HTML_PAGE = """
<!doctype html>
<html>
<head>
  <title>Optymalizacja tras</title>
</head>
<body>
  <h1>Tworzenie tras dla kierowców</h1>
  <form method="POST">
    Adresy (po jednym w linii):<br>
    <textarea name="addresses" rows="10" cols="50">{{addresses}}</textarea><br><br>
    Liczba kierowców: <input type="number" name="drivers" value="{{drivers}}" min="1" max="5"><br><br>
    <input type="submit" value="Generuj trasy">
  </form>
  {% if routes %}
    <h2>Trasy:</h2>
    <ul>
    {% for i, route in enumerate(routes) %}
      <li><b>Kierowca {{i+1}}:</b> {{route}}</li>
    {% endfor %}
    </ul>
  {% endif %}
</body>
</html>
"""

def divide_addresses(addresses, drivers):
    """Prosta funkcja dzieląca adresy na trasy kierowców"""
    routes = [[] for _ in range(drivers)]
    for idx, addr in enumerate(addresses):
        routes[idx % drivers].append(addr)
    return routes

@app.route("/", methods=["GET", "POST"])
def index():
    routes_display = None
    addresses_text = ""
    num_drivers = 1
    if request.method == "POST":
        addresses_text = request.form.get("addresses", "")
        num_drivers = int(request.form.get("drivers", 1))
        addresses = [a.strip() for a in addresses_text.splitlines() if a.strip()]
        
        # Dodajemy punkt startowy na początku każdej trasy
        routes_split = divide_addresses(addresses, num_drivers)
        routes_display = []
        for route in routes_split:
            full_route = [START_ADDRESS] + route
            routes_display.append(" → ".join(full_route))
    return render_template_string(HTML_PAGE, routes=routes_display, addresses=addresses_text, drivers=num_drivers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
