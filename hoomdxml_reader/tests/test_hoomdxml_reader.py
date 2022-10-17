"""
Unit and regression test for the hoomdxml_reader package.
"""

# Import package, test suite, and other packages as needed
import sys
import os
import pytest

import hoomdxml_reader as hxml


def test_hoomdxml_reader_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "hoomdxml_reader" in sys.modules
    
def test_loader():
    cwd = os.getcwd()
    print(cwd)
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml")
    
    assert len(system.box) == 3
    assert system.box == [10.0, 11.0, 12.0]

    assert system.n_particles == 10
    assert len(system.xyz) == 10
    assert system.xyz == [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [1.0, 0.0, 0.0], [1.5, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5, 2.0], [3.0, 1.0, 3.0], [2.5, 0.0, 1.0], [0.0, 2.0, 4.0]]
    
    assert len(system.bond_order) == 10
    assert system.bond_order == [1, 2, 2, 2, 1, 0, 0, 0, 0, 0]
    
    assert len(system.types) == 10
    assert system.types == ['CH3', 'CH2', 'CH2', 'CH2', 'CH3', 'water', 'water', 'water', 'water', 'water']
    
    assert len(system.bonds) == 4
    assert system.bonds == [['CH3-CH2', 0, 1], ['CH2-CH2', 1, 2], ['CH2-CH2', 2, 3], ['CH2-CH3', 3, 4]]
    
    assert len(system.angles) == 3
    assert system.angles == [['CH3-CH2-CH2', 0, 1, 2], ['CH2-CH2-CH2', 1, 2, 3], ['CH3-CH2-CH3', 2, 3, 4]]
    
    assert len(system.dihedrals) == 2
    assert system.dihedrals == [['CH3-CH2-CH2-CH2', 0, 1, 2, 3], ['CH2-CH2-CH2-CH3', 1, 2, 3, 4]]
    
    assert len(system.masses) == 10
    assert system.masses == [15.0, 14.0, 14.0, 14.0, 15.0, 18.0, 18.0, 18.0, 18.0, 18.0]

    assert len(system.charges) == 10
    assert system.charges == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    assert len(system.molecules) == 6
    assert len(system.graph) == 5
    
    assert len(system.unique_molecules) == 2
    assert 'water' in system.unique_molecules
    assert 'CH3CH2CH2CH2CH3' in system.unique_molecules
    
    # test ignoring particles with zero bond order
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml", ignore_zero_bond_order=True)
    assert len(system.molecules) == 1
    assert len(system.unique_molecules) == 1
    
    assert 'water' not in system.unique_molecules
    assert 'CH3CH2CH2CH2CH3' in system.unique_molecules
    
    # since this will have only a single molecule, we can more easily test
    # the Molecule class
    assert system.molecules[0].name == 'molecule0'
    assert system.molecules[0].pattern == 'CH3CH2CH2CH2CH3'
    assert len(system.molecules[0].types) == 5
    assert len(system.molecules[0].particles) == 5
    assert system.molecules[0].particles == [0, 1, 2, 3, 4]
    assert system.molecules[0].types  == ['CH3', 'CH2', 'CH2', 'CH2', 'CH3']
    
    #test ignoring identify molecules
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml", identify_molecules=False)
    assert len(system.molecules) == 0
    assert len(system.unique_molecules) == 0

def test_rename_molecules():
    cwd = os.getcwd()

    molecule_dict = {'CH3CH2CH2CH2CH3': 'pentane', 'water': 'SOL'}
    
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml")
    system.set_molecule_name_by_dictionary(molecule_dict)
    
    assert system.unique_molecules['water'] == 'SOL'
    assert system.unique_molecules['CH3CH2CH2CH2CH3'] == 'pentane'
        
    # ignore the zero bond order water molecules to directly check to ensure
    # the name in the Molecule class has been properly modified.
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml", ignore_zero_bond_order=True)
    system.set_molecule_name_by_dictionary(molecule_dict)

    assert system.molecules[0].name == 'pentane'
    


    
    

