import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np

class Molecule:
    def __init__(self, coordinates, symbols, atom_radii):
        self.coordinates = np.array(coordinates)  # Convertir coordenadas a un array NumPy
        self.symbols = np.array(symbols)
        self.atom_radii = {symbol: atom_radii.get(symbol, 1.5) for symbol in symbols}  # Diccionario de radios

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

def calculate_contact(molecule, direction_vector):
    n_atoms = len(molecule.coordinates)
    max_displacement = 0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            distance_vector = molecule.coordinates[i] - molecule.coordinates[j]
            distance = np.linalg.norm(distance_vector)
            projection = np.dot(distance_vector, direction_vector) / np.linalg.norm(direction_vector)
            normal_distance = np.sqrt(distance**2 - projection**2)
            sum_vdw = molecule.get_radius(i) + molecule.get_radius(j)
            if normal_distance <= sum_vdw:
                displacement = projection + np.sqrt(max(sum_vdw**2 - normal_distance**2, 0))
                if displacement > max_displacement:
                    max_displacement = displacement
    return max_displacement

def generate_xyz_data(molecule_data):
    xyz_data = ""
    for x, y, z, atom_type in molecule_data:
        xyz_data += f"{atom_type} {x:.3f} {y:.3f} {z:.3f}\n"
    return str(len(molecule_data)) + "\n\n" + xyz_data

def plot_molecule_with_stmol(original_xyz, transformed_xyz):
    xyzview = py3Dmol.view(width=800, height=400)
    xyzview.addModel(original_xyz, 'xyz')
    xyzview.addModel(transformed_xyz, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

st.title('3D Molecular Visualization with Automatic Displacement Calculation')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    molecule = Molecule(
        coordinates=[data[:3] for data in molecule_data],
        symbols=[data[3] for data in molecule_data],
        atom_radii={'C': 1.7, 'H': 1.2, 'O': 1.52, 'N': 1.55, 'S': 1.8}
    )
    direction_vector = np.array([1, 0, 0])  # Ejemplo de vector de dirección
    max_displacement = calculate_contact(molecule, direction_vector)
    displacement_vector = np.array([max_displacement, 0, 0])  # Aplicar el desplazamiento a lo largo del eje x
    transformed_molecule = [(x + displacement_vector[0], y, z, atom_type) for x, y, z, atom_type in molecule_data]
    original_xyz = generate_xyz_data(molecule_data)
    transformed_xyz = generate_xyz_data(transformed_molecule)
    plot_molecule_with_stmol(original_xyz, transformed_xyz)
