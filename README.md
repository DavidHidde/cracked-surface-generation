# Cracked surface data set generation framework

A data set generation framework for generating images and labels of cracked masonry structures for crack segmentation of masonry structures.
Using a novel crack generation algorithm and Blender as a rendering engine, cracks are generated from a 2D surface and embedded in 3D in Blender.
The data sets generated using this method can then be tested using the [networks from Dais et al.](https://github.com/dimitrisdais/crack_detection_CNN_masonry/tree/main).

![Example 1](img/1.png)
![Example 2](img/2.png)
![Example 3](img/3.png)

## Usage

The main crack generation can be tested through the playground scripts [`crack_path_generation_playground.py`](src/crack_path_generation_playground.py) [`crack_model_generation_playground.py`](src/crack_model_generation_playground.py), which allow for testing the path generation and model generation by tweaking some parameters in a UI. The paramters that aren't exposed (like trajectory generation and the surface) can be found in the [`default_parameters.py`](src/util/default_parameters.py) and the serialized `Surface` file `surface.dump`. Note that a new surface dump can be created by setting `DUMP_SURFACE` in [`generate_dataset.py`](src/generate_dataset.py).  

For testing the data set generation, you can simply run [`blender_start_render_script.py`](src/resources/blender_start_render_script.py) from within Blender to run the script for 1 image and with the default [`configuration.yaml`](src/resources/configuration.yaml). To run the script in the background for a set data set size and using a set configuration, you can run it from a terminal:

```bash
blender scene.blend --background --python blender_start_render_script.py -- -c <data_set_size> -p <configuration yaml file path>
```

where the argument `-c` is used to set the desired data set size and `-p` is the path to the configuration file that should be used.

## Requirements

* Blender >= 3.6.2, Blender versions past 3.6.5 have not been tested.
* Python >= 3.10, Python versions past 3.11 have not been tested

The Python dependencies for the source code can be installed using [src/requirements.txt](src/requirements.txt) and the model submodule using [model_requirements.txt](model_requirements.txt).  

To install all data generation dependencies, simply run:

```bash
pip install -r src/requirements.txt
```

To install all model testing dependencies, simply run:

```bash
pip install -r model_requirements.txt
git submodule init --recursive
```

### Blender

To install the dependencies into your Blender install, please run:

```bash
blender scene.blend --background --python blender_find_python_install
```

to find your Blender Python install. This command will also instruct how to install the requirements.

To use the default configuration parameters, the same HDRIs need to be added. The installation of the HDRIs needs to be done manually. For this, the following HDRIs need to be downloaded and inserted into `scene.blend` and set in the config:

* https://polyhaven.com/a/pond_bridge_night
* https://polyhaven.com/a/rotes_rathaus
* https://polyhaven.com/a/studio_garden
* https://polyhaven.com/a/urban_street_01
* https://polyhaven.com/a/stuttgart_suburbs

## Directory structure

The project is split up into directories as follows:

```txt
.
├── model: The segmentation network module.
└── src
    ├── crack_generation: Crack generation algorithm.
    ├── dataset_generation: Blender data set framework using crack generation.
    ├── resources: Assets of the project, including the Blender files and configuration needed to start the framework.
    └── util: Classes related to neither the crack generation neither the data set framework.
```

## Configuration

The framework uses a YAML file for setting most of the parameters. Please take a look at [`configuration.yaml`](src/resources/configuration.yaml) for some default values.

| Name                        |                             |                                |                   |              | Data type    | Description                                                                                 |
|-----------------------------|-----------------------------|--------------------------------|-------------------|--------------|--------------|---------------------------------------------------------------------------------------------|
| crack_generation_parameters |                             |                                |                   |              |              |                                                                                             |
|                             | crack_dimension_parameters  |                                |                   |              |              |                                                                                             |
|                             |                             | width                          |                   |              | float        | Initial width of the crack                                                                  |
|                             |                             | depth                          |                   |              | float        | Depth of the crack model                                                                    |
|                             |                             | depth_resolution               |                   |              | int          | Points to sample for the depth                                                              |
|                             |                             | sigma                          |                   |              | float        | Standard deviation of the Gaussian depth distribution                                       |
|                             |                             | width_stds_offset              |                   |              | float        | Offset of width points in standard deviations                                               |
|                             | crack_path_parameters       |                                |                   |              |              |                                                                                             |
|                             |                             | step_size                      |                   |              | float        | Gradient ascent step size                                                                   |
|                             |                             | gradient_influence             |                   |              | float        | Percent of how much of the gradient is used for path generation.                            |
|                             |                             | width_update_chance            |                   |              | float        | Percent chance for the width to be updated                                                  |
|                             |                             | breakthrough_chance            |                   |              | float        | Percent chance to ignore the gradient direction                                             |
|                             |                             | min_distance                   |                   |              | float        | Minimum distance between the current point and the next pivot point before generation stops |
|                             |                             | min_width                      |                   |              | float        | Minimum width of the crack before generation stops                                          |
|                             |                             | max_width_grow                 |                   |              | float        | Max increment the width is allowed to grow                                                  |
|                             |                             | max_width_grow_factor          |                   |              | float        | Percent of how much of the current width the width is allowed to grow                       |
|                             |                             | start_pointiness               |                   |              | int          | Number of width grow steps to perform at the beginning of the crack                         |
|                             |                             | end_pointiness                 |                   |              | int          | Number of width grow steps to perform at the end of the crack                               |
|                             |                             | smoothing                      |                   |              | int          | Size of the 1D Gaussian smoothing kernels                                                   |
|                             |                             | distance_improvement_threshold |                   |              | float        | Threshold for the distance gradient for points to be filtered out                           |
|                             | crack_trajectory_parameters |                                |                   |              |              |                                                                                             |
|                             |                             | along_bottom_chance            |                   |              | float        | Percent chance of the pivot point appearing along the bottom                                |
|                             |                             | along_diagonal_chance          |                   |              | float        | Percent chance of the pivot point appearing along the opposite corner                       |
|                             |                             | along_side_chance              |                   |              | float        | Percent chance of the pivot point appearing along the opposite side                         |
|                             |                             | max_pivot_brick_widths         |                   |              | int          | Maximum number of brick to use for the width of the pivot grid                              |
|                             |                             | max_pivot_brick_heights        |                   |              | int          | Maximum number of brick to use for the height of the pivot grid                             |
|                             |                             | max_pivot_points               |                   |              | int          | Maximum number of pivot points to generate                                                  |
|                             |                             | row_search_space_percent       |                   |              | float        | Percent of the row space to use for the starting point                                      |
|                             |                             | column_search_space_percent    |                   |              | float        | Percent of the column space to use for the starting point                                   |
| scene_generation_parameters |                             |                                |                   |              |              |                                                                                             |
|                             | assets                      |                                |                   |              |              |                                                                                             |
|                             |                             | safe_collections               |                   |              | list[str]    | Names of collections to not clear during scene clearing                                     |
|                             |                             | label_material                 |                   |              | str          | Name of the material to use for the crack label                                             |
|                             |                             | hdris                          |                   |              | list[str]    | Names of the HDRIs to use                                                                   |
|                             |                             | materials                      |                   |              | list[str]    | Names of the materials to use for the wall                                                  |
|                             |                             | scenes                         |                   |              | list[object] | Set of objects that describe a scene                                                        |
|                             |                             |                                | wall              |              | str          | Name of the wall object                                                                     |
|                             |                             |                                | mortar            |              | str          | Name of the mortar object of the wall                                                       |
|                             |                             |                                | other             |              | list[str]    | Names of other objects relevant to the scene                                                |
|                             |                             |                                | wall_properties   |              |              |                                                                                             |
|                             |                             |                                |                   | brick_width  | float        | Width of the bricks of the wall                                                             |
|                             |                             |                                |                   | brick_height | float        | Height of the bricks of the wall                                                            |
|                             |                             |                                |                   | mortar_size  | float        | Mortar size of the wall                                                                     |
|                             | camera_parameters           |                                |                   |              |              |                                                                                             |
|                             |                             | object                         |                   |              | str          | Name of the camera object                                                                   |
|                             |                             | rotation                       |                   |              |              |                                                                                             |
|                             |                             |                                | x                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum x camera rotation in radians                                                        |
|                             |                             |                                |                   | max          | float        | Maximum x camera rotation in radians                                                        |
|                             |                             |                                | y                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum y camera rotation in radians                                                        |
|                             |                             |                                |                   | max          | float        | Maximum y camera rotation in radians                                                        |
|                             |                             |                                | z                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum z camera rotation in radians                                                        |
|                             |                             |                                |                   | max          | float        | Maximum z camera rotation in radians                                                        |
|                             |                             | translation                    |                   |              |              |                                                                                             |
|                             |                             |                                | x                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum x camera translation                                                                |
|                             |                             |                                |                   | max          | float        | Maximum x camera translation                                                                |
|                             |                             |                                | y                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum y camera translation                                                                |
|                             |                             |                                |                   | max          | float        | Maximum y camera translation                                                                |
|                             |                             |                                | z                 |              |              |                                                                                             |
|                             |                             |                                |                   | min          | float        | Minimum z camera translation                                                                |
|                             |                             |                                |                   | max          | float        | Maximum z camera translation                                                                |
|                             | label_generation            |                                |                   |              |              |                                                                                             |
|                             |                             | patches                        |                   |              | int          | Number of patches to generate. 1 does not use the patch approach                            |
|                             |                             | thresholding                   |                   |              |              |                                                                                             |
|                             |                             |                                | min_active_pixels |              | int          | Minimum number of pixels that need to be active in a label for it to not get rejected       |
|                             |                             |                                | min_rgb_color     |              |              |                                                                                             |
|                             |                             |                                |                   | r            | int          | Minimum red value for thresholding                                                          |
|                             |                             |                                |                   | g            | int          | Minimum green value for thresholding                                                        |
|                             |                             |                                |                   | b            | int          | Minimum blue value for thresholding                                                         |
|                             |                             |                                | max_rgb_color     |              |              |                                                                                             |
|                             |                             |                                |                   | r            | int          | Maximum red value for thresholding                                                          |
|                             |                             |                                |                   | g            | int          | Maximum green value for thresholding                                                        |
|                             |                             |                                |                   | b            | int          | Maximum blue value for thresholding                                                         |
