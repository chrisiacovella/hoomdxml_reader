Installation
===============

installation instructions


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
To load a HOOMD-blue XML file, we need only pass the file path to the constructor.
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

Particle positions as a numpy array:

.. code:: ipython3

    print(system.xyz)

*output*:

.. code:: ipython3

    [[0.  0.  0. ]
     [0.5 0.  0. ]
     [1.  0.  0. ]
     [1.5 0.  0. ]
     [2.  0.  0. ]
     [0.  1.  0. ]
     [0.5 0.5 2. ]
     [3.  1.  3. ]
     [2.5 0.  1. ]
     [0.  2.  4. ]]

Other calls that correspond to each section in the XML data file shown above:
 
.. code:: ipython3

    system.bonds
    system.angles
    system.dihedrals
    system.masses
    system.charges
    system.bond_order

Note, the constructor and load functions have two additional arguments that can be set.  ``identify_molecules`` (default=True), controls whether we perform automated molecule detection. ``ignore_zero_bond_order`` (default=False) allows us to control whether particles with no connections (i.e., bond order = 0) are added to the list of molecules. By default these will be added to the list.

Accessing molecules
-------------------

By default, when an XML file is loaded, the code will generate a list of molecules based on the underlying connectivity (i.e., ``identify_molecules`` = True by default).  Particles that are bonded together will be considered to be part of the same molecule. For particles with no connections (i.e., bond order is 0), each particle itself will be considered a molecule.  Information about each molecule is saved in a simple container class.


.. autoclass:: hoomdxml_reader.molecule.Molecule
    :members:

The following code prints information related to each molecule.

.. code:: ipython3

    for molecule in system.molecules:
        print(molecule.name, molecule.particles, molecule.types, molecule.pattern)
 
 
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

