# AutoDQM
AutoDQM parses DQM histograms and identifies outliers by various statistical tests for further analysis by the user. Its output can be easily parsed by eye on an AutoPlotter-based html page which is automatically generated when you submit a query from the AutoDQM GUI. Full documentation for AutoDQM can be found on our [wiki](http://github.com/jkguiang/AutoDQM/wiki).

1. [Features](#features)
2. [Setting Up AutoDQM for Development](#setting-up-autodqm-for-development)
3. [Using AutoDQM Offline](#using-autodqm-offline)
4. [Environment Variables](#environment-variables)

## Features

###### AutoDQM.py
- [x] Outputs histograms that clearly highlight outliers
- [x] Creates a .txt file along with each .pdf with relevant information on it
- [x] Allows user to easily change input
- [x] Seeks and accurately finds outliers

###### index.php
- [x] Previews input in a readable way
- [x] Gives a clear indication of the status of a user's query 

###### plots.php
- [x] Dynamically displays text files below AutoPlotter toolbar
- [x] Unique url's for sharing plots pages with the data and reference data set names

## Setting Up AutoDQM for Development

More info in the [wiki](https://github.com/jkguiang/AutoDQM/wiki/Development)

## Using AutoDQM Offline

The `./run-offline.py` script can retrieve run data files and process them without needing a web server. Run `./run-offline.py --help` for all the options.

1. Supply certificate files to the environment variables below. Alternatively, the default uses the files produced when running voms-proxy-init, so that may work instead.
2. Use `./run-offline.py` to process data with AutoDQM

## Environment Variables

- `ADQM_CONFIG` location of the configuration file to use
- `ADQM_DB` location to store downloaded root files from offline DQM
- `ADQM_TMP` location to store generated temporary pdfs, pngs, etc
- `ADQM_SSLCERT` location of CMS VO authorized public key certificate to use in querying offline DQM
- `ADQM_SSLKEY` location of CMS VO authorized private ky to use in querying offline DQM
- `ADQM_CACERT` location of a CERN Grid CA certificate chain, if needed

