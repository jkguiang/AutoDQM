#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import errno
import json
import lxml.html
import os
import requests
from collections import namedtuple
from requests_futures.sessions import FuturesSession

TIMEOUT = 5

BASE_URL = 'https://cmsweb.cern.ch'
DQM_URL = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'

StreamProg = namedtuple('StreamProg', ('cur', 'total', 'path'))
DQMRow = namedtuple('DQMRow', ('name', 'full_name', 'url', 'size', 'date'))


def fetch_run(series, sample, run, cert, db='./db/'):
    """Fetch and cache a run data file.

    Returns the path to the downloaded file."""
    dl = stream_run(series, sample, run, cert, db=db)

    # Get the path from the first yield
    path = next(dl).path

    # Finish the download
    for _ in dl:
        pass
    return path


def stream_run(series, sample, run, cert, db='./db/', chunk_size=4096):
    """Stream and cache a run data file.

    Returns a generator that yields StreamProg tuples corresponding to the
    download progress."""
    run_path = _run_path(db, series, sample, run)
    run_dir = os.path.dirname(run_path)

    if not os.path.exists(run_path):
        _try_makedirs(run_dir)

        runs = fetch_run_list(series, sample, cert)
        run_info = next(r for r in runs if r.name == run)

        for prog in _stream_file(cert, run_info.url, run_path,
                                 chunk_size=chunk_size):
            yield prog

    size = os.path.getsize(run_path)
    yield StreamProg(size, size, run_path)


def fetch_series_list(cert, cache='./db/dqm_offline/'):
    """Return DQMRows corresponding to the series available on DQM Offline."""
    return _fetch_dqm_rows(DQM_URL, cert)


def fetch_sample_list(series, cert, cache='./db/dqm_offline/'):
    """Return DQMRows corresponding to the samples available under the given
    series."""
    series_rows = fetch_series_list(cert, cache=cache)
    url = next((r.url for r in series_rows if r.name == series))
    return _fetch_dqm_rows(url, cert)


def fetch_run_list(series, sample, cert,
                   cache='./db/dqm_offline/', workers=16):
    """Return DQMRows corresponding to the runs available under the given
    series and sample."""
    _try_makedirs(cache)
    sample_rows = fetch_sample_list(series, cert, cache=cache)
    sample_url = next((r.url for r in sample_rows if r.name == sample))

    # Get all run directories for this sample
    macrorun_rows = _fetch_dqm_rows(sample_url, cert)
    to_req = []

    # Determine which run directories are cached
    run_rows = []
    for mr in macrorun_rows:
        rows = _get_cache(cache, mr)
        if rows:
            run_rows += rows
        else:
            to_req.append(mr)

    # Callback to process dqm responses
    def cb(sess, resp):
        resp.data = _parse_dqm_page(resp.text)

    # Request uncached directories from the servers
    with FuturesSession(max_workers=workers) as rsess:
        rsess.cert = cert
        futures = [(mr, rsess.get(mr.url, background_callback=cb))
                   for mr in to_req]
        for mr, fut in futures:
            rows = fut.result().data
            run_rows += rows
            _write_cache(cache, mr, rows)

    return run_rows


def _get_cache(cache, parent_row):
    """Return the DQM page corresponding to parent_row as DQMRows if they are
    cached. Otherwise None."""
    cache_file = _cache_path(cache, parent_row)
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            dat = json.load(f)
            return [DQMRow(*r) for r in dat]
    else:
        return None


def _write_cache(cache, parent_row, dqm_rows):
    """Write a list of DQMRows to the cache under their parent_row."""
    cache_file = _cache_path(cache, parent_row)
    _try_makedirs(os.path.dirname(cache_file))
    with open(cache_file, 'w') as f:
        json.dump(dqm_rows, f)


def _cache_path(cache, parent_row):
    """Return the path to a cached DQM page specified by its parent DQMRow."""
    return os.path.join(cache, str(abs(hash(parent_row))))


def _fetch_dqm_rows(url, cert, timeout=TIMEOUT):
    """Return the DQMRows of a DQM page at url."""
    try:
        text = requests.get(url, cert=cert, timeout=timeout).text
    except requests.ConnectionError as e:
        raise error(e)
    except requests.Timeout as e:
        raise error(e)
    return _parse_dqm_page(text)


def _stream_file(cert, url, dest, chunk_size=4096):
    """Stream a file into a destination path.

    Returns a generator of StreamProg tuples to indicate download progress."""
    res = requests.get(url, cert=cert, stream=True)
    if not res:
        raise error("Failed to download file: {}".format(url))
    total = int(res.headers.get('content-length'))
    cur = 0
    with open(dest, 'wb') as f:
        for data in res.iter_content(chunk_size=chunk_size):
            cur += len(data)
            f.write(data)
            yield StreamProg(cur, total, dest)
    if cur != total:
        os.remove(dest)
        raise error("Failed to stream file: Final size {} less than total {}"
                    .format(cur, total))


def _parse_dqm_page(content):
    """Return the contents of a DQM series, sample, or macrorun page as a list
    of DQMRows."""
    dqm_rows = []
    tree = lxml.html.fromstring(content)
    tree.make_links_absolute(BASE_URL)

    for tr in tree.xpath('//tr'):
        td_strs = tr.xpath('td//text()')
        td_urls = tr.xpath('td/a/@href')

        full_name = td_strs[0]
        url = td_urls[0]
        size = int(td_strs[1]) if td_strs[1] != '-' else None
        date = td_strs[2]
        name = _parse_run_full_name(full_name) if size else full_name[:-1]

        dqm_rows.append(DQMRow(name, full_name, url, size, date))

    return dqm_rows


def _parse_run_full_name(full_name):
    """Return the simplified form of a full DQM run name.

    example:
    DQM_V0001_R000316293__ZeroBias__Run2018A-PromptReco-v2__DQMIO.root
    => 316293
    """
    name = full_name.split('_')[2][1:]
    return str(int(name))


def _run_path(db, series, sample, run):
    """Return the path to the specified run data file in the cached db."""
    return "{}/{}.root".format(os.path.join(db, series, sample), run)


def _try_makedirs(*args, **kwargs):
    """Make a directory if it doesn't exist"""
    try:
        return os.makedirs(*args, **kwargs)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class error(Exception):
    pass
