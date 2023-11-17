# Cracked surface data set generation framework

A data set generation framework for generating images and labels of cracked masonry structures for crack segmentation of masonry structures.
Using a novel crack generation algorithm and Blender as a rendering engine, cracks are generated from a 2D surface and embedded in 3D in Blender.
The data sets generated using this method can then be tested using the [networks from Dais et al.](https://github.com/dimitrisdais/crack_detection_CNN_masonry/tree/main).

![Example 1](img/1.png)
![Example 2](img/2.png)
![Example 3](img/3.png)

## Usage


## Requirements

* Blender >= 3.6.2, Blender versions past 3.6.5 have not been tested.
* Python >= 3.10, Python versions past 3.11 have not been tested

The Python dependencies for the soruce code can be installed using [src/requirements.txt](src/requirements.txt) and the model submodule using [model_requirements.txt](model_requirements.txt).  

To install all data generation dependencies, simply run:

```bash
pip install -r src/requirements.txt
```

To install all model testing dependencies, simply run:

```bash
pip install -r model_requirements.txt
git submodule init --recursive
```

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
