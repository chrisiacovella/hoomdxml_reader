Installation
===============

pip install
-----------
Check out the source from the github repository:

    $ git clone https://github.com/chrisiacovella/hoomdxml_reader.git

In the top level of hoomdxml_reader directory, use pip to install:

    $ pip install -e .

The core functions of the module will require networkx to be installed.
To create an environment named hoomdxml_reader with this necessary package,
run the following from the top level of the  hoomdxml_reader directory.


    $ conda env create -f environment.yml

Optional packages
-----------------
While not necessary to use the core functions of the Module, conversion to an mBuild ``Compound``, requires `mbuild <https://mbuild.mosdef.org/en/stable/getting_started/installation/installation.html>`_ to be installed.

    $ conda install -c conda-forge mbuild

To visualize mbuild ``Compounds`` in Jupyter notebooks, install `py3dmol <http://3dmol.csb.pitt.edu>`_:

    $ conda install -c conda-forge py3dmol
    
Building the documentation
--------------------------

This packag uses `sphinx <https://www.sphinx-doc.org/en/master/index.html>`_ to build its documentation. To build the docs locally, run the following while in the ``docs`` directory::

    $ pip install -r requirements.yaml
    $ make html

To view documentation, open ``$INSTALL_PATH/hoomdxml_reader/docs/_build/html/index.html`` in your web browser.
    
HOOMD-Blue XML file format
===========================
An example of the basic file format is below:

.. code:: xml

    <hoomd_xml version="1.2">
        <configuration time_step="0">
            <box Lx="10.0" Ly="10.0" Lz="10.0" units="sigma" />
            <position num="10" units="sigma">
                0.0 0.0 0.0
                0.5 0.0 0.0
                1.0 0.0 0.0
                1.5 0.0 0.0
                2.0 0.0 0.0
                0.0 1.0 0.0
                0.5 0.5 2.0
                3.0 1.0 3.0
                2.5 0.0 1.0
                0.0 2.0 4.0
            </position>
            <type>
                CH3
                CH2
                CH2
                CH2
                CH3
                water
                water
                water
                water
                water
            </type>
            <mass>
                15.0
                14.0
                14.0
                14.0
                15.0
                18.0
                18.0
                18.0
                18.0
                18.0
            </mass>
            <charge>
                0.0
                0.0
                0.0
                0.0
                0.0
                0.0
                0.0
                0.0
                0.0
                0.0
            </charge>
            <bond>
                CH3-CH2 0 1
                CH2-CH2 1 2
                CH2-CH2 2 3
                CH2-CH3 3 4
            </bond>
            <angle>
                CH3-CH2-CH2 0 1 2
                CH2-CH2-CH2 1 2 3
                CH3-CH2-CH3 2 3 4
            </angle>
            <dihedral>
                CH3-CH2-CH2-CH2 0 1 2 3
                CH2-CH2-CH2-CH3 1 2 3 4
            </dihedral>
        </configuration>
    </hoomd_xml>

Usage
============

Basic usage
------------
To load a HOOMD-blue XML file or GSD file, we need only pass the file path to the constructor.
.. code:: ipython3

    import hoomdxml_reader as hxml
    
    system = hxml.System("example.hoomdxml")

Alternatively, we can create an empty class and call the load function:

.. code:: ipython3

    import hoomdxml_reader as hxml
    
    system = hxml.System()
    system.load("example.hoomdxml")
    
With the system loaded we can easily extract various pieces of information.

For example, the total number of particles in the system:

.. code:: ipython3

    print(system.n_particles)

*output*:

.. code:: ipython3

    10

Particle positions are stored in a list where, e.g., the following would print the xyz coordinates of the first particle in the list:

.. code:: ipython3

    print(system.xyz[0])

*output*:

.. code:: ipython3

    [0.0, 0.0, 0.0]

Other calls that correspond to each section in the XML data file shown above:
 
.. code:: ipython3

    system.types
    system.bonds
    system.angles
    system.dihedrals
    system.impropers
    system.masses
    system.charges
    system.bond_order

Note, the constructor and load functions have two additional arguments that can be set.  ``identify_molecules`` (default=``True``), controls whether we perform automated molecule detection. ``ignore_zero_bond_order`` (default=``False``) allows us to control whether particles with no connections (i.e., bond order = 0) are added to the list of molecules. By default these will be added to the list.

Accessing molecules
-------------------

By default, when an XML file is loaded, the code will generate a list of molecules based on the underlying connectivity (i.e., ``identify_molecules = True`` by default).  Particles that are bonded together will be considered to be part of the same molecule. For particles with no connections (i.e., bond order is 0), each particle itself will be considered a molecule.  Information about each molecule is saved in a simple container class.


.. autoclass:: hoomdxml_reader.molecule.Molecule
    :members:

The following code prints information related to each molecule.

.. code:: ipython3

    for molecule in system.molecules:
        print(molecule.name, molecule.particles, molecule.types, molecule.pattern, molecule.bonds)
 
 
*output*:
 
.. code:: ipython3

    molecule0 [0, 1, 2, 3, 4] ['CH3', 'CH2', 'CH2', 'CH2', 'CH3'] CH3CH2CH2CH2CH3
    molecule1 [5] ['water'] water
    molecule1 [6] ['water'] water
    molecule1 [7] ['water'] water
    molecule1 [8] ['water'] water
    molecule1 [9] ['water'] water
 
Here, the code automatically searched for molecules for the same type, and assigned them the same name (i.e., each water molecule is given the name `molecule1`).These are named with the convention `molecule{n}` where n is an integer ranging from 0 to maximum number of unique molecule types in the system. Unnique molecules are identified by the ``pattern`` of each molecule,  which is a string made by concatenating the particle types of each particle in the molecule.  Any molecules with identical patterns are considered the same.

The ``System`` class stores a dict of the unique molecules:

.. code:: ipython3

    print(system.unique_molecules)

*output*:

.. code:: ipython3

    {'CH3CH2CH2CH2CH3': 'molecule0', 'water': 'molecule1'}

The information  stored in the ``unique_molecules`` dict can be used to create a new dict to define these with preferred names and reassign this information in the system.

.. code:: ipython3

    molecule_dict = {'CH3CH2CH2CH2CH3': 'pentane', 'water': 'water'}

    system.set_molecule_name_by_dictionary(molecule_dict)

    print(system.unique_molecules)
    
*output*:

.. code:: ipython3

    {'CH3CH2CH2CH2CH3': 'pentane', 'water': 'water'}


If we re-run the query about each molecule we can see the names have been re-assigned.

.. code:: ipython3

    for molecule in system.molecules:
        print(molecule.name, molecule.particles, molecule.types, molecule.pattern)

*output*:

.. code:: ipython3

    pentane [0, 1, 2, 3, 4] ['CH3', 'CH2', 'CH2', 'CH2', 'CH3'] CH3CH2CH2CH2CH3
    water [5] ['water'] water
    water [6] ['water'] water
    water [7] ['water'] water
    water [8] ['water'] water
    water [9] ['water'] water
    
If this information is known beforehand, the molecule dictionary can simply be passed to the constructor or load function.

Converting to an mBuild Compound
--------------------------------
The System class can be trivially converted to an `mBuild Compound <https://mbuild.mosdef.org/en/stable/topic_guides/data_structures.html#compound>`_. The mBuild ``Compound`` generated by the conversion function maintains the same general hierarchy of the ``System`` class (system->molecules->particles).

.. note::
    mBuild needs to be installed to use these functions.  Since this conversion is optional, mbuild was not included in the environment.yml file. To insall via conda, execute: ``conda install -c conda-forge mbuild``
    
For example, the following code will create an mbuild ``Compound`` from the instance of the ``System`` class.

.. code:: ipython3

    import hoomdxml_reader as hxml
    import hoomdxml_reader.convert as convert
    import mbuild as mb

    #system is an instance of the hoomdxml_reader System class
    system = hxml.System("example.hoomdxml")
    
    # we will rename the molecules in the system;
    # this is not necessary for the conversion but only done for clarity
    molecule_dict = {'CH3CH2CH2CH2CH3': 'pentane', 'water': 'water'}
    system.set_molecule_name_by_dictionary(molecule_dict)

    #mb_system is an instance of the mBuild Compound class
    mb_system = convert.System_to_Compound(system)
    
If py3Dmol is installed in your environment the mb_system can be easily visualized.

.. note::
    To install, execute: ``conda install -c conda-forge py3Dmol``
    

.. code:: ipython3

        mb_system.visualize()
  
The following code snippets demonstrate how to access information within the mBuild ``Compound`` that we created. Again, the goal was to define the ``Compound`` in such a way that it mimics the hierarchy in the ``System`` class. To access individual molecules, we can use the following syntax show below; this is possible because each molecule that was added to the mBuild ``Compound`` was given a label with the following syntax 'molecule[$]'. E.g., to access the first and third molecules in the system:


.. code:: ipython3

    print(mb_system['molecule'][0])
    print(mb_system['molecule'][2])

*output*:

.. code:: ipython3

    <pentane 5 particles, 4 bonds, non-periodic, id: 5177106848>
    <water 1 particles, 0 bonds, non-periodic, id: 5177105408>

.. note::
    The value of ``id`` will likely be different if executing this code locally; this hash is an internal book keeping step performed by mBuild.
   
Similarly, one can loop over all molecules in the ``Compound``:

.. code:: ipython3

    for molecule in mb_system['molecule']:
        print(molecule)
    
*output*:

.. code:: ipython3

    <pentane 5 particles, 4 bonds, non-periodic, id: 5177106848>
    <water 1 particles, 0 bonds, non-periodic, id: 5177107424>
    <water 1 particles, 0 bonds, non-periodic, id: 5177105408>
    <water 1 particles, 0 bonds, non-periodic, id: 5177103488>
    <water 1 particles, 0 bonds, non-periodic, id: 5177102960>
    <water 1 particles, 0 bonds, non-periodic, id: 5177106608>

Furthermore, one can access particles underlying a given molecule:

.. code:: ipython3

    for particle in mb_system['molecule'][0]:
        print(particle)

*output*:

.. code:: ipython3

    <CH3 pos=([0. 0. 0.]), 1 bonds, id: 5177103776>
    <CH2 pos=([0.5 0.  0. ]), 2 bonds, id: 5177107328>
    <CH2 pos=([1. 0. 0.]), 2 bonds, id: 5177103104>
    <CH2 pos=([1.5 0.  0. ]), 2 bonds, id: 5177106944>
    <CH3 pos=([2. 0. 0.]), 1 bonds, id: 5177106032>

Similar to molecules, particles in each molecule are added with the labels ``particle[$]``. As such, we can, e.g., access the first particle in each molecule as follows:

.. code:: ipython3

    for molecule in mb_system['molecule']:
        print(molecule['particle'][0])
    
    print('\nAccess just the first particle of the first molecule:')
    print(mb_system['molecule'][0]['particle'][0])


        
*output*:

.. code:: ipython3

    <CH3 pos=([0. 0. 0.]), 1 bonds, id: 5177103776>
    <water pos=([0. 1. 0.]), 0 bonds, id: 5177105888>
    <water pos=([0.5 0.5 2. ]), 0 bonds, id: 5177104160>
    <water pos=([3. 1. 3.]), 0 bonds, id: 5177107280>
    <water pos=([2.5 0.  1. ]), 0 bonds, id: 5177103872>
    <water pos=([0. 2. 4.]), 0 bonds, id: 5177107760>

    Access just the first particle of the first molecule
    <CH3 pos=([0. 0. 0.]), 1 bonds, id: 5177103776>

.. note::
    mBuild Compounds will contain information about position, particle type (i.e. name), molecule name, mass, charge, and any bonds.  Angle and dihedral information is not included, nor are quantities calculated automatically in the System class, such as bond order.

We can additionally restrict the conversion to specific unique molecules by passing a list of molecule names via the name_selection variable. For example, we can restrict our conversion to only the water molecules in the system:

.. code:: ipython3

    mb_system = convert.System_to_Compound(system, name_selection=['water'])

An individual molecule in the System class can be converted to an mBuild Compound.  This function can be used if one desires to have increased customization of the conversion than is provided in the System_to_Compound function.

.. code:: ipython3

    mb_molecule = convert.Molecule_to_Compound(system, system.molecules[0],
                                                name=system.molecules[0].name)
                                                
                                                
