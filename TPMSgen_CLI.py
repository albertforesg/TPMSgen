import copy
import os
import trimesh

import numpy as np
import pyvista as pv

from skimage import measure

# MAIN FUNCTIONS
# Plot TPMS equation:
def fn_plot_tpms_eq(tpms_type, sizes, cell_sizes, origin, unit_cell_mesh_resolution, c, mesh):
    # Generation of the meshgrid:
    tols = [0, 0, 0]
    X, Y, Z, tols, spacing  = generate_meshgrid(0, sizes, cell_sizes, unit_cell_mesh_resolution)

    # Generate TPMS:
    F, t = tpms_library(X, Y, Z, c, tpms_design, cell_sizes, origin)

    # Mesh TPMS:
    if tpms_type == 'Shell':
        mesh, vertices = mesh_shell(F, t, thickness, sizes, mesh, tols, spacing)
    else:
        mesh, vertices = mesh_skeletal(F, sizes, mesh, tols, spacing)

    # Colour TPMS vertices:
    color = []
    for vert in vertices:
        color.append(vert[0] * vert[1] * vert[2])
    color = np.array(color)

    # Plot TPMS vertices:
    plotter1 = pv.Plotter(window_size = [1400, 1600])
    _ = plotter1.add_title('Close this window to continue', font_size = 10)
    _ = plotter1.add_mesh(vertices, scalars = color, cmap = 'jet')
    _ = plotter1.remove_scalar_bar()
    _ = plotter1.show_grid()
    plotter1.show()

    return mesh, vertices

# Check face normals:
def fn_check_face_normals(mesh):
    # Calculate face centroids and normals:
    mesh_pv = pv.wrap(mesh)
    cent = mesh_pv.cell_centers().points
    direction = mesh_pv.cell_normals

    # Update output message:
    print('\nCheck if face normals are pointing OUT of the mesh')

    # Plot TPMS face normals:
    plotter2 = pv.Plotter(window_size = [1400, 1600])
    _ = plotter2.add_title('Close this window to continue', font_size = 10)
    _ = plotter2.add_mesh(mesh, color = True, show_edges = True)
    _ = plotter2.add_arrows(cent, direction, mag = 1)
    _ = plotter2.remove_scalar_bar()
    _ = plotter2.show_grid()
    plotter2.show()

    return mesh

# Check face normals:
def fn_flip_face_normals(mesh):
    # Flip mesh:
    mesh = pv.wrap(mesh)
    mesh.flip_normals()
    mesh = mesh_conversion(mesh)

    print('Face normals were flipped. Now face normals should be pointing OUT of the mesh')

    # Calculate face centroids and normals:
    mesh_pv = pv.wrap(mesh)
    cent = mesh_pv.cell_centers().points
    direction = mesh_pv.cell_normals
    
    # Plot TPMS face normals:
    plotter3 = pv.Plotter(window_size = [1400, 1600])
    _ = plotter3.add_title('Close this window to continue', font_size = 10)
    _ = plotter3.add_mesh(mesh, color = True, show_edges = True)
    _ = plotter3.add_arrows(cent, direction, mag = 1)
    _ = plotter3.remove_scalar_bar()
    _ = plotter3.show_grid()
    plotter3.show()

    return mesh

# Generate mesh:
def fn_generate_mesh(tpms_type, tpms_design, c, thickness, sizes, cell_sizes, origin, unit_cell_mesh_resolution, mesh, flip_face_normals):
    is_watertight = False
    k = int(5 / 100 * unit_cell_mesh_resolution)
    k_max = int(45 / 100 * unit_cell_mesh_resolution)
    k_increment = int(5 / 100 * unit_cell_mesh_resolution)
    iterative_mesh = copy.deepcopy(mesh)

    # Mesh generation iterative process:
    if tpms_type == 'Shell':
        # Generate bounding box:
        shell_bounding_box = trimesh.creation.box(extents = (sizes[0], sizes[1], sizes[2]), transform = None)
        while not is_watertight and k <= k_max:
            # Generation of the meshgrid:
            X, Y, Z, tols, spacing  = generate_meshgrid(k, sizes, cell_sizes, unit_cell_mesh_resolution)
            
            # Generate TPMS for intersection:
            F, t = tpms_library(X, Y, Z, c, tpms_design, cell_sizes, origin)

            # Mesh TPMS for intersection:
            iterative_mesh, _ = mesh_shell(F, t, thickness, sizes, iterative_mesh, tols, spacing)

            # Check face normals orientation:
            if flip_face_normals:
                iterative_mesh = pv.wrap(iterative_mesh)
                iterative_mesh.flip_normals()
                iterative_mesh = mesh_conversion(iterative_mesh)
            
            # Calculate intercection:
            iterative_mesh = trimesh.boolean.intersection((iterative_mesh, shell_bounding_box), engine = 'blender')
            
            # Check obtained results
            k += k_increment
            is_watertight = iterative_mesh.is_watertight
            if not iterative_mesh.is_watertight:
                iterative_mesh.fill_holes()
                is_watertight = iterative_mesh.is_watertight
    else:
        # Generate bounding box:
        bounding_box_1 = trimesh.creation.box(extents = (2 * sizes[0], 2 * sizes[1], 2 * sizes[2]), transform = None)
        bounding_box_2 = trimesh.creation.box(extents = (sizes[0], sizes[1], sizes[2]), transform = None)
        bounding_box = trimesh.boolean.difference((bounding_box_1, bounding_box_2), engine = 'blender')
        
        del bounding_box_1, bounding_box_2
        
        while not is_watertight and k <= k_max:
            # Generation of the meshgrid:
            X, Y, Z, tols, spacing  = generate_meshgrid(k, sizes, cell_sizes, unit_cell_mesh_resolution)
            
            # Generate TPMS for intersection:
            F, t = tpms_library(X, Y, Z, c, tpms_design, cell_sizes, origin)

            # Mesh TPMS for intersection:
            iterative_mesh, _ = mesh_skeletal(F, sizes, iterative_mesh, tols, spacing)

            # Check face normals orientation:
            if flip_face_normals:
                iterative_mesh = pv.wrap(iterative_mesh)
                iterative_mesh.flip_normals()
                iterative_mesh = mesh_conversion(iterative_mesh)
            
            # Calculate intercection:
            iterative_mesh = trimesh.boolean.difference((iterative_mesh, bounding_box), engine = 'blender')
            
            # Check obtained results
            k += k_increment
            is_watertight = iterative_mesh.is_watertight
            if not iterative_mesh.is_watertight:
                iterative_mesh.fill_holes()
                is_watertight = iterative_mesh.is_watertight

    # Update output message:
    if is_watertight:
        print('Mesh is generated!')
        print('The obtained mesh is watertight. If the opposite solution was desired, try using the opposite face normals direction.')
    else:
        print('Mesh is generated:')
        print('Cannot obtain a watertight mesh. Try increasing unit cell mesh resolution. Please, check results carefully and treat them to solve this issue.')
    
    # Plot generated mesh:
    plotter4 = pv.Plotter(window_size = [1400, 1600])
    _ = plotter4.add_title('Generated mesh can be exported into STL format', font_size = 10)
    _ = plotter4.add_mesh(iterative_mesh, color = True, show_edges = True)
    _ = plotter4.show_grid()
    plotter4.show()

    return iterative_mesh

# Export mesh:
def fn_export_stl_file(iterative_mesh, file_name, directory_path):
    export = trimesh.exchange.stl.export_stl_ascii(iterative_mesh)
    
    file_path = os.path.join(directory_path, file_name + '.stl')
    with open(file_path, 'w') as file:
        file.write(export)
    
    print('\nMesh exported as .STL into ' + file_path)

# SUPLEMENTARY FUNCTIONS:
# Generate meshgrid
def generate_meshgrid(k, sizes, cell_sizes, unit_cell_mesh_resolution):
    tol_x = k * cell_sizes[0] / unit_cell_mesh_resolution
    tol_y = k * cell_sizes[1] / unit_cell_mesh_resolution
    tol_z = k * cell_sizes[2] / unit_cell_mesh_resolution
    tols = [tol_x, tol_y, tol_z]

    xl = np.linspace(-sizes[0]/2 - tols[0], sizes[0]/2 + tols[0], int(sizes[0] / cell_sizes[0]) * unit_cell_mesh_resolution + 2 * k + 1)
    yl = np.linspace(-sizes[1]/2 - tols[1], sizes[1]/2 + tols[1], int(sizes[1] / cell_sizes[1]) * unit_cell_mesh_resolution + 2 * k + 1)
    zl = np.linspace(-sizes[2]/2 - tols[2], sizes[2]/2 + tols[2], int(sizes[2] / cell_sizes[2]) * unit_cell_mesh_resolution + 2 * k + 1)
    spacing = [xl, yl, zl]
    
    Y, X, Z = np.meshgrid(yl, xl, zl)

    return X, Y, Z, tols, spacing  

# Mesh conversion
def mesh_conversion(mesh_pv):
    faces_as_array = mesh_pv.faces.reshape((mesh_pv.n_faces, 4))[:, 1:]
    mesh = trimesh.Trimesh(mesh_pv.points, faces_as_array)

    return mesh

# Mesh Shell
def mesh_shell(F, t, thickness, sizes, mesh, tols, spacing):
    vertices_positive, faces_positive, vertex_normals_positive, _ = measure.marching_cubes(F, thickness * t, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])
    vertices_negative, faces_negative, vertex_normals_negative, _ = measure.marching_cubes(F, -thickness * t, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])

    for i, vert in enumerate(vertices_positive):
        vertices_positive[i, 0] = vert[0] - sizes[0]/2 - tols[0]
        vertices_positive[i, 1] = vert[1] - sizes[1]/2 - tols[1]
        vertices_positive[i, 2] = vert[2] - sizes[2]/2 - tols[2]

    for i, vert in enumerate(vertices_negative):
        vertices_negative[i, 0] = vert[0] - sizes[0]/2 - tols[0]
        vertices_negative[i, 1] = vert[1] - sizes[1]/2 - tols[1]
        vertices_negative[i, 2] = vert[2] - sizes[2]/2 - tols[2]

    vertices = np.concatenate((vertices_positive, vertices_negative))
    
    mesh_1 = trimesh.Trimesh(vertices = vertices_positive, faces = faces_positive, vertex_normals = vertex_normals_positive)
    mesh_2 = trimesh.Trimesh(vertices = vertices_negative, faces = faces_negative, vertex_normals = vertex_normals_negative)
    mesh_2 = pv.wrap(mesh_2)
    mesh_2.flip_normals()
    mesh_2 = mesh_conversion(mesh_2)

    mesh = trimesh.util.concatenate((mesh_1, mesh_2))
    
    del vertices_positive, faces_positive, vertex_normals_positive, vertices_negative, faces_negative, vertex_normals_negative, mesh_1, mesh_2

    return mesh, vertices

# Mesh Skeletal
def mesh_skeletal(F, sizes, mesh, tols, spacing):
    vertices, faces, _, _ = measure.marching_cubes(F, 0, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])
    for i, vert in enumerate(vertices):
        vertices[i, 0] = vert[0] - sizes[0]/2 - tols[0]
        vertices[i, 1] = vert[1] - sizes[1]/2 - tols[1]
        vertices[i, 2] = vert[2] - sizes[2]/2 - tols[2]
    
    mesh = trimesh.Trimesh(vertices = vertices, faces = faces)

    del faces

    return mesh, vertices

# TPMS library
def tpms_library(X, Y, Z, c, tpms_design, cell_sizes, origin):
    w_x = 1 / cell_sizes[0] * 2 * np.pi
    w_y = 1 / cell_sizes[1] * 2 * np.pi
    w_z = 1 / cell_sizes[2] * 2 * np.pi
    
    if tpms_design == 'Skeletal-TPMS Schoen gyroid' or tpms_design == 'Shell-TPMS Gyroid':
        F = (np.cos(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) + np.cos(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) + np.cos(w_z * (Z + origin[2])) * np.sin(w_x * (X + origin[0])) - c)   # J
        t = 0.125
    
    elif tpms_design == 'Skeletal-TPMS Schwarz diamond':
        F = (np.cos(w_x * (X + origin[0])) * np.cos(w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.sin(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) - c)   # K
        t = 0
    
    elif tpms_design == 'Skeletal-TPMS Schwarz primitive (pinched)' or tpms_design == 'Skeletal-TPMS Schwarz primitive':
        F = (np.cos(w_x * (X + origin[0])) + np.cos(w_y * (Y + origin[1])) + np.cos(w_z * (Z + origin[2])) - c)   # M, N
        t = 0
    
    elif tpms_design == 'Skeletal-TPMS Body diagonals with nodes':
        F = (2 * (np.cos(w_x * ((X + origin[0]))) * np.cos(w_y * (Y + origin[1])) + np.cos(w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.cos(w_z * (Z + origin[2])) * np.cos(w_x * (X + origin[0]))) - (np.cos(2 * w_x * (X + origin[0])) + np.cos(2 * w_y * (Y + origin[1])) + np.cos(2 * w_z * (Z + origin[2]))) - c) # O
        t = 0
    
    elif tpms_design == 'Shell-TPMS Diamond':
        F = (np.sin(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) + np.sin(w_x * (X + origin[0])) * np.cos(w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.cos(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.cos(w_x * (X + origin[0])) * np.cos(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) - c) # Q
        t = 0.115
    
    elif tpms_design == 'Shell-TPMS Lidinoid':
        F = (np.sin(2 * w_x * (X + origin[0])) * np.cos(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) + np.sin(w_x * (X + origin[0])) * np.sin(2 * w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.cos(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) * np.sin(2 * w_z * (Z + origin[2])) - np.cos(2 * w_x * (X + origin[0])) * np.cos(2 * w_y * (Y + origin[1])) - np.cos(2 * w_y * (Y + origin[1])) * np.cos(2 * w_z * (Z + origin[2])) - np.cos(2 * w_z * (Z + origin[2])) * np.cos(2 * w_x * (X + origin[0])) + 0.3 - c)
        t = 0.37
    
    elif tpms_design == 'Shell-TPMS Split-P':
        F = (1.1 * (np.sin(2 * w_x * (X + origin[0])) * np.cos(w_y * (Y + origin[1])) * np.sin(w_z * (Z + origin[2])) + np.sin(w_x * (X + origin[0])) * np.sin(2 * w_y * (Y + origin[1])) * np.cos(w_z * (Z + origin[2])) + np.cos(w_x * (X + origin[0])) * np.sin(w_y * (Y + origin[1])) * np.sin(2 * w_z * (Z + origin[2]))) - 0.2 * (np.cos(2 * w_x * (X + origin[0])) * np.cos(2 * w_y * (Y + origin[1])) + np.cos(2 * w_y * (Y + origin[1])) * np.cos(2 * w_z * (Z + origin[2])) + np.cos(2 * w_z * (Z + origin[2])) * np.cos(2 * w_x * (X + origin[0]))) - 0.4 * (np.cos(2 * w_x * (X + origin[0])) + np.cos(2 * w_y * (Y + origin[1])) + np.cos(2 * w_z * (Z + origin[2]))) - c)
        t = 0.19
    
    elif tpms_design == 'Shell-TPMS Schwarz':
        F = (np.cos(w_x * (X + origin[0])) + np.cos(w_y * (Y + origin[1])) + np.cos(w_z * (Z + origin[2])) - c)
        t = 0.0875
    
    else:
        print('Design not found in library')
        F = 0
        t = 0

    return F, t


if __name__ == "__main__":
    active_session = True
    while active_session:
        # Selection of TPMS typology:
        input_validator = False
        while not input_validator:
            print('\n[SH] for Shell')
            print('[SK] for Skeletal')
            tpms_type = input('Select TPMS typology: ')
            if tpms_type == 'SH':
                tpms_type = 'Shell'
                input_validator = True
            elif tpms_type == 'SK':
                tpms_type = 'Skeletal'
                input_validator = True
            else:
                print('Invalid input')

        if tpms_type == 'Shell':
            # Selection of Shell-TPMS design:
            input_validator = False
            while not input_validator:
                print('\n[1] for Gyroid')
                print('[2] for Diamond')
                print('[3] for Lidinoid')
                print('[4] for Split-P')
                print('[5] for Schwarz')
                tpms_design = input('Select Shell-TPMS design: ')
                if tpms_design == '1':
                    tpms_design = 'Shell-TPMS Gyroid'
                    input_validator = True
                elif tpms_design == '2':
                    tpms_design = 'Shell-TPMS Diamond'
                    input_validator = True
                elif tpms_design == '3':
                    tpms_design = 'Shell-TPMS Lidinoid'
                    input_validator = True
                elif tpms_design == '4':
                    tpms_design = 'Shell-TPMS Split-P'
                    input_validator = True
                elif tpms_design == '5':
                    tpms_design = 'Shell-TPMS Schwarz'
                    input_validator = True
                else:
                    print('Invalid input')

            # Selection of thickness:
            input_validator = False
            while not input_validator:
                thickness = input('\nEnter thickness in mm (default = 3 mm): ')
                if not thickness:
                    thickness = 3
                    c = 0
                    print(thickness)
                    input_validator = True
                else:
                    try:
                        thickness = float(thickness)
                        if thickness > 0:
                            c = 0
                            input_validator = True
                        else:
                            print('Invalid input')
                    except ValueError:
                        print('Invalid input')

        else:
            # Selection of Shell-TPMS design:
            input_validator = False
            while not input_validator:
                print('\n[1] for Schoen gyroid')
                print('[2] for Schwarz diamond')
                print('[3] for Schwarz primitive (pinched)')
                print('[4] for Schwarz primitive')
                print('[5] for Body diagonals with nodes')
                tpms_design = input('Select Skeletal-TPMS design: ')
                if tpms_design == '1':
                    tpms_design = 'Skeletal-TPMS Schoen gyroid'
                    input_validator = True
                elif tpms_design == '2':
                    tpms_design = 'Skeletal-TPMS Schwarz diamond'
                    input_validator = True
                elif tpms_design == '3':
                    tpms_design = 'Skeletal-TPMS Schwarz primitive (pinched)'
                    input_validator = True
                elif tpms_design == '4':
                    tpms_design = 'Skeletal-TPMS Schwarz primitive'
                    input_validator = True
                elif tpms_design == '5':
                    tpms_design = 'Skeletal-TPMS Body diagonals with nodes'
                    input_validator = True
                else:
                    print('Invalid input')
            
            # Selection of C value:
            input_validator = False
            while not input_validator:
                c = input('\nEnter C value (default = 0.5): ')
                if not c:
                    c = 0.5
                    thickness = 0
                    print(c)
                    input_validator = True
                else:
                    try:
                        c = float(c)
                        if c != 0:
                            thickness = 0
                            input_validator = True
                        else:
                            print('C value must be different from 0 in Skeletal-TPMS designs.')
                    except ValueError:
                        print('Invalid input')

        # Bounding box definition:
        print('\nEnter bounding box dimensions:')
        input_validator = False
        while not input_validator:
            x_size = input('Enter X bounding box dimension in mm (default = 40 mm): ')
            if not x_size:
                x_size = 40
                print(x_size)
                input_validator = True
            else:
                try:
                    x_size = float(x_size)
                    if x_size > 0:
                        input_validator = True
                    else:
                        print('X bounding box dimension must be positive')
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            y_size = input('Enter Y bounding box dimension in mm (default = 40 mm): ')
            if not y_size:
                y_size = 40
                print(y_size)
                input_validator = True
            else:
                try:
                    y_size = float(y_size)
                    if y_size > 0:
                        input_validator = True
                    else:
                        print('Y bounding box dimension must be positive')
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            z_size = input('Enter Z bounding box dimension in mm (default = 40 mm): ')
            if not z_size:
                z_size = 40
                print(z_size)
                input_validator = True
            else:
                try:
                    z_size = float(z_size)
                    if z_size > 0:
                        input_validator = True
                    else:
                        print('Z bounding box dimension must be positive')
                except:
                    print('Invalid input')
        sizes = [x_size, y_size, z_size]
        del x_size, y_size, z_size

        # Unit cell size definition:
        print('\nEnter unit cell dimensions:')
        input_validator = False
        while not input_validator:
            x_cell_size = input('Enter X unit cell dimension in mm (default = 40 mm): ')
            if not x_cell_size:
                x_cell_size = 40
                print(x_cell_size)
                input_validator = True
            else:
                try:
                    x_cell_size = float(x_cell_size)
                    if x_cell_size > 0:
                        if x_cell_size <= sizes[0]:
                            input_validator = True
                        else:
                            print('X unit cell dimension must be lower or equal than X bounding box dimension (' + str(sizes[0]) + ' mm)')
                    else:
                        print('X unit cell dimension must be positive and lower or equal than X bounding box dimension (' + str(sizes[0]) + ' mm)')
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            y_cell_size = input('Enter Y unit cell dimension in mm (default = 40 mm): ')
            if not y_cell_size:
                y_cell_size = 40
                print(y_cell_size)
                input_validator = True
            else:
                try:
                    y_cell_size = float(y_cell_size)
                    if y_cell_size > 0:
                        if y_cell_size <= sizes[1]:
                            input_validator = True
                        else:
                            print('Y unit cell dimension must be lower or equal than Y bounding box dimension (' + str(sizes[1]) + ' mm)')
                    else:
                        print('Y unit cell dimension must be positive and lower or equal than Y bounding box dimension (' + str(sizes[1]) + ' mm)')
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            z_cell_size = input('Enter Z unit cell dimension in mm (default = 40 mm): ')
            if not z_cell_size:
                z_cell_size = 40
                print(z_cell_size)
                input_validator = True
            else:
                try:
                    z_cell_size = float(z_cell_size)
                    if z_cell_size > 0:
                        if z_cell_size <= sizes[2]:
                            input_validator = True
                        else:
                            print('Z unit cell dimension must be lower or equal than Z bounding box dimension (' + str(sizes[2]) + ' mm)')
                    else:
                        print('Z unit cell dimension must be positive and lower or equal than Z bounding box dimension (' + str(sizes[2]) + ' mm)')
                except:
                    print('Invalid input')
        cell_sizes = [x_cell_size, y_cell_size, z_cell_size]
        del x_cell_size, y_cell_size, z_cell_size
        
        # Unit cell origin definition:
        print('\nEnter unit cell origin:')
        input_validator = False
        while not input_validator:
            x_origin = input('Enter X origin in mm (default = 0 mm): ')
            if not x_origin:
                x_origin = 0
                print(x_origin)
                input_validator = True
            else:
                try:
                    x_origin = float(x_origin)
                    input_validator = True
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            y_origin = input('Enter Y origin in mm (default = 0 mm): ')
            if not y_origin:
                y_origin = 0
                print(y_origin)
                input_validator = True
            else:
                try:
                    y_origin = float(y_origin)
                    input_validator = True
                except:
                    print('Invalid input')
        input_validator = False
        while not input_validator:
            z_origin = input('Enter Z origin in mm (default = 0 mm): ')
            if not z_origin:
                z_origin = 0
                print(z_origin)
                input_validator = True
            else:
                try:
                    z_origin = float(z_origin)
                    input_validator = True
                except:
                    print('Invalid input')
        origin = [x_origin, y_origin, z_origin]
        del x_origin, y_origin, z_origin

        # Unit cell origin definition:
        input_validator = False
        while not input_validator:
            unit_cell_mesh_resolution = input('\nEnter unit cell mesh resolution (minimum = 20, default = 50): ')
            if not unit_cell_mesh_resolution:
                unit_cell_mesh_resolution = 50
                print(str(unit_cell_mesh_resolution) + '\n')
                input_validator = True
            else:
                try:
                    unit_cell_mesh_resolution = int(unit_cell_mesh_resolution)
                    if unit_cell_mesh_resolution >= 20:
                        input_validator = True
                except:
                    print('Invalid input')

        # Plot TPMS equation:
        mesh = None
        mesh, vertices = fn_plot_tpms_eq(tpms_type, sizes, cell_sizes, origin, unit_cell_mesh_resolution, c, mesh)

        # Check face normals:
        mesh = fn_check_face_normals(mesh)

        # Flip face normals:
        input_validator = False
        while not input_validator:
            flip_face_normals = input('Is it necessary to flip face normals? (y/N)')
            if not flip_face_normals:
                flip_face_normals = False
                input_validator = True
            else:
                if flip_face_normals != 'n' and flip_face_normals != 'N' and flip_face_normals != 'y' and flip_face_normals != 'Y':
                    print('Invalid input')
                elif flip_face_normals == 'n' or flip_face_normals == 'N':
                    flip_face_normals = False
                    input_validator = True
                elif flip_face_normals == 'y' or flip_face_normals == 'Y':
                    flip_face_normals = True
                    mesh = fn_flip_face_normals(mesh)
                    input_validator = True

        # Generate mesh
        print('\nMesh generation in progress ...')
        mesh = fn_generate_mesh(tpms_type, tpms_design, c, thickness, sizes, cell_sizes, origin, unit_cell_mesh_resolution, mesh, flip_face_normals)


        # Export mesh
        input_validator = False
        while not input_validator:
            export_stl = input('\nDo you want to export the generated mesh as .STL? (Y/n)')
            if not export_stl:
                export_stl = True
                input_validator = True
            else:
                if export_stl != 'n' and export_stl != 'N' and export_stl != 'y' and export_stl != 'Y':
                    print('Invalid input')
                elif export_stl == 'n' or export_stl == 'N':
                    export_stl = False
                    input_validator = True
                elif export_stl == 'y' or export_stl == 'Y':
                    export_stl = True
                    input_validator = True
        if export_stl:
            file_name = input('Enter file name (without extension): ')
            directory_path = input('Enter directory path (default = root folder): ')
            if not directory_path:
                directory_path = os.getcwd()
            fn_export_stl_file(mesh, file_name, directory_path)
        
        # Create another design:
        input_validator = False
        while not input_validator:
            active_session = input('\nDo you want to create another design? (Y/n)')
            if not active_session:
                active_session = True
                input_validator = True
            else:
                if active_session != 'n' and active_session != 'N' and active_session != 'y' and active_session != 'Y':
                    print('Invalid input')
                elif active_session == 'n' or active_session == 'N':
                    active_session = False
                    input_validator = True
                    exit(0)
                elif active_session == 'y' or active_session == 'Y':
                    active_session = True
                    input_validator = True