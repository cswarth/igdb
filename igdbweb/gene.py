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
import json
from jinja2 import Environment, FileSystemLoader

def load_template(name):
    # Capture parent directory above where this script lives.  
    parent = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    print("__file__ = {}".format(__file__))
    print("os.path.dirname(__file__) = {}".format(os.path.dirname(__file__)))
    print("parent = {}".format(parent))
    templatedir = os.path.join(parent, 'templates')
    env = Environment(loader=FileSystemLoader(templatedir),
                          trim_blocks=True)
    # Alias str.format to strformat in template
    env.filters['strformat'] = str.format
    template = env.get_template(name)
    return template

class Gene(object):
    @classmethod
    def fromfile(cls, filename):
        gene = None
        with open(filename, 'rb') as fp:
            data = json.load(fp)
            if type(data) is dict:
                gene = cls(data)
        return gene
    
    def __init__(self, data):
        super(Gene, self).__init__()
        self.__dict__.update(data)


        

