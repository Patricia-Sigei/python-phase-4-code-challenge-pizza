#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        return jsonify(restaurant.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/restaurants", methods=["POST"])
def create_restaurant():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    
    if not name or not address:
        return jsonify({"error": "Name and address are required"}), 400

    try:
        restaurant = Restaurant(name=name, address=address)
        db.session.add(restaurant)
        db.session.commit()
        return jsonify(restaurant.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        db.session.delete(restaurant)
        db.session.commit()

        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pizzas/<int:id>", methods=["GET"])
def get_pizza(id):
    try:
        pizza = Pizza.query.get(id)
        if not pizza:
            return jsonify({"error": "Pizza not found"}), 404
        return jsonify(pizza.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)
        if not pizza or not restaurant:
            return jsonify({"errors": ["validation errors"]}), 400

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
