import json
from flask import request
from flask import Blueprint
from flask_restful import Resource, Api
from marshmallow import ValidationError
from groundstation import db
from groundstation.backend_api.models import FlightSchedules, FlightScheduleCommands, FlightScheduleCommandsArgs
from groundstation.backend_api.utils import create_context
from groundstation.backend_api.validators import FlightScheduleValidator, FlightSchedulePatchValidator
from datetime import datetime

flightschedule_blueprint = Blueprint('flightschedule', __name__)
api = Api(flightschedule_blueprint)

class Flightschedule(Resource):

    def __init__(self):
        self.validator = FlightSchedulePatchValidator()
        super(Flightschedule, self).__init__()

    @create_context
    def get(self, flightschedule_id):
        flightschedule = FlightSchedules.query.filter_by(id=flightschedule_id).first()

        if not flightschedule:
            response_object = {'status': 'fail','message': 'Flightschedule does not exist'}
            return response_object, 404
        else:
            response_object = {
                'status': 'success',
                'data': flightschedule.to_json()
            }
            return response_object, 200

    @create_context
    def patch(self, flightschedule_id, local_data=None):
        if not local_data:
            post_data = request.get_json()
        else:
            post_data = json.loads(local_data)

        flightschedule = FlightSchedules.query.filter_by(id=flightschedule_id).first()

        if not flightschedule:
            response_object = {'status': 'fail', 'message': 'Flightschedule does not exist'}
            return response_object, 404

        try:
            validated_data = self.validator.load(post_data)
        except ValidationError as err:
            print(err.messages)
            response_object = {
                'status': 'fail',
                'message': 'The posted data is not valid!',
                'errors': err.messages
            }
            return response_object, 400

        # go through the operations for this patch, inspired by the parse JSON syntax
        # we have replace, add, or remove as valid operations on the flight schedule
        flightschedule_commands = validated_data.pop('commands')
        for command in flightschedule_commands:
            if command['op'] == 'add':
                new_command = FlightScheduleCommands(
                        command_id=command['command']['command_id'], 
                        timestamp=command['timestamp']
                    )

                # iterate through args and add them to our flightschedule in the db
                arguments = command.pop('args')
                for arg_data in arguments:
                    arg = FlightScheduleCommandsArgs(
                            index=arg_data['index'],
                            argument=arg_data['argument']
                        )
                    new_command.arguments.append(arg)
                flightschedule.commands.append(new_command)
            elif command['op'] == 'replace':
                this_command = FlightScheduleCommands.query.filter_by(id=command['flightschedule_command_id']).first()
                this_command.timestamp = command['timestamp']
                this_command.command_id = command['command']['command_id']
                
                this_command.arguments.clear()
                arguments = command.pop('args')

                # iterate through args and add them to the db
                for arg_data in arguments:
                    arg = FlightScheduleCommandsArgs(
                            index=arg_data['index'],
                            argument=arg_data['argument']
                        )
                    this_command.arguments.append(arg)
            # delete the flight schedule command
            elif command['op'] == 'remove':
                this_command = FlightScheduleCommands.query.filter_by(id=command['flightschedule_command_id']).first()
                db.session.delete(this_command)
            else:
                pass

        db.session.commit()

        response_object = {
            'status': 'success',
            'data': flightschedule.to_json()
        }

        return response_object, 200

    @create_context
    def delete(self, flightschedule_id):
        flightschedule = FlightSchedules.query.filter_by(id=flightschedule_id).first()

        if not flightschedule:
            response_object = {'status': 'fail', 'message': 'Flightschedule does not exist'}
            return response_object, 404

        db.session.delete(flightschedule)
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': 'flightschedule succesfully deleted'
        }

        return response_object, 200



class FlightScheduleList(Resource):

    def __init__(self):
        self.validator = FlightScheduleValidator()
        super(FlightScheduleList, self).__init__()

    @create_context
    def get(self, local_args=None):
        """
        local_args : dict
        """

        if not local_args:
            # flask request
            query_limit = request.args.get('limit')
        else:
            # local request
            query_limit = local_args.get('limit')

        flightschedules = FlightSchedules.query.order_by(FlightSchedules.creation_date).limit(query_limit).all()
        response_object = {
            'status':'success',
            'data': {
                'flightschedules':[fs.to_json() for fs in flightschedules]
            }
        }
        return response_object, 200


    @create_context
    def post(self, local_data=None):

        if not local_data:
            post_data = request.get_json()
        else:
            post_data = json.loads(local_data)

        try:
            validated_data = self.validator.load(post_data)
        except ValidationError as err:
            response_object = {
                'status': 'fail',
                'message': 'The posted data is not valid!',
                'errors': err.messages
            }
            return response_object, 400

        # check that we are not queueing multiple flight schedules
        if validated_data['is_queued']:
            num_queued = FlightSchedules.query.filter_by(is_queued=True).count()
            if num_queued > 0:
                response_object = {
                    'status': 'fail',
                    'message': 'A Queued flight schedule already exists!'
                }
                return response_object, 400

        # TODO validate commands
        flightschedule_commands = validated_data.pop('commands')
        flightschedule = FlightSchedules(**validated_data)
        #db.session.add(flightschedule)

        for command_data in flightschedule_commands:
            command_id = command_data['command']['command_id']
            timestamp = command_data['timestamp']
            command = FlightScheduleCommands(command_id=command_id, timestamp=timestamp)
            flightschedule.commands.append(command)

            arguments = command_data.pop('args')
            for arg_data in arguments:
                index = arg_data['index']
                arg = arg_data['argument']
                argument = FlightScheduleCommandsArgs(index=index, argument=arg)
                command.arguments.append(argument)
                

        db.session.add(flightschedule)
        db.session.commit()

        response_object = {
            'status': 'success',
            'data': flightschedule.to_json()
        }

        return response_object, 201


api.add_resource(Flightschedule, '/api/flightschedules/<flightschedule_id>')
api.add_resource(FlightScheduleList, '/api/flightschedules')