hoomdxml_reader
======
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: http://opensource.org/licenses/MIT

..

*A lightweight module for reading legacy HOOMD-blue XML and GSD files and converting to mBuild Compounds*


`HOOMD-blue <https://glotzerlab.engin.umich.edu/hoomd-blue/>`_ is a molecular simulation engine highly optimized for use on GPUs. Older version of HOOMD-Blue  utilized an XML file format for defining simulation positions, masses, bonds, angles, etc. Support for this format has been deprecated since HOOMD-blue `v2 <https://hoomd-blue.readthedocs.io/en/next/changelog.html#v2-0-0-2016-06-22>`_ and completely removed since the release of `version 3 <https://hoomd-blue.readthedocs.io/en/v3.5.0/changelog.html?highlight=XML#v3-0-0-beta-1-2020-10-15>`_.  Nonetheless, it is still a convenient and descriptive file format, and the ability to read in such files is still important for analysis of older simulations that rely on this legacy format.
    
    
    
.. note::
    `mdtraj <hhttps://www.mdtraj.org/1.9.7/api/generated/mdtraj.load_hoomdxml.html?highlight=hoomd%20xml#mdtraj.load_hoomdxml>`_  provides support for the HOOMD-blue XML file format, including automated grouping of particles by connectivity, similar to this Module. It also provides support for GSD files. However, masses, charges, angles and dihedrals are not parsed from the files by mdtraj. `mdanalysis <https://userguide.mdanalysis.org/1.0.0/formats/reference/xml.html>`_ also has an XML reader, but similarly, does not do a full parsing of the information in the XML. This missing information may be necessary, especially for converting legacy XML files to the current `GSD <https://gsd.readthedocs.io>`_ file format used by HOOMD-blue or to convert to MoSDeF's  `mBuild Compounds <https://github.com/mosdef-hub/mbuild>` or `GMSO <https://github.com/mosdef-hub/gmso>`_ format.  This module provides a more complete parsing of the file and automated grouping into molecules and code to convert to mBuild Compounds.
    
=========================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
