import streamlit as st
from stmol import showmol
import py3Dmol

def read_sdf_from_string(content):
    """ Parsea el contenido de un archivo SDF desde un string. """
    lines = content.split('\n')
    xyz_data = ''
    reading_molecule = False

    for line in lines:
        if line.startswith('$$$$'):
            reading_molecule = False
        if reading_molecule:
            parts = line.split()
            if len(parts) >= 4 and parts[3].isalpha():
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    atom_type = parts[3]
                    xyz_data += f'{atom_type} {x:.3f} {y:.3f} {z:.3f}\n'
                except ValueError:
                    continue
        if line.strip().endswith('V2000'):
            reading_molecule = True

    return xyz_data

def plot_molecule_with_stmol(xyz_data):
    """ Muestra la molécula utilizando py3Dmol. """
    xyzview = py3Dmol.view(width=800, height=400)
    xyzview.addModel(xyz_data, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

# Streamlit App
st.title('Visualización Molecular 3D')

# Cargar archivo SDF
uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    xyz_data = read_sdf_from_string(file_content)
    plot_molecule_with_stmol(xyz_data)
