# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CopyLayerPath
                                 A QGIS plugin
 Quickly copy selected vector or raster layer path into clipboad (Ctrl+Shift+C) and paste layer (Ctrl+Shift+V) into same or other instance of QGIS including current style
                              -------------------
        begin                : 2016-11-09
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Miro Umlauf / AGE Consultants
        email                : miroslav.umlauf@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QApplication, QToolBar, QMenu
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources
import os
import tempfile


class CopyLayerPath:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CopyLayerPath_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Copy Layer Path')
        
        #check / add custom plugins toolbar (this plugin is meant to be part of plugins set)
        self.toolbar = self.iface.mainWindow().findChild( QToolBar, u'AGEPlugins' )
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'AGEPlugins')
            self.toolbar.setObjectName(u'AGEPlugins')

        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):

        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CopyLayerPath', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        shortcut_key=None,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
 
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        self.iface.registerMainWindowAction(action, shortcut_key)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        """Create the menu entries and toolbar icons inside the QGIS GUI.""" 
        # Add copy action        
        self.add_action(
            ":/plugins/CopyLayerPath/icon_copy.png",
            text=self.tr(u'Copy layer path'),
            callback=self.run,
            shortcut_key="Ctrl+Shift+C",
            parent=self.iface.mainWindow())
        # Add paste action       
        self.add_action(
            ":/plugins/CopyLayerPath/icon_load.png",
            text=self.tr(u'Load layer by path'),
            callback=self.loadLayer,
            shortcut_key="Ctrl+Shift+V",
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Copy Layer Path'),
                action)
            self.toolbar.removeAction(action)
    
    def loadLayer(self):
		"""Load layer from coppied path in clipboard if possible"""
        clipboard = QApplication.clipboard()
        layer = clipboard.text()
        layer_name = layer[layer.rfind('=')+1:]
        dataSourceUri = layer[:layer.rfind('?')]
        if "?raster" in layer:
            new_layer = self.iface.addRasterLayer(dataSourceUri,layer_name)
        elif "?vector" in layer:
            new_layer = self.iface.addVectorLayer(dataSourceUri,layer_name,"ogr")
        else:
            self.iface.messageBar().pushMessage("Info", "No path to layer in clipboard. Use Copy layer path first.", level=QgsMessageBar.INFO, duration=5)
        
        # Load and apply saved style
        my_path = tempfile.gettempdir()
        layer = self.iface.activeLayer()
        layer.loadNamedStyle(os.path.join(my_path,"CopyLayerPathStyle.qml"))
   

    def run(self):
        """Copy active layer path into clipboard, also save current style into temp directory to use when pasting layer"""
        
        layer_to_copy = False
        layer = self.iface.activeLayer().dataProvider().dataSourceUri()
        layer_iface_name = self.iface.activeLayer().name()
        layer_type = int(str(self.iface.activeLayer().type()))
		
		#Check if the layer is either vector or raster, otherwise inform it can't be copied
        if layer_type == 0:            
            layer = layer[:layer.rfind('|')]
            layer = layer + "?vector"
            layer_to_copy = True
        elif layer_type == 1:
            layer = layer + "?raster"
            layer_to_copy = True
        else:
            self.iface.messageBar().pushMessage("Info","Can't copy this type of layer.", level=QgsMessageBar.CRITICAL, duration=5)
        if layer_to_copy:
			#Change slashes in path to backslashes if on windows
			if os.name == "nt":
				layer = layer.replace("/","\\")
            
			# Initiate clipboard
			clipboard = QApplication.clipboard()
			# Copy current layer style into clipboard and get it
            self.iface.actionCopyLayerStyle().trigger()
            active_qml = clipboard.text()
            # Paste layer path into clipboard
			clipboard_text = layer + "=" + layer_iface_name
            clipboard.setText(clipboard_text)
            # Save copied style as QML into temp directory
			my_path = tempfile.gettempdir()
			file = open(os.path.join(my_path,"CopyLayerPathStyle.qml"), "w")
            file.write(active_qml)
            file.close()
            self.iface.messageBar().pushMessage("Info", "Layer path copied to clipboard: " + clipboard_text, level=QgsMessageBar.INFO, duration=5)