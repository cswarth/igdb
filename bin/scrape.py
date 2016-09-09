#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Description

Usage:
    fill in typical command-line usage

'''
from __future__ import print_function

import os
import re
import sys
import json
import errno    
import datetime
import argparse
from bs4 import BeautifulSoup
import requests
import logging
from collections import namedtuple
from jsonschema import validate

try:
    # try importing from python3 package
    from urllib.parse import urljoin
    from urllib.request import urlopen
except:
    from urllib import urlopen
    from urlparse import urljoin

baseurl = 'http://cgi.cse.unsw.edu.au/~ihmmune/IgPdb/Xgene.php'

def mksoup(url):
    # for the most part, this operates the same in both python3.5 and python2.7.
    # relies upon different imports for the two environments.
    if options.verbose:
        print(url)
    r = urlopen(url).read()
    soup = BeautifulSoup(r, "html.parser")
    return soup

# generator for top-level gene URLS
def nextgene(url):
    soup = mksoup(url)

    # r = urllib.urlopen(url).read()
    # soup = BeautifulSoup(r, "html.parser")
    genes = soup.find_all(href=re.compile("Xpoly.php"))
    genes = [urljoin(url, g.get('href')) for g in genes]
    for g in genes:
        yield g


# generator for polymophisms below genes
def nextpoly(url):
    for gene in nextgene(url):
        soup = mksoup(gene)
        poly = soup.find_all(href=re.compile("displayPoly.php"))
        poly = [urljoin(url, p.get('href')) for p in poly]
        for p in poly:
            yield p

IGInfo = namedtuple('IGInfo', ['type', 'family', 'position', 'allele'])
iginfo_regex =  re.compile(r'(?P<family>[^-]{4})[^-]*(-(?P<position>[^\*]*))?\*(?P<allele>.*)')

iginfo_regex =  re.compile(r'.*type=(?P<type>.)&poly=(?P<family>[^-]{4})[^-]*(-(?P<position>[^\*]*))?\*(?P<allele>.*)')

# http://cgi.cse.unsw.edu.au/~ihmmune/IgPdb/displayPoly.php?type=D&poly=IGHD3-16*p03

def parse_id(url):
    # IGHV1-18*p03
    # IGHV1-f*p03
    m = iginfo_regex.match(url)
    if m is not None:
        return IGInfo(**(m.groupdict()))
    print('failed to parse id "{}"'.format(url))
    return None

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def scrape_igpdb(url):
    soup = mksoup(url)
    id = soup.h1.get_text().split()[1]
    iginfo = parse_id(url)
    fasta = list(soup.find('div', class_='seq').stripped_strings)
    sequence = ''.join([s.lower() for s in fasta[1:]])

    data = {
        'id': id,
        'version': '0-0-1',
        'species': 'homo sapien',
        'family': iginfo.family,
        'type': iginfo.type,
        'position': 0,
        'allele': iginfo.allele,
        'created': datetime.datetime.now().isoformat(),
        'last_update': datetime.datetime.now().isoformat(),
        'sequence': sequence,

        #'confidence' : 3,
        #'alignment' : 12,
        #'references': None,
        #'cyst': None,
        #'tryp': None
        }

    return data


def main(argv=sys.argv[1:]):
    p = argparse.ArgumentParser()
    p.add_argument('-s', '--schema', default='ig_schema.json',
            help="""JSON schema file: [ %(default)s ]""")
    p.add_argument('-o', '--outdir', default="content",
            help="""Directory where content should be written: [ %(default)s ]""")
    p.add_argument('-c', '--count', default=0, type=int,
            help="""Process at most N genes.  This is meant for debugging; '0' means process all.: [ '%(default)d' ]""")
    p.add_argument('-n', '--dryrun', action='store_true',
            help="""do everythign short of writing to the filesystem.""")
    p.add_argument('-d', '--debug', action="store_true", default=False,
            help="""enable debug output.  Implies verbose, plus much more.""")
    p.add_argument('-v', '--verbose', action="store_true", default=False,
            help="""enable verbose output""")

    global options
    options = p.parse_args()

    if options.debug:
        options.verbose = True
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    # load the schema used for validation later on.
    with open(options.schema, 'rb') as fp:
        schema = json.load(fp)

    processed = 0
    for poly in nextpoly(baseurl):
        try:
            data = scrape_igpdb(poly)
        except:
            print("failed to parse!!")
            print(poly)
            sys.exit(1)

        # make sure that the data we are about to write out conforms with the expected schema. 
        #validate(data, schema)

        outfile = os.path.join(options.outdir,
                               data['type'].lower(),
                               data['id'].replace('*', '%') + '.json')
        
        if not options.dryrun:
            mkdir_p(os.path.dirname(outfile))
            with open(outfile, 'w') as outfile:
                json.dump(data, outfile, sort_keys=True,
                              indent=4, separators=(',', ': '))
        
        processed += 1
        if options.count > 0 and processed > options.count:
            break


if __name__ == "__main__":
    main(sys.argv[1:])
