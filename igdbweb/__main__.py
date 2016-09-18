#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Description

Usage:
    fill in typical command-line usage

'''
from __future__ import print_function

import os
import sys
import argparse
from flask_frozen import Freezer

from igdbweb import app

import os.path
os.environ['QRSSCREEN_SETTINGS'] = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'config.py')


# pass commandline arguments to flask app
# http://flask.pocoo.org/snippets/133/
#
# Start this app with,
# 	$ python -m igdbweb 
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-H', '--host', default="0.0.0.0",
                        help='Hostname of the Flask app [%default%]')
    parser.add_argument('-P', '--port', default=5000,
                        help='Port for the Flask app  [%default%]')
    parser.add_argument('-d', '--debug', default=False, action="store_true",
                        help='turn on debugging output  [%default%]')

    parser.add_argument('-f', '--freeze', default=False, action="store_true",
                        help="""freeze pages""")
    parser.add_argument('-t', '--template', default='template.jinja',
                        help="""Jinja2 Tempate file[default: %(default)]""")
    parser.add_argument('-c', '--content', default="content",
                        help="""Directory where content can be found: %(default)]""")
    parser.add_argument('-n', '--dryrun', action='store_true',
                        help="""do everythign short of writing to the filesystem.""")
    parser.add_argument('-o', '--output', default=None,
                        help='name of output graph file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='verbose output')

    global options
    options = parser.parse_args()
    print(options)
    app.config['OPTIONS'] = options

    if options.freeze:
        freezer = Freezer(app)
        print(freezer.root)
        freezer.run(
            debug=options.debug,
            host=options.host,
            port=int(options.port)
            )
        freezer.freeze()
    else:
        app.run(
            debug=options.debug,
            host=options.host,
            port=int(options.port)
        )

