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
import datetime
from bs4 import BeautifulSoup
import requests
import logging
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


def main(argv=sys.argv[1:]):
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    for (i, poly) in enumerate(nextpoly(baseurl)):
        print("opening {}".format(poly))

        soup = mksoup(poly)
        name = soup.h1.get_text().split()[1]
        fasta = list(soup.find('div', class_='seq').stripped_strings)
        sequence = ''.join([s.lower() for s in fasta[1:]])
        print("sequence {}".format(sequence))

        data = {
            "id": name,
            "version": "1",
            "created": datetime.datetime.now().isoformat(),
            "last_update": datetime.datetime.now().isoformat(),
            "sequence": sequence,
            "references": None,
            "cyst": None,
            "tryp": None
        }

        fname = name.replace('*', '%') + '.json'
        with open(os.path.join("content", fname), 'w') as outfile:
            json.dump(data, outfile, sort_keys=True,
                      indent=4, separators=(',', ': '))


if __name__ == "__main__":
    main(sys.argv[1:])
