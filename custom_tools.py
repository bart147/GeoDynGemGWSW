# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import csv
import os 
import inspect
import string
import random
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterBoolean,
                       QgsProject,
                       QgsMapLayerType,
                       QgsLayerTreeGroup,
                       QgsVectorFileWriter,
                       QgsProcessingParameterNumber,
                       QgsWkbTypes)
from qgis.core import QgsVectorLayer, QgsField, QgsProcessingParameterFile, QgsProcessingParameterString, QgsProcessingParameterVectorLayer, QgsProcessingMultiStepFeedback
from qgis.core import QgsExpression, QgsFeatureRequest, QgsExpressionContextScope, QgsExpressionContext, QgsProcessingLayerPostProcessorInterface
from qgis.PyQt.QtCore import QVariant
from qgis import processing
from qgis.utils import iface
from .Dijkstra import Graph, dijkstra

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
default_inp_fields = os.path.join(cmd_folder, 'inp_fields.csv')

# class Renamer (QgsProcessingLayerPostProcessorInterface):
#     def __init__(self, layer_name):
#         self.name = layer_name
#         super().__init__()
        
#     def postProcessLayer(self, layer, context, feedback):
#         layer.setName(self.name)

# def return_result_group():
#     '''depricated...'''
#     selNodes = iface.layerTreeView().selectedNodes()
#     selNode = selNodes[0] if selNodes else None
#     if isinstance(selNode, QgsLayerTreeGroup):
#         group = selNode
#     else:
#         root = QgsProject.instance().layerTreeRoot()
#         group = root.addGroup('Results')
#     return group

# def rename_layers_old(results, context, feedback):
#     #QgsProject.instance().reloadAllLayers() 
#     for key in results:
#         if context.willLoadLayerOnCompletion(results[key]):
#             random_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
#             global_key = key + "_" + random_string 
#             feedback.pushInfo("rename layer to {}".format(key))
#             globals()[global_key] = Renamer(key) #create unique global renamer instances
#             context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[global_key])
#             # add style
#             style = os.path.join(cmd_folder, "styles", key + ".qml")
#             if os.path.exists(style):
#                 layer = context.getMapLayer(results[key])
#                 layer.loadNamedStyle(style)
#     #QgsProject.instance().reloadAllLayers() 
#     return results, context, feedback

# def rename_layers(results, context, feedback):
#     #QgsProject.instance().reloadAllLayers() 
#     for key in results:
#         result = results[key]
#         if context.willLoadLayerOnCompletion(result):
#             feedback.pushInfo("rename layer to {}".format(key))
#             if context.willLoadLayerOnCompletion(result):
#                 layer_details = context.layerToLoadOnCompletionDetails(result)
#                 layer_details.name = "My output"
#             style = os.path.join(cmd_folder, "styles", key + ".qml")
#             if os.path.exists(style):
#                 layer = context.getMapLayer(results[key])
#                 layer.loadNamedStyle(style)
#     #QgsProject.instance().reloadAllLayers() 
#     return results, context, feedback

def default_layer(wildcard, geometryType=None):
    """
    Return layername or None based on wildcard
    Also filters for geometryType if specified where 0=point, 1=line, 2=poly
    """
    layers = QgsProject.instance().mapLayers()
    for layerid in layers:
        layer = layers[layerid]
        if geometryType != None: # only filter if geometryType is specified
            if layer.type() != QgsMapLayerType.VectorLayer:
                continue # skip layer if not Vector
            elif layer.geometryType() != geometryType:
                continue # skip if geometryType is different
        layername = layer.name()
        if wildcard.lower() in layername.lower():
            return layername
    return None

class QgsProcessingAlgorithmPost(QgsProcessingAlgorithm):

    final_layers = None
    result_folder = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.final_layers = { }

    def sort_key(self, item):
        """sort layers on geometry"""
        layer = item[1]
        geom_type = layer.geometryType()
        if geom_type == QgsWkbTypes.PointGeometry:
            return 0
        elif geom_type == QgsWkbTypes.LineGeometry:
            return 1
        elif geom_type == QgsWkbTypes.PolygonGeometry:
            return 2
        else:
            return 3  # For any other geometry types
    
    def postProcessAlgorithm(self, context, feedback):
        #QgsProject.instance().reloadAllLayers() 
        project = context.project()
        root = project.instance().layerTreeRoot()
        #group = root.addGroup('Results')
        #root = return_result_group()
        group = root.insertGroup(0, "Result " + self.displayName())
        hoofdgroup = group.addGroup("hoofdresultaten")
        subgroup = group.addGroup("tussenresultaten")
        subgroup.setItemVisibilityChecked(False)
        result_folder = self.result_folder
        if not result_folder:
            result_folder = os.path.join (cmd_folder, 'results')
            feedback.pushWarning(f"no result_folder was given, layers are written to default {result_folder}")
        #result_folder = r'G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\JHSW\results'
        rename = {}

        sorted_layers = sorted(self.final_layers.items(), key=self.sort_key)

        for index, item in enumerate(sorted_layers):
            
            layer = item[1]
            layername = item[0]

            if result_folder:
                layer_path = os.path.join (result_folder, layername+".gpkg")
                QgsVectorFileWriter.writeAsVectorFormat(layer, layer_path, 'utf-8', layer.crs())
                layer = QgsVectorLayer(layer_path, layername, 'ogr')

            if any(txt in layername for txt in [
                'tbv', 'Eindresultaat', 'Gebiedsgegevens_lijn', 'Eindpunten', 'Resultaat']) or \
                layername in ['LeidingenNietMeegenomen', 'Afvoerboom']: # promote these to hoofdresultaten
                group_to_add = hoofdgroup
            else:
                group_to_add = subgroup

            # add style
            style = os.path.join(cmd_folder, "styles", layername + ".qml")
            if os.path.exists(style):
                layer.loadNamedStyle(style)
            
            project.addMapLayers([layer], False)        
            group_to_add.addLayer(layer)
        
        self.final_layers.clear()
        return {}


class CustomToolBasicAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     INPUT = 'INPUT'
    #     OUTPUT = 'OUTPUT'
    result_folder = None

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CustomToolBasicAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'basic name'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('basic display name')

    def customAlgorithm(self, layer, parameters, feedback, **kwargs):
        """
        Here we define our own custom algorithm.
        """
        return layer

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('geodyn tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'geodyn_tools'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        #QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        
        # Extract by expression for copy
        alg_params = {
            'EXPRESSION': '$id IS NOT NULL',
            'INPUT': parameters['inputlayer'],
            'OUTPUT': 'memory:'
        }
        layer = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback)['OUTPUT']
        layer_path = os.path.join (cmd_folder, 'results', layer.name()+".gpkg")
        QgsVectorFileWriter.writeAsVectorFormat(layer, layer_path, 'utf-8', layer.crs())
        layer = QgsVectorLayer(layer_path, layer.name(), 'ogr')
        
        layer = self.customAlgorithm(layer, parameters, feedback)
        
        # Extract by expression for copy
        alg_params = {
            'EXPRESSION': '$id IS NOT NULL',
            'INPUT': layer,
            'OUTPUT': parameters['Output_layer']
        }

        outputs['result'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        results['Output_layer'] = outputs['result']['OUTPUT']
        
        return results

    
class CustomToolAllFunctionsAlgorithm(CustomToolBasicAlgorithm):
    """
    CustomToolBasicAlgortim with all custom funtions added
    """
    def get_name(self,f):
        """name function for sorting features in bereken_onderbemaling_POC_with_iteration"""
        return f['name']  # Define a custom key function for sorting
    
    def sort_fields(self, fields_to_sort_by, layer, feedback):
        """sort by multiple fields and add a new field order"""

        feedback.pushInfo("sort fields {}".format(fields_to_sort_by))
        
        # field1Id = "VAN_NAAR"
        # isInv1 = False
        # field2Id = "BERGING_M3"
        # isInv2 = True
        # field3Id = "length"
        # isInv3 = False

        field1Id, field2Id, field3Id = fields_to_sort_by

        order_field = "order"

        layer = self.vervang_None_door_0_voor_velden_in_lijst([field2Id], layer, feedback)

        featureList = list( layer.getFeatures() )
        #featureList = sorted(featureList, key=lambda f: f[field1Id], reverse=isInv1)
        #featureList = sorted(featureList, key=lambda f: f[field2Id], reverse=isInv2)
        #featureList = sorted(featureList, key=lambda f: f[field3Id], reverse=isInv3)
        featureList = sorted(featureList, key=lambda f: (f[field1Id],-f[field2Id],f[field3Id]) )

        layer.startEditing()

        # add order field
        layer.dataProvider().addAttributes( [QgsField(order_field, QVariant.Int)] )
        attrIdx = layer.dataProvider().fields().indexFromName( order_field )
        layer.updateFields() # tell the vector layer to fetch changes from the provider
                    
        for i, f in enumerate(featureList):
            layer.changeAttributeValue(f.id(), attrIdx, i+1)

        layer.commitChanges()


        return layer, feedback

    def retain_fields(self, fields_to_retain, layer, feedback):
        feedback.pushInfo("fields to retain {}".format(fields_to_retain))
        prov = layer.dataProvider()
        field_names = [field.name() for field in prov.fields()]
        field_names_to_delete = [fld for fld in field_names if fld not in fields_to_retain]
        field_indexes_to_delete = [layer.fields().indexFromName(fld) for fld in field_names_to_delete]
        feedback.pushInfo("fields to delete {}".format(field_names_to_delete))
        layer.dataProvider().deleteAttributes(field_indexes_to_delete)
        layer.updateFields()

        return layer, feedback

    def drop_empty_fields(self, layer, feedback):
        feedback.pushInfo("drop empty fields...")
        prov = layer.dataProvider()
        field_names = [field.name() for field in prov.fields()]
        

        field_names_to_delete = []
        for field_name in field_names:
            empty = True
            for feature in layer.getFeatures():
                if feature[field_name]:
                    empty = False
            if empty:
                field_names_to_delete.append(field_name)

        field_indexes_to_delete = [layer.fields().indexFromName(fld) for fld in field_names_to_delete]
        feedback.pushWarning("empty fields to delete:")
        for fld in field_names_to_delete:
            feedback.pushInfo(str("-" + fld))
        layer.dataProvider().deleteAttributes(field_indexes_to_delete)
        layer.updateFields()

        return layer, feedback

    def get_d_velden_csv(self, INP_FIELDS_CSV):
        """dictionary field-info ophalen uit excel zonder pandas met xlrd"""
    
        d_velden = {}
        f = open(INP_FIELDS_CSV, encoding="ISO-8859-1")
        input_file = csv.DictReader(f, delimiter=";")

        for srow in input_file:
            if not srow["fieldname"]:
                continue

            fld = {}

            # verplichte keys
            fld["order"] = int(srow["order"])
            fld["field_type"] = srow["type"]
            fld["field_alias"] = srow["alias"]
            fld["add_fld"] = srow["stap_toevoegen"]
            # optionele keys
            if str(srow["mag_niet_0_zijn"]) != "nan": # np.nan, df.notna() werkt niet en np.isnan() not supported
                fld["mag_niet_0_zijn"] = str(srow["mag_niet_0_zijn"]).split(";")
            #else:
                # fix_print_with_import
                #print((type(srow["mag_niet_0_zijn"]),srow["mag_niet_0_zijn"]))
            if str(srow["lengte"]) not in ["nan", ""," "]:
                fld["field_length"] = int(float(srow["lengte"]))
            if str(srow["expression"]) not in ["nan", ""," "]:
                fld["expression"] = srow["expression"]
            if str(srow["stap_bereken"]) not in ["nan", ""," "]:
                fld["bereken"] = srow["stap_bereken"]
            d_velden[srow["fieldname"]] = fld
        f.close()
        
        return d_velden

    def add_fieldAlias_from_dict(self, layer, d_fld, feedback):

        for field in layer.fields():
            fieldname = field.name()
            if fieldname in d_fld.keys():
                fld = d_fld[fieldname] # dict with field parameters
                feedback.pushInfo("veld alias '{}' toevoegen aan {}".format(fld["field_alias"], fieldname))
                fieldindex = layer.fields().indexFromName(fieldname)
                layer.setFieldAlias(fieldindex, fld["field_alias"])
        return layer

    def add_field_from_dict(self, fc, fld_name, d_fld, feedback):
        """add field. dict must be like
            d_fld[fld_name] = {
                'field_alias'   : 'your alias',
                'field_length'  : '50', (optional)
                'field_type'    : 'TEXT',
                } """
        ##if not isinstance(fc, QgsVectorLayer): fc = QgsVectorLayer(fc, "layer", "ogr")
        
        feedback.pushInfo("veld {} toevoegen".format(fld_name))
        fld = d_fld[fld_name] # dict with field parameters
        feedback.pushInfo("veld alias {}".format(fld["field_alias"]))
        if fld in [field.name() for field in fc.fields()]:
            return
        if "field_length" in list(fld.keys()):
            field_length = fld["field_length"]
        else:
            field_length = 10
        ##print_log("veld lengte = {}".format(field_length), "i")

        

        fldtype_mapper = {
            "TEXT" : QVariant.String,
            "LONG" : QVariant.Int,
            "SHORT": QVariant.Int,
            "DOUBLE":QVariant.Double,
            "FLOAT": QVariant.Double,
            "DATE" : QVariant.DateTime,
        }
        new_fld = QgsField(prec=2, name=fld_name, type=fldtype_mapper.get(fld["field_type"],QVariant.String), len=field_length)
        #new_fld.setAlias(fld["field_alias"])
        #new_fld.alias = fld["field_alias"]
        fieldindex = fc.fields().indexFromName(fld_name)
        if fieldindex == -1:
            fc.dataProvider().addAttributes([new_fld])
            #fc.updateFields()
            #fc.fields()[fieldindex].alias = fld["field_alias"]
            #fc.fields()[fieldindex].setAlias(fld["field_alias"])
            fc.updateFields()
            feedback.pushInfo("setveld alias {}".format(fld["field_alias"]))
            fc.setFieldAlias(fieldindex, fld["field_alias"])
            ##fc.updateFields()
        ##return fc

    def add_field_from_dict_label(self, fc, add_fld_value, d_fld, feedback):
        """velden toevoegen op basis van dict.keys 'add_fld', 'order' en 'fc' in d_fld
           maakt gebuikt van functie add_field_from_dict() maar dan voor een verzameling velden
           op basis van 'add_fld'. 'order' is optioneel voor het behouden van volgorde"""
        # select dict with "order" and "add_fld" keys
        d_fld_order = {k:v for (k,v) in list(d_fld.items()) if "add_fld" in list(v.keys()) and "order" in list(v.keys())}
        # subselect with "order" == add_fld_value
        d_fld_order = {k:v for (k,v) in list(d_fld_order.items()) if v["add_fld"] == add_fld_value}
        if len(d_fld_order) > 0:
            #print_log("velden met 'add_fld' : '{}' toevoegen op volgorde van 'order':".format(add_fld_value),"d")
            for fld, value in sorted(iter(d_fld_order.items()), key=lambda k_v: (k_v[1]["order"])): # sort by key "order"
                self.add_field_from_dict(fc, fld, d_fld, feedback)
        # select dict without "order" and "add_fld" keys
        d_fld_no_order = {k:v for (k,v) in list(d_fld.items()) if "add_fld" in list(v.keys()) and not "order" in list(v.keys())}
        # subselect with "order" == add_fld_value
        d_fld_no_order = {k:v for (k,v) in list(d_fld_no_order.items()) if v["add_fld"] == add_fld_value}
        if len (d_fld_no_order) > 0:
            #print_log("geen 'order' gevonden in d_velden, velden met 'add_fld' : '{}' toevoegen in willekeurige volgorde:".format(add_fld_value),"d")
            for fld in d_fld_no_order:
                self.add_field_from_dict(fc, fld, d_fld, feedback)
        return fc
    
    def bereken_veld(self, fc, fld_name, d_fld, feedback):
        """bereken veld m.b.v. 'expression' in dict
        als dict de key 'mag_niet_0_zijn' bevat, wordt een selectie gemaakt voor het opgegeven veld"""
        try:
            expression = d_fld[fld_name]["expression"]
            expression = expression.replace("[", '"').replace("]", '"')
            feedback.pushInfo("calculate {} = {}".format(fld_name, expression))
            #print_log(d_fld[fld_name], "d")
            if "mag_niet_0_zijn" in d_fld[fld_name]:
                l_fld = d_fld[fld_name]["mag_niet_0_zijn"]
                where_clause = " and ".join(
                    ['"{}" <> 0'.format(fld) for fld in l_fld])  # [FLD1,FLD2] -> "FLD1 <> 0 and FLD2 <> 0"
                expr = QgsExpression(where_clause)
                #print_log(where_clause, "d")
                #it = fc.getFeatures(QgsFeatureRequest(expr))  # iterator object
                #fc.selectByIds([i.id() for i in it])
                fc.selectByExpression(where_clause)

            # calculate field
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            context.appendScope(scope)
            e = QgsExpression(expression)
            ##e.prepare(fc.fields())

            fc.startEditing()
            idx = fc.fields().indexFromName(fld_name)
            for f in fc.getFeatures():
                scope.setFeature(f)
                f[idx] = e.evaluate(context)
                fc.updateFeature(f)
            fc.commitChanges()
            fc.selectByIds([])

        except Exception as e:
            feedback.pushWarning("probleem bij bereken veld {}! {}".format(fld_name,e))

        return fc

    def bereken_veld_label(self, fc, bereken, d_fld, feedback):
        """bereken velden op basis van label 'bereken' en fc in d_fld"""
        feedback.pushInfo("\nvelden met bereken '{}' uitrekenen:".format(bereken))
        i = 0
        for fld in d_fld:
            if not "bereken" in list(d_fld[fld].keys()): 
                continue
            ##feedback.pushInfo("{}: {}".format(fld, d_fld[fld]))
            if bereken == d_fld[fld]["bereken"]: 
                # TODO check if field exists
                #if not fld.excists:
                #    add_field_from_dict(self, fc, fld_name, d_fld, feedback)
                self.bereken_veld(fc, fld, d_fld, feedback)
                i += 1
        if i == 0:
            feedback.pushWarning("bereken stap '{}' niet gevonden in input_fields. Geen velden toegevoegd".format(bereken))
        else:
            feedback.pushInfo("{} velden berekend".format(i))

        return fc

    def bereken_onderbemaling_flds(self, layer, parameters, feedback):
        """bereken onderbemalingen voor SUM_WAARDE.
        Maakt selectie op basis van veld [ONTV_VAN] -> VAN_KNOOPN IN ('ZRE-123424', 'ZRE-234')"""
        # sum values op basis van selectie [ONTV_VAN]
        # model-input: POC_GEM_m3h;POC_GEM_onderbemalingen_m3h,POC_VGS_m3h;POC_VGS_onderbemalingen_m3h,DWA_BAG_m3h;DWA_BAG_onderbemalingen_m3h,PAR_DRINKWATER_m3h;PAR_DRINKWATER_onderbemalingen_m3h,ZAK_DRINKWATER_m3h;ZAK_DRINKWATER_onderbemalingen_m3h,TOT_DRINKWATER_m3h;TOT_DRINKWATER_onderbemalingen_m3h,VE_m3h;VE_onderbemalingen_m3h,ExAFW_2124;ExAFW_2124_onderbemalingen,ExAFW_3039;ExAFW_3039_onderbemalingen,ExAFW_4050;ExAFW_4050_onderbemalingen
        fields_to_calc = parameters.get('veldenlijst', "").split(",") # "field1;us_field1,field2;us_field2"
        # test if fields exist
        try:
            for field_name in [field_name for fields in fields_to_calc for field_name in fields.split(';')]:
                if layer.fields().indexFromName(field_name) == -1:
                    feedback.pushWarning("The field {} does not exist in layer {}!".format(field_name, layer.name()))
        except Exception as e:
            feedback.pushWarning('Field string not valid')
            feedback.pushWarning(f'{e}')
            return layer
        
        us_fields = set()
        layer.startEditing()
        for feature in layer.getFeatures():
            begin_fld = parameters.get('id_veld', "")
            ont_van_fld = parameters.get('ontvangt_van', "")
            VAN_KNOOPN = feature[begin_fld]
            ONTV_VAN = feature[ont_van_fld]
            if not str(ONTV_VAN) in ["NULL", ""," "]: # check of sprake is van onderbemaling
                feedback.pushDebugInfo("{} {} ontvangt van {}".format(begin_fld,VAN_KNOOPN,ONTV_VAN))
                where_clause = '"{}" IN ({})'.format(begin_fld, ONTV_VAN)
                ##where_clause = '"VAN_KNOOPN" = '+"'MERG10'"
                ##feedback.pushDebugInfo("where_clause = {}".format(where_clause))
                expr = QgsExpression(where_clause)
                ##feedback.pushDebugInfo(str(expr))
                if expr.hasParserError():
                    feedback.pushWarning("expression has parserError!")
                if expr.hasEvalError():
                    feedback.pushWarning("expression has Evaluation Error!")
                # TODO apparently using iterator object this is the old way
                # it = layer.getFeatures(QgsFeatureRequest(expr))  # iterator object
                # layer.selectByIds([i.id() for i in it])
                layer.selectByExpression(where_clause)
                feedback.pushDebugInfo("{} features selected".format(layer.selectedFeatureCount()))
                feedback.pushDebugInfo("selected id's: {}".format(layer.selectedFeatureIds()))
                for flds in fields_to_calc:
                    try:
                        field, sum_field = flds.split(";") # "field1;us_field1"
                        us_fields.add(sum_field)
                        sum_values = sum([float(f[field]) for f in layer.selectedFeatures() if str(f[field]) not in ["NULL","nan",""," "]])
                        layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(sum_field), round(sum_values,2))
                    except Exception as e:
                        feedback.pushWarning(str(e))

        layer.commitChanges()
        layer.selectByIds([])
        feedback.pushInfo(f"Onderbemalingen succesvol berekend voor {str(us_fields)}")
        
        return layer
    
    def bereken_onderbemaling_POC_with_iteration(self, layer, parameters, feedback):
        """bereken onderbemalingen voor SUM_WAARDE.
        Maakt selectie op basis van veld [ONTV_VAN] -> VAN_KNOOPN IN ('ZRE-123424', 'ZRE-234')"""
        # sum values op basis van selectie [ONTV_VAN]
        # model-input: POC_GEM_m3h;POC_GEM_onderbemalingen_m3h,POC_VGS_m3h;POC_VGS_onderbemalingen_m3h,DWA_BAG_m3h;DWA_BAG_onderbemalingen_m3h,PAR_DRINKWATER_m3h;PAR_DRINKWATER_onderbemalingen_m3h,ZAK_DRINKWATER_m3h;ZAK_DRINKWATER_onderbemalingen_m3h,TOT_DRINKWATER_m3h;TOT_DRINKWATER_onderbemalingen_m3h,VE_m3h;VE_onderbemalingen_m3h,ExAFW_2124;ExAFW_2124_onderbemalingen,ExAFW_3039;ExAFW_3039_onderbemalingen,ExAFW_4050;ExAFW_4050_onderbemalingen
        # default input fields
        begin_fld = parameters.get('id_veld', "")
        ont_van_fld = parameters.get('ontvangt_van', "")
        X_OPPOMP = "Aantal_Keer_Oppompen_Tot_En_Met_Afleverpunt" #voorheen "Aantal_Keer_Oppompen_Tot_Afleverpunt"
        Afvoercapaciteit_m3h = "Afvoercapaciteit_m3h"
        POC_theorie = "POC_Theorie_Totaal_m3h"
        # DWA_tot = "Sommatie_DWA_BAG_m3h" # "Sommatie_Droogweerafvoer_BAG_m3h"
        
        # POC_obm = "POC_Praktijk_Onderbem_DWA_obv_BAG_m3h"
        # POC_tot = "Sommatie_POC_Praktijk_DWA_obv_BAG_m3h"
        # POC_geb = "POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h" # "POC_Praktijk_Eigen_Rioleringsgebied_OBV_Droogweerafvoer_OBV_BAG_m3h"     
        # Afv_tot = "Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h"# "Sommatie_Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h"

        # fields input per source 
        fields_BAG_input =          ["Sommatie_DWA_BAG_m3h"]
        fields_Drinkwater_input =   ["Sommatie_Drinkwater_Totaal_m3h"]
        fields_VEs_input =          ["Sommatie_DWA_VEs_m3h"]

        # fields output per source 
        fields_BAG_output =         ["POC_Praktijk_Onderbem_DWA_obv_BAG_m3h", "Sommatie_POC_Praktijk_DWA_obv_BAG_m3h", "Sommatie_POC_Praktijk_DWA_obv_BAG_m3h_obv_afvoercap", "POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h", "Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h"]
        fields_Drinkwater_output =  ["POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h", "Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h", "Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h_obv_afvoercap", "POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h", "Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h"]
        fields_VEs_output =         ["POC_Praktijk_Onderbem_DWA_obv_VEs_m3h", "Sommatie_POC_Praktijk_DWA_obv_VEs_m3h", "Sommatie_POC_Praktijk_DWA_obv_VEs_m3h_obv_afvoercap", "POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h", "Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h"]

        fields_BAG = fields_BAG_input + fields_BAG_output
        fields_Drinkwater = fields_Drinkwater_input + fields_Drinkwater_output
        fields_VEs = fields_VEs_input + fields_VEs_output

        # test if fields exist
        fields_input = [begin_fld, ont_van_fld, X_OPPOMP, Afvoercapaciteit_m3h, POC_theorie] + fields_BAG_input + fields_Drinkwater_input + fields_VEs_input
        fields_output = fields_BAG_output + fields_Drinkwater_output + fields_VEs_output
        all_fields = fields_input + fields_output
        fields_missing = 0
        for field_name in all_fields:
            if layer.fields().indexFromName(field_name) == -1:
                feedback.pushWarning("The field {} does not exist in layer {}!".format(field_name, layer.name()))
                fields_missing += 1
                # Add the new field to the layer
                feedback.pushWarning(f"Adding missing field {field_name}")
                layer.dataProvider().addAttributes([QgsField(field_name, QVariant.Double)])

        if fields_missing > 0:
            feedback.pushWarning(f"{fields_missing} fields missing in input.")
        
        us_fields = set()
        layer.startEditing()

        for DWA_tot, POC_obm, POC_tot, POC_tot_cap, POC_geb, Afv_tot in [fields_BAG, fields_VEs, fields_Drinkwater]:
            sorted_features = sorted(layer.getFeatures(), key=lambda f: f[X_OPPOMP], reverse=True)
            for feature in sorted_features: #layer.getFeatures(): 
                VAN_KNOOPN = feature[begin_fld]
                ONTV_VAN = feature[ont_van_fld]
                feedback.pushDebugInfo(f"\ncalculate {VAN_KNOOPN}, niveau {feature[X_OPPOMP]}...")
                if not str(ONTV_VAN) in ["NULL", ""," "]: # check of sprake is van onderbemaling
                    feedback.pushDebugInfo("{} {} ontvangt van {}".format(begin_fld,VAN_KNOOPN,ONTV_VAN))
                    where_clause = '"{}" IN ({})'.format(begin_fld, ONTV_VAN)
                    where_clause_1N = '"{}" IN ({})'.format(begin_fld, ONTV_VAN)
                    ##where_clause = '"VAN_KNOOPN" = '+"'MERG10'"
                    ##feedback.pushDebugInfo("where_clause = {}".format(where_clause))
                    expr = QgsExpression(where_clause_1N)
                    ##feedback.pushDebugInfo(str(expr))
                    if expr.hasParserError():
                        feedback.pushWarning("expression has parserError!")
                    if expr.hasEvalError():
                        feedback.pushWarning("expression has Evaluation Error!")
                    # TODO apparently using iterator object this is the old way
                    # it = layer.getFeatures(QgsFeatureRequest(expr))  # iterator object
                    # layer.selectByIds([i.id() for i in it])
                    layer.selectByExpression(where_clause_1N)
                    feedback.pushDebugInfo("{} features selected".format(layer.selectedFeatureCount()))
                    feedback.pushDebugInfo("selected id's: {}".format(layer.selectedFeatureIds()))

                    # 1.) first update POC_Praktijk_Onderbem_DWA_obv_BAG_m3h with Sommatie_POC_Praktijk_DWA_obv_BAG_m3h_obv_afvoercap based on id's in Onderbemalingsgeb_IDs_1_Niveau_Diep
                    us_fields.add(POC_obm)
                    sum_values = sum([float(f[POC_tot_cap]) for f in layer.selectedFeatures() if str(f[POC_tot_cap]) not in ["NULL","nan",""," ","None"]])
                    POC_obm_sum = round(sum_values,2)
                else: # geen onderbemaling
                    POC_obm_sum = 0

                feedback.pushDebugInfo(f"{POC_obm} = {POC_obm_sum} (sum {POC_tot} van {ONTV_VAN})")
                feature[POC_obm] = POC_obm_sum
                DWA_tot_sum = feature[DWA_tot]
                feedback.pushDebugInfo(f'DWA_tot_sum={DWA_tot_sum}')
                # 2.) now calculate POC praktijk (POC_Praktijk_Eigen_Rioleringsgebied_OBV_Droogweerafvoer_OBV_BAG_m3h)
                Afvoercapaciteit_m3h_sum = feature[Afvoercapaciteit_m3h]
                if feature[POC_theorie] == None:
                    gemengd_stelsel = False
                elif feature[POC_theorie] > 0:
                    gemengd_stelsel = True
                else:
                    gemengd_stelsel = False
                if gemengd_stelsel:
                    if Afvoercapaciteit_m3h_sum == None:
                        feedback.pushWarning(f"Geen afvoercapaciteit bekend voor {VAN_KNOOPN}. POC praktijk berekening overgeslagen.")
                        POC_geb_sum = 0
                    elif Afvoercapaciteit_m3h_sum == 0:
                        feedback.pushWarning(f"Afvoercapaciteit is {Afvoercapaciteit_m3h_sum} voor {VAN_KNOOPN}. POC praktijk berekening overgeslagen.")
                        POC_geb_sum = 0
                    else:
                        POC_geb_sum = round(Afvoercapaciteit_m3h_sum - DWA_tot_sum - POC_obm_sum, 2) # Afvoercapaciteit_m3h - DWA totaal - POC uit onderbemaling)
                        feedback.pushDebugInfo(f"{POC_geb_sum} = {Afvoercapaciteit_m3h_sum} - {DWA_tot_sum} - {POC_obm_sum}, {POC_geb} = {Afvoercapaciteit_m3h} - {DWA_tot} - {POC_obm}")
                else:
                    POC_geb_sum = 0 # default
                if POC_geb_sum < 0:
                    feedback.pushWarning(f"{VAN_KNOOPN}: {POC_geb} ({POC_geb_sum}) < 0 (Afvalwateraanbod > Gemaalcapaciteit), {POC_geb} opslaan als 0")
                    POC_geb_sum = 0
                feature[POC_geb] = POC_geb_sum
                # 3.) calculate POC totaal
                POC_tot_sum = round(POC_geb_sum + POC_obm_sum, 2) # POC totaal = POC gebied + POC onderbemaling
                feature[POC_tot] = POC_tot_sum
                feedback.pushDebugInfo(f"{POC_tot_sum} = {POC_geb_sum} + {POC_obm_sum}, {POC_tot} = {POC_geb} + {POC_obm}")
                # 4.) calculate Afvalwater totaal
                Afv_tot_sum = round(DWA_tot_sum + POC_tot_sum, 2)
                feedback.pushDebugInfo(f"{Afv_tot_sum} = {DWA_tot_sum} + {POC_tot_sum}, {Afv_tot} = {DWA_tot} + {POC_tot}")
                feature[Afv_tot] = Afv_tot_sum
                # 5.) calculate POC totaal obv max. afvoercapaciteit (dit is de waarde die wordt gebruikt voor onderbemaling)
                if Afvoercapaciteit_m3h_sum and Afv_tot_sum > Afvoercapaciteit_m3h_sum:
                    feedback.pushDebugInfo(f"{VAN_KNOOPN}: Afvalwater totaal ({Afv_tot_sum}) > afvoercapaciteit ({Afvoercapaciteit_m3h_sum})")
                    POC_tot_cap_sum = Afvoercapaciteit_m3h_sum - DWA_tot_sum
                    if POC_tot_cap_sum < 0: # POC totaal obv afvoercap mag niet negatief zijn
                        POC_tot_cap_sum = 0
                    feedback.pushDebugInfo(f"{POC_tot_cap} = Afvoercapaciteit - DWA totaal ({POC_tot_cap_sum} = {Afvoercapaciteit_m3h_sum} - {DWA_tot_sum})")
                else:
                    POC_tot_cap_sum = POC_tot_sum # geen correctie voor afvoercapaciteit, POC totaal gelijk.
                feature[POC_tot_cap] = POC_tot_cap_sum
               
                layer.updateFeature(feature)                

        layer.commitChanges() # double?
        layer.selectByIds([])
        feedback.pushInfo(f"Onderbemalingen succesvol berekend voor {str(us_fields)}")
        
        return layer

    def bereken_onderbemaling(self, layer, d_fld, parameters, feedback):
        """bereken onderbemalingen voor SUM_WAARDE, SUM_BLA, etc..
        Maakt selectie op basis van veld [ONTV_VAN] -> VAN_KNOOPN IN ('ZRE-123424', 'ZRE-234')"""
        # sum values op basis van selectie [ONTV_VAN]
        fields_to_calc = parameters.get('fields_to_calc', [])
        if not fields_to_calc:
            for fld in d_fld:
                if parameters['uittevoerenstapininputfields'] == d_fld[fld]["bereken"]:
                    fields_to_calc.append({"expression": d_fld[fld]['expression'], "name": fld})
        
        # --- test
        # fields_to_calc = [{'expression': 'par_result_sum','name': 'X_WON_ONBG'}]
        # --- mapper example

        layer.startEditing()
        for feature in layer.getFeatures():
            begin_fld = "BEM_ID" 
            if parameters['alleendirecteonderbemaling']:
                ont_van_fld = "K_ONTV_1N"
            else:
                ont_van_fld = "K_ONTV_VAN"
            VAN_KNOOPN = feature[begin_fld]
            ONTV_VAN = feature[ont_van_fld]
            if not str(ONTV_VAN) in ["NULL", ""," "]: # check of sprake is van onderbemaling
                feedback.pushDebugInfo("{} {} ontvangt van {}".format(begin_fld,VAN_KNOOPN,ONTV_VAN))
                where_clause = '"{}" IN ({})'.format(begin_fld, ONTV_VAN)
                ##where_clause = '"VAN_KNOOPN" = '+"'MERG10'"
                ##feedback.pushDebugInfo("where_clause = {}".format(where_clause))
                expr = QgsExpression(where_clause)
                ##feedback.pushDebugInfo(str(expr))
                if expr.hasParserError():
                    feedback.pushWarning("expression has parserError!")
                if expr.hasEvalError():
                    feedback.pushWarning("expression has Evaluation Error!")
                # TODO apparently using iterator object this is the old way
                # it = layer.getFeatures(QgsFeatureRequest(expr))  # iterator object
                # layer.selectByIds([i.id() for i in it])
                layer.selectByExpression(where_clause)
                feedback.pushDebugInfo("{} features selected".format(layer.selectedFeatureCount()))
                feedback.pushDebugInfo("selected id's: {}".format(layer.selectedFeatureIds()))
                for d in fields_to_calc:
                    sum_field = d['name'] # te berekenen onderbemaling
                    field = d['expression'] # veld met gebiedsinformatie
                    try:
                        sum_values = sum([float(f[field]) for f in layer.selectedFeatures() if str(f[field]) not in ["NULL","nan",""," "]])
                        layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(sum_field), sum_values)
                    except Exception as e:
                        feedback.pushWarning(str(e))

        layer.commitChanges()
        layer.selectByIds([])
        feedback.pushInfo("Onderbemalingen succesvol berekend voor Plancap, drinkwater, woningen en ve's")
        
        return layer

    def lis2graph_ori(self, layer, feedback):
        """
        Maakt Graph met LIS-netwerk en bepaalt onderbemalingen.
        Vult [ONTV_VAN] en [X_OBEMAL].
        Gebruikt [LOOST_OP] en [VAN_KNOOPN] als edge (relation) en VAN_KNOOPN als node
        """
        # graph aanmaken
        graph = Graph()
        graph_rev = Graph()
        d_K_ONTV_VAN = {}    # alle onderliggende gemalen
        d_K_ONTV_VAN_n1 = {} # alle onderliggende gemalen op 1 niveau diep ivm optellen overcapaciteit
        feedback.pushInfo ("netwerk opslaan als graph...")
        VAN_FLD = "BEM_ID"
        NAAR_FLD = "NAAR_BEM_ID"
        LABEL = "VAN_KNOOPN"
        BM_NM = "BM_NM"
        d_LABEL = { }
        d_BM_NM = { }
        for feature in layer.getFeatures():  # .getFeatures()
            VAN_KNOOPN = feature[VAN_FLD]
            LOOST_OP = feature[NAAR_FLD]
            d_LABEL[VAN_KNOOPN] = feature[LABEL]
            d_BM_NM[VAN_KNOOPN] = feature[BM_NM] if layer.fields().indexFromName(BM_NM) != -1 else None
            graph.add_node(VAN_KNOOPN)
            graph_rev.add_node(VAN_KNOOPN)
            if LOOST_OP != None:
                graph.add_edge(VAN_KNOOPN, LOOST_OP, 1)  # richting behouden voor bovenliggende gebied
                graph_rev.add_edge(LOOST_OP, VAN_KNOOPN, 1)  # richting omdraaien voor onderliggende gebied
        edges_as_tuple = list(graph.distances)  # lijst met tuples: [('A', 'B'), ('C', 'B')]
        feedback.pushInfo("onderbemaling bepalen voor rioolgemalen en zuiveringen...")
        where_clause = "Join_Count > 0"
        layer.startEditing()
        for i, feature in enumerate(layer.getFeatures()):  # .getFeatures()
            ##if not feature["count"] >= 1: continue
            VAN_KNOOPN = feature[VAN_FLD]
            ##if not feature[NAAR_FLD]: continue 
            nodes = dijkstra(graph, VAN_KNOOPN)[0]
            ##print_log("nodes for {}: {}".format(VAN_KNOOPN,nodes), 'd')
            K_KNP_EIND, X_OPPOMP = [(key, value) for key, value in sorted(iter(nodes.items()), key=lambda k_v: (k_v[1], k_v[0]))][-1]
            ##print_log("endnode for {}: {},{}".format(VAN_KNOOPN,K_KNP_EIND, X_OPPOMP),'d')
            d_edges = dijkstra(graph_rev, VAN_KNOOPN)[1]  # {'B': 'A', 'C': 'B', 'D': 'C'}
            l_onderliggende_gemalen = str(list(d_edges))  # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_gemalen = l_onderliggende_gemalen.replace("u'", "'").replace("[", "").replace("]", "")
            # onderbemalingen 1 niveau diep
            l_onderliggende_gemalen_n1 = [start for start, end in edges_as_tuple if end == VAN_KNOOPN and start != VAN_KNOOPN]  # dus start['A', 'C'] uit tuples[('A', 'B'),('C', 'B')] als end == 'B'
            s_onderliggende_gemalen_n1 =  str(l_onderliggende_gemalen_n1).replace("u'", "'").replace("[", "").replace("]", "") # naar str() en verwijder u'tjes en haken
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_ONTV_VAN"), l_onderliggende_gemalen) # K_ONTV_VAN = 'ZRE-1','ZRE-2'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_ONTV_1N"), s_onderliggende_gemalen_n1) # K_ONTV_1N = 'ZRE-1'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("X_OBEMAL"), len(list(d_edges)))  
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("X_OBEMA_1N"), len(list(l_onderliggende_gemalen_n1)))        # X_OBEMAL = 2 (aantal onderbemalingen)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("X_OPPOMP"),  X_OPPOMP + 1)             # X_OPPOMP = 1 (aantal keer oppompen tot rwzi) met shortestPath ('RWZI','ZRE-4')
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_KNP_EIND"), K_KNP_EIND)              # eindbemalingsgebied / overnamepunt. bepaald uit netwerk.
            d_K_ONTV_VAN[VAN_KNOOPN] = l_onderliggende_gemalen
            d_K_ONTV_VAN_n1[VAN_KNOOPN] =  l_onderliggende_gemalen_n1
            # convert bemid's to description field
            l_onderliggende_desc = str([d_LABEL[key] for key in list(d_edges)]) # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_desc = l_onderliggende_desc.replace("u'", "'").replace("[", "").replace("]", "")
            l_onderliggende_desc_n1 = str([d_LABEL[key] for key in l_onderliggende_gemalen_n1]).replace("u'", "'").replace("[", "").replace("]", "")
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_ONTV_VAN_NAME"), l_onderliggende_desc) # K_ONTV_VAN = 'ZRE-1','ZRE-2'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_ONTV_1N_NAME"), l_onderliggende_desc_n1) # K_ONTV_1N = 'ZRE-1'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_KNP_EIND_NAME"), d_BM_NM[K_KNP_EIND])              # eindbemalingsgebied / overnamepunt. bepaald uit netwerk.

        layer.commitChanges()
        return [layer, d_K_ONTV_VAN, d_K_ONTV_VAN_n1]

    def lis2graph(self, layer, feedback):
        """
        Maakt Graph met LIS-netwerk en bepaalt onderbemalingen.
        Vult [ONTV_VAN] en [X_OBEMAL].
        Gebruikt [LOOST_OP] en [VAN_KNOOPN] als edge (relation) en VAN_KNOOPN als node
        """
        # graph aanmaken
        graph = Graph()
        graph_rev = Graph()
        d_K_ONTV_VAN = {}    # alle onderliggende gemalen
        d_K_ONTV_VAN_n1 = {} # alle onderliggende gemalen op 1 niveau diep ivm optellen overcapaciteit
        feedback.pushInfo ("netwerk opslaan als graph...")
        # VAN_FLD = "BEM_ID"      # unieke id
        # NAAR_FLD = "DS_BEM_ID"  # loost op 
        # AFVOERPUNT = "begin"    # afvoerpuntcode. meenemen als Afvoerpunten_onderbemalingen, N1_afvoerpunten_onderbemalingen, Naam_afleveringspunt
        # PC_ID = "PC_IDs"        # plancap gebieden meenemen als PC_IDs_onderbemalingen
        # BM_NM = "BM_NM"         # alternatief id field 3
        VAN_FLD = "Bemalingsgebied_ID"                  # unieke id
        NAAR_FLD = "Bemalingsgebied_ID_Lozingspunt"     # loost op 
        AFVOERPUNT = "Beginpunt_Afvoerrelatie"          # afvoerpuntcode. meenemen als Afvoerpunten_onderbemalingen, N1_afvoerpunten_onderbemalingen, Naam_afleveringspunt
        PC_ID = "Bouwprojecten_Eigen_Rioleringsgeb_IDs" # plancap gebieden meenemen als PC_IDs_onderbemalingen
        BM_NM = "BM_NM"                                 # alternatief id field 3
        d_AFVOERPUNT = { }
        d_PC_ID = { }
        d_BM_NM = { }
        for feature in layer.getFeatures():  # .getFeatures()
            VAN_KNOOPN = feature[VAN_FLD]
            LOOST_OP = feature[NAAR_FLD]
            d_AFVOERPUNT[VAN_KNOOPN] = feature[AFVOERPUNT]
            d_PC_ID[VAN_KNOOPN] = feature[PC_ID]
            d_BM_NM[VAN_KNOOPN] = feature[BM_NM] if layer.fields().indexFromName(BM_NM) != -1 else None
            graph.add_node(VAN_KNOOPN)
            graph_rev.add_node(VAN_KNOOPN)
            if LOOST_OP != None:
                graph.add_edge(VAN_KNOOPN, LOOST_OP, 1)  # richting behouden voor bovenliggende gebied
                graph_rev.add_edge(LOOST_OP, VAN_KNOOPN, 1)  # richting omdraaien voor onderliggende gebied
        edges_as_tuple = list(graph.distances)  # lijst met tuples: [('A', 'B'), ('C', 'B')]
        feedback.pushInfo("onderbemaling bepalen voor rioolgemalen en zuiveringen...")
        where_clause = "Join_Count > 0"
        layer.startEditing()
        # fields to fill
        Onderbemalingsgebied_IDs = "Onderbemalingsgebied_IDs" # Onderbemalingen
        Onderbemalingsgebied_IDs_1_NiveauDiep = "Onderbemalingsgeb_IDs_1_Niveau_Diep" # N1_onderbemalingen
        Aantal_Onderbemalingen = "Aantal_Onderbemalingen" # Aantal_onderbemalingen
        Aantal_Onderbemalingen_1_Niveau_Diep = "Aantal_Onderbemalingen_1_Niveau_Diep" # "N1_aantal_onderbemalingen"
        Aantal_Keer_Oppompen_Tot_Afleverpunt = "Aantal_Keer_Oppompen_Tot_En_Met_Afleverpunt"	# "X_OPPOMP"
        Rioleringsgebied_ID_Overnamepunt = "Rioleringsgebied_ID_Overnamepunt" # "BEM_ID_afleveringspunt"
        Afvoerpunten_Van_Onderbemalingen = "Afvoerpunten_Van_Onderbemalingen" # "Afvoerpunten_onderbemalingen"
        Afvoerpunten_1_Niveau_Diep = "Afvoerpunten_1_Niveau_Diep" # "N1_afvoerpunten_onderbemalingen"
        Naam_Overnamepunt = "Naam_Overnamepunt" # "Naam_afleveringspunt" 
        Bouwprojecten_IDs_Onderbemalingen = "Bouwprojecten_IDs_Onderbemalingen" # "PC_IDs_onderbemalingen"
        # test if fields exist
        l_fields_to_fill = [Onderbemalingsgebied_IDs, Onderbemalingsgebied_IDs_1_NiveauDiep, Aantal_Onderbemalingen, Aantal_Onderbemalingen_1_Niveau_Diep,
                            Aantal_Keer_Oppompen_Tot_Afleverpunt, Rioleringsgebied_ID_Overnamepunt, Afvoerpunten_Van_Onderbemalingen, Afvoerpunten_1_Niveau_Diep,
                            Naam_Overnamepunt, Bouwprojecten_IDs_Onderbemalingen]
        for field_name in l_fields_to_fill:
            if layer.fields().indexFromName(field_name) == -1:
                feedback.pushWarning("The field {} does not exist in layer {}!".format(field_name, layer.name()))

        for i, feature in enumerate(layer.getFeatures()):  # .getFeatures()
            ##if not feature["count"] >= 1: continue
            VAN_KNOOPN = feature[VAN_FLD]
            ##if not feature[NAAR_FLD]: continue 
            nodes = dijkstra(graph, VAN_KNOOPN)[0]
            ##print_log("nodes for {}: {}".format(VAN_KNOOPN,nodes), 'd')
            K_KNP_EIND, X_OPPOMP = [(key, value) for key, value in sorted(iter(nodes.items()), key=lambda k_v: (k_v[1], k_v[0]))][-1]
            ##print_log("endnode for {}: {},{}".format(VAN_KNOOPN,K_KNP_EIND, X_OPPOMP),'d')
            d_edges = dijkstra(graph_rev, VAN_KNOOPN)[1]  # {'B': 'A', 'C': 'B', 'D': 'C'}
            l_onderliggende_gemalen = str(list(d_edges))  # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_gemalen = l_onderliggende_gemalen.replace("u'", "'").replace("[", "").replace("]", "")
            # onderbemalingen 1 niveau diep
            l_onderliggende_gemalen_n1 = [start for start, end in edges_as_tuple if end == VAN_KNOOPN and start != VAN_KNOOPN]  # dus start['A', 'C'] uit tuples[('A', 'B'),('C', 'B')] als end == 'B'
            s_onderliggende_gemalen_n1 =  str(l_onderliggende_gemalen_n1).replace("u'", "'").replace("[", "").replace("]", "") # naar str() en verwijder u'tjes en haken
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Onderbemalingsgebied_IDs), l_onderliggende_gemalen) # 'BEM001','BEM002','BEM003'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Onderbemalingsgebied_IDs_1_NiveauDiep), s_onderliggende_gemalen_n1) # 'BEM002','BEM003'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Aantal_Onderbemalingen), len(list(d_edges)))  # 3 onderbemalingen
            # feedback.pushInfo(f"{VAN_KNOOPN}")
            # feedback.pushInfo(f"{len(list(d_edges))}")
            # feedback.pushInfo(f"{len(list(l_onderliggende_gemalen_n1))}")
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Aantal_Onderbemalingen_1_Niveau_Diep), len(list(l_onderliggende_gemalen_n1)))  # aantal onderbemalingen 1 niveau
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Aantal_Keer_Oppompen_Tot_Afleverpunt),  X_OPPOMP + 1)              # aantal keer oppompen tot rwzi
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Rioleringsgebied_ID_Overnamepunt), K_KNP_EIND)              # eindbemalingsgebied: BEM009
            d_K_ONTV_VAN[VAN_KNOOPN] = l_onderliggende_gemalen
            d_K_ONTV_VAN_n1[VAN_KNOOPN] =  l_onderliggende_gemalen_n1
            # convert bemid's to description field
            l_onderliggende_desc = str([d_AFVOERPUNT[key] for key in list(d_edges)]) # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_desc = l_onderliggende_desc.replace("u'", "'").replace("[", "").replace("]", "")
            l_onderliggende_desc_n1 = str([d_AFVOERPUNT[key] for key in l_onderliggende_gemalen_n1]).replace("u'", "'").replace("[", "").replace("]", "")
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Afvoerpunten_Van_Onderbemalingen), l_onderliggende_desc) # '38_9','345_23','52_1'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Afvoerpunten_1_Niveau_Diep), l_onderliggende_desc_n1) # '345_23','52_1'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Naam_Overnamepunt), d_BM_NM[K_KNP_EIND])  # laatste afvoerpunt code
            # add PC_IDs 
            l_onderliggende_PC_ID = str([d_PC_ID[key] for key in list(d_edges) if str(d_PC_ID[key]) != "NULL"]) # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_PC_ID = l_onderliggende_PC_ID.replace("u'", "'").replace("[", "").replace("]", "")
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(Bouwprojecten_IDs_Onderbemalingen), l_onderliggende_PC_ID) # lijst met onderliggende plancap id's

        layer.commitChanges()
        return [layer, d_K_ONTV_VAN, d_K_ONTV_VAN_n1]
    
    def vervang_None_door_0_voor_velden_in_lijst(self, l, layer, feedback):
        """
        Vervang alle None-waarden met 0 voor velden in lijst
        """
        feedback.pushInfo("Data voorbereiden en berekeningen uitvoeren...")
        feedback.pushInfo("Vervang None met 0 voor alle velden in lijst {}...".format(l))
        layer.startEditing()
        for fld in l:
            for f in layer.getFeatures():
                try:
                    if not f[fld]:#str(f[fld]) in ["NULL", "", " ", "nan"]:
                        ##feedback.pushDebugInfo("replace {} with 0 for fld {}".format(f[fld], fld))
                        layer.changeAttributeValue(f.id(), layer.fields().indexFromName(fld), 0)
                    else:
                        pass
                        ##feedback.pushDebugInfo("value {} != NULL for fld {}".format(f[fld], fld))

                except Exception as e:
                    feedback.pushWarning("fout bij omzetten None-waarden naar 0 bij veld {}. {}".format(fld, e))
        layer.commitChanges()
        return layer

    
class CustomToolsLis2GraphAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CustomToolsLis2GraphAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lis2graph'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('lis2graph')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Maakt Graph met LIS-netwerk en bepaalt onderbemalingen")   

    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        layer, d_K_ONTV_VAN, d_K_ONTV_VAN_n1 = self.lis2graph(layer, feedback)
        return layer
    

class CustomToolsAddFieldsFromDictAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CustomToolsAddFieldsFromDictAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'add fields from csv input fields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('add fields from csv input fields')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('inputfields', 'input_fields', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=default_inp_fields))
        self.addParameter(QgsProcessingParameterString('uittevoerenstapininputfields', 'uit te voeren stap in input_fields', multiLine=False, defaultValue='st2a'))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        d_fld = self.get_d_velden_csv(parameters['inputfields'])
        layer = self.add_field_from_dict_label(
            layer, 
            parameters['uittevoerenstapininputfields'],
            d_fld, 
            feedback
        )
        return layer


class CustomToolsCalcFieldsFromDictAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    def createInstance(self):
            return CustomToolsCalcFieldsFromDictAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'calc fields from csv input fields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('calc fields from csv input fields')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('inputfields', 'input_fields', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=default_inp_fields))
        self.addParameter(QgsProcessingParameterNumber('inw_per_adres', 'inw_per_adres', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=2.5))
        self.addParameter(QgsProcessingParameterString('uittevoerenstapininputfields', 'uit te voeren stap in input_fields', multiLine=False, defaultValue='st2a'))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        d_fld = self.get_d_velden_csv(parameters['inputfields'])
        if parameters.get('inw_per_adres', None):
            expression_DWA_BAG = f"[X_WON_TOT] * {parameters['inw_per_adres']} * 0.012"
            feedback.pushInfo(f'{expression_DWA_BAG=}')
            d_fld["DWA_BAG"]["expression"] = expression_DWA_BAG
        layer = self.bereken_veld_label(
            layer, 
            parameters['uittevoerenstapininputfields'],
            d_fld, 
            feedback
        )
        return layer
         

class CustomToolsBerekenOnderbemalingAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsBerekenOnderbemalingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'calc fields onderbemaling'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('calc fields onderbemaling')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterFile('inputfields', 'input_fields', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=r'G:\02_Werkplaatsen\07_IAN\bk\projecten\GeoDynGem\2022\inp_fields.csv'))
        self.addParameter(QgsProcessingParameterString('uittevoerenstapininputfields', 'uit te voeren stap in input_fields', multiLine=False, defaultValue='03_obm'))
        self.addParameter(QgsProcessingParameterBoolean('alleendirecteonderbemaling', 'alleen directe onderbemaling', defaultValue=False))
        #self.addParameter(QgsProcessingParameterFieldMapping('fields_to_calc', 'te berekenen velden met onderbemaling \n- "Source Expression" = veld met gebiedsinformatie \n- "Name" = veld met te berekenen onderbemaling'))
        #self.addParameter(QgsProcessingParameterFieldMapping('fields_to_calc_1n', 'te berekenen velden met onderbemaling 1 niveau'))
          
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        d_fld = self.get_d_velden_csv(parameters['inputfields'])
        layer = self.bereken_onderbemaling(layer, d_fld, parameters, feedback)
        return layer


class CustomToolsBerekenOnderbemalingFldsAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsBerekenOnderbemalingFldsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'calc fields upstream'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('calc fields upstream')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterString('id_veld', 'veld met unieke code', multiLine=False, defaultValue='Bemalingsgebied_ID'))
        self.addParameter(QgsProcessingParameterString('ontvangt_van', 'veld met opsomming onderbemaling id_velden', multiLine=False, defaultValue='Onderbemalingsgebied_IDs'))
        self.addParameter(QgsProcessingParameterString('veldenlijst', 'veldenlijst voor te berekenen onderbemaling (us): "field1;us_field1,field2;us_field2"', multiLine=False, defaultValue='POC_Theorie_Gemengd_m3h;POC_Theorie_Gemengd_Onderbem_m3h,POC_Theorie_VGS_m3h;POC_Theorie_VGS_Onderbem_m3h,DWA_BAG_m3h;DWA_BAG_Onderbemalingen_m3h,Drinkwater_Particulier_m3h;Drinkwater_Part_Onderbem_m3h,Drinkwater_Zakelijk_m3h;Drinkwater_Zak_Onderbem_m3h,Drinkwater_Totaal_m3h;Drinkwater_Totaal_Onderbem_m3h,DWA_VEs_m3h;DWA_VEs_Onderbemalingen_m3h,Extra_DWA_Periode_2124_m3h;Extra_DWA_Periode_Onderbem_2124_m3h,Extra_DWA_Periode_2529_m3h;Extra_DWA_Periode_Onderbem_2529_m3h,Extra_DWA_Periode_3039_m3h;Extra_DWA_Periode_Onderbem_3039_m3h,Extra_DWA_Periode_4050_m3h;Extra_DWA_Periode_Onderbem_4050_m3h'))
            
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        layer = self.bereken_onderbemaling_flds(layer, parameters, feedback)
        return layer
    

class CustomToolsBerekenOnderbemalingFldsPOCAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsBerekenOnderbemalingFldsPOCAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'calc fields upstream POC with iteration'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('calc fields upstream POC with iteration')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterString('id_veld', 'veld met unieke code', multiLine=False, defaultValue='Bemalingsgebied_ID'))
        self.addParameter(QgsProcessingParameterString('ontvangt_van', 'veld met opsomming onderbemaling id_velden', multiLine=False, defaultValue='Onderbemalingsgeb_IDs_1_Niveau_Diep'))
                    
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        layer = self.bereken_onderbemaling_POC_with_iteration(layer, parameters, feedback)
        return layer


class CustomToolsVervangNoneDoor0Algorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsVervangNoneDoor0Algorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'VervangNoneValuesMet0VoorVeldenlijst'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('vervang alle None-waarden met 0 voor velden in lijst')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterString(
                'veldenlijst', 
                'velden die omgezet moeten worden, gescheiden met ;', 
                multiLine=False, 
                defaultValue='X_WON_ONBG;X_WON_GEB;X_VE_ONBG;X_VE_GEB;DWR_GEBIED;DWR_ONBG;AW_15_24_G;AW_15_24_O;AW_25_50_G;AW_25_50_O;PAR_RESULT;ZAK_RESULT;AW_21_24_G;AW_21_24_O;AW_25_29_G;AW_25_29_O;AW_30_39_G;AW_30_39_O;AW_40_50_G;AW_40_50_O'
        ))
        
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        l = parameters['veldenlijst'].split(";")
        layer = self.vervang_None_door_0_voor_velden_in_lijst(l, layer, feedback)
        return layer


class CustomToolsRetainFieldsAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    Custom RetainFields Algorithm for compatibility with qgis versions before 3.22
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsRetainFieldsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'retainfields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('retainfields')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterString(
                'veldenlijst', 
                'velden die bewaard moeten worden, gescheiden met ;', 
                multiLine=False, 
                defaultValue="Bemalingsgebied_ID;Afvoercapaciteit_m3h;Bemalingsgebied_ID_Lozingspunt;POC_Theorie_Totaal_m3h;DWA_BAG_m3h;Onderbemalingsgeb_IDs_1_Niveau_Diep;Onderbemalingsgebied_IDs;DWA_BAG_Onderbemalingen_m3h;POC_Praktijk_Onderbem_DWA_obv_BAG_m3h;POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h;POC_Praktijk_Onderbem_DWA_obv_VEs_m3h;Sommatie_DWA_BAG_m3h;Sommatie_Drinkwater_Totaal_m3h;Sommatie_DWA_VEs_m3h;POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h;POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h;Sommatie_POC_Praktijk_DWA_obv_BAG_m3h;Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h;Sommatie_POC_Praktijk_DWA_obv_VEs_m3h;Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h;Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h;Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h;POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h"
        ))
        
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        #QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        
        # Extract by expression for copy
        alg_params = {
            'EXPRESSION': '$id IS NOT NULL',
            'INPUT': parameters['inputlayer'],
            'OUTPUT': 'memory:'
        }
        layer = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback)['OUTPUT']
        # apparently writeAsVectorFormat works miracles for alle custom tools except retainfields
        # layer_path = os.path.join (cmd_folder, 'results', layer.name()+".gpkg")
        # QgsVectorFileWriter.writeAsVectorFormat(layer, layer_path, 'utf-8', layer.crs())
        # layer = QgsVectorLayer(layer_path, layer.name(), 'ogr')
        
        layer = self.customAlgorithm(layer, parameters, feedback)
        
        # Extract by expression for copy
        alg_params = {
            'EXPRESSION': '$id IS NOT NULL',
            'INPUT': layer,
            'OUTPUT': parameters['Output_layer']
        }

        outputs['result'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        results['Output_layer'] = outputs['result']['OUTPUT']
        
        return results
    
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        l = parameters['veldenlijst'].split(";")
        layer, feedback = self.retain_fields(l, layer, feedback)
        return layer


class CustomToolsSortByMultipleFieldsAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    Custom SortByMultipleFields Algorithm
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.


    def createInstance(self):
        return CustomToolsSortByMultipleFieldsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'sortfields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('sortfields')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))      
        self.addParameter(QgsProcessingParameterString(
                'veldenlijst', 
                '3 velden om op te sorteren, gescheiden met ;', 
                multiLine=False, 
                defaultValue="VAN_NAAR;BERGING_M3;length"
        ))
        
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        l = parameters['veldenlijst'].split(";")
        layer, feedback = self.sort_fields(l, layer, feedback)
        return layer


class CustomToolsDropEmptyFieldsAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    Custom Algorithm to drop empty fields
    """

    def createInstance(self):
        return CustomToolsDropEmptyFieldsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'drop_empty_fields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('drop empty fields')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterVectorLayer('inputlayer', 'input_layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))     
        
    def customAlgorithm(self, layer, parameters, feedback):
        """
        Here we define our own custom algorithm.
        """
        layer, feedback = self.drop_empty_fields(layer, feedback)
        return layer
    

class CustomToolsAddFieldAliasFromCsvAlgorithm(CustomToolAllFunctionsAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    INPUT = 'INPUT'
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CustomToolsAddFieldAliasFromCsvAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'add fieldAlias from csv input fields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('add fieldAlias from csv input fields')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(QgsProcessingParameterFile('inputfields', 'input_fields', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=default_inp_fields))
        
    def processAlgorithm(self, parameters, context, model_feedback):
        # effects input directly so no new output is created
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        
        layer = self.parameterAsVectorLayer(
            parameters, 
            self.INPUT, 
            context
        )
        d_fld = self.get_d_velden_csv(parameters['inputfields'])
        layer = self.add_fieldAlias_from_dict(layer, d_fld, feedback)
        
        return results

    