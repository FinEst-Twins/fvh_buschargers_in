import json
import logging
import os

import sentry_sdk

from elasticapm.contrib.flask import ElasticAPM
from flask import Flask, jsonify, request
from fvhiot.utils.data import data_pack
from fvhiot.utils.http.flasktools import extract_data_from_flask_request
from kafka import KafkaProducer
from sentry_sdk.integrations.flask import FlaskIntegration

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

elastic_apm = ElasticAPM()

success_response_object = {"status": "success"}
success_code = 202
failure_response_object = {"status": "failure"}
failure_code = 400


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    logging.basicConfig(level=app.config["LOG_LEVEL"])
    logging.getLogger().setLevel(app.config["LOG_LEVEL"])

    # set up extensions
    if os.getenv("USE_ELASTIC"):
        elastic_apm.init_app(app)

    producer = KafkaProducer(
        bootstrap_servers=app.config["KAFKA_BROKERS"],
        security_protocol=app.config["SECURITY_PROTOCOL"],
        ssl_cafile=app.config["CA_FILE"],
        ssl_certfile=app.config["CERT_FILE"],
        ssl_keyfile=app.config["KEY_FILE"],
        value_serializer=lambda v: json.dumps(v).encode("ascii"),
        key_serializer=lambda v: json.dumps(v).encode("ascii"),
    )

    rawdata_producer = KafkaProducer(
        bootstrap_servers=app.config["KAFKA_BROKERS"],
        security_protocol=app.config["SECURITY_PROTOCOL"],
        ssl_cafile=app.config["CA_FILE"],
        ssl_certfile=app.config["CERT_FILE"],
        ssl_keyfile=app.config["KEY_FILE"],
    )

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app}

    @app.route("/")
    def hello_world():
        return jsonify(health="ok")

    @app.route("/debug-sentry")
    def trigger_error():
        division_by_zero = 1 / 0

    @app.route("/ocpp/v16/observations", methods=["POST"])
    def post_vehiclecharge_data():

        try:
            data = request.get_data()
            logging.info(f"post data goes like : {data[0:200]}")
            logging.debug(f"post data in json : {json.loads(data)}")

            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            producer.send(
                topic="finest.json.vehiclecharging.ocpp",
                key="",
                value=request.get_json(),
            )

            # Store raw data. Temporary hardcoded solution.
            try:
                raw_data_topic = "finest.rawdata.vehiclecharging.ocpp"
                packed_raw_data = data_pack(extract_data_from_flask_request(request))
                rawdata_producer.send(
                    topic=raw_data_topic,
                    key="",
                    value=packed_raw_data,
                )
                logging.info(f"Raw data sent to : {raw_data_topic}")
            except Exception as e:
                rawdata_producer.flush()
                logging.error("Send raw data error", e)
                # capture elastic exception, if env USE_ELASTIC is set
                if os.getenv("USE_ELASTIC"):
                    elastic_apm.capture_exception()

            return success_response_object, success_code

        except Exception as e:
            producer.flush()
            logging.error("post data error", e)
            # capture elastic exception, if env USE_ELASTIC is set
            if os.getenv("USE_ELASTIC"):
                elastic_apm.capture_exception()
            return failure_response_object, failure_code

    return app
