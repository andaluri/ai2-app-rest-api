import os
import urllib3
import requests
import geocoder
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pymongo import MongoClient
from flask import make_response
from bson.json_util import dumps
from bson.objectid import ObjectId

requests.packages.urllib3.disable_warnings()

def toJson(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

app = Flask(__name__)
api = Api(app)

earthRadiusInMiles = 3963.2

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

class Match(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('radius')
        parser.add_argument('source')
        parser.add_argument('id')
        args = parser.parse_args()
        radius = args['radius']
        source = args['source']
        id = args['id']
        myid = registrations.find_one({"_id":ObjectId(id)})
        result = ''
        if source == 'donor':
            result = toJson(patrons.find(), 200)
        else:
            result = toJson(donors.find(), 200)
        return result

class Match2(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('radius')
        parser.add_argument('source')
        parser.add_argument('id')
        args = parser.parse_args()
        
        radius = float(args['radius'])
        source = args['source']
        id = args['id']
        
        myid = registrations.find_one({"_id":ObjectId(id)})
        print myid

        results = []
        if myid is not None:
            dbptr = ''
            
            if source == 'donor':
                dbptr = patrons
            elif source == 'patron':
                dbptr = donors
            elif source == 'volunteer':
                dbptr = None
            
            if dbptr is not None:
                radius = radius / earthRadiusInMiles
                srchResults = registrations.find({ "location" : { "$geoWithin": { "$centerSphere": [ myid['location'], radius ] } } })
                if srchResults is not None:
                    for doc in srchResults:
                        print doc
                        print doc['_id']
                        docid = str(ObjectId(doc['_id']))
                        temp = dbptr.find_one({"id":docid})
                        print temp
                        if temp is not None:
                            id = temp['id']
                            food = temp['food']
                            reg = registrations.find_one({"_id":ObjectId(id)})
                            name = reg['name']
                            phone = reg['phone']
                            email = reg['email']
                            address1 = reg['address1']
                            address2 = reg['address2']
                            results.append({'id':id, 'food':food, 'name':name, 'phone':phone, 'email':email, 'address1':address1, 'address2':address2})
        
        return results, 201

class Donor(Resource):
    def get(self):
        return toJson(donors.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('food')
        args = parser.parse_args()
        
        donor = { 'id' : args['id'], 
                  'food' : args['food'] }
        
        result = donors.insert(donor)
        
        return 201
        
class Patron(Resource):
    def get(self):
        return toJson(patrons.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('food')
        args = parser.parse_args()

        patron = { 'id' : args['id'], 
                   'food' : args['food'] }
                        
        result = patrons.insert(patron)
        
        return 201
        
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
        
        return 201

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
        
        geoaddr = geocoder.google(args['address1'] + ' ' + args['address2'])
        print geoaddr
        if geoaddr is not None and geoaddr.latlng is not None and len(geoaddr.latlng) == 2:
            lon = geoaddr.latlng[1]
            lat = geoaddr.latlng[0]
            registration = {
                            'company' : args['company'], 
                            'name' : args['name'], 
                            'email' : args['email'], 
                            'phone' : args['phone'], 
                            'address1' : args['address1'], 
                            'address2' : args['address2'],
                            'location' : [lon, lat] }
                        
        result = registrations.insert(registration)
        
        return result, 201

api.add_resource(Registration, '/register')
api.add_resource(Donor, '/donate')
api.add_resource(Patron, '/receive')
api.add_resource(Volunteer, '/volunteer')
api.add_resource(Match, '/match')
api.add_resource(Match2, '/match2')

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP'), port=int(os.getenv('PORT')))
