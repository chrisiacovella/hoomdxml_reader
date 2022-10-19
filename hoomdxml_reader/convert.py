"""hoomdxml_reader Conversion functions """
import mbuild as mb

__all__ = ['Convert']

# convert an individual molecule to a mbuild compound
class Molecule_to_Compound(mb.Compound):
    """
    A child of the mbuild Compound class that is called by the
    System_to_Compound class.  This will add the particles
    associated with a given molecule to the mbuild Compound.
    Individual particles in this class can be accessed sequentially,
    e.g., for a given Compounded named mb_molecule,
    mb_molecule['particle'][0] would return the first particle in the
    molecule.
    
    Parameters
    ----------
        system : instance of the hoomdxml_reader System class
        molecule : instance of the hoomdxml_reader Molecule class.
            Particles associated with the molecule will be added
            to the mbuild Compound.
        name : name to give the overall mbuild Compound.
    """
    def __init__(self, system, molecule, name):
        super(Molecule_to_Compound, self).__init__(name=name)
        for i, particle in enumerate(molecule.particles):
            temp_particle = mb.Particle(name=molecule.types[i], pos=system.xyz[particle], charge=system.charges[particle], mass=system.masses[particle])
            self.add(temp_particle, label='particle[$]')


class System_to_Compound(mb.Compound):
    """
    A child of the mbuild Compound class.  This will convert
    an instance of the hoomdxml_reader System class to
    an mbuild Compound, preserving the hierarchy defined
    in the System class (i.e., system -> molecules -> particles).
    Individual molecules will be named according to the instance
    of the System class passed to this class. These can be accessed
    e.g., for a given Compounded named mb_system,
    mb_system['molecule'][0] would return  the first molecule in the
    Compound.

    Parameters
    ----------
        system : instance of the hoomdxml_reader System class
    """
    def __init__(self, system):
        super(System_to_Compound, self).__init__()
        
        for molecule in system.molecules:
            temp_molecule = Molecule_to_Compound(system, molecule, name=molecule.name)
            self.add(temp_molecule, label='molecule[$]')
            
        for bond in system.bonds:
            self.add_bond( (self[bond[1]], self[bond[2]]) )
