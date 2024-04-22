import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np
# Asumiendo que max_distance_closepacking.py está en el mismo directorio o en el path de Python
from max_distance_closepacking import calculate_max_displacement

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

st.title('3D Molecular Visualization')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    original_xyz = generate_xyz_data(molecule_data)
    max_displacement = calculate_max_displacement(molecule_data)
    displacement_vector = np.array([max_displacement, 0, 0])  # Example displacement along x-axis
    transformed_molecule = [(x + displacement_vector[0], y, z, atom_type) for x, y, z, atom_type in molecule_data]
    transformed_xyz = generate_xyz_data(transformed_molecule)
    plot_molecule_with_stmol(original_xyz, transformed_xyz)

