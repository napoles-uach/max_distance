import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np
from utils.molecule_functions import Molecule, read_sdf, rotate_molecule

def plot_molecule_with_stmol(coordinates, symbols, displacement_vector):
    xyz_data = ''
    for coord, symbol in zip(coordinates, symbols):
        # Asumimos que los símbolos ya están en el formato correcto para XYZ (C, H, O, N, etc.)
        xyz_data += f'{symbol} {coord[0]:.3f} {coord[1]:.3f} {coord[2]:.3f}\n'
    
    xyzview = py3Dmol.view(width=400, height=400)
    xyzview.addModel(xyz_data, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

# Streamlit App
st.title('Visualización Molecular 3D')

# Cargar los datos de la molécula
file_path = st.text_input('Ingrese la ruta del archivo SDF', 'path/to/your/file.sdf')
coordinates, symbols, atom_radii = read_sdf(file_path)

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
plot_molecule_with_stmol(displaced_coordinates, rotated_molecule.symbols, direction_vector)

