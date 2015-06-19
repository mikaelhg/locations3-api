#!/usr/bin/python2
# -*- coding: utf-8 -*-

import logging

from flask import *
from geoip2.errors import AddressNotFoundError
from werkzeug.contrib.fixers import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler

from geodb import GeoDatabase
import conf

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
conf.configure_app(app)
db = GeoDatabase()


def model_for_ip(ip):
    try:
        city = db.lookup(ip)
        return {'country_code': city.country.iso_code, 'continent': city.continent.code}
    except AddressNotFoundError:
        return None
    except ValueError:
        return None


@app.route('/address/<ip>')
def by_ip(ip):
    if ip.startswith('current'):
        model = model_for_ip(request.remote_addr)
    else:
        model = model_for_ip(ip)
    if model:
        return jsonify(model)
    else:
        return jsonify({}), 404


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(db.upgrade_db, 'interval', hours=conf.hours)
    db.upgrade_db()
    app.run(host='0.0.0.0', processes=4)
