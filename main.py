import logging
import typing
from datetime import datetime

from flask import Request, Response
from google.api_core.exceptions import NotFound
from google.cloud import firestore, bigquery


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


def get_or_create_table(client: bigquery.Client) -> bigquery.Table:
    try:
        dataset = client.get_dataset('pm_sensor')
    except NotFound as _:
        dataset = client.create_dataset('pm_sensor')

    # The default project ID is not set and hence a fully-qualified ID is required.
    table_ref = bigquery.TableReference(dataset, table_id='data')
    try:
        return client.get_table(table_ref)
    except NotFound as _:
        return client.create_table(bigquery.Table(table_ref, schema=[
            bigquery.SchemaField('humidity', 'NUMERIC', description='Sensor DHT22humidity in %'),
            bigquery.SchemaField('max_micro', 'NUMERIC', description=''),
            bigquery.SchemaField('min_micro', 'NUMERIC', description=''),
            bigquery.SchemaField('samples', 'NUMERIC', description=''),
            bigquery.SchemaField('sds_p1', 'NUMERIC', description='Sensor SDS011 PM10 in µg/m³'),
            bigquery.SchemaField('sds_p2', 'NUMERIC', description='Sensor PM2.5 PM10 in µg/m³'),
            bigquery.SchemaField('signal', 'NUMERIC', description='WiFi signal strength in dBm'),
            bigquery.SchemaField('temperature', 'NUMERIC', description='Sensor DHT22 temperature in °C'),
            bigquery.SchemaField('datetime', 'DATETIME', description='Datetime of measurement', mode='REQUIRED'),
        ]))


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

    sensor_data['datetime'] = datetime.now()

    db = firestore.Client()
    doc_ref = db.collection('pm_sensor')
    doc_ref.add(sensor_data)

    client = bigquery.Client()
    errors = client.insert_rows(get_or_create_table(client), [sensor_data])
    if errors:
        logging.warning('failed to store data in bigquery: %s', errors)
        return Response(status=500)

    return Response(status=201)
