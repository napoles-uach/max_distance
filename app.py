import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np
from utils.molecule_functions import Molecule, rotate_molecule

def read_sdf_from_string(content):
    """ Esta función parsea el contenido de un archivo SDF desde un string. """
    lines = content.split('\n')
    coordinates = []
    symbols = []
    molecule_data = []
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
                    molecule_data.append((x, y, z, atom_type))
                except ValueError:
                    continue
        if line.strip().endswith('V2000'):
            reading_molecule = True
            molecule_data = []  # Reiniciar para cada nueva molécula

    atom_radii = {'C': 1.7, 'H': 1.2, 'O': 1.52, 'N': 1.55, 'S': 1.8}
    for (x, y, z, atom_type) in molecule_data:
        coordinates.append([x, y, z])
        symbols.append(atom_type)

    return coordinates, symbols, atom_radii

def plot_molecule_with_stmol(coordinates, symbols):
    """ Genera y muestra la visualización de la molécula utilizando py3Dmol. """
    xyz_data = ''
    for coord, symbol in zip(coordinates, symbols):
        xyz_data += f'{symbol} {coord[0]:.3f} {coord[1]:.3f} {coord[2]:.3f}\n'
    
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
    coordinates, symbols, atom_radii = read_sdf_from_string(file_content)

    # Configuración de controles para la orientación y traslación
    angle = st.slider('Ángulo de Rotación (grados)', 0, 360, 0)
    direction_vector = np.array([
        st.number_input('Componente X del vector de traslación', value=0.0),
        st.number_input('Componente Y del vector de traslación', value=0.0),
        st.number_input('Componente Z del vector de traslación', value=0.0)
    ])

    # Convertir ángulo a radianes y calcular la nueva configuración de la molécula
    angle_rad = np.radians(angle)
    rotated_molecule = rotate_molecule(Molecule(coordinates, symbols, atom_radii), angle_rad)

    # Aplicar el vector de traslación
    displaced_coordinates = rotated_molecule.coordinates + direction_vector

    # Mostrar la figura con stmol
    plot_molecule_with_stmol(displaced_coordinates, rotated_molecule.symbols)

