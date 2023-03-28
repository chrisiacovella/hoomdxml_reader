hoomdxml_reader
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/chrisiacovella/hoomdxml_reader/workflows/CI/badge.svg)](https://github.com/chrisiacovella/hoomdxml_reader/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/chrisiacovella/hoomdxml_reader/branch/main/graph/badge.svg)](https://codecov.io/gh/chrisiacovella/hoomdxml_reader/branch/main)


# A lightweight module to read legacy hoomdxml files and GSD files and convert to mbuild Compounds.
Provides basic routines to read and extract information included in hoomdxml files and GSD files, and provides routines to convert to [mbuild](https://github.com/mosdef-hub/mbuild) ``Compounds``.  While there are other packages do support reading hoomdxml files, they do not parse all sections of the file. This code will also perform grouping of atoms into molecules based on connectivity.   

* [Documentation](https://hoomdxml-reader.readthedocs.io/en/latest/)

Other relevant links:

* [mBuild](https://github.com/mosdef-hub/mbuild)
* [HOOMD-blue](http://glotzerlab.engin.umich.edu/hoomd-blue/)
* [GSD](http://gsd.readthedocs.io)

## Installation 

Check out the source from the github repository:

    $ git clone https://github.com/chrisiacovella/hoomdxml_reader.git

In the top level of hoomdxml_reader directory, use pip to install:

    $ pip install -e .

The core functions of the module will require ``networkx`` to be installed.
To create an environment named hoomdxml_reader with this necessary package,
run the following from the top level of the  hoomdxml_reader directory.

    $ conda env create -f environment.yml

Optional packages
----------------
While not necessary to use the core functions of the Module, conversion to an mBuild ``Compound``, requires [mbuild](https://mbuild.mosdef.org/en/stable/getting_started/installation/installation.html) to be installed.

    $ conda install -c conda-forge mbuild

To visualize mbuild ``Compounds`` in Jupyter notebooks, install [py3dmol](http://3dmol.csb.pitt.edu):

    $ conda install -c conda-forge py3dmol
git push origin HEAD:

### Copyright

Copyright (c) 2022, Chris Iacovella


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.1.
