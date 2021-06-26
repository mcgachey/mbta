from flask import Blueprint, Flask, render_template, send_file, request, redirect, Response, jsonify
import logging
import uuid
import werkzeug.exceptions

import errors

app = Flask(__name__)
app.logger = logging.getLogger('trace')
app.config.update({
    'SECRET_KEY': '1773568e-60a3-427b-acd0-8670db5350f8'
})


@app.errorhandler(errors.NotFoundException)
def handle_object_not_found_error(e):
    code = str(uuid.uuid4())
    response = jsonify({"msg": e.entity_id, 'type': e.entity_type, 'code': code})
    response.status_code = 404
    logging.exception(f"Not found. Type: {e.entity_type}, id: {e.entity_id}, code: {code}")
    return response


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_page_not_found_error(e):
    code = str(uuid.uuid4())
    response = jsonify({"msg": request.url, 'code': code})
    response.status_code = 404
    logging.debug(f"Not found exception: {request.url}. Code: {code}")
    return response


@app.errorhandler(Exception)
def handle_any_error(e):
    code = str(uuid.uuid4())
    logging.exception(f"Unknown error {code}")
    response = jsonify({"msg": "An unexpected error occurred", "code": code})
    response.status_code = 500
    return response


@app.route('/', methods=['GET'])
def index():
    context = {}
    return render_template('index.html', **context)


logging.info("Started Gunicorn worker")
