#!/usr/bin/python2
# -*- coding: utf-8 -*-

import gzip
from tempfile import mkstemp
from os import fdopen
from contextlib import closing
from geoip2.errors import AddressNotFoundError
import logging
import geoip2.database
import requests

class GeoDatabase(object):
    def __init__(self):
        self.__url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
        self.__filename = None
        self.__reader = None
        self.__logger = logging.getLogger("app.geodb")
        self.upgrade_db()

    def __download_db(self):
        self.__logger.info('Downloading DB')
        with closing(requests.get(self.__url, stream=True)) as req:
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
                    self.__filename = outfile_name
                    self.__logger.info('Succeeded in downloading new DB, at <%s>' % self.__filename)
                except IOError:
                    self.__logger.exception('Ran into problems')
                finally:
                    if gz: gz.close()
                    if outfile: outfile.close()
                    if download: download.close()

    def upgrade_db(self):
        self.__download_db()
        if self.__reader:
            self.__reader.close()
        self.__reader = geoip2.database.Reader(self.__filename)

    def lookup(self, ip):
        try:
            city = self.__reader.city(ip)
            return {'country_code': city.country.iso_code, 'continent': city.continent.code}
        except AddressNotFoundError:
            return None
        except ValueError:
            return None

