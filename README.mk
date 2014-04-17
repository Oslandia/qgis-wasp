QGIS-WAsP
=========

Import/Export WAsP .map files

This plugin also provides an easy way to simplify height countours when the original DEM is not available.

Installation
------------

Support for WAsP .map format has been recently added to gdal. Your version of gdal may not include it. 

You will need to recompile geos and gdal to use this plugin (follow instructions from here http://trac.osgeo.org/geos and there http://trac.osgeo.org/gdal/wiki/BuildHints).

For Windows:
    Once you have succesfully compiled geos and gdal, put org2ogr.exe, gdalXXX.dll and geos_c.dll in the same directory.

You can clone or unzip this project directly into your .qgis2/python/plugins directory.

For the height contours simplification to work, you will need to have gdal installed (not necessarilly the latest version)

Configuration
-------------

Open QGIS and make sure that the plugin is correctly loaded (Plugin Manager). Check that you see the plugins button in your plugin toolbar.

Click on the configure button and set the ogr2ogr program you want to use (the one you have recompiled).

License
=======

This work is free software and licenced under the GNU GPL version 2 or any later version. See LICENSE file.
