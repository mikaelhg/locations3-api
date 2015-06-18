#!/usr/bin/python2
# -*- coding: utf-8 -*-

import gzip
from tempfile import mkstemp
from os import fdopen
from contextlib import closing
import logging

from flask import *
from geoip2.errors import AddressNotFoundError
from werkzeug.contrib.fixers import ProxyFix
import geoip2.database
from apscheduler.schedulers.background import BackgroundScheduler
import requests


class GeoDatabase:
    def __init__(self):
        self.filename = 'GeoLite2-City.mmdb'
        self.url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
        self.reader = None

    def download_db(self):
        logging.info('Downloading DB')
        with closing(requests.get(self.url, stream=True)) as r:
            if r.status_code == 200:
                (download_fd, download_name) = mkstemp(suffix='.mmdb.gz')
                download = fdopen(download_fd, 'w+b')
                download.write(r.content)
                download.seek(0)
                gz = gzip.GzipFile(fileobj=download, mode='rb')
                (outfile_fd, outfile_name) = mkstemp(suffix='.mmdb')
                outfile = fdopen(outfile_fd, 'wb')
                try:
                    outfile.write(gz.read())
                    self.filename = outfile_name
                    logging.info('Succeeded in downloading new DB, at <%s>' % self.filename)
                except IOError:
                    logging.exception('Ran into problems')
                finally:
                    if gz: gz.close()
                    if outfile: outfile.close()
                    if download: download.close()

    def upgrade_db(self):
        self.download_db()
        if self.reader:
            self.reader.close()
        self.reader = geoip2.database.Reader(self.filename)

    def lookup(self, ip):
        if not self.reader:
            self.upgrade_db()
        return db.reader.city(ip)


logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
db = GeoDatabase()


def model_for_ip(ip):
    try:
        city = db.lookup(ip)
        return {'country_code': city.country.iso_code, 'continent': city.continent.code}
    except AddressNotFoundError:
        return None
    except ValueError:
        return None


@app.before_first_request
def initialize():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(db.upgrade_db, 'interval', hours=6)


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
    app.run(use_debugger=False, debug=True, use_reloader=True, host='0.0.0.0')
