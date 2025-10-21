"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favorites


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET', 'POST'])
def handle_users():

    if request.method == 'GET':

        all_users = User.query.all()
        return jsonify([user.serialize() for user in all_users]), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400

        if not data.get('email') or not data.get('username') or not data.get('password'):
            return jsonify({'msg': 'Email, username, and password are required'}), 400

        existing_user = User.query.filter(
            (User.email == data.get('email')) |
            (User.username == data.get('username'))
        ).first()

        if existing_user:
            return jsonify({'msg': 'User with this email or username already exists'}), 400

        new_user = User(
            email=data.get('email'),
            username=data.get('username'),
            password=data.get('password'),
            is_active=data.get('is_active', True)
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'msg': 'User deleted successfully'}), 200


@app.route('/character', methods=['GET', 'POST'])
def handle_character():

    if request.method == 'GET':
        all_characters = Character.query.all()
        return jsonify([character.serialize() for character in all_characters]), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400

        if not data.get('name'):
            return jsonify({'msg': 'Name is required'}), 400

        existing_character = Character.query.filter_by(
            name=data.get('name')).first()
        if existing_character:
            return jsonify({'msg': 'Character already exists'}), 400

        new_character = Character(
            name=data.get('name'),
            gender=data.get('gender'),
            birth_year=data.get('birth_year'),
            homeplanet_id=data.get('homeplanet_id'),
            vehicle_id=data.get('vehicle_id')
        )

        db.session.add(new_character)
        db.session.commit()

        return jsonify(new_character.serialize()), 201


@app.route('/character/<int:character_id>', methods=['GET', 'DELETE'])
def handle_single_character(character_id):
    character = Character.query.get(character_id)

    if not character:
        return jsonify({'msg': 'Character not found'}), 404

    if request.method == 'GET':
        return jsonify(character.serialize()), 200

    elif request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify({'msg': 'Character deleted successfully'}), 200


@app.route('/planet', methods=['GET', 'POST'])
def handle_planet():

    if request.method == 'GET':
        all_planets = Planet.query.all()
        return jsonify([planet.serialize() for planet in all_planets]), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400

        if not data.get('name'):
            return jsonify({'msg': 'Planet name is required'}), 400

        existing_planet = Planet.query.filter_by(name=data.get('name')).first()
        if existing_planet:
            return jsonify({'msg': 'Planet already exists'}), 400

        new_planet = Planet(
            name=data.get('name'),
            climate=data.get('climate')
        )

        db.session.add(new_planet)
        db.session.commit()

        return jsonify(new_planet.serialize()), 201


@app.route('/planet/<int:planet_id>', methods=['GET', 'DELETE'])
def handle_single_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if not planet:
        return jsonify({'msg': 'Planet not found'}), 404

    if request.method == 'GET':
        return jsonify(planet.serialize()), 200

    elif request.method == 'DELETE':
        db.session.delete(planet)
        db.session.commit()
        return jsonify({'msg': 'Planet deleted successfully'}), 200


@app.route('/vehicle', methods=['GET', 'POST'])
def handle_vehicle():

    if request.method == 'GET':
        all_vehicles = Vehicle.query.all()
        return jsonify([vehicle.serialize() for vehicle in all_vehicles]), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400

        if not data.get('name'):
            return jsonify({'msg': 'Vehicle name is required'}), 400

        existing_vehicle = Vehicle.query.filter_by(
            name=data.get('name')).first()
        if existing_vehicle:
            return jsonify({'msg': 'Vehicle already exists'}), 400

        new_vehicle = Vehicle(
            name=data.get('name'),
            model=data.get('model'),
            manufacturer=data.get('manufacturer')
        )

        db.session.add(new_vehicle)
        db.session.commit()

        return jsonify(new_vehicle.serialize()), 201


@app.route('/vehicle/<int:vehicle_id>', methods=['GET', 'DELETE'])
def handle_single_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)

    if not vehicle:
        return jsonify({'msg': 'Vehicle not found'}), 404

    if request.method == 'GET':
        return jsonify(vehicle.serialize()), 200

    elif request.method == 'DELETE':
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({'msg': 'Vehicle deleted successfully'}), 200


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    favorites = Favorites.query.filter_by(user_id=user_id).all()

    return jsonify([favorite.serialize() for favorite in favorites]), 200


@app.route('/user/<int:user_id>/favorites/character/<int:character_id>', methods=['GET', 'POST', 'DELETE'])
def handle_favorite_character(user_id, character_id):

    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    character = Character.query.get(character_id)
    if not character:
        return jsonify({'msg': 'Character not found'}), 404

    if request.method == 'GET':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            character_id=character_id
        ).first()

        return jsonify({
            'is_favorite': favorite is not None,
            'user_id': user_id,
            'character_id': character_id
        }), 200

    elif request.method == 'POST':
        existing = Favorites.query.filter_by(
            user_id=user_id,
            character_id=character_id
        ).first()

        if existing:
            return jsonify({'msg': 'Character already in favorites'}), 400

        new_favorite = Favorites(
            user_id=user_id,
            character_id=character_id
        )

        db.session.add(new_favorite)
        db.session.commit()

        return jsonify(new_favorite.serialize()), 201

    elif request.method == 'DELETE':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            character_id=character_id
        ).first()

        if not favorite:
            return jsonify({'msg': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'msg': 'Character removed from favorites'}), 200


@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['GET', 'POST', 'DELETE'])
def handle_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'msg': 'Planet not found'}), 404

    if request.method == 'GET':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            planet_id=planet_id
        ).first()

        return jsonify({
            'is_favorite': favorite is not None,
            'user_id': user_id,
            'planet_id': planet_id
        }), 200

    elif request.method == 'POST':
        existing = Favorites.query.filter_by(
            user_id=user_id,
            planet_id=planet_id
        ).first()

        if existing:
            return jsonify({'msg': 'Planet already in favorites'}), 400

        new_favorite = Favorites(
            user_id=user_id,
            planet_id=planet_id
        )

        db.session.add(new_favorite)
        db.session.commit()

        return jsonify(new_favorite.serialize()), 201

    elif request.method == 'DELETE':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            planet_id=planet_id
        ).first()

        if not favorite:
            return jsonify({'msg': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'msg': 'Planet removed from favorites'}), 200


@app.route('/user/<int:user_id>/favorites/vehicle/<int:vehicle_id>', methods=['GET', 'POST', 'DELETE'])
def handle_favorite_vehicle(user_id, vehicle_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'msg': 'Vehicle not found'}), 404

    if request.method == 'GET':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            vehicle_id=vehicle_id
        ).first()

        return jsonify({
            'is_favorite': favorite is not None,
            'user_id': user_id,
            'vehicle_id': vehicle_id
        }), 200

    elif request.method == 'POST':
        existing = Favorites.query.filter_by(
            user_id=user_id,
            vehicle_id=vehicle_id
        ).first()

        if existing:
            return jsonify({'msg': 'Vehicle already in favorites'}), 400

        new_favorite = Favorites(
            user_id=user_id,
            vehicle_id=vehicle_id
        )

        db.session.add(new_favorite)
        db.session.commit()

        return jsonify(new_favorite.serialize()), 201

    elif request.method == 'DELETE':
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            vehicle_id=vehicle_id
        ).first()

        if not favorite:
            return jsonify({'msg': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'msg': 'Vehicle removed from favorites'}), 200


setup_admin(app)
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
