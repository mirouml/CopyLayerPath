# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CopyLayerPath
                                 A QGIS plugin
 Quickly copy selected vector or raster layer path into clipboad (Ctrl+Shift+C) and paste layer (Ctrl+Shift+V) into same or other instance of QGIS including current style
                             -------------------
        begin                : 2016-11-09
        copyright            : (C) 2016 by Miro Umlauf / AGE Consultants
        email                : miroslav.umlauf@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CopyLayerPath class from file CopyLayerPath.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .copy_layer_path import CopyLayerPath
    return CopyLayerPath(iface)
