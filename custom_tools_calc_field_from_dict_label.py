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
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis.core import QgsVectorLayer, QgsField, QgsProcessingParameterFile, QgsProcessingParameterString, QgsProcessingParameterVectorLayer, QgsProcessingMultiStepFeedback
from qgis.core import QgsExpression, QgsFeatureRequest, QgsExpressionContextScope, QgsExpressionContext
from qgis.PyQt.QtCore import QVariant
from qgis import processing


class CustomToolsCalcFieldsFromDictAlgorithm(QgsProcessingAlgorithm):
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

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

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
        return 'add fields from csv input fields'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('add fields from csv input fields')

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
        self.addParameter(QgsProcessingParameterFile('inputfields', 'input_fields', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=r'C:\Users\bkropf\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\GeodynGem\inp_fields.csv'))
        self.addParameter(QgsProcessingParameterString('uittevoerenstapininputfields', 'uit te voeren stap in input_fields', multiLine=False, defaultValue='st2a'))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_layer', 'output_layer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))


        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        
        #self.addParameter(
        #    QgsProcessingParameterVectorDestination(
        #        'FLD_OUTPUT',
        #        self.tr('fld output'),
        #    )
        #)
        ##self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT,self.tr('original Output layer')))
        
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
                fld["field_length"] = int(srow["lengte"])
            if str(srow["expression"]) not in ["nan", ""," "]:
                fld["expression"] = srow["expression"]
            if str(srow["stap_bereken"]) not in ["nan", ""," "]:
                fld["bereken"] = srow["stap_bereken"]
            d_velden[srow["fieldname"]] = fld
        f.close()
        
        return d_velden

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

        if fc.fields().indexFromName(fld_name) == -1:
            fc.dataProvider().addAttributes([QgsField(prec=2, name=fld_name, type=fldtype_mapper.get(fld["field_type"],QVariant.String), len=field_length)])
            fc.updateFields()

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
                it = fc.getFeatures(QgsFeatureRequest(expr))  # iterator object
                fc.selectByIds([i.id() for i in it])

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

    def bereken_veld_label(self, fc, bereken, d_fld, feedback):
        """bereken velden op basis van label 'bereken' en fc in d_fld"""
        feedback.pushInfo("\nvelden met label 'bereken' : '{}' uitrekenen:".format(bereken))
        for fld in d_fld:
            if not "bereken" in list(d_fld[fld].keys()): continue
            if bereken == d_fld[fld]["bereken"]: 
                # TODO check if field exists
                #if not fld.excists:
                #    add_field_from_dict(self, fc, fld_name, d_fld, feedback)
                self.bereken_veld(fc, fld, d_fld, feedback)


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
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

        #results['Result'] = outputs['copy_input']['OUTPUT']
        
        d_fld = self.get_d_velden_csv(parameters['inputfields'])
        
        self.bereken_veld_label(
            layer, 
            parameters['uittevoerenstapininputfields'],
            d_fld, 
            feedback
        )

        # self.add_field_from_dict_label(
        #     layer, 
        #     parameters['uittevoerenstapininputfields'],
        #     d_fld, 
        #     feedback
        # )
        
        # Extract by expression for copy
        alg_params = {
            'EXPRESSION': '$id IS NOT NULL',
            'INPUT': layer,
            'OUTPUT': parameters['Output_layer']
        }

        outputs['result'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        results['Output_layer'] = outputs['result']['OUTPUT']
        
        return results
