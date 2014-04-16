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
            QIcon(os.path.dirname(__file__) + "/configure.svg"),
            u"configure", self.iface.mainWindow()) )
        self.actions[-1].setWhatsThis("configure ogr2ogr path")
        self.actions[-1].triggered.connect(self.configure)

        # add actions in menus
        for a in self.actions:
            self.iface.addToolBarIcon(a)

    def unload(self):
        # Remove the plugin menu item and icon
        for a in self.actions:
            self.iface.removeToolBarIcon(a)

    def configure(self):
        print 'configure'
        self.ogr2ogr = QFileDialog.getOpenFileName(None, "Executable ogr2ogr a utiliser", self.ogr2ogr, "Executable (*.exe)");
        QSettings().setValue('PythonPlugins/wasp/ogr2ogr', self.ogr2ogr)

    def impor(self):
        print 'import'
        mapFile = QFileDialog.getOpenFileName(None, "Select File", "", "WAsP File (*.map)");
        if not mapFile: return
        shpDir = tempfile.gettempdir()+'/'+os.path.basename(mapFile) #TODO strip dir name
        cmd = [self.ogr2ogr,'-skipfailures','-overwrite','-f','"ESRI Shapefile"',shpDir,mapFile]
        if not os.path.isdir(shpDir):
            try: os.makedirs(shpDir)
            except: QMessageBox.warning(self.iface.mainWindow(), "Warning", u"Impossible de créer le répertoire "+shpDir)
        else:
            cmd.insert(1,'-overwrite')

        if self.__execCmd(cmd): 
            self.iface.addVectorLayer(shpDir, mapFile, "ogr")

    def expor(self):
        print 'export'
        mapFile = QFileDialog.getSaveFileName(None, "Save layer as", "", "WAsP File (*.map)");
        shpFile =  self.iface.activeLayer().source()
        cmd = [self.ogr2ogr,'-skipfailures','-f','"WAsP"',mapFile,shpFile]
        self.__execCmd(cmd)

    def __execCmd(self, cmd ):
        success = True
        print ' '.join(cmd)
        errFile = tempfile.gettempdir()+'/wasp.log'
        out = open(errFile,'w')
        try: 
            subprocess.check_call( cmd, stderr=out, shell=True)
        except subprocess.CalledProcessError as e: 
            QMessageBox.critical(self.iface.mainWindow(), "Erreur", ' '.join(cmd)+'\nerreur:\n voir '+errFile+' pour plus de detail ou ouvrir la Console Python et recomencer')
            success = False
            out.close()
            out = open(errFile)
            for l in out: print l
        return success


