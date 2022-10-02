import os

from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_restful import Resource, Api
from flask_marshmallow import Marshmallow

from flask_cors import CORS

import geojson

from datetime import datetime

# Define app
app = Flask(__name__)

env_settings_file = os.environ.get('SETTINGS_FILE', 'development')
app.logger.warning(F"Overriding base configuration with {env_settings_file}.py")
app.config.from_pyfile(F"settings/base.py")
app.config.from_pyfile(F"settings/{env_settings_file}.py")

# Cross-Origins features
CORS(app)
app.logger.warning(F"CORS Allowed domains : {app.config['ALLOWED_CORS_ORIGINS']}")
cors = CORS(app, resources={ r"/*": {"origins": F"{app.config['ALLOWED_CORS_ORIGINS']}"} })

# Init ORM modules
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Marshmallow as (de-|)serializer
ma = Marshmallow(app)
# Flask-Restful as API generator
api = Api(app)


class Point(db.Model):
    """
    Un Point est un objet dans la base donnée, un point est définit par
    latitude : compris entre 90 et -90, 0 à l'équateur
    longitude : compris entre 180 et -180, 0 à Greenwich
    element_name : Nom de l'objet a marquer
    comment : Non utilisé
    date : Date de la marque
    """
    id = db.Column('point_id', db.Integer, primary_key = True)
    element_name = db.Column(db.String(128), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(128))
    date = db.Column(db.DateTime,
                        default=datetime.utcnow, 
                        onupdate=datetime.utcnow,
                        nullable=False)

class PointSchema(ma.Schema):
    class Meta:
        fields = ('id', 'element_name', 'longitude', 'latitude', 'comment', 'date')


class PointListResource(Resource):
    def get(self):
        points = Point.query.all()
        return points_schema.dump(points)
    
    def post(self):
        #import pdb
        #pdb.set_trace()
        
        app.logger.warning("POST")
        date = request.form.get('date')
        if date:
            try:
                date=datetime.fromisoformat(request.form.get('date'))
            except Exception as e:
                app.logger.warning(e)
                return F'KeyError! ({e})', 400
        # Serialize new point !
        try:
            new_point = Point(
                element_name=request.form['element_name'],
                latitude=request.form['latitude'],
                longitude=request.form['longitude'],
                comment=request.form.get('comment'),
                date=date
        
            )
        except KeyError as e:
            app.logger.warning(e)
            return F'KeyError! ({e})', 400
        except Exception as e:
            app.logger.warning(e)
            return F'Bad request ! ({e})', 400
        # Storing date ton
        try:
            db.session.add(new_point)
            db.session.commit()
        except Exception as e:
            app.logger.warning(e)
            return 'failed to store in database!', 500
        return point_schema.dump(new_point)

class PointResource(Resource):
    def get(self, point_id):
        point = Point.query.get_or_404(point_id)
        return point_schema.dump(point)
        
    def delete(self, point_id):
        point = Point.query.get_or_404(point_id)
        db.session.delete(point)
        db.session.commit()
        return '', 204



point_schema = PointSchema()
points_schema = PointSchema(many=True)

api.add_resource(PointListResource, '/api/points/')
api.add_resource(PointResource, '/api/points/<int:point_id>/')


@app.route('/geojson')
def geojson_view():
    queryset = Point.query.all()
    catalog = {}
    attributes = {}
    for p in queryset:
        url = F"{request.url_root}/api/points/{p.id}/"
        if p.element_name not in catalog.keys():
                catalog[p.element_name] = [(p.longitude, p.latitude)]
                attributes[p.element_name] = { "url": url,
                                               "name": p.element_name }
        # Sinon, ajout du point à la clef
        else:
            catalog[p.element_name].append((p.longitude, p.latitude))

    # Transformation du catalog en objet GeoJSON
    elements = []
    for key in catalog.keys():
        e = catalog[key]
        if len(e) > 1:
            # Cas d'un element_name avec plusieurs Point
            # Transformation en LineString
            # + un Point pour le premier élément
            line = geojson.LineString(e)
            point = geojson.Point(e[0])
            # Add trajectory
            feature = geojson.Feature(geometry=line)
            elements.append(feature)
            # Add marker for first position
            feature = geojson.Feature(geometry=point,
                                      properties=attributes[key])
            elements.append(feature)
        else:
            # Cas d'un élement 
            point = geojson.Point(e[0])
            feature = geojson.Feature(geometry=point,
                                      properties=attributes[key])
            elements.append(feature)
    geo_collection = geojson.FeatureCollection(elements)
    return geo_collection


if __name__ == "__main__":
    app.run(host='0.0.0.0')
