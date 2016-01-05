import os
import urllib2
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pymongo import MongoClient
from flask import make_response
from bson.json_util import dumps

def toJson(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

app = Flask(__name__)
api = Api(app)

db = MongoClient()
if db != None:
    registrations = db.FoodApp.registrations
    donors = db.FoodApp.donors
    patrons = db.FoodApp.patrons
    volunteers = db.FoodApp.volunteers
else:
    abort(404, message="mongodb is not running")

DEFAULT_REPRESENTATIONS = {'application/json': toJson}
api.representations = DEFAULT_REPRESENTATIONS

class Donor(Resource):
    def get(self):
        return toJson(donors.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('food')
        args = parser.parse_args()
        
        donor = { 'id' : args['id'], 
                  'date' : args['date'], 
                  'food' : args['food'] }
        
        result = donors.insert(donor)
        
        return result, 201
        
class Patron(Resource):
    def get(self):
        return toJson(patrons.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('food')
        args = parser.parse_args()

        patron = { 'id' : args['id'], 
                   'date' : args['date'], 
                   'food' : args['food'] }
                        
        result = patrons.insert(patron)
        return result, 201
        
class Volunteer(Resource):
    def get(self):
        return toJson(volunteers.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('hours')

        args = parser.parse_args()

        volunteer = { 'id' : args['id'], 
                      'hours' : args['hours'] }
                        
        result = volunteers.insert(volunteer)
        return result, 201

class Registration(Resource):
    def get(self):
        return toJson(registrations.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('company')
        parser.add_argument('name')
        parser.add_argument('email')
        parser.add_argument('phone')
        parser.add_argument('address1')
        parser.add_argument('address2')
        args = parser.parse_args()

        registration = {'company' : args['company'], 
                        'name' : args['name'], 
                        'email' : args['email'], 
                        'phone' : args['phone'], 
                        'address1' : args['address1'], 
                        'address2' : args['address2'] }
                        
        result = registrations.insert(registration)
        return result, 201

api.add_resource(Registration, '/register')
api.add_resource(Donor, '/donate')
api.add_resource(Patron, '/receive')
api.add_resource(Volunteer, '/volunteer')

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP'), port=int(os.getenv('PORT')))
