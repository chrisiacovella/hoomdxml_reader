"""
Module for reading legacy hoomd XML formatted files.

"""

__all__ = ["System"]

import networkx as nx
import gsd.hoomd

import xml.etree.ElementTree as ET

from hoomdxml_reader.molecule import Molecule
from warnings import warn

class System(object):
    """
    Class that stores system information from XML and GSD files.
    
    A class to load hoomd XML or GSD formatted configuration files and store the
    information encoded in these files. This class will also optionally
    goup the underlying particles into molecules, inferred based upon
    the connectivity of particles as defined in the bonds section of
    the configuration file. If an XML or GSD file is passed during instantiation,
    it will load and parse file provided.
                 
    Parameters
    ----------
    file : string, optional, default=None
        Name of the hoomd xml or gsd file to load
    frame : int, optional, default=0
    identify_molecules : bool, optional, default=True
        If True, the code will group the particles based upon their underlying connectivity.
        Particles bonded together will be considered a molecule
    ignore_zero_bond_order : bool, optional, default=False
        If True, particles without any bonds (i.e., bond order = 0) will be ignored when
        identifying molecules (i.e., they will not appear in the molecule list).
        If False, a particle with bond order = 0 will be considered to be a molecule.
    molecule_dict : dict, dtype=str, optional, default=None
        A dict that defines the molecule 'pattern' and associated user defined name.
        This is used for renaming molecules automatically identified.
    Returns
    ------
    """

    def __init__(self, file=None, frame=0, identify_molecules=True, ignore_zero_bond_order=False, molecule_dict=None):
        """Initialize the System class.
        
        This initializes the System class.  If an XML or GSD file is passed during instantiation,
        it will load and parse file provided.
        
        Parameters
        ----------
        file : string, optional, default=None
            Name of the hoomd xml or gsd file to load
        frame : int, optional, default=0
        identify_molecules : bool, optional, default=True
            If True, the code will group the particles based upon their underlying connectivity.
            Particles bonded together will be considered a molecule
        ignore_zero_bond_order : bool, optional, default=False
            If True, particles without any bonds (i.e., bond order = 0) will be ignored when
            identifying molecules (i.e., they will not appear in the molecule list).
            If False, a particle with bond order = 0 will be considered to be a molecule.
        molecule_dict : dict, dtype=str, optional, default=None
            A dict that defines the molecule 'pattern' and associated user defined name.
            This is used for renaming molecules automatically identified.
        Returns
        ------
        """
        self._filename = None
        self._xyz = []
        self._n_particles = 0
        self._types = []
        self._bond_order = []
        self._bonds = []
        self._angles = []
        self._dihedrals = []
        self._impropers = []
        self._charges = []
        self._masses = []
        self._frame = frame
        self._box = []
            
        self._molecules = []
        self._unique_molecules = {}
        
        self._identify_molecules = identify_molecules
        self._ignore_zero_bond_order = ignore_zero_bond_order
        
        if file is not None:
            self._filename = file
            ext = file.split('.')[-1]
            if "xml" in ext:
                self._load_xml()
            elif "gsd" in ext:
                self._load_gsd(frame=self._frame)

            if self._identify_molecules == True:
                self._infer_molecules()
            if molecule_dict is not None:
                self.set_molecule_name_by_dictionary(molecule_dict)
                
    def _clear(self):
        self._filename = None
        self._xyz = []
        self._n_particles = 0
        self._types = []
        self._bond_order = []
        self._bonds = []
        self._angles = []
        self._dihedrals = []
        self._impropers = []
        self._charges = []
        self._masses = []
        self._box = []
            
        self._molecules = []
        self._unique_molecules = {}
        
    # essentially the same workflow as the constructor
    def load(self, file=None, frame=0, identify_molecules=True, ignore_zero_bond_order=False, molecule_dict=None):
        """Loads an xml or gsd file.
        
        Load the xml or GSD file into the system class. This function will clear
        any information already loaded into the System class.
        
        Parameters
        ----------
        file : string, optional, default=None
            Name of the hoomd xml or gsd file to load
        frame : int, optional, default=0
        identify_molecules : bool, optional, default=True
            If True, the code will group the particles based upon their underlying connectivity.
            Particles bonded together will be considered a molecule
        ignore_zero_bond_order : bool, optional, default=False
            If True, particles without any bonds (i.e., bond order = 0) will be ignored when
            identifying molecules (i.e., they will not appear in the molecule list).
            If False, a particle with bond order = 0 will be considered to be a molecule.
        molecule_dict : dict, dtype=str, optional, default=None
            A dict that defines the molecule 'pattern' and associated user defined name.
            This is used for renaming molecules automatically identified.
        Returns
        ------
        """
        if file is None:
            raise Exception("You must provide the name of the XML or GSD file to parse.")
        else:
            self._clear()
            self._identify_molecules = identify_molecules
            self._ignore_zero_bond_order = ignore_zero_bond_order
            self._frame = frame
            self._filename = file
            
            ext = file.split('.')[-1]
            if "xml" in ext:
                self._load_xml()
            elif "gsd" in ext:
                self._load_gsd(frame=self._frame)
            if self._identify_molecules == True:
                self._infer_molecules()
            if molecule_dict is not None:
                self.set_molecule_name_by_dictionary(molecule_dict)
                
    """
    # This would populate the fields from an mdtraj trajectory.
    # I've commented this out because mdtraj format requires us to assume information,
    # for example, about charge and mass, and does not including angle, dihedral, or improper information
    def convert_mdtraj(self, mdtraj=None, frame=0, identify_molecules=True, ignore_zero_bond_order=False):
        if mdtraj is None:
            raise Exception("mdtraj traj not defined")
        else:
            self._ignore_zero_bond_order = ignore_zero_bond_order
            self._identify_molecules = identify_molecules
            self._clear()
            
            for xyz in fconfig.particles.position:
                self._xyz.append(xyz)
                self._charges.append(0) #assumes charge is zero
                self._masses.append(1) #assumes mass is unity beacuse mdtraj doesn't store it.
            
            self._n_particles = len(self._xyz)

            for atom in mdtraj.top.atoms:
                self._types.append(atom.name)
            self._box = list(mdtraj.unitcell_lengths[frame])
            self._bonds = []
            for bond in mdtraj.top.bonds:
                temp_bond = [f'{bond.atom1.name}{bond.atom2.name}', bond.atom1.index, bond.atom2.index]
                self._bonds.append(temp_bond)
            
            self._calc_bond_order()
            if self._identify_molecules == True:
                self._infer_molecules()
    """
    # generic function to parse the topology entries,
    # takes the element as an argument and  number of entries per line
    def _parse_topology(self, element, length):
        temp_element = self._config.find(element)
        if temp_element is not None:
            temp_text = temp_element.text
            agg_array = []
            entry_temp = temp_text.split()
            for i in range(0, len(entry_temp), length):
                temp_array = []
                temp_array.append(entry_temp[i])
                for j in range(1, length):
                    temp_array.append(int(entry_temp[i+j]))
                agg_array.append(temp_array)
            return agg_array
    
    # a generic function to parse a list of floats defined in the text between opening/closing tags for a given element
    def _parse_floats(self, element):
        temp_element = self._config.find(element)
        temp_text = temp_element.text
        agg_array = []
        entry_temp = temp_text.split()
        for i in range(0, len(entry_temp)):
            agg_array.append(float(entry_temp[i]))
        return agg_array

    def _calc_bond_order(self):
        # calculate bond_order
        for i in range(0, self.n_particles):
            self._bond_order.append(0)
            
        for bond in self._bonds:
            i = bond[1]
            j = bond[2]
            self._bond_order[i] += 1
            self._bond_order[j] += 1
    
    #  function to load and parse the XML
    def _load_xml(self):
        self._tree = ET.parse(self._filename)
        self._root = self._tree.getroot()
        self._config =  self._root.find('configuration')
        
        # parse box information
        box_element = self._config.find('box')
        self._box = [float(box_element.attrib['Lx']), float(box_element.attrib['Ly']), float(box_element.attrib['Lz'])]
        
        # parse position data
        pos_element = self._config.find('position')
        self._n_particles = int(pos_element.attrib['num'])
        positions_text = pos_element.text

        pos_temp = positions_text.split()
        xyz_temp = []
        for i in range(0, len(pos_temp), 3):
            temp_array = [float(pos_temp[i]), float(pos_temp[i+1]), float(pos_temp[i+2])]
            self._xyz.append(temp_array)
        
        
        # parse types
        type_element = self._config.find('type')
        type_text = type_element.text
        self._types = type_text.split()

        # parse mass
        self._masses = self._parse_floats(element='mass')
    
        # parse charge
        self._charges = self._parse_floats(element='charge')

        # parse topological info
        self._bonds = self._parse_topology(element='bond', length=3)
        self._angles = self._parse_topology(element='angle', length=4)
        self._dihedrals = self._parse_topology(element='dihedral', length=5)
        self._impropers = self._parse_topology(element='improper', length=5)

        # calculate bond_order
        self._calc_bond_order()
        
    # function to load and parse the GSD
    def _load_gsd(self, frame):
        
        f = gsd.hoomd.open(name=self._filename, mode='rb')
        snapshot = f[frame]
        
        
        for i, xyz in enumerate(snapshot.particles.position):
            self._xyz.append(list(xyz))
            self._masses.append(float(snapshot.particles.mass[i]))
            self._charges.append(float(snapshot.particles.charge[i]))
            
        self._box = [float(snapshot.configuration.box[0]), float(snapshot.configuration.box[1]), float(snapshot.configuration.box[2])]
        
        for typeid in snapshot.particles.typeid:
            self._types.append(snapshot.particles.types[typeid])

        for bond, typeid in zip(snapshot.bonds.group,snapshot.bonds.typeid):
            temp_bond = [snapshot.bonds.types[typeid], int(bond[0]), int(bond[1])]
            self._bonds.append(temp_bond)
        
        for angle, typeid in zip(snapshot.angles.group,snapshot.angles.typeid):
            temp_angle = [snapshot.angles.types[typeid], int(angle[0]), int(angle[1]), int(angle[2])]
            self._angles.append(temp_angle)
        
        for dihedral, typeid in zip(snapshot.dihedrals.group,snapshot.dihedrals.typeid):
            temp_dihedral = [snapshot.dihedrals.types[typeid], int(dihedral[0]), int(dihedral[1]), int(dihedral[2]), int(dihedral[3])]
            self._dihedrals.append(temp_dihedral)

        for improper, typeid in zip(snapshot.impropers.group,snapshot.impropers.typeid):
            temp_improper = [snapshot.impropers.types[typeid], int(improper[0]), int(improper[1]), int(improper[2]), int(improper[3])]
            self._impropers.append(temp_improper)
        
        self._n_particles = len(self._xyz)
        
        # calculate bond_order
        self._calc_bond_order()
            
    # use networkx to create a graph, then look for which components are connected
    def _infer_molecules(self):
        self._graph = nx.Graph()
        for bond in self._bonds:
            self._graph.add_edge(bond[1],bond[2])
        
        for c in nx.connected_components(self._graph):
            mol_temp = Molecule()
            temp = list(c)
            temp.sort()
            
            for item in temp:
                mol_temp.add_particle(item, self._types[item])
            for edge in self._graph.subgraph(c).edges:
                mol_temp.add_bond(list(edge))
            
            self._molecules.append(mol_temp)
            
        if self._ignore_zero_bond_order == False:
            for i, bo in enumerate(self._bond_order):
                if bo == 0:
                    mol_temp = Molecule()
                    mol_temp.add_particle(i, self._types[i])
                    
                    self._molecules.append(mol_temp)
        
        temp_set = set()
        self._unique_molecules = {}
        for molecule in self._molecules:
            temp_set.add(molecule.pattern)
        
        temp_list = list(temp_set)
        for i, temp_str in enumerate(temp_list):
            self._unique_molecules[temp_str] = f'molecule{i}'
        
        for molecule in self._molecules:
             molecule.set_molecule_name(self._unique_molecules[molecule.pattern])
             
    # reads in a dictionary that includes the molecule pattern as a key with the user defined name as the associated value,
    # and re-assigns names of each molecule found for that pattern.
    
    def set_molecule_name_by_dictionary(self, molecule_dict):
        """Assign molecule names.
        
        This function will assign names to the molecules in the system based upon the provided dictionary.
        A pattern is constructed by concatenating partice names together into a single string.
        Unique patterns in the system can be found in the `unique_molecules` dictionary.
        
        Parameters
        ----------
        molecule_dict : dict, dtype=str
            A dict that defines the molecule 'pattern' and associated user defined name.
            This is used for renaming molecules automatically identified.
            Molecule pattern as the key and associated molecule name as the value in the dict,
            i.e., {pattern: name}
        Returns
        -------
        """
        for mol_name in molecule_dict:
            self._unique_molecules[mol_name] = molecule_dict[mol_name]
            
        for molecule in self._molecules:
             molecule.set_molecule_name(self._unique_molecules[molecule.pattern])
    @property
    def n_particles(self):
        """The total number of particles in the system
                                                
        Parameters
        ----------
        Returns
        -------
        n_particles : int
            Number of particles in the system
        """
        return self._n_particles
        
    @property
    def n_bonds(self):
        """The total number of bonds in the system

        Parameters
        ----------
        Returns
        -------
        n_bonds : int
            Number of bonds in the system
        """
        return len(self._bonds)
    
    @property
    def n_angles(self):
        """The total number of angles in the system

        Parameters
        ----------
        Returns
        -------
        n_angles : int
            Number of angles in the system
        """
        return len(self._angles)
        
    @property
    def n_dihedrals(self):
        """The total number of dihedrals in the system

        Parameters
        ----------
        Returns
        -------
        n_dihedrals : int
            Number of dihedrals in the system
        """
        return len(self._dihedrals)
    
    @property
    def n_impropers(self):
        """The total number of impropers in the system

        Parameters
        ----------
        Returns
        -------
        n_impropers : int
            Number of impropers in the system
        """
        return len(self._impropers)
 
    @property
    def xyz(self):
        """A list of xyz coordinates for each particle.
        
        Parameters
        ----------
        Returns
        -------
        xyz : list shape=(3,n_particles), dtype=float
            List containing a list of x, y, z coordinates of each particle.
        """
        return self._xyz
    
    @property
    def types(self):
        """A list of all particle types.
                
        Parameters
        ----------
        Returns
        -------
        types : list, shape=(1,n_particles), dtype=str
            List of type names of all particles in the system.

        """
        return self._types
 
    @property
    def masses(self):
        """A list of all masses defined in the source file.
                        
        Parameters
        ----------
        Returns
        -------
        masses : list, shape=(1,n_particles), dtype=float
            List of masses of all particles in the system.
        """
        return self._masses
        
    @property
    def charges(self):
        """A list of all charges defined in the source file.
                                
        Parameters
        ----------
        Returns
        -------
        charges : list, shape=(1,n_particles), dtype=float
            List of charges of all particles in the system.
        """
        return self._charges
        
    @property
    def bonds(self):
        """A list of all bonds defined in the source file.
                                        
        Parameters
        ----------
        Returns
        -------
        bonds : list, shape=(3, n_bonds), dtype=(str, int, int)
            List of all bonds in the system.  The first entry per bond is the
            name of the bond (str) as defined in the source file.
        """
        return self._bonds

    @property
    def angles(self):
        """A list of all angles defined in the source file.
        
        Parameters
        ----------
        Returns
        -------
        angles : list, shape=(4, n_angles), dtype=(str, int, int, int)
            List of all angles in the system.  The first entry per angles is the
            name of the angle (str) as defined in the source file.
        """
        return self._angles
   
    @property
    def dihedrals(self):
        """A list of all dihedrals defined in the source file
                
        Parameters
        ----------
        Returns
        -------
        dihedrals : list, shape=(5, n_dihedrals), dtype=(str, int, int, int, int)
            List of all dihedrals in the system.  The first entry per dihedral is the
            name of the dihedral (str) as defined in the source file.
        """
        return self._dihedrals

    @property
    def impropers(self):
        """A list of all impropers defined in the source file
        
        Parameters
        ----------
        Returns
        -------
        impropers : list, shape=(5, n_impropers), dtype=(str, int, int, int, int)
            List of all impropers in the system.  The first entry per improper is the
            name of the improper (str) as defined in the source file.
        """
        return self._impropers

    @property
    def molecules(self):
        """This is a list of all molecules found in the system, where each entry corresponds to an instance of the Molecule class.
                
        Parameters
        ----------
        Returns
        -------
        molecules : list, dtype=Molecule
            List containing each molecule identified by the code. Each entry
            in the list is an instance of the Molecule class.
        """
        return self._molecules

    @property
    def unique_molecules(self):
        """A dict that contains the molecule pattern as the key and associated molecule name as the value, for each unique molecule in the system.
                        
        Parameters
        ----------
        Returns
        -------
        unique_molecules : dict, dtype=str
            A dict that provides the molecule 'pattern' and associated assigned name ("molecule{i}")
            for each unique molecule type identified in the system. This is useful for allowing definition of
            the molecule_dict for assigning molecules names.
        """
        return self._unique_molecules

    @property
    def graph(self):
        """A networkx graph generated from the bond information included in the source file.
                                
        Parameters
        ----------
        Returns
        -------
        graph : networkx graph
            NetworkX graph constructed from all bonds defined in the XML file

        """
        return self._graph
        
    @property
    def bond_order(self):
        """A list containing an integer bond order (i.e., total number of bonds) of each particle in the system.
                                        
        Parameters
        ----------
        Returns
        -------
        bond_order : list, shape=(1,n_particles), dtype=int
            A list of the bond order of each particle in the system.
        """
        return self._bond_order


    
    @property
    def box(self):
        """List of the box lengths defined in the source file.
                                                
        Parameters
        ----------
        Returns
        -------
        box : list, shape(3), dtype=float,
            List of the box length formatted as [Lx, Ly, Lz]
        """
        return self._box
        
            
