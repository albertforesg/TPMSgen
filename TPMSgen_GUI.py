from src import core

import os
import sys
import trimesh

import numpy as np
import pyvista as pv

from PyQt5 import uic
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDesktopWidget, QFileDialog, QSizeGrip
from skimage import measure

# GUI menu functions:
class gui_menu(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('TPMSgen_GUI.ui', self)

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
                self.shell_thickness_input.setText('3')
                self.thickness = 3

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

            # Get C value or thickness:
            if self.tpms_type == 'Shell':
                self.c = 0
                self.thickness = float(self.shell_thickness_input.text())
            else:
                self.c = float(self.skeletal_c_input.text())
                self.thickness = None

            # Update output message:
            self.message_output_label.setText('Next step:')
            self.message_output_label.setStyleSheet('color : black')
            self.message_output.setText('Inspect the generated TPMS\ndesign and check the orientation\nof its face normals.')
            
            # Plot TPMS equation:
            self.mesh, self.vertices = core.fn_plot_tpms_eq(self.tpms_type, self.tpms_design, self.sizes, self.cell_sizes, self.origin, self.unit_cell_mesh_resolution, self.c, self.thickness, self.mesh)

            # Activate check normals button:
            self.change_visibility(self.check_normals_button, True)

    def fn_check_face_normals(self):
        # Update output message:
        self.message_output_label.setText('Next step:')
        self.message_output_label.setStyleSheet('color : black')
        self.message_output.setText('Check if face normals are\npointing OUT of the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')

        # Check face normals:
        self.mesh = core.fn_check_face_normals(self.mesh, True)

        # Activate check normals button:
        self.change_visibility(self.flip_normals_button, True)

        # Activate flip normals button:
        self.change_visibility(self.generate_mesh_button, True)

    def fn_flip_face_normals(self):
        # Flip face normals
        self.mesh = core.fn_flip_face_normals(self.mesh, True)
        if self.flip_face_normals:
            self.flip_face_normals = False
        else:
            self.flip_face_normals = True

        # Update output message:
        self.message_output_label.setText('Next step:')
        self.message_output_label.setStyleSheet('color : black')
        self.message_output.setText('Check if face normals are\npointing OUT to the mesh. If not,\nplease flip them. Then proceeed\nto generate mesh.')

        # Deactivate check normals button:
        self.change_visibility(self.view_mesh_button, False)

        # Deactivate check normals button:
        self.change_visibility(self.export_stl_file_button, False)

    def fn_generate_mesh(self):
        # Generate mesh:
        self.iterative_mesh = core.fn_generate_mesh(self.tpms_type, self.tpms_design, self.c, self.thickness, self.sizes, self.cell_sizes, self.origin, self.unit_cell_mesh_resolution, self.mesh, self.flip_face_normals, True)

        # Update output message:
        if self.iterative_mesh.is_watertight:
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
        self.flip_face_normals = False
        self.iterative_mesh = None
        self.mesh = None
        self.origin = None
        self.sizes = None
        self.t = None
        self.thickness = None
        self.tpms_library_items = None
        self.tpms_type = None
        self.tpms_design = None
        self.unit_cell_mesh_resolution = None
        self.vertices = None

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

        self.shell_thickness_input.setText('3')

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
        self.message_output.setText('Set your design parameters and\nplot the equation of the choosen \nTPMS typology.')

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
    # ui
    ui = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
<class>tpms_generator_gui</class>
<widget class="QMainWindow" name="tpms_generator_gui">
<property name="geometry">
<rect>
    <x>0</x>
    <y>0</y>
    <width>839</width>
    <height>530</height>
</rect>
</property>
<property name="sizePolicy">
<sizepolicy hsizetype="Minimum" vsizetype="Preferred">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
</sizepolicy>
</property>
<property name="windowTitle">
<string>TPMSgen</string>
</property>
<widget class="QWidget" name="centralwidget">
<property name="sizePolicy">
    <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
    </sizepolicy>
</property>
<widget class="QWidget" name="verticalLayoutWidget_2">
    <property name="geometry">
    <rect>
    <x>10</x>
    <y>10</y>
    <width>821</width>
    <height>481</height>
    </rect>
    </property>
    <layout class="QVBoxLayout" name="verticalLayout_2">
    <item>
    <layout class="QGridLayout" name="gridLayout_2">
    <item row="0" column="0">
        <layout class="QGridLayout" name="gridLayout">
        <item row="0" column="6">
        <layout class="QVBoxLayout" name="verticalLayout_3">
        <item>
            <widget class="QLabel" name="label_3">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Preferred">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="font">
            <font>
            <bold>true</bold>
            </font>
            </property>
            <property name="text">
            <string>ACTIONS</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignTop</set>
            </property>
            </widget>
        </item>
        <item>
            <widget class="Line" name="line_4">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="orientation">
            <enum>Qt::Horizontal</enum>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="plot_tpms_eq_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>Plot TPMS equation</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="check_normals_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="MinimumExpanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>Check face normals</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="flip_normals_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="MinimumExpanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>Flip face normals</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="generate_mesh_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>Generate mesh</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="view_mesh_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>View mesh</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QPushButton" name="export_stl_file_button">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string>Export STL file</string>
            </property>
            </widget>
        </item>
        <item>
            <spacer name="verticalSpacer">
            <property name="orientation">
            <enum>Qt::Vertical</enum>
            </property>
            <property name="sizeHint" stdset="0">
            <size>
            <width>200</width>
            <height>40</height>
            </size>
            </property>
            </spacer>
        </item>
        <item>
            <widget class="QLabel" name="message_output_label">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Preferred">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="font">
            <font>
            <bold>true</bold>
            </font>
            </property>
            <property name="text">
            <string/>
            </property>
            </widget>
        </item>
        <item>
            <widget class="Line" name="line_2">
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="orientation">
            <enum>Qt::Horizontal</enum>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QLabel" name="message_output">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Maximum">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>200</width>
            <height>0</height>
            </size>
            </property>
            <property name="text">
            <string/>
            </property>
            </widget>
        </item>
        </layout>
        </item>
        <item row="0" column="1">
        <widget class="Line" name="line_3">
        <property name="orientation">
            <enum>Qt::Vertical</enum>
        </property>
        </widget>
        </item>
        <item row="0" column="0">
        <layout class="QVBoxLayout" name="verticalLayout">
        <item>
            <widget class="QLabel" name="label_1">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="font">
            <font>
            <bold>true</bold>
            </font>
            </property>
            <property name="text">
            <string>TPMS TYPOLOGY SELECTOR</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignTop</set>
            </property>
            </widget>
        </item>
        <item>
            <widget class="Line" name="line_7">
            <property name="orientation">
            <enum>Qt::Horizontal</enum>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QLabel" name="label_4">
            <property name="text">
            <string>Designs library:</string>
            </property>
            </widget>
        </item>
        <item>
            <widget class="QListWidget" name="designs_library">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Minimum" vsizetype="Expanding">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="minimumSize">
            <size>
            <width>270</width>
            <height>0</height>
            </size>
            </property>
            <property name="maximumSize">
            <size>
            <width>16777215</width>
            <height>280</height>
            </size>
            </property>
            </widget>
        </item>
        <item>
            <layout class="QGridLayout" name="gridLayout_4">
            <item row="1" column="2">
            <widget class="QLabel" name="units_1">
            <property name="text">
                <string>mm</string>
            </property>
            </widget>
            </item>
            <item row="0" column="1">
            <widget class="QLineEdit" name="skeletal_c_input">
            <property name="sizePolicy">
                <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                <horstretch>0</horstretch>
                <verstretch>0</verstretch>
                </sizepolicy>
            </property>
            <property name="text">
                <string/>
            </property>
            <property name="alignment">
                <set>Qt::AlignCenter</set>
            </property>
            </widget>
            </item>
            <item row="1" column="0">
            <widget class="QLabel" name="label_11">
            <property name="text">
                <string>Thickness: </string>
            </property>
            <property name="alignment">
                <set>Qt::AlignCenter</set>
            </property>
            </widget>
            </item>
            <item row="0" column="0">
            <widget class="QLabel" name="label_10">
            <property name="text">
                <string>C: </string>
            </property>
            <property name="alignment">
                <set>Qt::AlignCenter</set>
            </property>
            </widget>
            </item>
            <item row="1" column="1">
            <widget class="QLineEdit" name="shell_thickness_input">
            <property name="sizePolicy">
                <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                <horstretch>0</horstretch>
                <verstretch>0</verstretch>
                </sizepolicy>
            </property>
            <property name="alignment">
                <set>Qt::AlignCenter</set>
            </property>
            </widget>
            </item>
            <item row="2" column="1">
            <spacer name="verticalSpacer_2">
            <property name="orientation">
                <enum>Qt::Vertical</enum>
            </property>
            <property name="sizeType">
                <enum>QSizePolicy::Fixed</enum>
            </property>
            <property name="sizeHint" stdset="0">
                <size>
                <width>20</width>
                <height>30</height>
                </size>
            </property>
            </spacer>
            </item>
            </layout>
        </item>
        </layout>
        </item>
        <item row="0" column="5">
        <widget class="Line" name="line">
        <property name="orientation">
            <enum>Qt::Vertical</enum>
        </property>
        </widget>
        </item>
        <item row="0" column="2">
        <layout class="QGridLayout" name="gridLayout_3">
        <item row="4" column="1">
            <widget class="QLineEdit" name="bounding_box_x_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="5" column="2">
            <widget class="QLabel" name="units_3">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="9" column="0">
            <widget class="QLabel" name="axis_5">
            <property name="text">
            <string>Y:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="4" column="2">
            <widget class="QLabel" name="units_2">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="13" column="0">
            <widget class="QLabel" name="axis_8">
            <property name="text">
            <string>Y:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="7" column="0" colspan="3">
            <widget class="QLabel" name="label_7">
            <property name="text">
            <string>Unit cell dimensions:</string>
            </property>
            </widget>
        </item>
        <item row="8" column="0">
            <widget class="QLabel" name="axis_4">
            <property name="text">
            <string>X:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="10" column="1">
            <widget class="QLineEdit" name="unit_cell_z_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="9" column="2">
            <widget class="QLabel" name="units_6">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="4" column="0">
            <widget class="QLabel" name="axis_1">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="text">
            <string>X:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="11" column="0" colspan="3">
            <widget class="QLabel" name="label_8">
            <property name="text">
            <string>Unit cell origin:</string>
            </property>
            </widget>
        </item>
        <item row="14" column="2">
            <widget class="QLabel" name="units_10">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="2" column="0" colspan="3">
            <widget class="QLabel" name="label_6">
            <property name="text">
            <string>Bounding box dimensions:</string>
            </property>
            </widget>
        </item>
        <item row="12" column="0">
            <widget class="QLabel" name="axis_7">
            <property name="text">
            <string>X:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="10" column="2">
            <widget class="QLabel" name="units_7">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="14" column="0">
            <widget class="QLabel" name="axis_9">
            <property name="text">
            <string>Z:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="5" column="1">
            <widget class="QLineEdit" name="bounding_box_y_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="12" column="1">
            <widget class="QLineEdit" name="unit_cell_origin_x_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="8" column="2">
            <widget class="QLabel" name="units_5">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="8" column="1">
            <widget class="QLineEdit" name="unit_cell_x_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="6" column="2">
            <widget class="QLabel" name="units_4">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="0" column="0" colspan="3">
            <widget class="QLabel" name="label_2">
            <property name="font">
            <font>
            <bold>true</bold>
            </font>
            </property>
            <property name="text">
            <string>DESIGN CONFIGURATOR</string>
            </property>
            </widget>
        </item>
        <item row="12" column="2">
            <widget class="QLabel" name="units_8">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="14" column="1">
            <widget class="QLineEdit" name="unit_cell_origin_z_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="6" column="0">
            <widget class="QLabel" name="axis_3">
            <property name="text">
            <string>Z:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="13" column="2">
            <widget class="QLabel" name="units_9">
            <property name="text">
            <string>mm</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter</set>
            </property>
            </widget>
        </item>
        <item row="10" column="0">
            <widget class="QLabel" name="axis_6">
            <property name="text">
            <string>Z:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="1" column="0" colspan="3">
            <widget class="Line" name="line_5">
            <property name="orientation">
            <enum>Qt::Horizontal</enum>
            </property>
            </widget>
        </item>
        <item row="9" column="1">
            <widget class="QLineEdit" name="unit_cell_y_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="6" column="1">
            <widget class="QLineEdit" name="bounding_box_z_dim_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="15" column="0" colspan="3">
            <layout class="QHBoxLayout" name="horizontalLayout">
            <item>
            <widget class="QLabel" name="label_9">
            <property name="text">
                <string>Unit cell mesh resolution:</string>
            </property>
            </widget>
            </item>
            <item>
            <widget class="QLineEdit" name="mesh_resolution_input">
            <property name="sizePolicy">
                <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                <horstretch>0</horstretch>
                <verstretch>0</verstretch>
                </sizepolicy>
            </property>
            <property name="alignment">
                <set>Qt::AlignCenter</set>
            </property>
            </widget>
            </item>
            </layout>
        </item>
        <item row="5" column="0">
            <widget class="QLabel" name="axis_2">
            <property name="text">
            <string>Y:</string>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        <item row="13" column="1">
            <widget class="QLineEdit" name="unit_cell_origin_y_input">
            <property name="sizePolicy">
            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
            <horstretch>0</horstretch>
            <verstretch>0</verstretch>
            </sizepolicy>
            </property>
            <property name="alignment">
            <set>Qt::AlignCenter</set>
            </property>
            </widget>
        </item>
        </layout>
        </item>
        </layout>
    </item>
    </layout>
    </item>
    <item>
    <widget class="Line" name="line_6">
    <property name="orientation">
        <enum>Qt::Horizontal</enum>
    </property>
    </widget>
    </item>
    <item>
    <widget class="QLabel" name="label_12">
    <property name="font">
        <font>
        <pointsize>10</pointsize>
        <italic>false</italic>
        </font>
    </property>
    <property name="text">
        <string>Developed by Albert Forés Garriga, Héctor Garcia de la Torre, Ricard Lado Roigé, Giovanni Gómez Gras and Marco A. Pérez Martínez</string>
    </property>
    </widget>
    </item>
    <item>
    <widget class="QLabel" name="label_13">
    <property name="font">
        <font>
        <pointsize>10</pointsize>
        <italic>false</italic>
        </font>
    </property>
    <property name="text">
        <string>IQS School of Engineering, Universitat Ramon Llull (Barcelona, Spain)</string>
    </property>
    </widget>
    </item>
    </layout>
</widget>
</widget>
<widget class="QStatusBar" name="statusbar"/>
</widget>
<resources/>
<connections/>
</ui>
    '''

    with open('TPMSgen_GUI.ui', 'w') as file:
        file.write(ui)

    app = QApplication(sys.argv)
    GUI = gui_menu()
    GUI.move(800, int((QDesktopWidget().screenGeometry().height() - GUI.height()) / 2))
    GUI.show()
    sys.exit(app.exec_())