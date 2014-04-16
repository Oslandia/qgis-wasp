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
        self.ogr2ogr = os.path.abspath(QFileDialog.getOpenFileName(None, "Executable ogr2ogr a utiliser", self.ogr2ogr, "Executable (*.exe)"));
        QSettings().setValue('PythonPlugins/wasp/ogr2ogr', self.ogr2ogr)

    def impor(self):
        if not self.ogr2ogr : self.configure()
        mapFile = os.path.abspath(QFileDialog.getOpenFileName(None, "Select File", "", "WAsP File (*.map)"));
        if not mapFile: return
        shpDir = os.path.abspath(tempfile.gettempdir()+'\\'+os.path.basename(mapFile).replace('.map','.shp'))
        cmd = [self.ogr2ogr,'-skipfailures','-overwrite','-f',"ESRI Shapefile",shpDir,mapFile]
        if os.path.exists(shpDir):
            cmd.insert(1,'-overwrite')

        if self.__execCmd(cmd): 
            self.iface.addVectorLayer(shpDir, mapFile, "ogr")

    def expor(self):
        if not self.ogr2ogr : self.configure()
        if not self.iface.activeLayer(): QMessageBox.warning(self.iface.mainWindow(), "Attention", u'Aucune couche selectionnées')
       
        d = QDialog()
        d.setWindowTitle('Option du pilote WAsP')
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
        self.__execCmd(cmd)

    def __execCmd(self, cmd ):
        success = True
        errFile = tempfile.gettempdir()+'\wasp.log'
        # because of a bug in subprocess, we must set all streams, even if we are only interested in stderr
        err = open(tempfile.gettempdir()+'\wasp.out','w')
        inp = open(tempfile.gettempdir()+'\wasp.inp','w')
        inp.write('')
        inp.close()
        inp = open(inp.name,'r')
        print ' '.join(cmd)
        subprocess.call( cmd, stdout=err, stdin=inp, stderr=err, env={'PATH': str(os.path.dirname(cmd[0]))} )            
        err.close()
        err = open(err.name)
        for l in err:
            l.strip()
            print l
            success = False
        if not success: QMessageBox.critical(self.iface.mainWindow(), "Erreur", ' '.join(cmd)+'\nerreur:\n voir '+err.name+' pour plus de detail ou ouvrir la Console Python et recomencer')
        return success


