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
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET','POST', 'DELETE'])
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

@app.route('/character', methods=['GET'])
def handle_character():

    all_characters = Character.query.all()  
    return jsonify([character.serialize() for character in all_characters]), 200

@app.route('/admin/character', methods=['GET', 'POST', 'DELETE'])
def admin_handle_character():
    
    if request.method == 'GET':
        
        all_characters = Character.query.all()
        return jsonify([character.serialize() for character in all_characters]), 200
    
    elif request.method == 'POST':
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400
        
        if not data.get('name'):
            return jsonify({'msg': 'Name is required'}), 400
        
        existing_character = Character.query.filter_by(name=data.get('name')).first()
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
@app.route('/character/<int:charcter_id', methods= 'DELETE')
@app.route('/planet', methods=['GET'])
def handle_planet():

    all_planets = Planet.query.all()  
    return jsonify([planet.serialize() for planet in all_planets]), 200

@app.route('/admin/planet', methods=['GET', 'POST'])
def admin_handle_planet():
    
    if request.method == 'GET':
        
        all_characters = Character.query.all()
        return jsonify([character.serialize() for character in all_characters]), 200
    
    elif request.method == 'POST':
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({'msg': 'Check JSON body'}), 400
        
        if not data.get('name'):
            return jsonify({'msg': 'Name is required'}), 400
        
        existing_character = Character.query.filter_by(name=data.get('name')).first()
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



#planets
#vehicles

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
