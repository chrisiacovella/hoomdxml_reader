"""
Module for reading legacy hoomd XML formatted files.

"""

__all__ = ["System"]

import networkx as nx
import xml.etree.ElementTree as ET

from hoomdxml_reader.molecule import Molecule
from warnings import warn

class System(object):
    """
    System class.
    
    
    A class to load hoomd XML formatted configuration files and store the
    information encoded in these files. This class will also optionally
    goup the underlying particles into molecules, inferred based upon
    the connectivity of particles as defined in the bonds section of
    the XML file.

    Parameters
    ----------
        xml_file : string, default=None
            Name of the hoomd xml file to load
        identify_molecules : bool, default=True
            If True, the code will group the particles based upon their underlying connectivity.
            Particles bonded together will be considered a molecule
        ignore_zero_bond_order : bool, default=False
            If True, particles without any bonds (i.e., bond order = 0) will be ignored when
            identifying molecules (i.e., they will not appear in the molecule list).
            If False, a particle with bond order = 0 will be considered to be a molecule.
        molecule_dict : dict, dtype=str
            A dict that defines the molecule 'pattern' and associated user defined name.
            This is used for renaming molecules automatically identified.
            
    Returns
    -------
    n_particles : int
        Number of particles in the entire system
    xyz : list shape=(3,n_particles), dtype=float
        List containing a list of x, y, z coordinates of each particle.
    types : list, shape=(1,n_particles), dtype=str
        List of type names of all particles in the system.
    masses : list, shape=(1,n_particles), dtype=float
        List of masses of all particles in the system.
    charges : list, shape=(1,n_particles), dtype=float
        List of charges of all particles in the system.
    bonds : list, shape=(3, n_particles), dtype=(str, int, int)
        List of all bonds in the system.  The first entry per bond is the
        name of the bond (str) as defined in the xml file,
        followed by indices for each particle in the bond.
    angles : list, shape=(4, n_particles), dtype=(str, int, int, int)
        List of all angles in the system.  The first entry per angle is the
        name of the angle (str) as defined in the xml file,
        followed by indices for each particle in the angle.
    dihedrals : list, shape=(5, n_particles), dtype=(str, int, int, int, int)
        List of all dihedrals in the system.  The first entry per dihedral is the
        name of the dihedral (str) as defined in the xml file,
        followed by indices for each particle in the dihedral.
    molecules : list, dtype=Molecule
        List containing each molecule identified by the code. Each entry
        in the list is an instance of the Molecule class.
    unique_molecules : dict, dtype=str
        A dict that provides the molecule 'pattern' and associated assigned name ("molecule{i}")
        for each unique molecule type identified in the system.
        This is useful for allowing definition of the molecule_dict for assigning molecules names.
    graph : networkx graph
        NetworkX graph constructed from all bonds defined in the XML file
    bond_order : list, shape=(1,n_particles), dtype=int
        A list of the bond order of each particle in the system.
    
    box : list, shape(3), dtype=float,
        Dimensions of the box as defined in the xml file, in order: Lx, Ly, and Lz.
        
    """
    def __init__(self, xml_file=None, identify_molecules=True, ignore_zero_bond_order=False):
        
        self._xyz = []
        self._n_particles = 0
        self._types = []
        self._bond_order = []
        
        self._molecules = []
        self._unique_molecules = {}
        
        self._identify_molecules = identify_molecules
        self._ignore_zero_bond_order = ignore_zero_bond_order
        
        if xml_file is not None:
            self._xml_file = xml_file
            self._load_xml()
            if self._identify_molecules == True:
                self._infer_molecules()
    
    # essentially the same workflow as the constructor
    def load(self, xml_file=None, identify_molecules=True, ignore_zero_bond_order=False):
    
        self._identify_molecules = identify_molecules
        self._ignore_zero_bond_order = ignore_zero_bond_order
        
        if xml_file is None:
            warn("XML file not defined")
        else:
            self._xml_file = xml_file
            self._load_xml()
            if self._identify_molecules == True:
                self._infer_molecules()

    # generic function to parse the topology entries,
    # takes the element as an argument and  number of entries per line
    def _parse_topology(self, element, length):
        temp_element = self._config.find(element)
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


    # main function to load and parse the XML
    def _load_xml(self):
        self._tree = ET.parse(self._xml_file)
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
    
        # calculate bond_order
        for i in range(0, self.n_particles):
            self._bond_order.append(0)
            
        for bond in self._bonds:
            i = bond[1]
            j = bond[2]
            self._bond_order[i] += 1
            self._bond_order[j] += 1
            
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
        for mol_name in molecule_dict:
            self._unique_molecules[mol_name] = molecule_dict[mol_name]
            
        for molecule in self._molecules:
             molecule.set_molecule_name(self._unique_molecules[molecule.pattern])
    @property
    def xyz(self):
        """A list of xyz coordinates for each particle, as defined in the source file."""
        return self._xyz
    
    @property
    def types(self):
        """A list of all particle types defined in the source file."""
        return self._types
 
    @property
    def masses(self):
        """A list of all masses defined in the source file."""
        return self._masses
        
    @property
    def charges(self):
        """A list of all charges defined in the source file."""
        return self._charges
        
    @property
    def bonds(self):
        """A list of all bonds defined in the source file."""
        return self._bonds

    @property
    def angles(self):
        """A list of all angles defined in the source file."""
        return self._angles
   
    @property
    def dihedrals(self):
        """A list of all dihedrals defined in the source file"""
        return self._dihedrals
        
    @property
    def molecules(self):
        """This is a list of all molecules found in the system, where each entry corresponds to an instance of the Molecule class."""
        return self._molecules

    @property
    def unique_molecules(self):
        """A dict that contains the molecule pattern as the key and associated molecule name as the value, for each unique molecule in the system. """
        return self._unique_molecules

    @property
    def graph(self):
        """A networkx graph generated from the bond information included in the source file."""
        return self._graph
        
    @property
    def bond_order(self):
        """A list containing an integer bond order (i.e., total number of bonds) of each particle in the system"""
        return self._bond_order

    @property
    def n_particles(self):
        """The total number of particles found in the XML file"""
        return self._n_particles
    
    @property
    def box(self):
        """List of the box length in order Lx, Ly, Lz. Boxes are assumed to be centered a the origin."""
        return self._box
        
            
"""
if __name__ == "__main__":
    print(canvas())
"""
