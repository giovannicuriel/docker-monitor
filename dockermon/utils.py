""" Assorted utils used throughout the service """
import base64
import json
import random
from flask import make_response


def format_response(status, message=None):
    """ Utility helper to generate default status responses """
    if message:
        payload = json.dumps({'message': message, 'status': status})
    elif 200 <= status < 300:
        payload = json.dumps({'message': 'ok', 'status': status})
    else:
        payload = json.dumps({'message': 'Request failed', 'status': status})

    return make_response(payload, status)


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'=' * (4 - missing_padding)
    return base64.decodestring(data)


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

