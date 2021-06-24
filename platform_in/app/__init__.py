from flask import Flask
import os
import sys
from flask import jsonify
from elasticapm.contrib.flask import ElasticAPM
import logging
from flask import jsonify, request
import json
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer, Producer
import xmltodict
import certifi

logging.basicConfig(level=logging.INFO)
#elastic_apm = ElasticAPM()
# print(app.config, file=sys.stderr)

success_response_object = {"status":"success"}
success_code = 202
failure_response_object = {"status":"failure"}
failure_code = 400

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def kafka_avro_produce(avroProducer, topic, data):

    try:
        avroProducer.produce(topic=topic, value=data)
        logging.debug("avro produce")
        avroProducer.poll(2)
        if len(avroProducer) != 0:
            return False
    except BufferError:
        logging.error("local buffer full", len(avroProducer))
        return False
    except Exception as e:
        logging.error(e)
        return False

    return True

def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # set up extensions
    #elastic_apm.init_app(app)

    # value_schema = avro.load("avro/vehiclecharging.avsc")
    # avroProducer = AvroProducer(
    #     {
    #         "bootstrap.servers": app.config["KAFKA_BROKERS"],
    #         "security.protocol": app.config["SECURITY_PROTOCOL"],
    #         "sasl.mechanism": app.config["SASL_MECHANISM"],
    #         "sasl.username": app.config["SASL_UNAME"],
    #         "sasl.password": app.config["SASL_PASSWORD"],
    #         "ssl.ca.location": certifi.where(),
    #         #"debug": "security,cgrp,fetch,topic,broker,protocol",
    #         "on_delivery": delivery_report,
    #         "schema.registry.url": app.config["SCHEMA_REGISTRY_URL"] ,
    #     },
    #     default_value_schema=value_schema,
    # )

    producer = Producer(
        {
            "bootstrap.servers": app.config["KAFKA_BROKERS"],
            "security.protocol": app.config["SECURITY_PROTOCOL"],
            "sasl.mechanism": app.config["SASL_MECHANISM"],
            "sasl.username": app.config["SASL_UNAME"],
            "sasl.password": app.config["SASL_PASSWORD"],
            "ssl.ca.location": certifi.where(),
            #"debug": "security,cgrp,fetch,topic,broker,protocol",
            "on_delivery": delivery_report
        }
    )

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app}

    @app.route("/")
    def hello_world():
        return jsonify(health="ok")

    @app.route("/ocpp/v16/observations", methods=["POST"])
    def post_vehiclecharge_data():
        try:
            #data = request.get_data()
            data = request.get_json()
            #logging.info(f"post observation: {data}")

            # topic =
            # kafka_avro_produce(avroProducer, topic, data_dict)
            producer.poll(0)

        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
            producer.produce('test.finest.rawdata.vehiclecharging.ocpp', data, callback=delivery_report)

            return success_response_object,success_code

        except Exception as e:
            producer.flush()
            logging.error("post data error", e)
            #elastic_apm.capture_exception()

    return app

