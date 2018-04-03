import os, sys
import pycurl 
import StringIO 
import ast
import urllib2
import json
import datetime
from HTMLParser import HTMLParser

import ROOT


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
        for link in self.links[1:]: # First link is Up and should be ignored
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

def get_cert_curl():
    c = pycurl.Curl()
    # cms voms member host certificate to authenticate adqm to cmsweb.cern.ch, defaults to voms-proxy-init certificate
    c.setopt(pycurl.SSLCERT, os.getenv('ADQM_SSLCERT', '/tmp/x509up_u%s' % str(os.getuid())))
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
    c.setopt(pycurl.URL, url) 
    c.perform() 
    content = b.getvalue()
    return content

def get_file_with_cert(url, fname_out):
    c = get_cert_curl() 
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.NOPROGRESS, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    with open(fname_out, "w") as fhout:
        c.setopt(c.WRITEFUNCTION, fhout.write)
        c.perform()

def get_runs(limit, series, sample):

    # Progress bar
    from tqdm import tqdm

    # List to store all run numbers
    runs = []

    # Get HTML content from DQM GUI
    content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/{0}/{1}/".format(series, sample))
    parser = HTMLParserRuns()
    parser.feed(content)
    allRuns = parser.get_run_linktimestamps()
    curdate = datetime.datetime.utcnow()

    # Parse each dqm link, get run number
    for run_link in tqdm(allRuns):
        old_link = run_link[0]
        new_content = get_url_with_cert(run_link[0])
        new_parser = HTMLParserRuns()
        new_parser.clear()
        new_parser.feed(new_content)
        parsed = new_parser.get_run_linktimestamps()

        for new_link in tqdm(parsed):
            split_link = new_link[0].split(old_link)[-1]
            if ".root" not in split_link:
                continue
            run = split_link.split("_")[2]
            run = run.split("R000")[-1]
            runs.append(int(run))
            if len(runs) == limit:
                return sorted(runs, reverse=True)
        
    return sorted(runs, reverse=True)

def fetch(series, sample, run):

    # Silence ROOT warnings
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    # Path to directory containing all data
    main_dir = os.path.dirname(os.path.dirname(os.getcwd()))

    # Get list of files already in database
    db_dir = "{0}/data/database/{1}/{2}".format(main_dir, series, sample)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    dbase = os.listdir(db_dir)

    # Download file if not already in database
    if "{0}.root".format(run) not in dbase:
        content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/{0}/{1}/".format(series, sample))
        parser = HTMLParserRuns()
        parser.feed(content)
        allRuns = parser.get_run_linktimestamps()
        curdate = datetime.datetime.utcnow()

        # Retrieve run if exists
        found = False
        for run_link in allRuns:
            if run[:4] in run_link[0]:
                new_content = get_url_with_cert(run_link[0])
                new_parser = HTMLParserRuns()
                new_parser.clear()
                new_parser.feed(new_content)
                parsed = new_parser.get_run_linktimestamps()

                for new_link in parsed:
                    if run in new_link[0]:
                        found = True
                        get_file_with_cert(new_link[0], "{0}/{1}.root".format(db_dir, run))

        if not found:
            return False, "File not found: {0}".format(run)
        
        return True, None

    # Return if already in database
    else:
        return True, None


if __name__=='__main__':
    pass
    # fetch(run="301531", year="2017", sample="SingleMuon", targ_dir="")
    # print(get_runs(limit=5, year="2017", sample="SingleMuon"))
