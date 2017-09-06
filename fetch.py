import os, sys
import pycurl 
import StringIO 
import ast
import urllib2
import json
import datetime
import pprint
from HTMLParser import HTMLParser


class HTMLParserRuns(HTMLParser):
    """
    parses pages with formatting like
    https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/StreamExpress/0003019xx/
    >>> parser = HTMLParserRuns()
    >>> parser.feed(content)
    >>> pprint.pprint(parser.get_run_linktimestamps())
    """
    links = []
    timestamps = []
    BASE_URL = "https://cmsweb.cern.ch"
    cur_tag = None
    def handle_starttag(self, tag, attrs):
        self.cur_tag = tag
        if tag == "a":
            self.links.append(dict(attrs)["href"])

    def handle_data(self, data):
        if self.cur_tag == "td":
            if "UTC" in data:
                self.timestamps.append(datetime.datetime.strptime(data.strip(), "%Y-%m-%d %H:%M:%S %Z"))

    def get_run_links(self):
        new_links = []
        for link in self.links:
            if "/000" not in link: continue
            new_links.append(self.BASE_URL + link)
        return new_links

    def get_run_timestamps(self):
        return self.timestamps

    def get_run_linktimestamps(self):
        """
        return list of pairs of (link to run, UTC timestamp)
        Note that timestamp should be compared to datetime.datetime.utcnow() to see 
        if the folder has been updated
        """
        new_pairs = []
        for link,ts in zip(self.get_run_links(), self.get_run_timestamps()):
            if ".root" in link and "DQMIO" not in link: continue
            new_pairs.append([link,ts])
        return new_pairs

    def clear(self):
        self.links = []
        self.timestamps = []

def get_proxy_file():
    cert_file = '/tmp/x509up_u%s' % str(os.getuid())
    return cert_file

def curl_progress(total_to_download, total_downloaded, total_to_upload, total_uploaded):
    if total_to_download:
        to_print = progress_bar(1.0*total_downloaded/total_to_download)
        sys.stdout.write("\r"+to_print)
        sys.stdout.flush()

def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return [v, v, v]
    i = int(h*6.)
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return [v, t, p]
    elif i == 1: return [q, v, p]
    elif i == 2: return [p, v, t]
    elif i == 3: return [p, q, v]
    elif i == 4: return [t, p, v]
    elif i == 5: return [v, p, q]

def progress_bar(fraction, width=40, do_color=True, do_unicode=True,override_color=[]):
    fraction = min(max(fraction, 0.), 1.)
    nfilled = int(fraction * width)
    color_open, color_close = "", ""
    filled = "#"*nfilled
    unfilled = "-"*(width-nfilled)
    if do_unicode:
        filled = unichr(0x2589).encode('utf-8') * nfilled
        unfilled = unichr(0x2594+24).encode('utf-8')*(width-nfilled)

    if do_color:
        if override_color:
            rgb = override_color
        else:
            rgb = hsv_to_rgb(1.0 / 3.6 * fraction, 0.9, 0.9)
        color_open = "\033[38;2;%i;%i;%im" % tuple(rgb)
        color_close = "\033[0m"
    return "|{0}{1}{2}{3}| [{4:.1f}%]".format(color_open,filled, color_close,unfilled,100.0*fraction)

def get_url_with_cert(url):
    b = StringIO.StringIO() 
    c = pycurl.Curl() 
    cert = get_proxy_file()
    c.setopt(pycurl.WRITEFUNCTION, b.write) 
    c.setopt(pycurl.CAPATH, '/etc/grid-security/certificates') 
    c.unsetopt(pycurl.CAINFO)
    c.setopt(pycurl.SSLCERT, cert)
    c.setopt(pycurl.URL, url) 
    c.perform() 
    content = b.getvalue()
    return content

def get_file_with_cert(url, fname_out):
    c = pycurl.Curl() 
    cert = get_proxy_file()
    c.setopt(pycurl.CAPATH, '/etc/grid-security/certificates') 
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.SSLCERT, cert)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.unsetopt(pycurl.CAINFO)
    c.setopt(pycurl.NOPROGRESS, 0)
    c.setopt(pycurl.PROGRESSFUNCTION, curl_progress)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    with open(fname_out, "w") as fhout:
        c.setopt(c.WRITEFUNCTION, fhout.write)
        c.perform()

def fetch():
    print("Fetching DQM files...")
    # content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/SingleMuon/0003019xx/")
    # old_content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/SingleMuon/0003022xx/")
    content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/SingleMuon/")
    # print get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/StreamExpress/")
    # print get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/StreamExpress/0003019xx/")

    parser = HTMLParserRuns()
    parser.feed(content)
    allRuns = parser.get_run_linktimestamps()
    curdate = datetime.datetime.utcnow()

    toParse = []

    # Check for new runs
    for link in allRuns:
        linkdate = link[1]
        if linkdate.month == curdate.month and linkdate.day == curdate.day:
            toParse.append(link[0])

    # Parse new runs for new root files
    for url in toParse:
        print(url)
        new_content = get_url_with_cert(url)
        new_parser = HTMLParserRuns()
        new_parser.clear()
        new_parser.feed(new_content)
        parsedLst = new_parser.get_run_linktimestamps()

        for new_link in parsedLst:
            fname = new_link[0].split("DQM")[1].split("_")[2].split("R000")[1]
            linkdate = new_link[1]

            if linkdate.month == curdate.month and linkdate.day == curdate.day:
                fname = new_link[0].split("DQM")[1].split("_")[2].split("R000")[1]
                print("\nNew file found: {0}\nFile date: {1}        Current date: {2}\n".format(fname, linkdate, curdate))
                print("url: {0}".format(new_link[0]))
                get_file_with_cert(new_link[0], "root_files/{0}.root".format(fname))

    print("\n")


if __name__=='__main__':
    fetch()
