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

def generate_xyz_data(molecule_data, displacement_vector=np.array([0,0,0])):
    """ Genera datos XYZ modificados con un vector de desplazamiento. """
    xyz_data = ""
    for x, y, z, atom_type in molecule_data:
        x += displacement_vector[0]
        y += displacement_vector[1]
        z += displacement_vector[2]
        xyz_data += f"{atom_type} {x:.3f} {y:.3f} {z:.3f}\n"

    return str(len(molecule_data)) + "\n\n" + xyz_data

def plot_molecule_with_stmol(xyz_data):
    if not xyz_data:
        st.error("No molecule data found. Please check the SDF file.")
        return

    xyzview = py3Dmol.view(width=800, height=400)
    xyzview.addModel(xyz_data, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

# Streamlit App
st.title('3D Molecular Visualization with Orientation and Translation Controls')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
angle = st.slider('Rotation angle (degrees)', 0, 360, 180)
direction_vector = np.array([
    st.number_input('Translation vector X', value=0.0),
    st.number_input('Translation vector Y', value=0.0),
    st.number_input('Translation vector Z', value=0.0)
])

if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    rotation_angle = np.radians(angle)  # Convert angle to radians for rotation calculations
    # Here you might add rotation logic if needed using numpy or similar to adjust molecule_data
    xyz_data = generate_xyz_data(molecule_data, displacement_vector=direction_vector)
    plot_molecule_with_stmol(xyz_data)
