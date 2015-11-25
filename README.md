QGIS-WAsP
=========

Import/Export WAsP .map files

This plugin also provides an easy way to simplify height countours when the original DEM is not available.

Installation
------------

To install the Plugin, the best method is to use the QGIS extension manager. Run the extension manager, look for WAsP and install the plugin.

Alternatively, you can clone or unzip this project directly into your .qgis2/python/plugins directory.

Configuration
-------------

Open QGIS and make sure that the plugin is correctly loaded (Plugin Manager). Check that you see the plugins buttons are in your plugin toolbar.

Click on the configure button and set the ogr2ogr program you want to use. On Linux it should be in @/usr/bin@. On Windows it is located in your OSGeo4W / QGIS installation. The configuration is kept between QGIS sessions.

Versions notes
--------------

Support for WAsP .map format has been added to GDAL/OGR >= 1.11.0. Your version should normally support this by default for recent QGIS versions.

For the height contours simplification to work, you will need to have gdal installed. It should be installed by default with recent versions of QGIS. 


License
=======

This work is free software and licenced under the GNU GPL version 2 or any later version. See LICENSE file.
