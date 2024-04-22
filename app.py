import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Asumiendo que las clases y funciones como Molecule, read_sdf, etc., ya están definidas.

def plot_molecule(coordinates, symbols, atom_radii, displacement_vector):
    fig = go.Figure()
    atom_color = {'C': 'green', 'H': 'white', 'O': 'red', 'N': 'blue', 'S': 'yellow'}

    for coord, symbol in zip(coordinates, symbols):
        radius = atom_radii.get(symbol, 1.0)
        theta, phi = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        for addition in [0, 1]:
            disp = displacement_vector * addition
            x = coord[0] + disp[0] + radius * np.sin(phi) * np.cos(theta)
            y = coord[1] + disp[1] + radius * np.sin(phi) * np.sin(theta)
            z = coord[2] + disp[2] + radius * np.cos(phi)
            color = atom_color.get(symbol, 'grey')
            fig.add_trace(go.Surface(x=x, y=y, z=z, colorscale=[[0, color], [1, color]], showscale=False))

    fig.update_layout(title='Visualización Molecular 3D con Imagen Desplazada', autosize=False,
                      width=800, height=800, margin=dict(l=0, r=0, b=0, t=0))
    return fig

# Streamlit App
st.title('Visualización Molecular 3D')

# Cargar los datos de la molécula
coordinates, symbols, atom_radii = read_sdf('tu_archivo_sdf.sdf')

# Configuración de controles para la orientación y traslación
angle = st.slider('Ángulo de Rotación (grados)', 0, 360, 0)
direction_vector = np.array([
    st.number_input('Componente X del vector de traslación', value=1.0),
    st.number_input('Componente Y del vector de traslación', value=0.0),
    st.number_input('Componente Z del vector de traslación', value=0.0)
])

# Convertir ángulo a radianes y calcular la nueva configuración de la molécula
angle_rad = np.radians(angle)
rotated_molecule = rotate_molecule(Molecule(coordinates, symbols, atom_radii), angle_rad)
displacement_length = np.linalg.norm(direction_vector)
if displacement_length == 0:
    st.error('El vector de traslación no puede ser el vector cero.')
else:
    normalized_direction_vector = direction_vector / displacement_length
    max_displacement = calculate_contact(rotated_molecule, normalized_direction_vector)
    displacement_vector = max_displacement * normalized_direction_vector

    # Mostrar la figura
    fig = plot_molecule(rotated_molecule.coordinates, rotated_molecule.symbols, atom_radii, displacement_vector)
    st.plotly_chart(fig)
