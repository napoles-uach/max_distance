import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np

def read_sdf_from_string(content):
    """ Parsea el contenido de un archivo SDF desde un string. """
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

def rotate_molecule(molecule_data, angle_rad):
    """ Rotates molecule data around the Z-axis by a given angle in radians. """
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad), np.cos(angle_rad), 0],
        [0, 0, 1]
    ])
    rotated_data = []
    for x, y, z, atom_type in molecule_data:
        rotated_coords = np.dot(rotation_matrix, np.array([x, y, z]))
        rotated_data.append((rotated_coords[0], rotated_coords[1], rotated_coords[2], atom_type))
    return rotated_data

def generate_xyz_data(molecule_data):
    """ Generates XYZ format data from molecule data. """
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

# Streamlit App
st.title('3D Molecular Visualization with Orientation and Translation Controls')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
angle = st.slider('Rotation angle (degrees)', 0, 360, 180)
translation_vector = np.array([
    st.number_input('Translation vector X', value=1.0),
    st.number_input('Translation vector Y', value=0.0),
    st.number_input('Translation vector Z', value=0.0)
])

if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    angle_rad = np.radians(angle)
    rotated_data = rotate_molecule(molecule_data, angle_rad)
    # Apply translation to rotated data
    translated_data = [(x + translation_vector[0], y + translation_vector[1], z + translation_vector[2], atom_type) for x, y, z, atom_type in rotated_data]
    
    original_xyz = generate_xyz_data(rotated_data)
    transformed_xyz = generate_xyz_data(translated_data)
    plot_molecule_with_stmol(original_xyz, transformed_xyz)
