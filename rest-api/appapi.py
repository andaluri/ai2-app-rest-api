import os
import urllib3
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pymongo import MongoClient
from flask import make_response
from bson.json_util import dumps

urllib3.disable_warnings()

def toJson(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

app = Flask(__name__)
api = Api(app)

db = MongoClient()
if db != None:
    issues = db.reports.issues
    tips = db.tips.tips
else:
    abort(404, message="mongodb is not running")

DEFAULT_REPRESENTATIONS = {'application/json': toJson}
api.representations = DEFAULT_REPRESENTATIONS


class RecycleTips(Resource):
    def get(self):
       return toJson(tips.find(), 200)

class ProblemReports(Resource):
    def get(self):
        return toJson(issues.find(), 200)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('reportDate')
        parser.add_argument('reportText')
        parser.add_argument('reportLon')
        parser.add_argument('reportLat')
        args = parser.parse_args()
        
        lon = float(args['reportLon'])
        lat = float(args['reportLat'])
        
        #Longitude first, Latitude next as per MongoDb indexing guidelines
        issue = {'reportDate' : args['reportDate'], 
                 'reportText' : args['reportText'], 
                 'reportLoc' : [ lon, lat ] }
                 
        issues.insert(issue)
        return 201

api.add_resource(ProblemReports, '/problemReports')
api.add_resource(RecycleTips, '/recycleTips')

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP'), port=int(os.getenv('PORT')))
