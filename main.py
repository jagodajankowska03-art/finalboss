from flask import Flask, request, render_template_string
from geopy.geocoders import Nominatim
from itertools import cycle
app = Flask(__name__)
geolocator = Nominatim(user_agent="route_optimizer")
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Optymalizacja tras</title>
    <style>#map {{ height: 500px; width: 100%; }}</style>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}"></script>
</head>
<body>
    <h1>Optymalizacja tras dla kierowców</h1>
    <form method="POST">
        <label>Adresy (po jednym w linii):</label><br>
        <textarea name="addresses" rows="10" cols="40">{{addresses}}</textarea><br><br>
        <label>Liczba kierowców:</label>
        <input type="number" name="drivers" value="{{drivers}}" min="1"><br><br>
        <label>Adres startowy:</label>
        <input type="text" name="start_address" value="{{start_address}}" size="40"><br><br>
        <input type="submit" value="Generuj trasy">
    </form>
    {% if routes %}
        <h2>Trasy:</h2>
        {% for i, route in enumerate(routes, 1) %}
            <h3>Kierowca {{i}}</h3>
            <ol>
            {% for addr in route %}
                <li>{{addr}}</li>
            {% endfor %}
            </ol>
        {% endfor %}
        <div id="map"></div>
        <script>
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 12,
                center: {{lat: {{center_lat}}, lng: {{center_lon}} }}
            }});
            {% for route in route_coords %}
                var routePath = new google.maps.Polyline({{
                    path: [
                        {% for lat, lon in route %}
                        {{lat}}, {{lon}},
                        {% endfor %}
                    ],
                    geodesic: true,
                    strokeColor: '#ff0000',
                    strokeOpacity: 1.0,
                    strokeWeight: 2
                }});
                routePath.setMap(map);
            {% endfor %}
        </script>
    {% endif %}
</body>
</html>
"""
def geocode(address):
    loc = geolocator.geocode(address)
    if loc:
        return (loc.latitude, loc.longitude)
    return None
def divide_addresses(address_list, num_drivers):
    routes = [[] for _ in range(num_drivers)]
    driver_cycle = cycle(range(num_drivers))
    for addr in address_list:
        routes[next(driver_cycle)].append(addr)
    return routes
@app.route("/", methods=["GET", "POST"])
def index():
    addresses = ""
    drivers = 1
    start_address = "ul. Ekologiczna 12, 05-080 Klaudyn"
    routes = None
    route_coords = None
    center_lat = 52.2297  # Warszawa
    center_lon = 21.0122
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # <-- AIzaSyD2MbzX1UhM7-TeEc13hyuyNO7d9p7OWqg
    if request.method == "POST":
        addresses = request.form.get("addresses", "")
        drivers = int(request.form.get("drivers", 1))
        start_address = request.form.get("start_address", start_address)
        address_list = [a.strip() for a in addresses.split("\n") if a.strip()]
        address_list.insert(0, start_address)  # dodajemy startowy adres
        routes = divide_addresses(address_list, drivers)
        # Konwersja adresów na współrzędne
        route_coords = []
        all_coords = []
        for route in routes:
            coords = []
            for addr in route:
                loc = geocode(addr)
                if loc:
                    coords.append(loc)
            route_coords.append(coords)
            all_coords.extend(coords)
        if all_coords:
            center_lat = sum(lat for lat, lon in all_coords) / len(all_coords)
            center_lon = sum(lon for lat, lon in all_coords) / len(all_coords)
    return render_template_string(HTML_PAGE,
                                  addresses=addresses,
                                  drivers=drivers,
                                  start_address=start_address,
                                  routes=routes,
                                  route_coords=route_coords,
                                  center_lat=center_lat,
                                  center_lon=center_lon,
                                  api_key=api_key)
if __name__ == "__main__":
    app.run(debug=True)










