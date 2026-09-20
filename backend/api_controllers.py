from flask_restful import Api, Resource, reqparse
from .models import *

api = Api()

# PARSER FOR SERVICES
service_parser = reqparse.RequestParser()
service_parser.add_argument('name', required=True, help="Name of the service cannot be blank.")
service_parser.add_argument('description', required=True, help="Description of the service cannot be blank.")
service_parser.add_argument('price', type=float, required=True, help="Price of the service must be a float.")
service_parser.add_argument('time_required', required=True, help="Time required for the service cannot be blank.")

class ServiceAPI(Resource):

    def get(self):
        services = Service.query.all()
        service_list = []
        for service in services:
            service_details = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'time_required': service.time_required
            }
            service_list.append(service_details)
        return {"services": service_list}, 200
    
    def post(self):
        service_data = service_parser.parse_args()
        new_service = Service(
            id=generate_service_id(),  
            name=service_data['name'],
            description=service_data['description'],
            price=service_data['price'],
            time_required=service_data['time_required']
        )
        db.session.add(new_service)
        db.session.commit()
        return {"message": "Service created!", "service_id": new_service.id}, 201
    
    def put(self, service_id):
        service_data = service_parser.parse_args()
        service = Service.query.filter_by(id=service_id).first()
        if service:
            service.name = service_data['name']
            service.description = service_data['description']
            service.price = service_data['price']
            service.time_required = service_data['time_required']
            db.session.commit()
            return {"message": "Service updated!"}, 200
        else:
            return {"message": "Service not found!"}, 404
       
    def delete(self, service_id):
        service = Service.query.filter_by(id=service_id).first()
        if service:
            db.session.delete(service)
            db.session.commit()
            return {"message": "Service deleted!"}, 200
        else:
            return {"message": "Service not found!"}, 404
        
api.add_resource(ServiceAPI, '/api/service', '/api/service/<string:service_id>')

def generate_service_id():
    last_service = Service.query.order_by(Service.id.desc()).first()
    next_id = int(last_service.id[2:]) + 1 if last_service else 1
    return f"00{next_id:03}"  
