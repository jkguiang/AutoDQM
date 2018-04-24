#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import datetime
import cerncert
from HTMLParser import HTMLParser
from urlparse import urljoin
from multiprocessing import Pool

class DQMParser(HTMLParser):
    """
    parses pages with formatting like
    https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run2017/StreamExpress/0003019xx/
    >>> parser = DQMParser()
    >>> parser.feed(content)
    >>> pprint.pprint(parser.get_run_linktimestamps())
    """
        
    BASE_URL = "https://cmsweb.cern.ch"
    
    def __init__(self):
        HTMLParser.__init__(self)
        
        self.rows = []
        
        self.in_tr = False
        self.in_td = False
        self.in_a = False

        self.name = None
        self.link = None
        self.timestamp = None
    
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.in_tr = True
        elif tag == 'td':
            self.in_td = True
        elif tag == "a":
            self.in_a = True
            if self.in_tr and self.in_td:
                self.link = urljoin(self.BASE_URL, dict(attrs)["href"])

    def handle_data(self, data):
        if self.in_tr and self.in_td and self.in_a:
            self.name = data
        elif self.in_tr and self.in_td and "UTC" in data:
            self.timestamp = datetime.datetime.strptime(data.strip(), "%Y-%m-%d %H:%M:%S %Z")
    
    def handle_endtag(self, tag):
        if tag == 'tr':
            self.in_tr = False
            self.add_row()
        elif tag == 'td':
            self.in_td = False
        elif tag == "a":
            self.in_a = False

    def add_row(self):
        if self.name and self.link and self.timestamp:
            if self.name[-1] == '/': self.name = self.name[:-1]
            self.rows.append({"name": self.name, "url": self.link, "timestamp": self.timestamp.isoformat()})
            self.name = self.link = self.timestamp = None
        else: 
            raise Exception("Malformed row found, name: {0}, link: {1}, timestamp: {2}".format(self.name, self.link, self.timestamp))

    def get_rows(self):
        return self.rows


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

def get_file(url, outname):
    cerncert.get_file_with_cert(url, outname)

# Grabs a DQM directory page and parses it into a list of row dicts
def get_page(url):
    content = cerncert.get_url_with_cert(url)
    parser = DQMParser()
    parser.feed(content)
    return parser.get_rows()

def hash_page(url, timestamp):
    return str(hash(url + timestamp))[1:]

# Grabs a DQM directory page from the cache if the url and timestamp match
# Otherwise grabs the page and adds it to the cache
def get_cache(url, timestamp):
    cache_dir = os.environ['ADQM_TMP'] + 'dqm_cache/'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        
    hashed = hash_page(url, timestamp)
    try:
        with open(cache_dir + hashed) as f:
            page = json.load(f)
    except:
        page = get_page(url)
        with open(cache_dir + hashed, 'w') as f:
            json.dump(page, f)
    return page

def clean_run_fname(fname):
    return fname.split('_')[2][4:]

def get_series():
    return get_page("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/") 

def get_samples(series):
    return get_page("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/{0}/".format(series))

# Bit of a hack to supply a function to Pool.map
# Could be changed by switching Pool libraries
# Unfortunate that native Pool doesn't support lambdas
class GetRunDir(object):
    def __init__(self, runDirs):
        self.runDirs = runDirs
    def __call__(self, i):
        return get_cache(self.runDirs[i]['url'], self.runDirs[i]['timestamp'])

def get_runs(series, sample):
    runDirs = get_page("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/{0}/{1}/".format(series, sample))
    runs = []
    
    # Setup a pool to parallize getting run directories, 64 is mostly arbitrary
    pool = Pool(64)
    run_arrs = pool.map(GetRunDir(runDirs), range(len(runDirs)))

    # Flatten results of pool
    runs = [r for run_arr in run_arrs for r in run_arr]

    # Filter out non DQMIO runs
    runs = [r for r in runs if 'DQMIO' in r['name']]
    for run in runs:
        run['name'] = clean_run_fname(run['name'])
    return runs

def fetch(series, sample, run):

    # Path to directory containing all data
    db = os.getenv('ADQM_DB')
    if not os.path.exists(db):
        os.makedirs(db)

    # Get list of files already in database
    db_dir = "{0}/{1}/{2}".format(db, series, sample)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    dbase = os.listdir(db_dir)

    # Download file if not already in database
    if "{0}.root".format(run) not in dbase:
        found = False
        runRows = get_runs(series, sample)
        for r in runRows:
            if str(run) == r["name"]:
                found = True
                get_file(r["url"], "{0}/{1}.root".format(db_dir, run))

        if not found:
            return False, "Series: {0}, sample: {1}, run: {2} not found on offline DQM".format(series, sample, run)
        
        return True, None

    # Return if already in database
    else:
        return True, None


if __name__=='__main__':
    pass
    # fetch(run="301531", year="2017", sample="SingleMuon", targ_dir="")
    # print(get_runs(limit=5, year="2017", sample="SingleMuon"))
