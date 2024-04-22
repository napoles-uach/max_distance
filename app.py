def read_sdf_from_string(content):
    """ Parsea el contenido de un archivo SDF desde un string. """
    lines = content.split('\n')
    xyz_data = ''
    atom_count = 0
    reading_molecule = False

    for line in lines:
        if line.startswith('$$$$'):
            reading_molecule = False  # Finalizar la lectura al encontrar el final del bloque de molécula
        elif line.strip().endswith('V2000'):
            reading_molecule = True  # Iniciar la lectura después de encontrar 'V2000'
            continue  # Evitar incluir la línea 'V2000' en el procesamiento

        if reading_molecule:
            parts = line.strip().split()
            if len(parts) >= 4 and parts[3].isalpha():  # Verifica si la línea contiene coordenadas y símbolos
                try:
                    x, y, z = map(float, parts[:3])
                    atom_type = parts[3]
                    xyz_data += f'{atom_type} {x:.3f} {y:.3f} {z:.3f}\n'
                    atom_count += 1
                except ValueError:
                    continue  # Manejo de error por si alguna conversión falla

    # Preparar el formato XYZ con el conteo de átomos y una línea en blanco
    xyz_data_formatted = f"{atom_count}\n\n{xyz_data}"
    return xyz_data_formatted

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
st.title('Visualización Molecular 3D')

uploaded_file = st.file_uploader("Upload your SDF file", type=["sdf"])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    xyz_data = read_sdf_from_string(file_content)
    plot_molecule_with_stmol(xyz_data)

