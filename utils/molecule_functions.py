import numpy as np

class Molecule:
    def __init__(self, coordinates, symbols, atom_radii):
        self.coordinates = np.array(coordinates)
        self.symbols = symbols
        self.atom_radii = {symbol: atom_radii.get(symbol, 1.5) for symbol in symbols}

    def get_radius(self, atom_index):
        return self.atom_radii[self.symbols[atom_index]]

def read_sdf_from_string(content):
    lines = content.split('\n')
    molecule_data = []
    reading_molecule = False

    for line in lines:
        if line.startswith('$$$$'):
            reading_molecule = False
        elif line.strip().endswith('V2000'):
            reading_molecule = True
            continue

        if reading_molecule:
            parts = line.strip().split()
            if len(parts) >= 4 and parts[3].isalpha():
                try:
                    x, y, z = map(float, parts[:3])
                    atom_type = parts[3]
                    molecule_data.append((x, y, z, atom_type))
                except ValueError:
                    continue
    return molecule_data

def read_sdf_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    lines = content.split('\n')
    molecule_data = []
    reading_molecule = False

    for line in lines:
        if line.startswith('$$$$'):
            reading_molecule = False
        elif line.strip().endswith('V2000'):
            reading_molecule = True
            continue

        if reading_molecule:
            parts = line.strip().split()
            if len(parts) >= 4 and parts[3].isalpha():
                try:
                    x, y, z = map(float, parts[:3])
                    atom_type = parts[3]
                    molecule_data.append((x, y, z, atom_type))
                except ValueError:
                    continue
    return molecule_data

def apply_rotation(molecule, angles):
    rx, ry, rz = np.radians(angles)
    Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])
    R = np.dot(Rz, np.dot(Ry, Rx))
    rotated_coords = np.dot(molecule.coordinates, R.T)
    return Molecule(rotated_coords, molecule.symbols, molecule.atom_radii)

def calculate_contact(molecule, direction_vector):
    n_atoms = len(molecule.coordinates)
    max_displacement = 0

    for i in range(n_atoms):
        for j in range( n_atoms):
            distance_vector = molecule.coordinates[i] - molecule.coordinates[j]
            distance = np.linalg.norm(distance_vector)
            projection = np.dot(distance_vector, direction_vector) / np.linalg.norm(direction_vector)
            normal_distance = np.sqrt(distance**2 - projection**2)
            sum_vdw = molecule.get_radius(i) + molecule.get_radius(j)
            if normal_distance <= sum_vdw:
                displacement = projection + np.sqrt(max(sum_vdw**2 - normal_distance**2, 0))
                if displacement > max_displacement:
                    max_displacement = displacement
                    index_i=i
                    index_j=j
    return max_displacement#,index_i , index_j



def generate_xyz_data(molecule):
    xyz_data = ""
    for i in range(len(molecule.coordinates)):
        x, y, z = molecule.coordinates[i]
        atom_type = molecule.symbols[i]
        xyz_data += f"{atom_type} {x:.3f} {y:.3f} {z:.3f}\n"
    return str(len(molecule.coordinates)) + "\n\n" + xyz_data
