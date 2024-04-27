import streamlit as st
from stmol import showmol
import py3Dmol
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
    return max_displacement,i , j



def generate_xyz_data(molecule):
    xyz_data = ""
    for i in range(len(molecule.coordinates)):
        x, y, z = molecule.coordinates[i]
        atom_type = molecule.symbols[i]
        xyz_data += f"{atom_type} {x:.3f} {y:.3f} {z:.3f}\n"
    return str(len(molecule.coordinates)) + "\n\n" + xyz_data



def plot_molecule_with_stmol(original_xyz, transformed_xyz):
    xyzview = py3Dmol.view(width=800, height=400)
    xyzview.addModel(original_xyz, 'xyz')
    xyzview.addModel(transformed_xyz, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

st.markdown('## Automatic Molecular Displacement Calculation')

col1,col2=st.columns([2,3])
file_path = col1.selectbox("Choose a molecule",['PCBM-3D-structure-CT1089645246.sdf','ChEBI_27732.sdf','cholesterol-3D-structure-CT1001897301.sdf'])#'PCBM-3D-structure-CT1089645246.sdf'
molecule_data = read_sdf_from_file(file_path)
molecule = Molecule(
    coordinates=[data[:3] for data in molecule_data],
    symbols=[data[3] for data in molecule_data],
    atom_radii={'C': 1.7, 'H': 1.2, 'O': 1.52, 'N': 1.55, 'S': 1.8}
)

#----------
uploaded_file = col2.file_uploader("Upload your SDF file, only molecules with C,H,O,N,S atoms", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    molecule = Molecule(
        coordinates=[data[:3] for data in molecule_data],
        symbols=[data[3] for data in molecule_data],
        atom_radii={'C': 1.7, 'H': 1.2, 'O': 1.52, 'N': 1.55, 'S': 1.8}
    )
#----------

angle_x = st.sidebar.slider('Rotation angle around X-axis (degrees)', 0, 360, 0)
angle_y = st.sidebar.slider('Rotation angle around Y-axis (degrees)', 0, 360, 0)
angle_z = st.sidebar.slider('Rotation angle around Z-axis (degrees)', 0, 360, 0)

rotated_molecule = apply_rotation(molecule, (angle_x, angle_y, angle_z))

direction_vector = np.array([1, 0, 0])
max_displacement,atom_i,atom_j = calculate_contact(rotated_molecule, direction_vector)
displacement_vector = np.array([max_displacement, 0, 0])
transformed_coords = rotated_molecule.coordinates + displacement_vector
transformed_molecule = Molecule(transformed_coords, rotated_molecule.symbols, rotated_molecule.atom_radii)

original_xyz = generate_xyz_data(rotated_molecule)
transformed_xyz = generate_xyz_data(transformed_molecule)
st.markdown("## Displacement: "+"{:.2f}".format(max_displacement) + " Å")
plot_molecule_with_stmol(original_xyz,transformed_xyz)



