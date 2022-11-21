
# %%
# prepare the environment
import sys
from qgis.core import *
# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

sys.path.append(r'C:\OSGeo4W64\apps\qgis-ltr\python\plugins') # Folder where Processing is located
sys.path.append(r'C:\Users\bkropf\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins') # Folder where Private plugins are located

import processing
from processing.core.Processing import Processing
Processing.initialize()


# %%
# Run the algorithm
layer_files = r'G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\JHSW\layer_files'
inp_knooppunten = os.path.join(layer_files, "Gebiedsgegevens Kikker", "Kikker_gebiedsgegevens_testdataset_punt.shp")
inp_polygon = os.path.join(layer_files, "Gebiedsgegevens obv GWSW", "Gebiedsgegevens_GWSW_bemalingsgebieden.shp")
point_layer = QgsVectorLayer(inp_knooppunten, 'test', 'ogr')

feedback = QgsProcessingFeedback()

params = {
    "INPUT" : point_layer,
    "INTERSECT" : inp_polygon,
    "PREDICATE" : 0, # 0: intersect
    "METHOD" : 0, # 0: creating new selection
}

# See https://gis.stackexchange.com/a/276979/4972 for a list of algorithms
res = processing.run("qgis:selectbylocation", params, feedback=feedback)
res['OUTPUT'] # Access your output layer

# %%
#  
QgsVectorFileWriter.writeAsVectorFormat(point_layer, os.path.join(layer_files,"test_selection.shp"), "utf-8",
                                            point_layer.crs(), "ESRI Shapefile", True)

# %%
ins = QgsProject.instance() 
pr_file = r"G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\JHSW\JHSW_3.22.qgz"
ins.read(pr_file)

# %%
layers = ins.mapLayersByName("test") #

# %%
ins.addMapLayer(point_layer)
#%%
ins.write(pr_file)

# %%
# Exit applications
QgsApplication.exitQgis()
QApplication.exit()

# %%
