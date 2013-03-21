#!/usr/bin/env python
from __future__ import with_statement
import urllib
import json
import sys
import os
import time
from os.path import join, dirname, exists
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify, Blueprint, current_app
from .icinga import Icinga
import socket

socket.setdefaulttimeout(15)

BACKENDS = []

retcon = Blueprint('retcon', __name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config.from_envvar("RETCON_CONFIG")
    app.debug = True
    app._backends = []
    for backend_config in app.config["BACKENDS"]:
        app._backends.append(apply(Icinga, backend_config))
    app.register_blueprint(retcon)
    return app


@retcon.route('/api/<something>')
def issues(something):
    things = []
    for backend in current_app._backends:
        things.extend(backend.fetch(something))
    d = {}
    d[something] = things
    return jsonify(**d)


@retcon.route('/api/ack', methods=['POST'])
def ack():
    be = request.form['backend']
    backend = [b for b in current_app._backends if b.backend_name == be][0]
    service = request.form['service']
    if service.lower() == 'host check':
        service = None
    backend.ack(
        request.form['host'],
        service,
        int(request.form['duration']),
    )
    return 'OK'


@retcon.route('/')
def index():
    return render_template(
        'index.html',
    )

if __name__ == '__main__':
    create_app().run()
