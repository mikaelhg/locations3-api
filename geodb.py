#!/usr/bin/python2
# -*- coding: utf-8 -*-

import gzip
from tempfile import mkstemp
from os import fdopen
from contextlib import closing
import logging
import geoip2.database
import requests

class GeoDatabase(object):
    def __init__(self):
        self.url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
        self.filename = None
        self.reader = None

    def download_db(self):
        logging.info('Downloading DB')
        with closing(requests.get(self.url, stream=True)) as req:
            if req.status_code == 200:
                (download_fd, download_name) = mkstemp(prefix='GeoLite2-City.', suffix='.mmdb.gz')
                download = fdopen(download_fd, 'w+b')
                download.write(req.content)
                download.seek(0)
                gz = gzip.GzipFile(fileobj=download, mode='rb')
                (outfile_fd, outfile_name) = mkstemp(prefix='GeoLite2-City.', suffix='.mmdb')
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
        return self.reader.city(ip)
