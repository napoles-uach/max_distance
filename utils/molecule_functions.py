import numpy as np

class Molecule:
    def __init__(self, coordinates, symbols, atom_radii):
        self.coordinates = np.array(coordinates)  # Array de coordenadas de vectores
        self.symbols = np.array(symbols)  # Array de símbolos químicos de los átomos
        self.atom_radii = atom_radii  # Diccionario de radios de van der Waals para cada tipo de átomo

def read_sdf(file_path):
    """ Lee un archivo SDF y extrae las coordenadas, símbolos y radios de van der Waals de los átomos. """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    coordinates = []
    symbols = []
    molecule_data = []
    reading_molecule = False

    for line in lines:
        if line.startswith('$$$$'):
            reading_molecule = False
        if reading_molecule:
            parts = line.split()
            if len(parts) >= 4 and parts[3].isalpha():  # Confirma que hay un símbolo de elemento
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    atom_type = parts[3]
                    molecule_data.append((x, y, z, atom_type))
                except ValueError:
                    continue
        if line.strip().endswith('V2000'):
            reading_molecule = True
            molecule_data = []  # Reiniciar para cada nueva molécula

    atom_radii = {
        'C': 1.7, 'H': 1.2, 'O': 1.52, 'N': 1.55, 'S': 1.8
    }
    for (x, y, z, atom_type) in molecule_data:
        coordinates.append([x, y, z])
        symbols.append(atom_type)

    return coordinates, symbols, atom_radii

def rotate_molecule(molecule, angle):
    """ Rota una molécula alrededor del eje Z por un ángulo dado en radianes. """
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    new_coordinates = np.dot(molecule.coordinates, rotation_matrix.T)
    return Molecule(new_coordinates, molecule.symbols, molecule.atom_radii)

def calculate_contact(molecule, direction_vector):
    """ Calcula el desplazamiento máximo necesario para evitar superposición entre átomos en una dirección dada. """
    n_atoms = len(molecule.coordinates)
    max_displacement = 0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            distance_vector = molecule.coordinates[i] - molecule.coordinates[j]
            distance = np.linalg.norm(distance_vector)
            projection = np.dot(distance_vector, direction_vector) / np.linalg.norm(direction_vector)
            normal_distance = np.sqrt(distance**2 - projection**2)
            sum_vdw = molecule.atom_radii[molecule.symbols[i]] + molecule.atom_radii[molecule.symbols[j]]
            if normal_distance <= sum_vdw:
                displacement = projection + np.sqrt(max(sum_vdw**2 - normal_distance**2, 0))
                if displacement > max_displacement:
                    max_displacement = displacement
    return max_displacement
