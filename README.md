# QGISTopoToolbox

## How to use

Once [installed](#installing) and enabled, the TopoToolbox plugin integrates with QGIS through the Processing Toolbox, giving you access to a set of terrain-analysis tools based on the topotoolbox Python library. All tools included in the plugin are located in:

`Processing Toolbox → TopoToolbox`

Inside the TopoToolbox group, you will find all available algorithms, including:

- Fillsinks
- Excesstopography
- Gradient8
- Curvature
- Evans slope
- prominence
- z Score
- extract_streams and stream_network do the same thing but with a different approach. Which is preferred still needs to be decided.

The layers are saved as .tif files. This means that the algorithms represent workflows made up of one or more topotoolbox functions based on the desired output.

## Installing

1. Compress the repository into a .zip file. Use `python3 zip_plugin.py` to automatically exclude parts of the repository that are not needed (for example ./venv/)
2. Navigate to 'Plugins' → 'Manage and Install Plugins...'
3. Click on 'Install from ZIP'
4. Select the .zip file and click 'Install Plugin'

This plugin requires the Python package topotoolbox, which is not installed in QGIS by default. This is why we use the plugin [qpip](https://plugins.qgis.org/plugins/a00_qpip/) (which is still in early development and may cause errors). If you try to install the TopoToolbox plugin without having qpip installed beforehand, QGIS will ask you to install qpip. After the installation, qpip will ask you to install the missing dependencies. Install them and everything should be in working order.

> [!WARNING]
> The dependencies will be installed with their specified versions. This means that dependencies shared across different plugins may break due to different requirements.

We have to do it this way because QGIS only ships with certain packages installed. However, this plugin needs the topotoolbox package and its dependencies. On Windows, the OSGeo4W shell can be used to install packages that can be used in QGIS. On Linux, QGIS uses the default Python installation. Therefore, for packages to be usable, they must be added to the default Python path. The qpip plugin solves this issue.

### Script for creating plugin zip

Since manually zipping the whole repository may include unwanted files (.venv) you can use the zip_plugin Python command line tool. Use it by calling `python3 zip_plugin.py`

To use a custom name for the created zip, use `python3 zip_plugin.py -o SomeDifferentName.zip`

## Developing

Since QPIP attempts to install all packages in the `requiirements.txt` when installing the QGIS TopoToolbox plugin, the packages used for ensuring code quality are in a separate file. Use `pip install -r requirements-dev.txt` to install everything needed to be able to run the tests (This will not install the QGIS packages that are used, they are only provided in QGIS).

Instead of pylint/mypy, like in the PyTopoToolbox package, we use the black formatter and ruff for this plugin. This is, because: writing a new `QgsProcessingAlgorithm` involves a lot of repeating functions which don't need a docstring, the imported qgis modules are not available for type checking, qgis naming conventions not matching pep8 guidelines, [...].

To check if your code complies with our standards use pre-commit. This will run all checks that will be running when you open a new pull-request and format your python files.

```bash
# Add hook:
pre-commit install
# Remove hook:
pre-commit uninstall
# To run manually:
pre-commit run
# To run on all files:
pre-commit run --all-files
```

You can also use black and ruff manually:

```bash
# Reformat files
black .
# Check what would be reformated
black --check --diff .
# Check ruff checks
ruff check .
```

### How to add more Algorithms to the Processing Toolbox

1. Create a new .py file in the [algorithms](./algorithms/) folder
2. Create the QgsProcessingAlgorithm like in already existing files
3. Import the created class in [topotoolboxplugin.py](./topotoolboxplugin.py) and add it to loadAlgorithms function
4. Zip the again and reinstall the plugin in QGIS