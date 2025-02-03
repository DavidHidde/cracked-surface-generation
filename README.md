# Cracked surface dataset generation framework

A dataset generation framework for generating images and labels of cracked masonry structures for crack segmentation of masonry structures.
Using a novel crack generation algorithm and Blender as a rendering engine, cracks are generated from a 2D surface and embedded in 3D in Blender.
The datasets generated using this method were originally tested using the [networks from Dais et al.](https://github.com/DavidHidde/CNN-masonry-crack-tasks).

![Example 1](img/1.png)
![Example 2](img/2.png)
![Example 3](img/3.png)

## Usage

The main crack generation can be tested through the playground script [`crack_generation_playground.py`](src/crack_generation_playground.py), which allow for testing the path generation and depth map generation by tweaking some parameters in a UI. All important parameters are tweakable, and some others are found as hardcoded constants in the code. The default parameters can be found in the [`default_parameters.py`](src/util/default_parameters.py), and any depth map texture can be used as an input for the playground.

For testing the dataset generation, you can simply run [`blender_start_render_script.py`](src/blender_start_render_script.py) from within Blender to run the script for 1 image and with the default [`configuration.yaml`](src/resources/configuration.yaml). To run the script in the background for a set dataset size and using a set configuration, you can run it from a terminal:

```bash
blender resources/scene.blend -b -P blender_start_render_script.py -- --cycles-device <device> -s <dataset_size> -c <configuration yaml file path> [-r <retries> -o <output>]
```

where the `<device>` is one of `[CPU, CUDA, OPTIX, HIP, ONEAPI, METAL]`, argument `-s` is used to set the desired dataset size and `-c` is the path to the configuration file that should be used. The optional `-r` and `-o` options serve to control the maximum number of render retries and output directory respectively.

**!! IMPORTANT !!**  
The workflow this framework uses modifies both material and compositing settings. For consistency, the material of a surface should be initialized using the standard node wrangler workflow (`Ctrl + Shift + T` while selecting the BSDF) and the existing compositor nodes are removed and overriden with a new flow.

## Requirements

* Blender >= 3.6.2, Blender versions past 4.2.3 have not been tested.
* Python >= 3.10, Python versions past 3.11 have not been tested

The Python dependencies for the source code can be installed using [src/dev_requirements.txt](src/dev_requirements.txt).  

To install all data generation dependencies, simply run:

```bash
pip install -r dev_requirements.txt
```

### Blender

To install the dependencies into your Blender install, please run:

```bash
blender -b -P blender_install_dependencies.py
```

to install the necessary dependencies into Blender. Note that some dependency version may differ between Blender and your own install due to the pre-installed modules in Blender's Python. To test if the framework is setup correctly, you can use the provided `scene.blend` and `configuration.yaml`:

```bash
blender resources/scene.blend -b -P blender_start_render_script.py -- --cycles-device <device> -s 1 -c resources/configuration.yaml -r 1 -o test
```

Note that this requires the HDRIs to be installed manually (see [`info on the scene.blend file`](#sceneblend-features))

In some cases, installing dependencies into Blender's Python install is not possible, in which case the script will run but will install the dependencies elsewhere. Blender provides options like [using the system install](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html#python-options) or the use of [environment variables](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html#environment-variables) to fix this.  

## Configuration

The framework uses a YAML file for setting most of the parameters. Please see [`configuration.yaml`](src/resources/configuration.yaml) for an example configuration including default values.

### Crack generation parameters (`crack_generation`)

| Name                              | Data type    | Description                                                                                                |
|-----------------------------------|--------------|------------------------------------------------------------------------------------------------------------|
| **`dimensions`**                  |              |                                                                                                            |
| `width`                           | float        | Initial width of the crack                                                                                 |
| `depth`                           | float        | Depth of the crack model                                                                                   |
| `sigma`                           | float        | Standard deviation of the Gaussian depth distribution                                                      |
| `width_stds_offset`               | float        | Offset of width points in standard deviations                                                              |
| **`path`**                        |              |                                                                                                            |
| `step_size`                       | float        | Gradient ascent step size                                                                                  |
| `gradient_influence`              | float        | Percent of how much of the gradient is used for path generation.                                           |
| `width_update_chance`             | float        | Percent chance for the width to be updated                                                                 |
| `breakthrough_chance`             | float        | Percent chance to ignore the gradient direction                                                            |
| `min_distance`                    | float        | Minimum distance between the current point and the next pivot point before generation stops                |
| `min_width`                       | float        | Minimum width of the crack before generation stops                                                         |
| `max_width_grow`                  | float        | Max increment the width is allowed to grow                                                                 |
| `smoothing_type`                  | str          | Type of smoothing, `gaussian` for 1D Gaussian smoothing and `moving_average` for moving average smoothing  |
| `smoothing`                       | int          | Size of the smoothing kernels in each direction                                                            |
| `distance_improvement_threshold`  | float        | Threshold for the distance gradient for points to be filtered out                                          |
| **`trajectory`**                  |              |                                                                                                            |
| `along_bottom_chance`             | float        | Percent chance of the pivot point appearing along the bottom                                               |
| `along_diagonal_chance`           | float        | Percent chance of the pivot point appearing along the opposite corner                                      |
| `along_side_chance`               | float        | Percent chance of the pivot point appearing along the opposite side                                        |
| `max_pivot_brick_widths`          | int          | Maximum number of brick to use for the width of the pivot grid                                             |
| `max_pivot_brick_heights`         | int          | Maximum number of brick to use for the height of the pivot grid                                            |
| `max_pivot_points`                | int          | Maximum number of pivot points to generate                                                                 |
| `row_search_space_percent`        | float        | Percent of the row space to use for the starting point                                                     |
| `column_search_space_percent`     | float        | Percent of the column space to use for the starting point                                                  |

### Scene generation parameters (`scene_generation_parameters`)

| Name                  | Data type    | Description                                                                            |
|-----------------------|--------------|----------------------------------------------------------------------------------------|
| **`assets`**          |              |                                                                                        |
| `hdris`               | list[str]    | Names of the HDRIs to use                                                              |
| `wall`                | str          | Name of the wall object in a scene                                                     |
| `other`               | list[str]    | Names of other objects relevant to the scene                                           |
| **`camera`**          |              |                                                                                        |
| `object`              | str          | Name of the camera object                                                              |
| `min`                 | float        | Minimum x/y/z camera rotation (in radians) or translation (in meters)                  |
| `max`                 | float        | Maximum x/y/z camera rotation (in radians) or translation (in meters)                  |
| **`label`**           |              |                                                                                        |
| `x`                   | int          | Resolution width                                                                       |
| `y`                   | int          | Resolution height                                                                      |
| `patches`             | int          | Number of patches to generate. 1 does not use the patch approach                       |
| `min_active_pixels`   | int          | Minimum number of pixels that need to be active in a label for it to not get rejected  |
| `crack`               | float        | Threshold to apply to the crack pixels. Recommended to leave unchanged.                |
| `ao`                  | float        | Threshold for the ambient occlusion map. Recommended to leave unchanged.               |

## Generated datasets

The datasets generated using the V1 test configurations can be found on [HuggingFace](https://huggingface.co/datasets/DavidHidde/synthetic-masonry-surfaces).

## `scene.blend` features

The Blender source file `scene.blend` contains a couple of features which are handy for testing and developing the method. It contains some simple wall geometry with a [bricks material](https://polyhaven.com/a/red_brick) applied and correctly set up UVs. The presupplied HDRIs can be found on Poly Haven:

* https://polyhaven.com/a/pond_bridge_night
* https://polyhaven.com/a/rotes_rathaus
* https://polyhaven.com/a/studio_garden
* https://polyhaven.com/a/urban_street_01
* https://polyhaven.com/a/stuttgart_suburbs

Finally, the "Node programming" view and some scripts are setup to facilitate easier development of the framework. The "Render test script" allows for the framework to be run once within Blender as well.

## Directory structure

The project is split up into directories as follows:

```txt
.
└── src
    ├── crack_generation: Crack generation algorithm.
    ├── dataset_generation: Blender dataset framework using crack generation.
    ├── resources: Assets of the project, including the Blender files and configuration needed to start the framework.
    └── util: General purpose classes/functions.
```
