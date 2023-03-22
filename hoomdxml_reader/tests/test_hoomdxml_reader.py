"""
Unit and regression test for the hoomdxml_reader package.
"""

# Import package, test suite, and other packages as needed
import sys
import os
import pytest

import hoomdxml_reader as hxml
from hoomdxml_reader.molecule import Molecule
import hoomdxml_reader.convert as convert
import mbuild as mb



def test_hoomdxml_reader_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "hoomdxml_reader" in sys.modules
 
def test_loader_gsd():
    cwd = os.getcwd()
    system = hxml.System(cwd + "/hoomdxml_reader/tests/test.gsd")
    
    assert system._identify_molecules == True
    assert system._ignore_zero_bond_order == False
    
    assert len(system.box) == 3
    assert system.box == [7.0, 5.0, 4.0]
    assert system.n_particles == 8
    assert len(system.xyz) == 8
    assert system.xyz == [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [3.0, 1.0, 0.0]]
    
    assert len(system.bond_order) == 8
    assert system.bond_order == [1, 2, 2, 1, 1, 2, 2, 1]
    
    assert len(system.types) == 8
    assert system.types == ['A', 'A', 'B', 'B', 'A', 'A', 'B', 'B']
    
    assert len(system.bonds) == 6
    assert len(system.angles) == 4
    assert len(system.dihedrals) == 2
    assert len(system.impropers) == 2
    
    assert system.bonds == [['A-A', 0, 1], ['A-B', 1, 2], ['B-B', 2, 3], ['A-A', 4, 5], ['A-B', 5, 6], ['B-B', 6, 7]]
    
    assert system.angles == [['A-A-B', 0, 1, 2], ['A-B-B', 1, 2, 3], ['A-A-B', 4, 5, 6], ['A-B-B', 5, 6, 7]]
    
    assert system.dihedrals == [['A-A-B-B', 0, 1, 2, 3], ['A-A-B-B', 4, 5, 6, 7]]
    assert system.impropers == [['improp', 0, 1, 2, 3], ['improp', 4, 5, 6, 7]]
    
    assert len(system.masses) == 8
    assert system.masses == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    assert len(system.charges) == 8
    assert system.charges == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    assert len(system.molecules) == 2
    assert len(system.unique_molecules) == 1
    assert 'AABB' in system.unique_molecules
    
def test_loader_xml_basic():
    cwd = os.getcwd()
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml")
    
    assert system._identify_molecules == True
    assert system._ignore_zero_bond_order == False
    
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
 
    assert len(system.impropers) == 2
    assert system.impropers == [['CH3-CH2-CH2-CH2', 0, 1, 2, 3], ['CH2-CH2-CH2-CH3', 1, 2, 3, 4]]

    assert len(system.masses) == 10
    assert system.masses == [15.0, 14.0, 14.0, 14.0, 15.0, 18.0, 18.0, 18.0, 18.0, 18.0]

    assert len(system.charges) == 10
    assert system.charges == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    assert len(system.molecules) == 6
    assert len(system.graph) == 5
    
    assert len(system.unique_molecules) == 2
    assert 'water' in system.unique_molecules
    assert 'CH3CH2CH2CH2CH3' in system.unique_molecules
 
def test_loader_xml_ignore_zero_bo():
    cwd = os.getcwd()
    # test ignoring particles with zero bond order
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml", ignore_zero_bond_order=True)
    
    assert system._identify_molecules == True
    assert system._ignore_zero_bond_order == True
    
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
    assert system.molecules[0].n_particles == 5
    assert system.molecules[0].particles == [0, 1, 2, 3, 4]
    assert system.molecules[0].types  == ['CH3', 'CH2', 'CH2', 'CH2', 'CH3']
    
    #test ignoring identify molecules
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml", identify_molecules=False)
    
    assert system._identify_molecules == False
    assert system._ignore_zero_bond_order == False
    
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
    

def test_Molecule_class():
    molecule = Molecule()
    
    assert len(molecule.particles) == 0
    assert len(molecule.types) == 0
    assert molecule.pattern == ''
    assert molecule.name == 'none'
    assert molecule.n_particles == 0

    molecule.add_particle(0,'test1')
    assert len(molecule.particles) == 1
    assert len(molecule.types) == 1
    assert molecule.types == ['test1']
    assert molecule.pattern == 'test1'
    assert molecule.n_particles == 1

    molecule.add_particle(1,'test2')
    molecule.set_molecule_name('test_molecule')

    assert len(molecule.particles) == 2
    assert len(molecule.types) == 2
    assert molecule.types == ['test1', 'test2']
    assert molecule.pattern == 'test1test2'
    assert molecule.n_particles == 2
    assert molecule.name == 'test_molecule'

@pytest.mark.skipif(sys.platform == 'win32', reason="mbuild CI is failing on windows for an unknown reason.")
def test_mBuild_conversion():
    cwd = os.getcwd()

    molecule_dict = {'CH3CH2CH2CH2CH3': 'pentane', 'water': 'SOL'}
    
    system = hxml.System(cwd + "/hoomdxml_reader/tests/example.hoomdxml")
    system.set_molecule_name_by_dictionary(molecule_dict)
    
    mb_system = convert.System_to_Compound(system)
    
    assert mb_system.n_particles == 10

    assert len(mb_system['molecule']) == 6
    assert len(mb_system['molecule'][0]['particle']) == 5
    assert len(mb_system['molecule'][1]['particle']) == 1
    
    assert mb_system['molecule'][0].name == 'pentane'
    assert mb_system['molecule'][1].name == 'SOL'
    assert mb_system['molecule'][2].name == 'SOL'
    assert mb_system['molecule'][3].name == 'SOL'
    assert mb_system['molecule'][4].name == 'SOL'
    assert mb_system['molecule'][5].name == 'SOL'

    assert mb_system['molecule'][0].n_bonds == 4
    assert mb_system['molecule'][1].n_bonds == 0
    assert mb_system['molecule'][2].n_bonds == 0
    assert mb_system['molecule'][3].n_bonds == 0
    assert mb_system['molecule'][4].n_bonds == 0
    assert mb_system['molecule'][5].n_bonds == 0
    
    assert mb_system['molecule'][0]['particle'][0].n_direct_bonds == 1
    assert mb_system['molecule'][0]['particle'][1].n_direct_bonds == 2
    assert mb_system['molecule'][0]['particle'][2].n_direct_bonds == 2
    assert mb_system['molecule'][0]['particle'][3].n_direct_bonds == 2
    assert mb_system['molecule'][0]['particle'][4].n_direct_bonds == 1

    assert mb_system['molecule'][1]['particle'][0].n_direct_bonds == 0
    assert mb_system['molecule'][2]['particle'][0].n_direct_bonds == 0
    assert mb_system['molecule'][3]['particle'][0].n_direct_bonds == 0
    assert mb_system['molecule'][4]['particle'][0].n_direct_bonds == 0
    assert mb_system['molecule'][5]['particle'][0].n_direct_bonds == 0


    assert mb_system['molecule'][0]['particle'][0].name == 'CH3'
    assert mb_system['molecule'][0]['particle'][1].name == 'CH2'
    assert mb_system['molecule'][0]['particle'][2].name == 'CH2'
    assert mb_system['molecule'][0]['particle'][3].name == 'CH2'
    assert mb_system['molecule'][0]['particle'][4].name == 'CH3'

    assert mb_system['molecule'][1]['particle'][0].name == 'water'
    assert mb_system['molecule'][2]['particle'][0].name == 'water'
    assert mb_system['molecule'][3]['particle'][0].name == 'water'
    assert mb_system['molecule'][4]['particle'][0].name == 'water'
    assert mb_system['molecule'][5]['particle'][0].name == 'water'


    assert list(mb_system['molecule'][0]['particle'][0].pos) == [0.0, 0.0, 0.0]
    assert list(mb_system['molecule'][0]['particle'][1].pos) == [0.5, 0.0, 0.0]
    assert list(mb_system['molecule'][0]['particle'][2].pos) == [1.0, 0.0, 0.0]
    assert list(mb_system['molecule'][0]['particle'][3].pos) == [1.5, 0.0, 0.0]
    assert list(mb_system['molecule'][0]['particle'][4].pos) == [2.0, 0.0, 0.0]
    
    assert list(mb_system['molecule'][1]['particle'][0].pos) == [0.0, 1.0, 0.0]
    assert list(mb_system['molecule'][2]['particle'][0].pos) == [0.5, 0.5, 2.0]
    assert list(mb_system['molecule'][3]['particle'][0].pos) == [3.0, 1.0, 3.0]
    assert list(mb_system['molecule'][4]['particle'][0].pos) == [2.5, 0.0, 1.0]
    assert list(mb_system['molecule'][5]['particle'][0].pos) == [0.0, 2.0, 4.0]

    mb_system_pentane = convert.System_to_Compound(system, name_selection=['pentane'])
    assert mb_system_pentane.n_particles == 5
    assert mb_system_pentane['molecule'][0].name == 'pentane'
    
    assert list(mb_system_pentane['molecule'][0]['particle'][0].pos) == [0.0, 0.0, 0.0]
    assert list(mb_system_pentane['molecule'][0]['particle'][1].pos) == [0.5, 0.0, 0.0]
    assert list(mb_system_pentane['molecule'][0]['particle'][2].pos) == [1.0, 0.0, 0.0]
    assert list(mb_system_pentane['molecule'][0]['particle'][3].pos) == [1.5, 0.0, 0.0]
    assert list(mb_system_pentane['molecule'][0]['particle'][4].pos) == [2.0, 0.0, 0.0]
    
    assert mb_system_pentane['molecule'][0]['particle'][0].n_direct_bonds == 1
    assert mb_system_pentane['molecule'][0]['particle'][1].n_direct_bonds == 2
    assert mb_system_pentane['molecule'][0]['particle'][2].n_direct_bonds == 2
    assert mb_system_pentane['molecule'][0]['particle'][3].n_direct_bonds == 2
    assert mb_system_pentane['molecule'][0]['particle'][4].n_direct_bonds == 1
    
    
    mb_system_sol = convert.System_to_Compound(system, name_selection=['SOL'])
    assert mb_system_sol.n_particles == 5
    assert mb_system_sol['molecule'][0].name == 'SOL'
    assert mb_system_sol['molecule'][1].name == 'SOL'
    assert mb_system_sol['molecule'][2].name == 'SOL'
    assert mb_system_sol['molecule'][3].name == 'SOL'
    assert mb_system_sol['molecule'][4].name == 'SOL'

    assert list(mb_system_sol['molecule'][0]['particle'][0].pos) == [0.0, 1.0, 0.0]
    assert list(mb_system_sol['molecule'][1]['particle'][0].pos) == [0.5, 0.5, 2.0]
    assert list(mb_system_sol['molecule'][2]['particle'][0].pos) == [3.0, 1.0, 3.0]
    assert list(mb_system_sol['molecule'][3]['particle'][0].pos) == [2.5, 0.0, 1.0]
    assert list(mb_system_sol['molecule'][4]['particle'][0].pos) == [0.0, 2.0, 4.0]

    assert mb_system_sol['molecule'][0]['particle'][0].n_direct_bonds == 0
    assert mb_system_sol['molecule'][1]['particle'][0].n_direct_bonds == 0
    assert mb_system_sol['molecule'][2]['particle'][0].n_direct_bonds == 0
    assert mb_system_sol['molecule'][3]['particle'][0].n_direct_bonds == 0
    assert mb_system_sol['molecule'][4]['particle'][0].n_direct_bonds == 0
