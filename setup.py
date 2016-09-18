from setuptools import setup, find_packages

setup(name='igdbweb',
      version='0.1.0',
      description='Immunoglobin germline web interface',
      author='Chris Warth <cwarth@fredhutch.org>',
      packages=find_packages('igdbweb'),
      package_data={'igdbweb': ['templates/*']},
      )
