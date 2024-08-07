"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""

import processing
import os
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingUtils,
                       QgsProject)
from .custom_tools import rename_layers, default_inp_fields, default_layer, QgsProcessingAlgorithmPost, cmd_folder
from qgis.utils import iface
from PyQt5 import Qt
       
class Stap2Genereer_afvoerrelaties(QgsProcessingAlgorithmPost):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebieden', 'bemalingsgebieden_tbv_stap2', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('bemalingsgebieden_tbv_stap2')))
        self.addParameter(QgsProcessingParameterVectorLayer('gebiedsgegevenspunttbvstap2', 'Gebiedsgegevens_punt_tbv_stap2', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('Gebiedsgegevens_punt_tbv_stap2')))
        self.addParameter(QgsProcessingParameterVectorLayer('leidingen', 'gebiedsgegevens_lijn_tbv_stap2', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('gebiedsgegevens_lijn_tbv_stap2')))
        ##self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input_fields.csv', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=default_inp_fields))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Van_naar', 'VAN_NAAR', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebiedsgegevens_lijn_selectie', 'Gebiedsgegevens_lijn_selectie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindpunten_in_eindgebied_selected', 'eindpunten_in_eindgebied_selected', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerboom', 'afvoerboom', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Van_naar_sel', 'VAN_NAAR_SEL', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        parameters['inputfieldscsv'] = default_inp_fields
        self.result_folder = parameters['result_folder']
        #QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(30, model_feedback)
        results = {}
        outputs = {}

        # Point on surface BEM
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': parameters['bemalingsgebieden'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointOnSurfaceBem'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Add geometry attributes
        alg_params = {
            'CALC_METHOD': 0,  # Layer CRS
            'INPUT': parameters['leidingen'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddGeometryAttributes'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Aggregate BERGING_M3 by BEM_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'sum','delimiter': ',','input': 'BERGING_M3','length': 0,'name': 'BERGING_M3','precision': 0,'type': 6},{'aggregate': 'first_value','delimiter': ',','input': 'BEM_ID','length': 0,'name': 'BEM_ID','precision': 0,'type': 10}],
            'GROUP_BY': 'BEM_ID',
            'INPUT': parameters['gebiedsgegevenspunttbvstap2'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateBerging_m3ByBem_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator lineID
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'lineID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'lijn-'  ||  lpad( ($id),3,'0')",
            'INPUT': outputs['AddGeometryAttributes']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLineid'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract beginpunt
        alg_params = {
            'INPUT': outputs['FieldCalculatorLineid']['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractBeginpunt'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Extract eindpunt
        alg_params = {
            'INPUT': outputs['FieldCalculatorLineid']['OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractEindpunt'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Join van BEMnaam
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractBeginpunt']['OUTPUT'],
            'JOIN': parameters['bemalingsgebieden'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': 'VAN_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinVanBemnaam'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Join naar BEMnaam
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractEindpunt']['OUTPUT'],
            'JOIN': parameters['bemalingsgebieden'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': 'NAAR_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinNaarBemnaam'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join van naar knoop
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'lineID',
            'FIELDS_TO_COPY': ['NAAR_BEM_ID'],
            'FIELD_2': 'lineID',
            'INPUT': outputs['JoinVanBemnaam']['OUTPUT'],
            'INPUT_2': outputs['JoinNaarBemnaam']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinVanNaarKnoop'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator VAN_NAAR
        alg_params = {
            'FIELD_LENGTH': 100,
            'FIELD_NAME': 'VAN_NAAR',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': '"VAN_BEM_ID" || \' -> \' || "NAAR_BEM_ID"',
            'INPUT': outputs['JoinVanNaarKnoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVan_naar'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by expression VAN<>NAAR
        # Drukriolering eruit filteren
        alg_params = {
            'EXPRESSION': ' "VAN_BEM_ID"<> "NAAR_BEM_ID" ',
            'INPUT': outputs['FieldCalculatorVan_naar']['OUTPUT'],
            'OUTPUT': parameters['Van_naar']
        }
        outputs['ExtractByExpressionVannaar'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Van_naar'] = outputs['ExtractByExpressionVannaar']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # sortfields
        # custom sort function based on VAN_NAAR, BERGING_M3 (largest), length (shortest)
        alg_params = {
            'inputlayer': outputs['ExtractByExpressionVannaar']['OUTPUT'],
            'veldenlijst': 'VAN_NAAR;BERGING_M3;length',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Sortfields'] = processing.run('GeoDynTools:sortfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Order by field order
        alg_params = {
            'ASCENDING': True,
            'EXPRESSION': 'order',
            'INPUT': outputs['Sortfields']['Output_layer'],
            'NULLS_FIRST': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['OrderByFieldOrder'] = processing.run('native:orderbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Delete duplicates by attribute VAN_NAAR
        # Hier selecteren op langste stuk? Check toevoegen in meerdere stelsels?
        alg_params = {
            'FIELDS': ['VAN_NAAR'],
            'INPUT': outputs['OrderByFieldOrder']['OUTPUT'],
            'OUTPUT': parameters['Van_naar_sel']
        }
        outputs['DeleteDuplicatesByAttributeVan_naar'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Van_naar_sel'] = outputs['DeleteDuplicatesByAttributeVan_naar']['OUTPUT']

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Extract afvoerlijnen selectie
        alg_params = {
            'INPUT': parameters['leidingen'],
            'INTERSECT': outputs['DeleteDuplicatesByAttributeVan_naar']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Gebiedsgegevens_lijn_selectie']
        }
        outputs['ExtractAfvoerlijnenSelectie'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebiedsgegevens_lijn_selectie'] = outputs['ExtractAfvoerlijnenSelectie']['OUTPUT']

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Join bemalingsgebieden to afvoer_selectie
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['bemalingsgebieden'],
            'JOIN': outputs['DeleteDuplicatesByAttributeVan_naar']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'NON_MATCHING': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBemalingsgebiedenToAfvoer_selectie'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['bemalingsgebieden'],
            'JOIN': outputs['DeleteDuplicatesByAttributeVan_naar']['OUTPUT'],
            'JOIN_FIELDS': ['VAN_KNOOPN','NAAR_KNOOP','NAAR_BEM_ID'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Join van naar data aan lijnen - deze koppelen
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'lineID',
            'FIELDS_TO_COPY': ['VAN_BEM_ID','NAAR_BEM_ID','VAN_NAAR'],
            'FIELD_2': 'lineID',
            'INPUT': outputs['FieldCalculatorLineid']['OUTPUT'],
            'INPUT_2': outputs['DeleteDuplicatesByAttributeVan_naar']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinVanNaarDataAanLijnenDezeKoppelen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculate NAAR_BEM_ID if IS NULL
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'NAAR_BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': ' if( "NAAR_BEM_ID" IS NULL, "BEM_ID", "NAAR_BEM_ID")',
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculateNaar_bem_idIfIsNull'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join POS van naar data
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['lineID','VAN_BEM_ID','NAAR_BEM_ID','VAN_NAAR'],
            'FIELD_2': 'VAN_BEM_ID',
            'INPUT': outputs['PointOnSurfaceBem']['OUTPUT'],
            'INPUT_2': outputs['JoinVanNaarDataAanLijnenDezeKoppelen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinPosVanNaarData'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines) stroomdiagram punt in polygoon van BEM - STROOMDIAGRAM - AFVOERBOOM
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['JoinPosVanNaarData']['OUTPUT'],
            'HUB_FIELD': 'NAAR_BEM_ID',
            'HUB_FIELDS': [''],
            'SPOKES': outputs['PointOnSurfaceBem']['OUTPUT'],
            'SPOKE_FIELD': 'BEM_ID',
            'SPOKE_FIELDS': ['"WATER"'],
            'OUTPUT': parameters['Afvoerboom']
        }
        outputs['JoinByLinesHubLinesStroomdiagramPuntInPolygoonVanBemStroomdiagramAfvoerboom'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Afvoerboom'] = outputs['JoinByLinesHubLinesStroomdiagramPuntInPolygoonVanBemStroomdiagramAfvoerboom']['OUTPUT']

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # add fields st1a
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['FieldCalculateNaar_bem_idIfIsNull']['OUTPUT'],
            'uittevoerenstapininputfields': 'st1a',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddFieldsSt1a'] = processing.run('GeoDynTools:add fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Extract eindpunt in eindgebied 
        alg_params = {
            'INPUT': outputs['ExtractEindpunt']['OUTPUT'],
            'INTERSECT': outputs['JoinBemalingsgebiedenToAfvoer_selectie']['NON_MATCHING'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractEindpuntInEindgebied'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # lis2graph
        alg_params = {
            'inputlayer': outputs['AddFieldsSt1a']['Output_layer'],
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Lis2graph'] = processing.run('GeoDynTools:lis2graph', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Extract eindpunten by afvoerselectie
        alg_params = {
            'INPUT': outputs['ExtractEindpuntInEindgebied']['OUTPUT'],
            'INTERSECT': outputs['ExtractAfvoerlijnenSelectie']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Eindpunten_in_eindgebied_selected']
        }
        outputs['ExtractEindpuntenByAfvoerselectie'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindpunten_in_eindgebied_selected'] = outputs['ExtractEindpuntenByAfvoerselectie']['OUTPUT']

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Join attributes punt by field VAN_KNOOPN
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'VAN_KNOOPN',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'VAN_KNOOPN',
            'INPUT': outputs['Lis2graph']['Output_layer'],
            'INPUT_2': parameters['gebiedsgegevenspunttbvstap2'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesPuntByFieldVan_knoopn'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Rename field BERGING_M3 to BERGING_M3_SP
        alg_params = {
            'FIELD': 'BERGING_M3',
            'INPUT': outputs['JoinAttributesPuntByFieldVan_knoopn']['OUTPUT'],
            'NEW_NAME': 'BERGING_M3_SP',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RenameFieldBerging_m3ToBerging_m3_sp'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Join BERGING_M3 by field BEM_ID
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['BERGING_M3'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['RenameFieldBerging_m3ToBerging_m3_sp']['OUTPUT'],
            'INPUT_2': outputs['AggregateBerging_m3ByBem_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinBerging_m3ByFieldBem_id'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # calc fields '01_gwsw' from csv input fields
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['JoinBerging_m3ByFieldBem_id']['OUTPUT'],
            'uittevoerenstapininputfields': '01_gwsw',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields01_gwswFromCsvInputFields'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Drop field(s)
        alg_params = {
            'COLUMN': ['BEM_ID_2','distance_2','NUMMER','VAN_KNOOPN_2','NAAR_KNOOP_2'],
            'INPUT': outputs['CalcFields01_gwswFromCsvInputFields']['Output_layer'],
            'OUTPUT': parameters['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3']
        }
        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'] = outputs['DropFields']['OUTPUT']

        # --- this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            #results, context, feedback = rename_layers(results, context, feedback)
            context.setLayersToLoadOnCompletion({})
            for key in results:
                self.final_layers[key] = QgsProcessingUtils.mapLayerFromString(results[key], context)        
 
        return results

    

    def name(self):
        return 'stap 2.) genereer_afvoerrelaties'

    def displayName(self):
        return 'stap 2.) Genereer afvoerrelaties'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Stap2Genereer_afvoerrelaties()
    

        # ----- copy this code before returning results in algorithm class 
        # this is needed to rename layers. looks funky, but works!
        # if not parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
        #     for key in results:
        #         feedback.pushInfo("rename layer to {}".format(key))
        #         globals()[key] = Renamer(key) #create unique global renamer instances
        #         context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[key])