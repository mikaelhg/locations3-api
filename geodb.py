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
from struct import *
import socket

class GeoDatabase(object):
    """ A MaxMind GeoLite2 geolocation database updater and connector. """

    def __init__(self):
        self.__url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
        self.__filename = None
        self.__reader = None
        self.__logger = logging.getLogger("app.geodb")
        self.upgrade_db()

    def __download_db(self):
        self.__logger.info('Downloading DB')
        headers = {'User-Agent': 'https://github.com/mikaelhg/locations3-api 1.0'}
        with closing(requests.get(self.__url, headers=headers, stream=True)) as req:
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

class EdgeDatabase(object):
    """ An Akamai EdgeScape geolocation server connector. """

    def __init__(self, host='localhost', port=2001):
        self.__host = host
        self.__port = port
        self.__number = 0
        self.__logger = logging.getLogger("app.edgedb")

    def upgrade_db(self):
        pass

    @classmethod
    def __splitmap(cls, mapdata):
        for e in mapdata.split('\x00'):
            if '=' in e:
                yield e.split('=')

    @classmethod
    def __request(cls, number, ip):
        fmt = '>BBHHBB%is' % (len(ip) + 1)
        return pack(fmt, 3, 0, number, 2048, 0, 0, str(ip))

    @classmethod
    def __response(cls, data, num, ip):
        fmt = '>BBHHBB%is%is' % (len(ip), len(data) - len(ip) - 8)
        (version, flags, r_number, length, r_error, reserved, r_ip, mapdata) = unpack(fmt, data)
        if num != r_number or r_error != 0 or ip != r_ip:
            return None
        return {k: v for (k, v) in EdgeDatabase.__splitmap(mapdata)}

    def __query(self, number, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((self.__host, self.__port))
            request = self.__request(number, ip)
            sock.send(request)
            data, addr = sock.recvfrom(1024)
        except socket.error:
            self.__logger.exception('Failed with UDP socket')
            return None
        finally:
            sock.close()
        return self.__response(data, number, ip)

    def lookup(self, ip):
        self.__number += 1
        return self.__query(self.__number, ip)
