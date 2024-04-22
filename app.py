import streamlit as st
from stmol import showmol
import py3Dmol
import numpy as np

def read_sdf_from_string(content):
    """ Parsea el contenido de un archivo SDF desde un string y extrae los datos de la molécula. """
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

def calculate_max_displacement(molecule_data):
    """ Calcula la máxima distancia entre puntos (átomos) en la molécula para establecer un desplazamiento adecuado. """
    max_distance = 0
    for i in range(len(molecule_data)):
        for j in range(i + 1, len(molecule_data)):
            dist = np.linalg.norm(np.array(molecule_data[i][:3]) - np.array(molecule_data[j][:3]))
            if dist > max_distance:
                max_distance = dist
    return max_distance

def generate_xyz_data(molecule_data):
    """ Genera datos en formato XYZ para la visualización en py3Dmol. """
    xyz_data = ""
    for x, y, z, atom_type in molecule_data:
        xyz_data += f"{atom_type} {x:.3f} {y:.3f} {z:.3f}\n"
    return str(len(molecule_data)) + "\n\n" + xyz_data

def plot_molecule_with_stmol(original_xyz, transformed_xyz):
    """ Utiliza py3Dmol para visualizar la molécula original y la molécula transformada. """
    xyzview = py3Dmol.view(width=800, height=400)
    xyzview.addModel(original_xyz, 'xyz')
    xyzview.addModel(transformed_xyz, 'xyz')
    xyzview.setStyle({'sphere': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=800)

# Streamlit App
st.title('3D Molecular Visualization with Automatic Displacement Calculation')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    molecule_data = read_sdf_from_string(file_content)
    original_xyz = generate_xyz_data(molecule_data)
    max_displacement = calculate_max_displacement(molecule_data)
    displacement_vector = np.array([max_displacement, 0, 0])  # Desplazamiento a lo largo del eje x
    transformed_molecule = [(x + displacement_vector[0], y, z, atom_type) for x, y, z, atom_type in molecule_data]
    transformed_xyz = generate_xyz_data(transformed_molecule)
    plot_molecule_with_stmol(original_xyz, transformed_xyz)
    st.write(max_displacement)

