import logging
import json
from flask import request
from flask import Blueprint
from flask import make_response
from marshmallow import Schema, fields, post_dump, ValidationError
from dockermon.app import app

manager = Blueprint("manager", __name__)

LOGGER = logging.getLogger('docker-manager.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)


class CreateContainerActionSchema(Schema):
    image_label = fields.Str(required=True)
    args = fields.Str(required=True)

createActionSchemaList = CreateContainerActionSchema(many=True)


def retrieve_headers(request):
    """
        Retrieve common headers from HTTP request
    """
    headers = {}

    return headers

@manager.route("/exec", methods=["POST"])
def docker_exec():
    """
        Start up a new docker container
    """
    result = {
        "message": "",
        "error": ""
    }
    error_code = 200
    try:
        execData = request.get_json()
        createActions = createActionSchemaList.load(execData)
        
        headers = retrieve_headers(request)


        for container in createActions.data:
            LOGGER.info("I should load " + json.dumps(container))
        
        result["message"] = "ok"
    except ValidationError as error:
        result["message"] = "Missing mandatory parameter"
        result["error"] = json.dumps(error)
        error_code = 401
    except ValueError as error:
        result["message"] = "Can't parse input"
        result["error"] = json.dumps(error)
        error_code = 401

    return make_response(json.dumps(result), error_code)
app.register_blueprint(manager)
