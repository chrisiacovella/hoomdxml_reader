"""hoomdxml_reader Molecule class """

__all__ = ['Molecule']

class Molecule(object):
    """
    A class to store information about an individual molecule in the system.

    Parameters
    ----------
        particle_index : int
            Index of the particle to add to the molecule
        particle_type : str
            Type name associated with a given particle
        molecule_name : str
            Name of the molecule

    Returns
    -------
    n_particles : int
        Number of particles in the molecule
    particles : list, shape=(1,n_particles), dtype=int
        List of particles in the system.
    types : list, shape=(1,n_particles), dtype=str
        List of type names of particles in the molecule
    pattern : str
        String constructed by concatenating entries in types list.
    name : str
        Name of the molecule.
        
    """


    def __init__(self):
        self._particles = []
        self._types = []
        self._pattern = ''
        self._name = 'none'
    
    def add_particle(self, particle_index, particle_type):
        self._particles.append(particle_index)
        self._types.append(particle_type)
        self._pattern = self._pattern + particle_type
        
    def set_molecule_name(self, molecule_name):
        self._name = molecule_name

    @property
    def particles(self):
        """List of indices of particles in the molecule in numerical order"""
        return self._particles
        
    @property
    def types(self):
        """List containing the type of particle in the particles list"""
        return self._types

    @property
    def pattern(self):
        """String constructed by concatenating entries in types.
        This is used to identify the total number of unique molecules in a system."""
        return self._pattern

    @property
    def name(self):
        """Name of the molecule """
        return self._name
        
    @property
    def n_particles(self):
        """Number of particles in the molecule """
        return len(self._particles)
