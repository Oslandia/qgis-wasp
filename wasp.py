# -*- coding: utf-8 -*-
"""
/***************************************************************************
wasp
                                 A QGIS plugin
description=import/export of WAsP .map files
                              -------------------
        begin                : 2013-12-04
        copyright            : (C) 2013 by Oslandia
        email                : infos@oslandia.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import re
import os
import os.path
import tempfile
import subprocess

qset = QSettings( "oslandia", "wasp_qgis_plugin" )

class WAsP:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.ogr2ogr = QSettings().value('PythonPlugins/wasp/ogr2ogr')
        

    def initGui(self):
        self.actions.append( QAction(
            QIcon(os.path.dirname(__file__) + "/configure.svg"),
            u"configure", self.iface.mainWindow()) )
        self.actions[-1].setWhatsThis("configure ogr2ogr path")
        self.actions[-1].triggered.connect(self.configure)

        self.actions.append( QAction(
            QIcon(os.path.dirname(__file__) + "/import.svg"),
            u"import", self.iface.mainWindow()) )
        self.actions[-1].setWhatsThis("import map file")
        self.actions[-1].triggered.connect(self.impor)

        self.actions.append( QAction(
            QIcon(os.path.dirname(__file__) + "/export.svg"),
            u"export", self.iface.mainWindow()) )
        self.actions[-1].setWhatsThis("export map file")
        self.actions[-1].triggered.connect(self.expor)

        self.actions.append( QAction(
            QIcon(os.path.dirname(__file__) + "/simplify.svg"),
            u"simplify", self.iface.mainWindow()) )
        self.actions[-1].setWhatsThis("simplify height contours")
        self.actions[-1].triggered.connect(self.simplify)

        # add actions in menus
        for a in self.actions:
            self.iface.addToolBarIcon(a)

    def unload(self):
        # Remove the plugin menu item and icon
        for a in self.actions:
            self.iface.removeToolBarIcon(a)

    def configure(self):
        self.ogr2ogr = os.path.abspath(QFileDialog.getOpenFileName(None, "ogr2ogr executable", self.ogr2ogr, "Executable (*.exe);; All (*)"));
        QSettings().setValue('PythonPlugins/wasp/ogr2ogr', self.ogr2ogr)

    def impor(self):
        if not self.ogr2ogr : self.configure()
        mapFile = os.path.abspath(QFileDialog.getOpenFileName(None, "Select File", "", "WAsP File (*.map)"));
        if not mapFile: return
        shpDir = os.path.join(os.path.abspath(tempfile.gettempdir()), os.path.basename(mapFile).replace('.map','.shp'))
        cmd = [self.ogr2ogr,'-skipfailures','-overwrite','-f',"ESRI Shapefile",shpDir,mapFile]
        if os.path.exists(shpDir):
            cmd.insert(1,'-overwrite')

        if self.__execCmd(cmd): 
            self.iface.addVectorLayer(shpDir, mapFile, "ogr")

    def expor(self):
        if not self.ogr2ogr : self.configure()
        if not self.iface.activeLayer(): 
            QMessageBox.warning(self.iface.mainWindow(), "Warning", u'No layer selected')
            return
       
        d = QDialog()
        d.setWindowTitle('WAsP driver options')
        layout = QVBoxLayout(d)
        buttonBox = QDialogButtonBox(d)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        buttonBox.accepted.connect(d.accept)
        buttonBox.rejected.connect(d.reject)
        firstField = QComboBox( d )
        secondField = QComboBox( d )
        firstField.addItem( '[first field]' )
        secondField.addItem( '[second field]' )
        
        for f in self.iface.activeLayer().pendingFields(): 
            firstField.addItem( f.name() )
            secondField.addItem( f.name() )
        
        lineEdit = QLineEdit( d )
        lineEdit.setText('[tolerance]')
        
        layout.addWidget( firstField )
        layout.addWidget( secondField )
        layout.addWidget( lineEdit )
        layout.addWidget( buttonBox )
        if not d.exec_() : return
 
        mapFile = os.path.abspath(QFileDialog.getSaveFileName(None, "Save layer as", "", "WAsP File (*.map)"));
        shpFile = os.path.abspath(self.iface.activeLayer().source())
        cmd = [self.ogr2ogr,'-skipfailures','-f','WAsP']
        fields = ''
        if firstField.currentText() != '[first field]': fields += firstField.currentText()
        if secondField.currentText() != '[second field]': fields += ','+firstField.currentText()
        if fields: cmd += ['-lco','WASP_FIELDS='+fields]
        if lineEdit.text() != '[tolerance]': cmd += ['-lco','WASP_TOLERANCE='+lineEdit.text()]
        
        cmd += [mapFile,shpFile]
        if self.__execCmd(cmd):
            if not mapFile: return
            shpDir = os.path.join(os.path.abspath(tempfile.gettempdir()), os.path.basename(mapFile).replace('.map','.shp'))
            cmd = [self.ogr2ogr,'-skipfailures','-overwrite','-f',"ESRI Shapefile",shpDir,mapFile]
            if os.path.exists(shpDir):
                cmd.insert(1,'-overwrite')

            if self.__execCmd(cmd): 
                self.iface.addVectorLayer(shpDir, mapFile, "ogr")

    def simplify(self):
        if not self.ogr2ogr : self.configure()
        if not self.iface.activeLayer(): 
            QMessageBox.warning(self.iface.mainWindow(), "Warning", u'No layer selected')
            return

        d = QDialog()
        d.setWindowTitle('Height countours simplification')
        layout = QVBoxLayout(d)
        buttonBox = QDialogButtonBox(d)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        buttonBox.accepted.connect(d.accept)
        buttonBox.rejected.connect(d.reject)
        firstField = QComboBox( d )
        firstField.addItem( '[elevation field]' )
        
        for f in self.iface.activeLayer().pendingFields(): 
            firstField.addItem( f.name() )
        
        lineEdit = QLineEdit( d )
        lineEdit.setText('2')
        lineEdit2 = QLineEdit( d )
        lineEdit2.setText('10')
        
        layout.addWidget( QLabel("Elevation field" ) )
        layout.addWidget( firstField )
        layout.addWidget( QLabel("Simplification factor (>1)" ) )
        layout.addWidget( lineEdit )
        layout.addWidget( QLabel("Height resolution" ) )
        layout.addWidget( lineEdit2 )
        layout.addWidget( buttonBox )
        if not d.exec_() : return
 
        output_file = os.path.abspath(QFileDialog.getSaveFileName(None, "Save layer as", "", "ESRI Shapefile (*.shp)"));
        input_file = os.path.abspath(self.iface.activeLayer().source())

        
        field_name = firstField.currentText()
        heigh_resolution = lineEdit2.text()
        simplification_factor = float(lineEdit.text())

        basename = os.path.basename(input_file).replace('.shp','')
        out_high_res_dem = os.path.join( os.path.abspath(tempfile.gettempdir()), basename+'_high_res.tiff')
        out_low_res_dem = os.path.join( os.path.abspath(tempfile.gettempdir()), basename+'_low_res.tiff')

        out_res = str(int(4096/simplification_factor))
        if not self.__execCmd( ['gdal_rasterize', '-a_nodata', '0', '-ts', '4096', '4096', '-a', field_name, '-l', basename, input_file, out_high_res_dem] ): return
        if not self.__execCmd( ['gdal_fillnodata.py', out_high_res_dem, out_high_res_dem ] ): return
        if not self.__execCmd( ['gdalwarp', '-ts', out_res, out_res, '-overwrite', out_high_res_dem, out_low_res_dem ] ) : return

        if os.path.exists(output_file):
            os.remove(output_file)
            
        if not self.__execCmd( ['gdal_contour', '-a', field_name, '-i', heigh_resolution, '-f', 'ESRI Shapefile', out_low_res_dem, output_file ] ): return

        self.iface.addVectorLayer(output_file, basename+' simplified', "ogr")

    def __execCmd(self, cmd ):
        success = True
        errFile = os.path.join(os.path.abspath(tempfile.gettempdir()), 'wasp.log')
        # because of a bug in subprocess, we must set all streams, even if we are only interested in stderr
        out = open(os.path.join(os.path.abspath(tempfile.gettempdir()), 'wasp.out'),'w')
        err = open(os.path.join(os.path.abspath(tempfile.gettempdir()), 'wasp.err'),'w')
        inp = open(os.path.join(os.path.abspath(tempfile.gettempdir()), 'wasp.inp'),'w')
        inp.write('')
        inp.close()
        inp = open(inp.name,'r')
        print ' '.join(cmd)
        subprocess.call( cmd, stdout=out, stdin=inp, stderr=err )            
        err.close()
        err = open(err.name)
        for l in err:
            l.strip()
            print l
            success = False
        if not success: 
            QMessageBox.critical(self.iface.mainWindow(), "Error", ' '.join(cmd)+'\nerror:\n see '+err.name+' for details ou open Python Console and retry')

        return success


