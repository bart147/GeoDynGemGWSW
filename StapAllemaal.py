"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""
import os
import processing
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProject,
                       QgsVectorLayer)
from .custom_tools import rename_layers, default_inp_fields, default_layer, QgsProcessingAlgorithmPost, cmd_folder

        
class GeodynAlleStappen(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden', 'Input bemalingsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('input bemalingsgebieden',geometryType=2)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2)', 'GWSW knooppunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_knooppunt',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2)', 'GWSW kunstwerken', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_kunstwerk',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2)', 'GWSW verbindingen', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('netwerk_verbinding',geometryType=1)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2)', 'BGT inlooptabel', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('inlooptabel', geometryType=2)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2) (2)', 'Plancap', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('plancap', geometryType=2)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3)', "VE's", optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('ve_', geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3) (2)', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('drinkwater', geometryType=0)))
        ##self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input_fields_csv', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue='G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv'))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap1_leidingen_niet_meegenomen', 'Stap1_leidingen_niet_meegenomen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap1_rioolstelsel_buffer_10m_buffer', 'Stap1_rioolstelsel_buffer_10m_buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_bemalingsgebieden', 'Stap2_afvoerrelaties_bemalingsgebieden', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_rioolgemalen', 'Stap2_afvoerrelaties_rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap2_rioolgemalen_gekoppeld', 'Stap2_rioolgemalen_gekoppeld', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'Eindresultaat', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Result_all_fields', 'Result_all_fields', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap3_exafw_per_bem_id', 'Stap3_ExAFW_per_bem_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_pc_id', 'Stap3_Plancap_pc_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap3_bgt_intersect', 'Stap3_bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap3_meerdere_plancaps_in_bemalingsgebied', 'Stap3_meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_in_meerdere_bemalingsgebieden', 'Stap3_plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        parameters['inputfieldscsv'] = default_inp_fields
        dummy_folder = "dummy_gpkg"
        if not parameters['inputbemalingsgebieden (2) (2) (3)']:
            parameters['inputbemalingsgebieden (2) (2) (3)'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "ve_empty.gpkg"), "ve_empty", "ogr")
        if not parameters['inputbemalingsgebieden (2) (2) (2) (2)']:
            parameters['inputbemalingsgebieden (2) (2) (2) (2)'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "bgt_inlooptabel_empty.gpkg"), "bgt_inlooptabel_empty", "ogr")
        if not parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)']:
            parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "plancap_empty.gpkg"), "plancap_empty", "ogr")
        QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # stap 1.) GWSW to Geodyn
        alg_params = {
            'Bemalingsgebieden_tbv_stap2': 'TEMPORARY_OUTPUT',
            'Eindpunten': 'TEMPORARY_OUTPUT',
            'GWSWBemalingsgebieden': parameters['inputbemalingsgebieden'],
            'GWSWnetwerkknooppunt': parameters['inputbemalingsgebieden (2)'],
            'GWSWnetwerkkunstwerk': parameters['inputbemalingsgebieden (2) (2)'],
            'MaxzoekafstandRG': 3,
            'netwerkverbinding': parameters['inputbemalingsgebieden (2) (2) (2)'],
            'Bemalingsgebieden_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Berging_uit_knopen': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'GebiedsgegevensStap1AllAtt': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_punt_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'GemengdeEnVuilwaterstelsels': QgsProcessing.TEMPORARY_OUTPUT,
            'LeidingenNietMeegenomen': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer_10m': QgsProcessing.TEMPORARY_OUTPUT,
            'Stelselkenmerken': QgsProcessing.TEMPORARY_OUTPUT
        }
        #alg_params['keepName'] = True
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'bemalingsgebieden': outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2'],
            'gebiedsgegevenspunttbvstap2': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_punt_tbv_stap2'],
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2'],
            'Afvoerboom': QgsProcessing.TEMPORARY_OUTPUT,
            'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten_in_eindgebied_selected': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_selectie': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar_sel': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # stap 3.) bereken afvalwaterprognose
        alg_params = {
            'bemalingsgebiedenstats': outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'bgtinlooptabel': parameters['inputbemalingsgebieden (2) (2) (2) (2)'],
            'inputdrinkwater': parameters['inputbemalingsgebieden (2) (2) (3) (2)'],
            'inputplancap': parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'],
            'inputves': parameters['inputbemalingsgebieden (2) (2) (3)'],
            'Bemalingsgebieden_joined_stats': QgsProcessing.TEMPORARY_OUTPUT,
            'Bgt_intersect': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindresultaat': QgsProcessing.TEMPORARY_OUTPUT,
            'Exafw_per_bem_id': QgsProcessing.TEMPORARY_OUTPUT,
            'Meerdere_plancaps_in_bemalingsgebied': QgsProcessing.TEMPORARY_OUTPUT,
            'Plancap_in_meerdere_bemalingsgebieden': QgsProcessing.TEMPORARY_OUTPUT,
            'Plancap_pc_id': QgsProcessing.TEMPORARY_OUTPUT,
            'Result_all_fields': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_drinkwater': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_ve': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)  
        
        # --- add below each alg_params {} 
        # alg_params['keepName'] = True

        #results, context, feedback = rename_layers(results, context, feedback)

        return results

    def name(self):
        return 'Alle stappen achter elkaar GWSW'

    def displayName(self):
        return 'Alle stappen achter elkaar GWSW'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return GeodynAlleStappen()    

        # ----- copy this code before returning results in algorithm class 
        # this is needed to rename layers. looks funky, but works!
        # for key in results:
        #     feedback.pushInfo("rename layer to {}".format(key))
        #     globals()[key] = Renamer(key) #create unique global renamer instances
        #     context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[key])