QGIS-WAsP
=========

Import/Export WAsP .map files

This plugin also provides an easy way to simplify height countours when the original DEM is not available.

Installation
------------

Support for WAsP .map format has been added to GDAL/OGR >= 1.11.0. Your version should normally support this by default for recent QGIS versions.

To install the Plugin, the best method is to use the QGIS extension manager.

Alternatively, you can clone or unzip this project directly into your .qgis2/python/plugins directory.

For the height contours simplification to work, you will need to have gdal installed. It should be installed by default. 

Configuration
-------------

Open QGIS and make sure that the plugin is correctly loaded (Plugin Manager). Check that you see the plugins button in your plugin toolbar.

Click on the configure button and set the ogr2ogr program you want to use (the one you have recompiled).

License
=======

This work is free software and licenced under the GNU GPL version 2 or any later version. See LICENSE file.
