#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import pycurl
import StringIO
from collections import namedtuple

CernCert = namedtuple('CernCert', ('sslcert', 'sslkey', 'cainfo'))


def get_cert_curl(cert):
    # NSS_STRICT_NOFORK=DISABLED allows for multiprocessed curl requests with cert
    os.environ['NSS_STRICT_NOFORK'] = 'DISABLED'
    c = pycurl.Curl()

    # cms voms member host certificate to authenticate adqm to cmsweb.cern.ch
    c.setopt(pycurl.SSLCERT, cert.sslcert)
    # cms voms member host certificate key
    c.setopt(pycurl.SSLKEY, cert.sslkey)
    # cern root ca to verify cmsweb.cern.ch
    if cert.cainfo:
        c.setopt(pycurl.CAINFO, cert.cainfo)
    return c


def get_url_with_cert(cert, url):
    b = StringIO.StringIO()
    c = get_cert_curl(cert)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.URL, str(url))
    c.perform()
    content = b.getvalue()
    return content


def get_file_with_cert(cert, url, fname_out):
    c = get_cert_curl(cert)
    c.setopt(pycurl.URL, str(url))
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.NOPROGRESS, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    with open(fname_out, "w") as fhout:
        c.setopt(c.WRITEFUNCTION, fhout.write)
        c.perform()
