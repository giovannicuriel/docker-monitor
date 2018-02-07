import logging
import json
from flask import request
from flask import Blueprint
from flask import make_response
from marshmallow import Schema, fields, post_dump, ValidationError
from dockermon.app import app
from utils import decode_base64

manager = Blueprint("manager", __name__)

LOGGER = logging.getLogger('docker-manager.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)


class CreateContainerActionSchema(Schema):
    image_label = fields.Str(required=True)
    args = fields.Str(required=True)

createActionSchemaList = CreateContainerActionSchema(many=True)


def get_allowed_service(token):
    """
        Parses the authorization token, returning the service to be used when
        configuring the FIWARE backend

        :param token: JWT token to be parsed
        :returns: Fiware-service to be used on API calls
        :raises ValueError: for invalid token received
    """
    if not token or len(token) == 0:
        raise ValueError("Invalid authentication token")

    payload = token.split('.')[1]
    try:
        data = json.loads(decode_base64(payload))
        return data['service']
    except Exception as ex:
        raise ValueError("Invalid authentication token - not json object", ex)


def init_tenant_context(request, db):
    try:
        token = request.headers['authorization']
    except KeyError:
        raise HTTPRequestError(401, "No authorization token has been supplied")

    tenant = get_allowed_service(token)
    init_tenant(tenant, db)
    return tenant


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
