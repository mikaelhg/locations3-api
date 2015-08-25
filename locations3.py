#!/usr/bin/python2
# -*- coding: utf-8 -*-

from flask import *
from werkzeug.contrib.fixers import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler

from geodb import GeoDatabase, EdgeDatabase
import conf

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
conf.configure_app(app)
if conf.dbtype is 'maxmind':
    db = GeoDatabase()
else:
    db = EdgeDatabase()

@app.route('/address/<ip>')
def location_for_ip(ip):
    if ip.startswith('current'):
        model = db.lookup(request.remote_addr)
    else:
        model = db.lookup(ip)
    if model:
        return jsonify(model)
    else:
        return jsonify({}), 404


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(db.upgrade_db, 'interval', hours=conf.hours)
    app.run(host='0.0.0.0', processes=4)
