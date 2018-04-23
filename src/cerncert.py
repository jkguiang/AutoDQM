import os
import pycurl
import StringIO


def get_cert_curl():
    # NSS_STRICT_NOFORK=DISABLED allows for multiprocessed curl requests with cert
    os.environ['NSS_STRICT_NOFORK'] = 'DISABLED'
    c = pycurl.Curl()
    
    # cms voms member host certificate to authenticate adqm to cmsweb.cern.ch
    c.setopt(pycurl.SSLCERT, os.getenv('ADQM_SSLCERT'))
    
    # cms voms member host certificate key
    if 'ADQM_SSLKEY' in os.environ:
        c.setopt(pycurl.SSLKEY, os.getenv('ADQM_SSLKEY'))
    # cern root ca to verify cmsweb.cern.ch
    if 'ADQM_CERNCA' in os.environ:
        c.setopt(pycurl.CAINFO, os.getenv('ADQM_CERNCA'))
    return c


def get_url_with_cert(url):
    b = StringIO.StringIO()
    c = get_cert_curl()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.URL, str(url))
    c.perform()
    content = b.getvalue()
    return content


def get_file_with_cert(url, fname_out):
    c = get_cert_curl()
    c.setopt(pycurl.URL, str(url))
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.NOPROGRESS, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    with open(fname_out, "w") as fhout:
        c.setopt(c.WRITEFUNCTION, fhout.write)
        c.perform()
