import os

from src import core

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
        mesh, vertices = core.fn_plot_tpms_eq(tpms_type, tpms_design, sizes, cell_sizes, origin, unit_cell_mesh_resolution, c, thickness, mesh)

        # Check face normals:
        mesh = core.fn_check_face_normals(mesh)

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
                    mesh = core.fn_flip_face_normals(mesh)
                    input_validator = True

        # Generate mesh
        print('\nMesh generation in progress ...')
        mesh = core.fn_generate_mesh(tpms_type, tpms_design, c, thickness, sizes, cell_sizes, origin, unit_cell_mesh_resolution, mesh, flip_face_normals)


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
            core.fn_export_stl_file(mesh, file_name, directory_path)
        
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