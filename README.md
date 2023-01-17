# TPMSgen

**Triply Periodic Minimal Surfaces**, also known as TPMS, are a class of mathematical surfaces that are periodic in all three spatial dimensions. They are known for their unique geometric properties, such as a lack of local extrema and a high degree of symmetry. These surfaces have a wide range of applications, including in architecture, engineering, and materials science. They have been studied extensively by mathematicians and have been found to have many interesting properties, such as the existence of an infinite number of distinct TPMS. They are also related to other mathematical structures such as soap films, minimal surfaces, and constant mean curvature surfaces.

[**TPMSgen**](https://github.com/albertforesg/TPMSgen) is a powerful program based on **Python** that allows users to easily design and generate Triply Periodic Minimal Surface (TPMS) geometries. It features a user-friendly interface with multiple **design parameters** (TPMS typology, specimen dimensions, unit cell size…) that makes it simple to generate their corresponding 3D model employing their mathematical equations. In addition, the program offers the possibility to export the 3D model in the **.STL** file format, which can be later used for fabrication with additive manufacturing technologies or in finite element simulation studies. This makes [**TPMSgen**](https://github.com/albertforesg/TPMSgen) a versatile tool for architects, engineers, and material scientists who are interested in exploring the unique properties of TPMS and their potential applications.

![TPMSgen](https://user-images.githubusercontent.com/81706331/212754604-6bf67f0f-b447-4496-8e0a-cb3c199b3c98.png)

---

## Built-in TPMS designs

The current library of [**TPMSgen**](https://github.com/albertforesg/TPMSgen) features a total of 10 distinct TPMS typologies, including 5 skeletal and 5 shell morphologies. These typologies provide users with a wide range of options for designing and exploring different TPMS geometries, and the ability to choose between skeletal and shell structures allows for even greater flexibility in their designs.

| Shell-TPMS Unit Cell Designs             |  Skeletal-TPMS Unit Cell Designs |
:-------------------------:|:-------------------------:
![Gyroid](https://user-images.githubusercontent.com/81706331/212520075-61342071-74e8-4a0c-abcf-6d7c4e0b2b0f.png) | ![Schoen Gyroid](https://user-images.githubusercontent.com/81706331/212520098-fa5b5f22-cd61-4911-96df-fa7c7154e5f3.png)
![Diamond](https://user-images.githubusercontent.com/81706331/212520079-ea284516-671c-4ec8-8540-510663d1fe84.png) | ![Schwarz Diamond](https://user-images.githubusercontent.com/81706331/212520101-3db607d9-cc28-4036-9d74-31e0583dd23d.png)
![Lidinoid](https://user-images.githubusercontent.com/81706331/212520087-77b587e0-c96f-4ed0-846e-e0ff68a5f94c.png) | ![Schwarz Primitive (pinched)](https://user-images.githubusercontent.com/81706331/212520106-87890470-5ee5-4857-b95c-2b7d2bcd28e5.png)
![Split-P](https://user-images.githubusercontent.com/81706331/212520090-54eccde5-42f4-4c08-9005-09529f2ea752.png) | ![Schwarz Primitive](https://user-images.githubusercontent.com/81706331/212520110-a109381d-d538-4e91-8528-9b3cc7bc4d04.png)
![Schwarz](https://user-images.githubusercontent.com/81706331/212520094-0863ce69-5f61-41ea-a1cc-f3939d13902a.png) | ![Body Diagonals with Nodes](https://user-images.githubusercontent.com/81706331/212520113-e11ff779-645f-43e4-ad5d-1994a2a10e17.png)

### Equations of Shell-TPMS designs:

#### a) Gyroid:

$\sin(x) \cdot \cos(y) + \sin(y) \cdot \cos(z) + \sin(z) \cdot \cos(x) = 0$

#### b) Diamond

$\sin(x) \cdot \sin(y) \cdot \sin(z) + \sin(x) \cdot \cos(y) \cdot \cos(z) + \cos(x) \cdot \sin(y) \cdot \cos(z) + \cos(x) \cdot \cos(y) \cdot \sin(z) = 0$

#### c) Lidinoid:

$\sin(2x) \cdot \cos(y) \cdot \sin(z) + \sin(x) \cdot \sin(2y) \cdot \cos(z) + \cos(x) \cdot \sin(y) \cdot \sin(2z) -$
$\quad - \cos(2x) \cdot \cos(2y) - \cos(2y) \cdot \cos(2z) - \cos(2z) \cdot \cos(2x) + 0.3 = 0$

#### d) Split-P:

$1.1 \cdot \left[ \sin(2x) \cdot \cos(y) \cdot \sin(z) + \sin(x) \cdot \sin(2y) \cdot \cos(z) + \cos(x) \cdot \sin(y) \cdot \sin(2z) \right] - $
$\quad - 0.2 \cdot \left[ \cos(2x) \cdot \cos(2y) + \cos(2y) \cdot \cos(2z) + \cos(2z) \cdot \cos(2x) \right] - 0.4 \cdot \left[ \cos(2x) + \cos(2y) + \cos(2z) \right] = 0$

#### e) Schwarz:

$\cos(x) + \cos(y) + \cos(z) = 0$


### Equations of Skeletal-TPMS desgins:

#### f) Schoen Gyroid:

$\sin(x) \cdot \cos(y) + \sin(y) \cdot \cos(z) + \sin(z) \cdot \cos(x) - C = 0$

#### g) Schwarz Diamond:

$\cos(x) \cdot \cos(y) \cdot \cos(z) + \sin(x) \cdot \sin(y) \cdot \sin(z) - C = 0$

#### h) Schwarz Primitive (pinched):

$\cos(x) + \cos(y) + \cos(z) - C = 0$

#### i) Schwarz Primitive:

$\cos(x) + \cos(y) + \cos(z) - C = 0$

#### j) Body Diagonals with Nodes:

$2 \cdot \left[ \cos(x) \cdot \cos(y) + \cos(y) \cdot \cos(z) + \cos(z) \cdot \cos(x) \right] - \left[ \cos(2x) + \cos(2y) + \cos(2z) \right] - C = 0$

---

## Quick Start

A standalone release has already been published and it is the simpliest way to execute the [**TPMSgen**](https://github.com/albertforesg/TPMSgen) application. 

- Operating Systems:
    - Windows
    - MacOS (GUI version only for x86 architectures)
    - Linux
- Hardware: 4GB of RAM or more

Some of the operations that [**TPMSgen**](https://github.com/albertforesg/TPMSgen) employs to create the mesh of the desired TPMS designs also require that [Blender](https://www.blender.org/download/) (version 3.4.1+) software is installed in your computer. You can follow the available [documentation](https://www.blender.org/support/) for troubleshooting during its installation.

## Run TPMSgen using local Python Interpreter

If the compiled files of the release are not available for your system of choice, you can run the GUI version or execute the CLI version of [**TPMSgen**](https://github.com/albertforesg/TPMSgen) from your Python interpreter.

- Python version: 3.9 or 3.10
- Required Libraries:
    - numpy
    - pyvista
    - scikit_image
    - skimage
    - trimesh
    - vtk
    - PyQt5 (only for GUI version
    
### Installing prerequisites for Python 3.9:

The `requirements_python_3_9.txt` file lists all the Python libraries that [**TPMSgen**](https://github.com/albertforesg/TPMSgen) depends on. If needed, they can be easily installed by running the following code:

```bash
pip install -r requirements_python_3_9.txt
```

### Installing prerequisites for Python 3.10:

The `requirements_python_3_10.txt` file lists all the Python libraries that [**TPMSgen**](https://github.com/albertforesg/TPMSgen) depends on. If needed, they can be easily installed by running the following code:

```bash
pip install -r requirements_python_3_10.txt
```

### Running TPMSgen application from terminal

Once prerequisites have been installed you can run the following code to open the GUI version of [**TPMSgen**](https://github.com/albertforesg/TPMSgen) from your Python interpreter 

```bash
python TPMSgen_GUI.py
```

Furthermore, if your system does not satisfy some of the requisites to run that version of the code, you can always execute the CLI version of the application:

```bash
python TPMSgen_CLI.py
```

---

## Interface preview / Help

Let's take a closer look at the user interface of [**TPMSgen**](https://github.com/albertforesg/TPMSgen) through a series of screenshots. The following pictures will provide a visual representation of the program and the process to generate the mesh of the desired TPMS design and export it into **.STL** format. In particular, you will be able to see its layout, the different buttons and design parameters provided in the main menu, as well as the rest of the program's features.

### Main menu

This is the main menu of [**TPMSgen**](https://github.com/albertforesg/TPMSgen). Here, the user can easily select one of the 10 popular TPMS typologies included in its library. Then, the rest of the design parameters (*C value* -only for Skeletal designs- and *thickness* -only for Shell designs-, *specimen dimensions*, *unit cell size*, *unit cell origin*…) can be set. Moreover, the appropiate mesh density can be selected by modifying the *unit cell mesh resolution* parameter.

![Main menu](https://user-images.githubusercontent.com/81706331/212754634-4941e974-dad7-46d9-b9f7-b23d93c61147.png)

### Vertices generation

When all the design parameters are properly set, the vertices of the sample can be generated by clicking on the **Plot TPMS equation** button. The following plot will be displayed, and the user can check the shape of the generated equation according to the choosen preferences.

![Vertices](https://user-images.githubusercontent.com/81706331/212511031-57cb2c76-9377-42b5-8ea9-aafbf7140e48.png)

### Face normals inspection

When the desired shape is obtained, the normals' direction of the faces of the mesh must be carefully inspected in order to obtain a proper watertight **.STL**. To do so, click on the **Check face normals** button, and a new figure will appear. Depending on the typology of the choosen TPMS (Shell o Skeletal), check that the plotted normals are orientated according to the instructions that are displayed in the bottom-right corner of the main menu. If not, flip them by just by clicking on the **Flip face normals** button.

![Face normals](https://user-images.githubusercontent.com/81706331/212511074-81564c47-6f31-48ff-862f-7ebbc986c726.png)

### Mesh preview

After checking the orientation of the face nomals, it is now time to generate the final watertight mesh by clicking on the **Generate mesh** button. Depending on the selected design parameters, this process may take a few minutes. When the calculation finishes, the message in the bottom-right corner will be updated indicating the quality of the achieved mesh. If the process doesn't succeed in obtaining the expected watertight mesh, try increasing the unit cell mesh resolution value or flipping the face normals.

In all cases, the result can be plotted and exported into **.STL** file format by clicking on the **View mesh** and **Export STL file** buttons, respectivelly.

![Mesh](https://user-images.githubusercontent.com/81706331/212511172-339de4fe-e169-4aa8-9791-4215f01efe70.png)

## How can I cite this application?

To correctly cite the application it is necessary to refer to the Github repository and the paper.

```bibtex
@software{TPMSgen,
	author = {{A. For{\'{e}}s-Garriga, H. Garc{\'{i}}a de la Torre, R. Lado-Roig{\'{e}}, G. G{\'{o}}mez- Gras, and M. A. P{\'{e}}rez.}},
	title = {TPMSgen},
	url = {https://github.com/albertforesg/TPMSgen},
	version = {},
	date = {2023-01-15},
}

@article{fores_2023,
  title={Mechanical performance of additively manufactured three-dimensional lightweight cellular solids: experimental and numerical analysis.},
  doi = {},
  author={A. For{\'{e}}s-Garriga, P{\'{e}}rez, Marco A., G. G{\'{o}}mez-Gras},
  journal={Materials & Design},
  year={2023},
  note = { (Under review) }
}
```
---

## Acknowledgements

This work has been supported by the **Ministry of Science, Innovation and Universities** through the project **New Developments in Lightweight Composite Sandwich Panels with 3D Printed Cores (3DPC) - RTI2018-099754-A-I00**.
