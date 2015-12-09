import os
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from pymongo import MongoClient
from flask import make_response
from bson.json_util import dumps

app = Flask(__name__)
api = Api(app)



db = MongoClient()
reports = db.reports
issues = reports.issues
tips = db.tips.tips


def toJson(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

DEFAULT_REPRESENTATIONS = {'application/json': toJson}
api.representations = DEFAULT_REPRESENTATIONS

class RecycleTips(Resource):
    def get(self):
       return toJson(tips.find(), 200)

class ProblemReports(Resource):
    def get(self):
        #resp = []
        #for rec in issues.find():
        #    resp.append(rec['reportDate'])
        #return toJson(resp, 201)
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
        issue = {'reportDate' : args['reportDate'], 'reportText' : args['reportText'], 'reportLoc' : [ lon, lat ] }
        reports.issues.insert(issue)
        return 201

api.add_resource(ProblemReports, '/problemReports')
api.add_resource(RecycleTips, '/recycleTips')

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP'), port=int(os.getenv('PORT')))

