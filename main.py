from flask import Flask, request, render_template_string
from geopy.geocoders import Nominatim
import folium
import time

app = Flask(__name__)
geolocator = Nominatim(user_agent="debiut-kierowcy")

HTML = """
<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Debiut – planowanie tras</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f2f2f2;
}
.container {
    max-width: 900px;
    margin: 40px auto;
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}
h1 {
    margin-top: 0;
}
textarea, input {
    width: 100%;
    padding: 10px;
    margin-top: 8px;
}
button {
    margin-top: 20px;
    padding: 12px 20px;
    font-size: 16px;
    background: #1f4fff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
.map {
    margin-top: 30px;
}
.error {
    color: red;
    margin-top: 10px;
}
</style>
</head>
<body>
<div class="container">
<h1>Debiut – planowanie tras kierowców</h1>

<form method="post">
<label>Adres startowy</label>
<input name="start" value="{{ start }}" required>

<label>Adresy dostaw (jeden w linii)</label>
<textarea name="addresses" rows="8" required>{{ addresses }}</textarea>

<label>Liczba kierowców</label>
<input type="number" name="drivers" min="1" max="
