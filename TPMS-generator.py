import os
import sys
import trimesh

import numpy as np
import pyvista as pv

from PyQt5 import uic
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDesktopWidget, QFileDialog
from skimage import measure

# GUI menu functions:
class gui_menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('tpms_generator_gui.ui', self)

        # Initialize variables:
        self.initialize_variables()

        # Initialize visibilities:
        self.reset_visibility()
        
        # Load default values:
        self.load_default_values()

        # TPMS design selector changed:
        self.designs_library.currentRowChanged.connect(self.fn_tpms_selector_changed)

        # Design configurator changeed parameters:
        self.skeletal_c_input.textChanged.connect(self.reset_visibility)
        self.shell_thickness_input.textChanged.connect(self.reset_visibility)
        self.bounding_box_x_dim_input.textChanged.connect(self.reset_visibility)
        self.bounding_box_y_dim_input.textChanged.connect(self.reset_visibility)
        self.bounding_box_z_dim_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_x_dim_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_y_dim_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_z_dim_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_origin_x_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_origin_y_input.textChanged.connect(self.reset_visibility)
        self.unit_cell_origin_z_input.textChanged.connect(self.reset_visibility)
        self.mesh_resolution_input.textChanged.connect(self.reset_visibility)

        # Plot TPMS equation button pressed:
        self.plot_tpms_eq_button.clicked.connect(self.fn_plot_tpms_eq)

        # Check normals button pressed:
        self.check_normals_button.clicked.connect(self.fn_check_face_normals)

        # Flip normals button pressed:
        self.flip_normals_button.clicked.connect(self.fn_flip_face_normals)

        # Generate mesh button pressed:
        self.generate_mesh_button.clicked.connect(self.fn_generate_mesh)

        # View mesh button pressed:
        self.view_mesh_button.clicked.connect(self.fn_view_mesh)

        # Export STL file button pressed:
        self.export_stl_file_button.clicked.connect(self.fn_export_stl_file)

    def fn_tpms_selector_changed(self):
        # Checking TPMS type:
        tpms_type_changed = False
        row = self.designs_library.currentRow()
        if row < 5:
            if self.tpms_type != 'Shell':
                tpms_type_changed = True
            self.tpms_type = 'Shell'
        else:
            if self.tpms_type != 'Skeletal':
                tpms_type_changed = True
            self.tpms_type = 'Skeletal'
        self.tpms_design = self.tpms_library_items[row]
        
        # Updating data fields:
        if self.tpms_type == 'Shell':
            self.skeletal_c_input.setEnabled(False)
            self.skeletal_c_input.setText('0')
            self.c = 0
            self.shell_thickness_input.setEnabled(True)
            if tpms_type_changed:
                self.shell_thickness_input.setText('1')
                self.thickness = 1

        if self.tpms_type == 'Skeletal':
            self.skeletal_c_input.setEnabled(True)
            if tpms_type_changed:
                self.skeletal_c_input.setText('0.5')
                self.c = 0.5
            self.shell_thickness_input.setEnabled(False)
            self.shell_thickness_input.setText('--')
            self.thickness = 0

        del tpms_type_changed
        
        # Reset visibilities:
        self.reset_visibility()

    def fn_plot_tpms_eq(self):
        # Check input data warnings:
        self.check_input_data()

        # Plotting vertices:
        if not self.are_warnings:
            # Generation of the meshgrid:
            self.sizes = [float(self.bounding_box_x_dim_input.text()), float(self.bounding_box_y_dim_input.text()), float(self.bounding_box_z_dim_input.text())]
            self.cell_sizes = [float(self.unit_cell_x_dim_input.text()), float(self.unit_cell_y_dim_input.text()), float(self.unit_cell_z_dim_input.text())]
            self.origin = [float(self.unit_cell_origin_x_input.text()), float(self.unit_cell_origin_y_input.text()), float(self.unit_cell_origin_z_input.text())]
            self.unit_cell_mesh_resolution = int(self.mesh_resolution_input.text())
            self.tols = [0, 0, 0]
            self.X, self.Y, self.Z, self.tols, self.spacing  = self.generate_meshgrid(0)

            # Generate TPMS:
            if self.tpms_type == 'Shell':
                self.c = 0
                self.thickness = float(self.shell_thickness_input.text())
            else:
                self.c = float(self.skeletal_c_input.text())
                self.thickness = None
            self.F = self.tpms_library(self.X, self.Y, self.Z)

            # Mesh TPMS:
            if self.tpms_type == 'Shell':
                self.mesh, self.vertices = self.mesh_shell(self.F, self.mesh, self.tols, self.spacing)
            else:
                self.mesh, self.vertices = self.mesh_skeletal(self.F, self.mesh, self.tols, self.spacing)

            # Colour TPMS vertices:
            color = []
            for vert in self.vertices:
                color.append(vert[0] * vert[1] * vert[2])
            color = np.array(color)

            # Update output message:
            self.message_output_label.setText('Next step:')
            self.message_output_label.setStyleSheet('color : black')
            self.message_output.setText('Inspect the generated TPMS\ndesign and check the orientation\nof its face normals.')

            # Plot TPMS vertices:
            self.plotter = pv.Plotter(window_size = [1400, 1600])
            _ = self.plotter.add_title('Close this window to continue', font_size = 10)
            _ = self.plotter.add_mesh(self.vertices, scalars = color, cmap = 'jet')
            _ = self.plotter.remove_scalar_bar()
            _ = self.plotter.show_grid()
            self.plotter.show()
            
            # Activate check normals button:
            self.change_visibility(self.check_normals_button, True)

    def fn_check_face_normals(self):
        # Calculate face centroids and normals:
        mesh_pv = pv.wrap(self.mesh)
        cent = mesh_pv.cell_centers().points
        direction = mesh_pv.cell_normals

        # Update output message:
        self.message_output_label.setText('Next step:')
        self.message_output_label.setStyleSheet('color : black')
        if self.tpms_type == 'Shell':
            self.message_output.setText('Check if face normals are\npointing OUT of the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')
        else:
            self.message_output.setText('Check if face normals are\npointing IN to the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')

        # Plot TPMS face normals:
        self.plotter = pv.Plotter(window_size = [1400, 1600])
        _ = self.plotter.add_title('Close this window to continue', font_size = 10)
        _ = self.plotter.add_mesh(self.mesh, color = True, show_edges = True)
        _ = self.plotter.add_arrows(cent, direction, mag = 1)
        _ = self.plotter.remove_scalar_bar()
        _ = self.plotter.show_grid()
        self.plotter.show()

        # Activate check normals button:
        self.change_visibility(self.flip_normals_button, True)

        # Activate flip normals button:
        self.change_visibility(self.generate_mesh_button, True)

    def fn_flip_face_normals(self):
        # Flip mesh:
        self.mesh = pv.wrap(self.mesh)
        self.mesh.flip_normals()
        self.mesh = self.mesh_conversion(self.mesh)
        if self.flip_face_normals:
            self.flip_face_normals = False
        else:
            self.flip_face_normals = True

        # Calculate face centroids and normals:
        mesh_pv = pv.wrap(self.mesh)
        cent = mesh_pv.cell_centers().points
        direction = mesh_pv.cell_normals

        # Update output message:
        self.message_output_label.setText('Next step:')
        self.message_output_label.setStyleSheet('color : black')
        if self.tpms_type == 'Shell':
            self.message_output.setText('Check if face normals are\npointing OUT of the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')
        else:
            self.message_output.setText('Check if face normals are\npointing IN to the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')

        # Plot TPMS face normals:
        self.plotter = pv.Plotter(window_size = [1400, 1600])
        _ = self.plotter.add_title('Close this window to continue', font_size = 10)
        _ = self.plotter.add_mesh(self.mesh, color = True, show_edges = True)
        _ = self.plotter.add_arrows(cent, direction, mag = 1)
        _ = self.plotter.remove_scalar_bar()
        _ = self.plotter.show_grid()
        self.plotter.show()

        # Deactivate check normals button:
        self.change_visibility(self.view_mesh_button, False)

        # Deactivate check normals button:
        self.change_visibility(self.export_stl_file_button, False)

    def fn_generate_mesh(self):
        self.is_watertight = False
        k = int(5 / 100 * self.unit_cell_mesh_resolution)
        k_max = int(45 / 100 * self.unit_cell_mesh_resolution)
        k_increment = int(5 / 100 * self.unit_cell_mesh_resolution)

        # Mesh generation iterative process:
        if self.tpms_type == 'Shell':
            # Generate bounding box:
            self.shell_bounding_box = trimesh.creation.box(extents = (self.sizes[0], self.sizes[1], self.sizes[2]), transform = None)
            while not self.is_watertight and k <= k_max:
                # Generation of the meshgrid:
                X, Y, Z, tols, spacing  = self.generate_meshgrid(k)
                
                # Generate TPMS for intersection:
                F = self.tpms_library(X, Y, Z)

                # Mesh TPMS for intersection:
                self.iterative_mesh, _ = self.mesh_shell(F, self.iterative_mesh, tols, spacing)

                # Check face normals orientation:
                if self.flip_face_normals:
                    self.iterative_mesh = pv.wrap(self.iterative_mesh)
                    self.iterative_mesh.flip_normals()
                    self.iterative_mesh = self.mesh_conversion(self.iterative_mesh)
                
                # Calculate intercection:
                self.iterative_mesh = trimesh.boolean.intersection((self.iterative_mesh, self.shell_bounding_box), engine = 'blender')
                
                # Check obtained results
                k += k_increment
                self.is_watertight = self.iterative_mesh.is_watertight
                if not self.iterative_mesh.is_watertight:
                    self.iterative_mesh.fill_holes()
                    self.is_watertight = self.iterative_mesh.is_watertight
        else:
            # Generate bounding box:
            bounding_box_1 = trimesh.creation.box(extents = (2 * self.sizes[0], 2 * self.sizes[1], 2 * self.sizes[2]), transform = None)
            bounding_box_2 = trimesh.creation.box(extents = (self.sizes[0], self.sizes[1], self.sizes[2]), transform = None)
            self.bounding_box = trimesh.boolean.difference((bounding_box_1, bounding_box_2), engine = 'blender')
            
            del bounding_box_1, bounding_box_2
            
            while not self.is_watertight and k <= k_max:
                # Generation of the meshgrid:
                X, Y, Z, tols, spacing  = self.generate_meshgrid(k)
                
                # Generate TPMS for intersection:
                F = self.tpms_library(X, Y, Z)

                # Mesh TPMS for intersection:
                self.iterative_mesh, _ = self.mesh_skeletal(F, self.iterative_mesh, tols, spacing)

                # Check face normals orientation:
                if self.flip_face_normals:
                    self.iterative_mesh = pv.wrap(self.iterative_mesh)
                    self.iterative_mesh.flip_normals()
                    self.iterative_mesh = self.mesh_conversion(self.iterative_mesh)
                
                # Calculate intercection:
                self.iterative_mesh = trimesh.boolean.difference((self.iterative_mesh, self.bounding_box), engine = 'blender')
                
                # Check obtained results
                k += k_increment
                self.is_watertight = self.iterative_mesh.is_watertight
                if not self.iterative_mesh.is_watertight:
                    self.iterative_mesh.fill_holes()
                    self.is_watertight = self.iterative_mesh.is_watertight

        # Update output message:
        if self.is_watertight:
            self.message_output_label.setText('Mesh is generated:')
            self.message_output_label.setStyleSheet('color : green')
            self.message_output.setText('The obtained mesh is watertight.\nIf the opposite solution was\ndesired, try flipping face normals.')
        else:
            self.message_output_label.setText('Mesh is generated:')
            self.message_output_label.setStyleSheet('color : orange')
            self.message_output.setText('Cannot obtain a watertight mesh.\nTry increasing unit cell mesh\nresolution. Please, check results\ncarefully and treat them to solve\nthis issue.')

        # Activate check normals button:
        self.change_visibility(self.view_mesh_button, True)

        # Activate check normals button:
        self.change_visibility(self.export_stl_file_button, True)

    def fn_view_mesh(self):
        # Plot generated mesh:
        self.plotter = pv.Plotter(window_size = [1400, 1600])
        _ = self.plotter.add_title('Generated mesh can be exported into STL format', font_size = 10)
        _ = self.plotter.add_mesh(self.iterative_mesh, color = True, show_edges = True)
        _ = self.plotter.show_grid()
        self.plotter.show()

    def fn_export_stl_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Export STL', None, 'STL Files (.stl);;All Files ()')

        if file_path != '':
            suffix = QFileInfo(file_path).suffix()
            if len(suffix) > 0 and suffix != '.stl':
                self.show_warning_messagebox('Incorrect file format for exporting the generated mesh.')
            else:
                file_path += '.stl'
                export = trimesh.exchange.stl.export_stl_ascii(self.iterative_mesh)
                with open(file_path, 'w') as file:
                    file.write(export)

    def change_visibility(self, variable, state):
        variable.setEnabled(state)

    def check_input_data(self):
        # Warnings inspector:
        self.are_warnings = False

        # Checking thickness value:
        if not self.are_warnings:
            if self.tpms_type == 'Shell':
                try:
                    float(self.shell_thickness_input.text())
                    if not (float(self.shell_thickness_input.text()) > 0):
                        self.show_warning_messagebox('Please, check thickness value.')
                        self.are_warnings = True
                except:
                    self.show_warning_messagebox('Please, check thickness value.')
                    self.are_warnings = True

        # Checking C value:
        if not self.are_warnings:
            if self.tpms_type == 'Skeletal':
                try:
                    float(self.skeletal_c_input.text())
                    if not (float(self.skeletal_c_input.text()) != 0):
                        self.show_warning_messagebox('Please, check C value.')
                        self.are_warnings = True
                except:
                    self.show_warning_messagebox('Please, check C value.')
                    self.are_warnings = True

        # Checking bounding box dimensions:
        if not self.are_warnings:
            try:
                float(self.bounding_box_x_dim_input.text())
                float(self.bounding_box_y_dim_input.text())
                float(self.bounding_box_z_dim_input.text())
                if not (float(self.bounding_box_x_dim_input.text()) > 0 and float(self.bounding_box_y_dim_input.text()) > 0 and float(self.bounding_box_z_dim_input.text()) > 0):
                    self.show_warning_messagebox('Please, check bounnding box dimensions.')
                    self.are_warnings = True
            except:
                self.show_warning_messagebox('Please, check bounnding box dimensions.')
                self.are_warnings = True
            
        # Checking unit cell dimensions:
        if not self.are_warnings:
            try:
                float(self.unit_cell_x_dim_input.text())
                float(self.unit_cell_y_dim_input.text())
                float(self.unit_cell_z_dim_input.text())
                
                if not ((float(self.unit_cell_x_dim_input.text()) > 0 and float(self.unit_cell_x_dim_input.text()) <= float(self.bounding_box_x_dim_input.text())) and (float(self.unit_cell_y_dim_input.text()) > 0 and float(self.unit_cell_y_dim_input.text()) <= float(self.bounding_box_y_dim_input.text())) and (float(self.unit_cell_z_dim_input.text()) > 0 and float(self.unit_cell_z_dim_input.text()) <= float(self.bounding_box_z_dim_input.text()))):
                    self.show_warning_messagebox('Please, check unit cell dimensions.')
                    self.are_warnings = True
            except:
                self.show_warning_messagebox('Please, check unit cell dimensions.')
                self.are_warnings = True
            
        # Checking unit cell origin:
        if not self.are_warnings:
            try:
                float(self.unit_cell_origin_x_input.text())
                float(self.unit_cell_origin_y_input.text())
                float(self.unit_cell_origin_z_input.text())
            except:
                self.show_warning_messagebox('Please, check unit cell origin.')
                self.are_warnings = True

        # Checking unit cell mesh resolution:
        if not self.are_warnings:
            try:
                int(self.mesh_resolution_input.text())
                if not (int(self.mesh_resolution_input.text()) >= 20):
                    self.show_warning_messagebox('Please, check unit cell mesh resolution value (minimum 20, type int.).')
                    self.are_warnings = True
            except:
                self.show_warning_messagebox('Please, check unit cell mesh resolution value (minimum 20, type int.).')
                self.are_warnings = True

    def generate_meshgrid(self, k):
        tol_x = k * self.cell_sizes[0] / self.unit_cell_mesh_resolution
        tol_y = k * self.cell_sizes[1] / self.unit_cell_mesh_resolution
        tol_z = k * self.cell_sizes[2] / self.unit_cell_mesh_resolution
        tols = [tol_x, tol_y, tol_z]

        xl = np.linspace(-self.sizes[0]/2 - tols[0], self.sizes[0]/2 + tols[0], int(self.sizes[0] / self.cell_sizes[0]) * self.unit_cell_mesh_resolution + 2 * k + 1)
        yl = np.linspace(-self.sizes[1]/2 - tols[1], self.sizes[1]/2 + tols[1], int(self.sizes[1] / self.cell_sizes[1]) * self.unit_cell_mesh_resolution + 2 * k + 1)
        zl = np.linspace(-self.sizes[2]/2 - tols[2], self.sizes[2]/2 + tols[2], int(self.sizes[2] / self.cell_sizes[2]) * self.unit_cell_mesh_resolution + 2 * k + 1)
        spacing = [xl, yl, zl]
        
        Y, X, Z = np.meshgrid(yl, xl, zl)

        return X, Y, Z, tols, spacing  

    def initialize_variables(self):
        self.are_warnings = None
        self.c = None
        self.cell_sizes = None
        self.faces = None
        self.flip_face_normals = False
        self.is_watertight = None
        self.iterative_mesh = None
        self.mesh = None
        self.origin = None
        self.shell_bounding_box = None
        self.sizes = None
        self.skeletal_bounding_box = None
        self.spacing = None
        self.t = None
        self.thickness = None
        self.tols = None
        self.tpms_library_items = None
        self.tpms_type = None
        self.tpms_design = None
        self.unit_cell_mesh_resolution = None
        self.vertices = None
        self.X = None
        self.Y = None
        self.Z = None

    def load_default_values(self):
        # Initialize Skeletal-TPMS designs library:
        self.tpms_library_items = [
            'Shell-TPMS Gyroid',
            'Shell-TPMS Diamond',
            'Shell-TPMS Lidinoid',
            'Shell-TPMS Split-P',
            'Shell-TPMS Schwarz',
            'Skeletal-TPMS Schoen gyroid',
            'Skeletal-TPMS Schwarz diamond',
            'Skeletal-TPMS Schwarz primitive (pinched)',
            'Skeletal-TPMS Schwarz primitive',
            'Skeletal-TPMS Body diagonals with nodes'
        ]
        self.designs_library.addItems(self.tpms_library_items)
        self.designs_library.setCurrentRow(0)
        self.tpms_type = 'Shell'
        self.tpms_design = self.tpms_library_items[0]

        self.bounding_box_x_dim_input.setText('40')
        self.bounding_box_y_dim_input.setText('40')
        self.bounding_box_z_dim_input.setText('40')

        self.unit_cell_x_dim_input.setText('40')
        self.unit_cell_y_dim_input.setText('40')
        self.unit_cell_z_dim_input.setText('40')

        self.unit_cell_origin_x_input.setText('0')
        self.unit_cell_origin_y_input.setText('0')
        self.unit_cell_origin_z_input.setText('0')

        self.mesh_resolution_input.setText('50')

        self.skeletal_c_input.setText('0')
        self.skeletal_c_input.setEnabled(False)

        self.shell_thickness_input.setText('1')

        # Update output message:
        self.message_output_label.setText('Start:')
        self.message_output_label.setStyleSheet('color : black')
        self.message_output.setText('Set your design parameters and\nplot the equation of the choosen \nTPMS typology.')

    def mesh_conversion(self, mesh_pv):
        faces_as_array = mesh_pv.faces.reshape((mesh_pv.n_faces, 4))[:, 1:]
        mesh = trimesh.Trimesh(mesh_pv.points, faces_as_array)

        return mesh

    def mesh_shell(self, F, mesh, tols, spacing):
        vertices_positive, faces_positive, vertex_normals_positive, _ = measure.marching_cubes(F, self.thickness * self.t, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])
        vertices_negative, faces_negative, vertex_normals_negative, _ = measure.marching_cubes(F, -self.thickness * self.t, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])

        for i, vert in enumerate(vertices_positive):
            vertices_positive[i, 0] = vert[0] - self.sizes[0]/2 - tols[0]
            vertices_positive[i, 1] = vert[1] - self.sizes[1]/2 - tols[1]
            vertices_positive[i, 2] = vert[2] - self.sizes[2]/2 - tols[2]

        for i, vert in enumerate(vertices_negative):
            vertices_negative[i, 0] = vert[0] - self.sizes[0]/2 - tols[0]
            vertices_negative[i, 1] = vert[1] - self.sizes[1]/2 - tols[1]
            vertices_negative[i, 2] = vert[2] - self.sizes[2]/2 - tols[2]

        vertices = np.concatenate((vertices_positive, vertices_negative))
        
        mesh_1 = trimesh.Trimesh(vertices = vertices_positive, faces = faces_positive, vertex_normals = vertex_normals_positive)
        mesh_2 = trimesh.Trimesh(vertices = vertices_negative, faces = faces_negative, vertex_normals = vertex_normals_negative)
        mesh_2 = pv.wrap(mesh_2)
        mesh_2.flip_normals()
        mesh_2 = self.mesh_conversion(mesh_2)

        mesh = trimesh.util.concatenate((mesh_1, mesh_2))
        
        del vertices_positive, faces_positive, vertex_normals_positive, vertices_negative, faces_negative, vertex_normals_negative, mesh_1, mesh_2

        return mesh, vertices

    def mesh_skeletal(self, F, mesh, tols, spacing):
        vertices, faces, _, _ = measure.marching_cubes(F, 0, spacing = [np.diff(spacing[0])[0], np.diff(spacing[1])[0], np.diff(spacing[2])[0]])
        for i, vert in enumerate(vertices):
            vertices[i, 0] = vert[0] - self.sizes[0]/2 - tols[0]
            vertices[i, 1] = vert[1] - self.sizes[1]/2 - tols[1]
            vertices[i, 2] = vert[2] - self.sizes[2]/2 - tols[2]
        
        mesh = trimesh.Trimesh(vertices = vertices, faces = faces)

        del faces

        return mesh, vertices

    def reset_visibility(self):
        self.check_normals_button.setEnabled(False)
        self.flip_normals_button.setEnabled(False)
        self.generate_mesh_button.setEnabled(False)
        self.view_mesh_button.setEnabled(False)
        self.export_stl_file_button.setEnabled(False)

        # Update output message:
        self.message_output_label.setText('Start:')
        self.message_output_label.setStyleSheet('color : black')
        self.message_output.setText('Set your design parameters and plot the equation of the choosen \nTPMS typology.')

    def show_warning_messagebox(self, text):
        # Initialize message Box
        msg = QMessageBox()
        
        # Setting icon for message box
        msg.setIcon(QMessageBox.Warning)

        # Setting message for message Box
        msg.setText('Warning\t\t\t')
        
        # Setting message box window title
        msg.setWindowTitle('Warning')

        # Setting message box informative text
        msg.setInformativeText(text)
        
        # Declaring buttons on message Box
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Show message box
        retval = msg.exec_()

    def tpms_library(self, X, Y, Z):
        w_x = 1 / self.cell_sizes[0] * 2 * np.pi
        w_y = 1 / self.cell_sizes[1] * 2 * np.pi
        w_z = 1 / self.cell_sizes[2] * 2 * np.pi
        
        if self.tpms_design == 'Skeletal-TPMS Schoen gyroid' or self.tpms_design == 'Shell-TPMS Gyroid':
            F = (np.cos(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) + np.cos(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) + np.cos(w_z * (Z + self.origin[2])) * np.sin(w_x * (X + self.origin[0])) - self.c)   # J
            self.t = 0.125
        
        elif self.tpms_design == 'Skeletal-TPMS Schwarz diamond':
            F = (np.cos(w_x * (X + self.origin[0])) * np.cos(w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.sin(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) - self.c)   # K
        
        elif self.tpms_design == 'Skeletal-TPMS Schwarz primitive (pinched)' or self.tpms_design == 'Skeletal-TPMS Schwarz primitive':
            F = (np.cos(w_x * (X + self.origin[0])) + np.cos(w_y * (Y + self.origin[1])) + np.cos(w_z * (Z + self.origin[2])) - self.c)   # M, N
        
        elif self.tpms_design == 'Skeletal-TPMS Body diagonals with nodes':
            F = (2 * (np.cos(w_x * ((X + self.origin[0]))) * np.cos(w_y * (Y + self.origin[1])) + np.cos(w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.cos(w_z * (Z + self.origin[2])) * np.cos(w_x * (X + self.origin[0]))) - (np.cos(2 * w_x * (X + self.origin[0])) + np.cos(2 * w_y * (Y + self.origin[1])) + np.cos(2 * w_z * (Z + self.origin[2]))) - self.c) # O
        
        elif self.tpms_design == 'Shell-TPMS Diamond':
            F = (np.sin(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) + np.sin(w_x * (X + self.origin[0])) * np.cos(w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.cos(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.cos(w_x * (X + self.origin[0])) * np.cos(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) - self.c) # Q
            self.t = 0.115
        
        elif self.tpms_design == 'Shell-TPMS Lidinoid':
            F = (np.sin(2 * w_x * (X + self.origin[0])) * np.cos(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) + np.sin(w_x * (X + self.origin[0])) * np.sin(2 * w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.cos(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) * np.sin(2 * w_z * (Z + self.origin[2])) - np.cos(2 * w_x * (X + self.origin[0])) * np.cos(2 * w_y * (Y + self.origin[1])) - np.cos(2 * w_y * (Y + self.origin[1])) * np.cos(2 * w_z * (Z + self.origin[2])) - np.cos(2 * w_z * (Z + self.origin[2])) * np.cos(2 * w_x * (X + self.origin[0])) + 0.3 - self.c)
            self.t = 0.37
        
        elif self.tpms_design == 'Shell-TPMS Split-P':
            F = (1.1 * (np.sin(2 * w_x * (X + self.origin[0])) * np.cos(w_y * (Y + self.origin[1])) * np.sin(w_z * (Z + self.origin[2])) + np.sin(w_x * (X + self.origin[0])) * np.sin(2 * w_y * (Y + self.origin[1])) * np.cos(w_z * (Z + self.origin[2])) + np.cos(w_x * (X + self.origin[0])) * np.sin(w_y * (Y + self.origin[1])) * np.sin(2 * w_z * (Z + self.origin[2]))) - 0.2 * (np.cos(2 * w_x * (X + self.origin[0])) * np.cos(2 * w_y * (Y + self.origin[1])) + np.cos(2 * w_y * (Y + self.origin[1])) * np.cos(2 * w_z * (Z + self.origin[2])) + np.cos(2 * w_z * (Z + self.origin[2])) * np.cos(2 * w_x * (X + self.origin[0]))) - 0.4 * (np.cos(2 * w_x * (X + self.origin[0])) + np.cos(2 * w_y * (Y + self.origin[1])) + np.cos(2 * w_z * (Z + self.origin[2]))) - self.c)
            self.t = 0.19
        
        elif self.tpms_design == 'Shell-TPMS Schwarz':
            F = (np.cos(w_x * (X + self.origin[0])) + np.cos(w_y * (Y + self.origin[1])) + np.cos(w_z * (Z + self.origin[2])) - self.c)
            self.t = 0.0875
        
        else:
            print('Design not found in library')
            F = 0
            self.t = 0

        return F

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    GUI = gui_menu()
    GUI.move(800, int((QDesktopWidget().screenGeometry().height() - GUI.height()) / 2))
    GUI.show()
    sys.exit(app.exec_())