#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
JSON schema testing
http://json-schema.org/
https://spacetelescope.github.io/understanding-json-schema/index.html


Usage:
    fill in typical command-line usage

'''
from __future__ import print_function

import os
import sys
import json
import argparse

from jsonschema import validate

# Generate the names of all json input files under `dir`, yielding each
# one in turn until there are no more files left to process.
def content_file_iterator(dir="content"):
    for root, dirs, files in os.walk(dir):
        for f in files:
            if os.path.splitext(f)[1] == '.json':
                yield os.path.join(root, f)


# http://stackoverflow.com/a/3172940/1135316
def flatten(alist):
    for item in alist:
        if isinstance(item, list):
            for subitem in item: yield subitem
        else:
            yield item
                
def main(argv=sys.argv[1:]):
    def existing_file(fname):
        """
        Argparse type for an existing file
        """
        if not (os.path.isfile(fname) or os.path.isdir(fname)) :
            raise ValueError("Invalid file or directory: " + str(fname))
        return fname

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--schema', default='ig_schema.json',
            help="""JSON schema file: %(default)]""")
    parser.add_argument('-v', '--verbose', default=False,
            help="""enable verbose output""")
    parser.add_argument("files", nargs='+', help='json files to be validated', type=existing_file)

    global options
    options = parser.parse_args()

    # load the schema
    try:
        with open(options.schema, 'rb') as fp:
            schema = json.load(fp)
    except ValueError as e:
        print('parse error while reading schema file "{}"'.format(options.schema), file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)

    # expand any directories in command line args into unique list of files.
    files = [ list(content_file_iterator(f)) if os.path.isdir(f) else f for f in options.files]
    files = set(flatten(files))
        
    for f in files:
        with open(f, 'rb') as fp:
            content = json.load(fp)
            if type(content) == dict:
                print("{} - {}".format(f, validate(content, schema) is None))

if __name__ == "__main__":
   main(sys.argv[1:])
   


