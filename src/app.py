"""
This module starts the API server and contains the API endpoints.
"""

import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Favorite


app = Flask(__name__)
app.url_map.strict_slashes = False


# Database configuration
db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://",
        "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# We use user ID 1 because authentication has not been created yet.
CURRENT_USER_ID = 1


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Route not found"}), 404


@app.route("/")
def sitemap():
    return generate_sitemap(app)


def get_current_user():
    """
    Temporarily returns user 1 as the current user.
    Later, authentication would identify the logged-in user.
    """
    return db.session.get(User, CURRENT_USER_ID)


# ---------------------------------------------------------
# PEOPLE ENDPOINTS
# ---------------------------------------------------------

@app.route("/people", methods=["GET"])
def get_people():
    people = Person.query.all()

    return jsonify([
        person.serialize()
        for person in people
    ]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    person = db.session.get(Person, people_id)

    if person is None:
        return jsonify({
            "error": "Person not found"
        }), 404

    return jsonify(person.serialize()), 200


# ---------------------------------------------------------
# PLANET ENDPOINTS
# ---------------------------------------------------------

@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()

    return jsonify([
        planet.serialize()
        for planet in planets
    ]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = db.session.get(Planet, planet_id)

    if planet is None:
        return jsonify({
            "error": "Planet not found"
        }), 404

    return jsonify(planet.serialize()), 200


# ---------------------------------------------------------
# USER ENDPOINTS
# ---------------------------------------------------------

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify([
        user.serialize()
        for user in users
    ]), 200


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": (
                "Current user not found. "
                "Create user ID 1 using the Flask admin."
            )
        }), 404

    return jsonify({
        "user": user.serialize(),
        "favorites": [
            favorite.serialize()
            for favorite in user.favorites
        ]
    }), 200


# ---------------------------------------------------------
# PERSON FAVORITES
# ---------------------------------------------------------

@app.route(
    "/favorite/people/<int:people_id>",
    methods=["POST"]
)
def add_person_favorite(people_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": (
                "Current user not found. "
                "Create user ID 1 using the Flask admin."
            )
        }), 404

    person = db.session.get(Person, people_id)

    if person is None:
        return jsonify({
            "error": "Person not found"
        }), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user.id,
        person_id=person.id
    ).first()

    if existing_favorite is not None:
        return jsonify({
            "error": "This person is already a favorite"
        }), 400

    favorite = Favorite(
        user_id=user.id,
        person_id=person.id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "message": "Person added to favorites",
        "favorite": favorite.serialize()
    }), 201


@app.route(
    "/favorite/people/<int:people_id>",
    methods=["DELETE"]
)
def delete_person_favorite(people_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Current user not found"
        }), 404

    favorite = Favorite.query.filter_by(
        user_id=user.id,
        person_id=people_id
    ).first()

    if favorite is None:
        return jsonify({
            "error": "Person favorite not found"
        }), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "message": "Person removed from favorites"
    }), 200


# ---------------------------------------------------------
# PLANET FAVORITES
# ---------------------------------------------------------

@app.route(
    "/favorite/planet/<int:planet_id>",
    methods=["POST"]
)
def add_planet_favorite(planet_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": (
                "Current user not found. "
                "Create user ID 1 using the Flask admin."
            )
        }), 404

    planet = db.session.get(Planet, planet_id)

    if planet is None:
        return jsonify({
            "error": "Planet not found"
        }), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user.id,
        planet_id=planet.id
    ).first()

    if existing_favorite is not None:
        return jsonify({
            "error": "This planet is already a favorite"
        }), 400

    favorite = Favorite(
        user_id=user.id,
        planet_id=planet.id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "message": "Planet added to favorites",
        "favorite": favorite.serialize()
    }), 201


@app.route(
    "/favorite/planet/<int:planet_id>",
    methods=["DELETE"]
)
def delete_planet_favorite(planet_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Current user not found"
        }), 404

    favorite = Favorite.query.filter_by(
        user_id=user.id,
        planet_id=planet_id
    ).first()

    if favorite is None:
        return jsonify({
            "error": "Planet favorite not found"
        }), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "message": "Planet removed from favorites"
    }), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )