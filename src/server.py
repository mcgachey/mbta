from flask import Blueprint, Flask, render_template, send_file, request, redirect, Response, jsonify
import logging
import os
import uuid
import werkzeug.exceptions

import errors
import mbta

app = Flask(__name__)
app.logger = logging.getLogger('trace')
app.config.update({
    'SECRET_KEY': os.environ.get('FLASK_SECRET_KEY')
})

mbta_api = mbta.MbtaApi(os.environ.get('MBTA_API_KEY'))


@app.errorhandler(errors.UnexpectedServerResponseException)
def handle_unexpected_server_response(e):
    code = str(uuid.uuid4())
    context = {'msg': f"Got an unexpected response from the MBTA API. Check the logs for code: {code}"}
    logging.exception(f"Unexpected response {e.status_code} ({e.body}). Code {code}")
    return render_template('error.html', **context), 500


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_page_not_found_error(e):
    context = {'msg': f"URL not found: {request.url}"}
    logging.debug(f"Not found exception: {request.url}.")
    return render_template('error.html', **context), 404


@app.errorhandler(Exception)
def handle_any_error(e):
    code = str(uuid.uuid4())
    context = {'msg': f"An unexpected error occurred. Check the logs for code: {code}"}
    logging.exception(f"Unknown error {code}")
    return render_template('error.html', **context), 500


@app.route('/', methods=['GET'])
def index():
    context = {
        'routes': mbta_api.routes()
    }
    return render_template('index.html', **context)


# @app.route('/ajax/routes', methods=['GET'])
# def routes():
#     logging.info("Sendin routes")
#     return jsonify({'data': [{r.to_dict()} for r in mbta_api.routes()]})


logging.info("Started Gunicorn worker")
