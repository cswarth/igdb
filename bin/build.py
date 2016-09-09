#!/usr/bin/env python
# to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
# first copy index.html tp the `site/` directory
# Cribbed from https://gist.github.com/cobyism/4730490
#    git subtree push --prefix site origin gh-pages

from __future__ import print_function


import os
import sys
import json
import argparse
import datetime
import getpass
import hashlib
import pandas as pd
from cStringIO import StringIO
from jinja2 import Environment, FileSystemLoader

from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC

# global options dict for command line arguments
options = dict()

def load_template(name):
    # Capture parent directory above where this script lives.  
    parent = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    templatedir = os.path.join(parent, 'templates')
    env = Environment(loader=FileSystemLoader(templatedir),
                          trim_blocks=True)
    # Alias str.format to strformat in template
    env.filters['strformat'] = str.format
    template = env.get_template(name)
    return template

class Gene(object):
    template = load_template('gene.jinja')
    
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
        self.data = data


    # Write a FASTA file containing the gene id and nucleotide sequence.
    # If `options.dryrun` is TRUE, don't actually write the file, but do everything else.
    #
    # return: string name of the fasta file.
    def render_fasta(self):
        print(self.data['id'])

        def to_fasta(seq):
            fp = StringIO()
            record = SeqRecord(Seq(seq, IUPAC.extended_dna),
                                   id=self.data['id'], description="")
            SeqIO.write(record, fp,
                    'fasta')
            return fp.getvalue()

        
        fasta = to_fasta(self.data['sequence'])
        
        digest = hashlib.sha1(fasta).hexdigest()
        print('fasta -> {}'.format(digest))
        outname = os.path.join(options.output, digest)
        if not options.dryrun:
            with open(outname, "w") as f:
                f.write(fasta)

        self.data['fastafile'] = digest
        return outname
        

    # Write a PHYLIP file containing the gene id and nucleotide sequence.
    # If `options.dryrun` is TRUE, don't actually write the file, but do everything else.
    #
    # return: string name of the fasta file.
    def render_phylip(self):
        print(self.data['id'])

        def to_phylip(seq):
            fp = StringIO()
            seq = seq.replace('.', '-')
            record = SeqRecord(Seq(seq, IUPAC.extended_dna),
                                   id=self.data['id'])
            SeqIO.write(record, fp, 'phylip-relaxed')
            return fp.getvalue()

        
        fasta = to_phylip(self.data['sequence'])
        
        digest = hashlib.sha1(fasta).hexdigest()
        print('phylip -> {}'.format(digest))
        outname = os.path.join(options.output, digest)
        if not options.dryrun:
            with open(outname, "w") as f:
                f.write(fasta)

        self.data['phylipfile'] = digest
        return outname
        

    # Render this gene through jinja template to produce HTML file.
    # If `options.dryrun` is TRUE, don't actually write the file, but do everything else.
    #
    # return: string name of the html file.
    def render_html(self):
        renderdict = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'command': " ".join(sys.argv),
            'workdir': os.getcwd(),
            'user': getpass.getuser(),
            'title': 'IgDB',
        }
                
        renderdict.update(self.data)
        page = Gene.template.render(**renderdict) 
        html = page.encode('utf-8')

        # write the html to a file named with the sha1 hash of its contents.
        digest = hashlib.sha1(html).hexdigest()
        print('{} -> {}'.format(self.data['id'], digest))
        outname = os.path.join(options.output, digest)
        if not options.dryrun:
            with open(outname, "w") as f:
                f.write(html)
        self.htmlfile = digest
        return outname


# Generate the names of all json input files under `dir`, yielding each
# one in turn until there are no more files left to process.
def content_file_iterator(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            if os.path.splitext(f)[1] == '.json':
                yield os.path.join(root, f)



def main():
    p = argparse.ArgumentParser()
    p.add_argument('-t', '--template', default='template.jinja',
            help="""Jinja2 Tempate file[default: %(default)]""")
    p.add_argument('-c', '--content', default="content",
            help="""Directory where content can be found: %(default)]""")
    p.add_argument('-o', '--output', default="output",
            help="""Directory where output should be left: %(default)]""")
    p.add_argument('-n', '--dryrun', action='store_true',
            help="""do everythign short of writing to the filesystem.""")
    p.add_argument('-v', '--verbose', default=False,
            help="""enable verbose output""")

    global options
    print(type(options))
    options = p.parse_args()
    print(type(options))

    # read in JSON file

    # produce web page and various download files.
    # web page should be allowed to download any of the available formats.

    objects = [Gene.fromfile(f) for f in content_file_iterator(options.content)]
    objects = [o for o in objects if o is not None]
    for g in objects:
        if g is not None:
            g.render_fasta()
            g.render_phylip()
            g.render_html()



    # render the index page
    renderdict = {
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'command': " ".join(sys.argv),
        'workdir': os.getcwd(),
        'user': getpass.getuser(),
        'title': 'IgDB',
        'genes': objects
        }
    print(objects)
    index_tpl = load_template('index.jinja')
    page = index_tpl.render(**renderdict) 
    html = page.encode('utf-8')
    print(html)
    outname = os.path.join(options.output, 'index.html')
    if not options.dryrun:
            with open(outname, "w") as f:
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

            


