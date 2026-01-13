from flask import Flask, request, render_template_string
import googlemaps
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

API_KEY = "AIzaSyD2MbzX1UhM7-TeEc13hyuyNO7d9p7OWqg"
gmaps = googlemaps.Client(key=API_KEY)

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Optymalizacja tras</title>
</head>
<body>
    <h2>Podaj adresy (po jednym w linii):</h2>
    <form method="post">
        <textarea name="addresses" rows="10" cols="50">{{ addresses }}</textarea><br><br>
        Liczba kierowców: <input type="number" name="drivers" value="{{ drivers }}" min="1" max="5"><br><br>
        <input type="submit" value="Generuj trasy">
    </form>
    {% if maps %}
        <h2>Trasy:</h2>
        {% for map_iframe in maps %}
            <iframe src="{{ map_iframe }}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe><br><br>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def geocode_addresses(addresses):
    coords = []
    for addr in addresses:
        try:
            geocode_result = gmaps.geocode(addr)
            if geocode_result:
                loc = geocode_result[0]['geometry']['location']
                coords.append((loc['lat'], loc['lng']))
        except Exception as e:
            print(f"Błąd geokodowania {addr}: {e}")
    return coords

def create_distance_matrix(coords):
    import math
    def haversine(c1, c2):
        R = 6371  # km
        lat1, lon1 = c1
        lat2, lon2 = c2
        from math import radians, cos, sin, asin, sqrt
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c
    size = len(coords)
    matrix = [[0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i != j:
                matrix[i][j] = int(haversine(coords[i], coords[j])*1000)  # w metrach
    return matrix

def solve_vrp(distance_matrix, num_vehicles):
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    routes = []
    if solution:
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            routes.append(route)
    return routes

def generate_google_maps_iframe(addresses, routes):
    iframes = []
    for route in routes:
        ordered = [addresses[i] for i in route]
        base = "https://www.google.com/maps/embed/v1/directions?key=" + API_KEY
        origin = ordered[0]
        destination = ordered[-1]
        waypoints = ordered[1:-1]
        wp_str = "|".join(waypoints)
        url = f"{base}&origin={origin}&destination={destination}"
        if waypoints:
            url += f"&waypoints={wp_str}"
        iframes.append(url)
    return iframes

@app.route("/", methods=["GET", "POST"])
def index():
    maps = None
    addresses = ""
    drivers = 1
    if request.method == "POST":
        addresses = request.form["addresses"]
        drivers = int(request.form.get("drivers", 1))
        addr_list = [a.strip() for a in addresses.splitlines() if a.strip()]
        coords = geocode_addresses(addr_list)
        if coords:
            dist_matrix = create_distance_matrix(coords)
            routes = solve_vrp(dist_matrix, drivers)
            maps = generate_google_maps_iframe(addr_list, routes)
    return render_template_string(HTML_TEMPLATE, maps=maps, addresses=addresses, drivers=drivers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
