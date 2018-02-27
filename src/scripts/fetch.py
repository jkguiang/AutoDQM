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
        for link in self.links:
            # if "/000" not in link: continue
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
    c.setopt(pycurl.NOPROGRESS, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    with open(fname_out, "w") as fhout:
        c.setopt(c.WRITEFUNCTION, fhout.write)
        c.perform()

def get_runs(limit, year, sample):

    # Progress bar
    from tqdm import tqdm

    # List to store all run numbers
    runs = []

    # Get HTML content from DQM GUI
    content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run{0}/{1}/".format(year, sample))
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

# Check to ensure config file is properly set up, compile into smaller root file with only subsystem-related histograms
def compile(run, config, targ_dir, f, new_f):

    # Load configs
    main_gdir = config["main_gdir"].format(run)
    hists = config["hists"]

    # Loop over all histograms, compile into smaller root file
    for hist in hists:
        # Clear new_hist variable - loop checks for existence of new_hist to determine success
        new_hist = None

        # Get output name for histogram (if "" or None, name of hist is not changed)
        name_out = hist["name_out"]

        # Get name of hist
        h = hist["path"].split("/")[-1]
        # Get path to hist
        gdir = hist["path"].split(h)[0]

        # Reset current directory to f
        f.cd()

        # Generate map of histograms for wildcard searches:
        # Get keys of directory
        keys = f.GetDirectory("{0}{1}".format(main_gdir, gdir))
        h_map = []
        # Populate map
        for key in keys.GetListOfKeys():
            h_map.append(key.GetName())

        # Wildcard search
        if "*" in h:
            # Check entire directory for files matching wildcard
            for name in h_map:
                if h.split("*")[0] in name:
                    new_hist = f.Get("{0}{1}{2}".format(main_gdir, gdir, name))
                    if new_hist:
                        # Rename hist if output name given
                        if name_out:
                            new_hist.SetName(name_out)
                        else:
                            hist["name_out"] = new_hist.GetName()
                        new_f = ROOT.TFile("{0}/{1}.root".format(targ_dir, run), "update")
                        new_f.cd()
                        new_hist.Write()
                        new_f.Close()
                    else:
                        return False, "File not found: {0}".format(hist)
        # Normal search
        else:
            new_hist = f.Get("{0}{1}{2}".format(main_gdir, gdir, h))
            if new_hist:
                # Rename hist if output name given
                if name_out:
                    new_hist.SetName(name_out)
                else:
                    hist["name_out"] = new_hist.GetName()
                new_f = ROOT.TFile("{0}/{1}.root".format(targ_dir, run), "update")
                new_f.cd()
                new_hist.Write()
                new_f.Close()
            else:
                return False, "File not found: {0}".format(hist)

    # Update config with new name_out's
    config["hists"] = hists
    with open("{0}/data/configs.json".format(main_dir), "w") as fhout:
        json.dump(config, fhout, sort_keys = True, indent = 4, separators = (',', ':'))

    f.Close()
    return True, None

def fetch(run, sample, targ_dir):

    # Silence ROOT warnings
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    # Path to directory containing all data
    main_dir = os.path.dirname(os.path.dirname(os.getcwd()))

    # Load configs
    with open("{0}/data/configs.json".format(main_dir)) as config_file:
        config = json.load(config_file)
    year = config["year"]

    # Get list of files already in database
    db_dir = "{0}/data/database/Run{1}/{2}".format(main_dir, year, sample)
    dbase = os.listdir(db_dir)

    # Download file if not already in database
    if "{0}.root".format(run) not in dbase:
        content = get_url_with_cert("https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/Run{0}/{1}/".format(year, sample))
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

        #Retrieve downloaded file from database
        f = ROOT.TFile.Open("{0}/{1}.root".format(db_dir, run))

    # Retrieve file from database
    else:
        f = ROOT.TFile.Open("{0}/{1}.root".format(db_dir, run))

    # Compile root file into smaller root file ONLY if user passes in a target directory
    if targ_dir:
        # Create new .root file to be compiled, recreate if it alread exists
        new_f = ROOT.TFile("{0}/{1}.root".format(targ_dir, run), "recreate")
        new_f.Close()

        # Check configs.json to make sure all histogram objects exist, compile into smaller .root file
        return(compile(run, config, targ_dir, f, new_f))
    else:
        f.Close()
        return True, None

if __name__=='__main__':
    # fetch(run="301531", year="2017", sample="SingleMuon", targ_dir="")
    print(get_runs(limit=20, year="2017", sample="SingleMuon"))
