import logging
import typing
from datetime import datetime

from flask import Request, Response
from google.cloud import firestore


class RequestInvalidError(Exception):
    pass


def extract_sensor_data(data: typing.Optional[dict]) -> typing.Dict[str, typing.Any]:
    """ Extract and validates the sensor data in the request data.
    :raises RequestInvalidError if the request is not valid.
    """
    if not data:
        raise RequestInvalidError('no data')
    sensor_data = data.get('sensordatavalues')
    if not isinstance(sensor_data, list):
        raise RequestInvalidError('no sensor data list')
    r = {}
    for sensor in sensor_data:
        typ = sensor.get('value_type')
        if not isinstance(typ, str):
            raise RequestInvalidError('value type is not a string')
        typ = typ.lower()
        val = sensor.get('value')
        if not isinstance(val, str):
            raise RequestInvalidError('raw value is not a string')
        try:
            val = float(val)
        except ValueError as e:
            raise RequestInvalidError('value is not a float: {}'.format(e))
        r[typ] = val
    return r


def pm_sensor_storage(request: Request) -> Response:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    try:
        sensor_data = extract_sensor_data(request.get_json(silent=True))
    except RequestInvalidError as e:
        logging.warning('invalid request: %s', e)
        return Response(status=400)

    sensor_data['timestamp'] = datetime.now()

    db = firestore.Client()
    doc_ref = db.collection('pm_sensor')
    doc_ref.add(sensor_data)
    return Response(status=201)
