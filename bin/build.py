#!/usr/bin/env python
# to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
# first copy index.html tp the `site/` directory
# Cribbed from https://gist.github.com/cobyism/4730490
#    git subtree push --prefix site origin gh-pages

from __future__ import print_function

from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.util.browser import view
from bokeh.models import Legend
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Spectral11

import os
import sys
import json
import argparse
import datetime
import getpass
import hashlib
import collections
import pandas as pd
from cStringIO import StringIO
from jinja2 import Environment, FileSystemLoader

from collections import OrderedDict
from collections import defaultdict

genes = defaultdict(dict)

class Gene(defaultdict):
    def __init__(self, name=None):
        super(Gene, self).__init__(self, dict)

    def load():
        pass
    
    def render():
        pass


# convert a dict to an appropriate gene page.
def render_page(filename):
    env = Environment(loader=FileSystemLoader(THIS_DIR),
                          trim_blocks=True)
    # Alias str.format to strformat in template
    env.filters['strformat'] = str.format
    template = env.get_template("templates/gene.jinja")

    renderdict = {
        'date':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'command':" ".join(sys.argv),
        'workdir':os.getcwd(),
        'user':getpass.getuser(),
        'title':"IgDB"
        }

    page = None
    with open(filename, 'rb') as fp:
        obj = json.load(fp)
        if type(obj) is dict:
            renderdict.update(obj)
            page = template.render(**renderdict) 
            
    return page

    # to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
    # first copy index.html tp the `site/` directory
    # Cribbed from https://gist.github.com/cobyism/4730490
    #    git subtree push --prefix site origin gh-pages
    # if a.view:
    #     view(a.outfile)


# Generate the names of all json gene files under `dir`, yielding each
# one in turn until there are no more files left to process.
def content_file_iterator(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            if os.path.splitext(f)[1] == '.json':
                yield os.path.join(root, f)


# Capture parent directory above 'templates/'
THIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--template', default='template.jinja',
            help="""Jinja2 Tempate file[default: %(default)]""")
    p.add_argument('-c', '--content', default="content",
            help="""Directory where content can be found (relative of absolute): %(default)]""")
    p.add_argument('-o', '--output', default="output",
            help="""Directory where output should be left: %(default)]""")
    p.add_argument('-n', '--dryrun', action='store_true',
            help="""dry run""")
    p.add_argument('-v', '--verbose', default=False,
            help="""enable verbose output""")
    a = p.parse_args()

    # read in JSON file

    # produce web page and various download files.
    # web page should be allowed to download any of the available formats.
    
    # Read the index
    # produce individual pages
    # Each has the name, sequence, evidence,and dowload links
    # produce the downloadable content
    # filterable?
    for f in content_file_iterator(a.content):
        page = render_page(f)
        if page is not None:
            html = page.encode('utf-8')
            digest = hashlib.sha1(html).hexdigest()
            print('{} -> {}'.format(f, digest))
            if not a.dryrun:
                with open(os.path.join(a.output, digest), "w") as f:
                    f.write(html)
                    

    
    # idx = pd.read_csv(os.path.join(a.content, 'index.csv'))
    # for row in idx.itertuples(index=False):
    #     print(row)

    #     page = render_page(**row._asdict())
    #     html = page.encode('utf-8')
    #     digest = hashlib.sha1(html).hexdigest()
    #     with open(os.path.join(a.output, digest), "w") as f:
    #         f.write(html)
        

    # create the index page that has a link to all the pages just created.



    
if __name__ == '__main__':
    main()

            


