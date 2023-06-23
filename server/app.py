#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, g
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

@app.before_request
def find_scientist_by_id(): 
    if request.endpoint == "scientistbyid":
        id_ = request.view_args.get("id")
        if scientist := db.session.get(Scientist, id_):
            g.scientist = scientist
        else:
            return make_response({"error": "Scientist not found"}, 404)


class Scientists(Resource):
    def get(self):
        scientists = [s.to_dict(rules=("-missions",)) for s in Scientist.query.all()]
        return make_response(scientists, 200)
    def post(self):
        try: 
            data = request.get_json()
            new_scientist = Scientist(**data)
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(rules=("-missions",)), 201)
        except Exception as e: 
            return make_response({"errors": str(e)}, 400)
        
class ScientistById(Resource):
    def get(self, id): 
        scientist = g.get("scientist")
        return make_response(scientist.to_dict(), 200)
    def patch(self, id): 
        scientist = g.get("scientist")
        try: 
            data = request.get_json()
            for k, v in data.items(): 
                setattr(scientist, k, v)
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(rules=("-missions",)), 202)
        except Exception as e: 
            return make_response({"errors": str(e)}, 400)
    def delete(self, id): 
        scientist = g.get("scientist")
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)

class Planets(Resource):
    def get(self):
        planets = [p.to_dict(rules=("-missions",)) for p in Planet.query.all()]
        return make_response(planets, 200)

class Missions(Resource):
    def post(self):
        try: 
            data = request.get_json()
            new_mission = Mission(**data)
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except Exception as e: 
            return make_response({"errors": str(e)}, 400)


api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistById, "/scientists/<int:id>")
api.add_resource(Planets, "/planets")
api.add_resource(Missions, "/missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
