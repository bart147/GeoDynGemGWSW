"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""
import processing
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProject)
from .custom_tools import rename_layers, default_inp_fields

        
class GeodynAlleStappen(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden', 'Input bemalingsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2)', 'GWSW knooppunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2)', 'GWSW kunstwerken', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2)', 'GWSW verbindingen', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2)', 'BGT inlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2) (2)', 'Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3)', "VE's", types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3) (2)', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input_fields_csv', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue='G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_leidingen_niet_meegenomen', 'Stap1_leidingen_niet_meegenomen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_rioolstelsel_buffer_10m_buffer', 'Stap1_rioolstelsel_buffer_10m_buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_bemalingsgebieden', 'Stap2_afvoerrelaties_bemalingsgebieden', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_rioolgemalen', 'Stap2_afvoerrelaties_rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_rioolgemalen_gekoppeld', 'Stap2_rioolgemalen_gekoppeld', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'Eindresultaat', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_exafw_per_bem_id', 'Stap3_ExAFW_per_bem_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_pc_id', 'Stap3_Plancap_pc_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_bgt_intersect', 'Stap3_bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_meerdere_plancaps_in_bemalingsgebied', 'Stap3_meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_in_meerdere_bemalingsgebieden', 'Stap3_plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        parameters['inputfieldscsv'] = default_inp_fields
        QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # stap 1.) GWSW to Geodyn
        alg_params = {
            'GWSWBemalingsgebieden': parameters['inputbemalingsgebieden'],
            'GWSWnetwerkknooppunt': parameters['inputbemalingsgebieden (2)'],
            'GWSWnetwerkkunstwerk': parameters['inputbemalingsgebieden (2) (2)'],
            'MaxzoekafstandRG': 3,
            'netwerkverbinding': parameters['inputbemalingsgebieden (2) (2) (2)'],
            'Bemalingsgebieden_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'GebiedsgegevensStap1AllAtt': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_punt_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'GemengdeEnVuilwaterstelsels': QgsProcessing.TEMPORARY_OUTPUT,
            'LeidingenNietMeegenomen': parameters['Stap1_leidingen_niet_meegenomen'],
            'Rioolstelsel_buffer': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer_10m': parameters['Stap1_rioolstelsel_buffer_10m_buffer']
        }
        alg_params['keepName'] = True
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stap1_leidingen_niet_meegenomen'] = outputs['Stap1GwswToGeodyn']['LeidingenNietMeegenomen']
        results['Stap1_rioolstelsel_buffer_10m_buffer'] = outputs['Stap1GwswToGeodyn']['Rioolstelsel_buffer_10m']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'bemalingsgebieden': outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2'],
            'gebiedsgegevenspunttbvstap2': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_punt_tbv_stap2'],
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2'],
            'Afvoerboom': parameters['Stap2_afvoerrelaties_bemalingsgebieden'],
            'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten_in_eindgebied_selected': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_selectie': parameters['Stap2_afvoerrelaties_rioolgemalen'],
            'Van_naar': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar_sel': parameters['Stap2_rioolgemalen_gekoppeld']
        }
        alg_params['keepName'] = True
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stap2_afvoerrelaties_bemalingsgebieden'] = outputs['Stap2Genereer_afvoerrelaties']['Afvoerboom']
        results['Stap2_afvoerrelaties_rioolgemalen'] = outputs['Stap2Genereer_afvoerrelaties']['Gebiedsgegevens_lijn_selectie']
        results['Stap2_rioolgemalen_gekoppeld'] = outputs['Stap2Genereer_afvoerrelaties']['Van_naar_sel']

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
            'Bgt_intersect': parameters['Stap3_bgt_intersect'],
            'Exafw_per_bem_id': parameters['Stap3_exafw_per_bem_id'],
            'Meerdere_plancaps_in_bemalingsgebied': parameters['Stap3_meerdere_plancaps_in_bemalingsgebied'],
            'Plancap_in_meerdere_bemalingsgebieden': parameters['Stap3_plancap_in_meerdere_bemalingsgebieden'],
            'Plancap_pc_id': parameters['Stap3_plancap_pc_id'],
            'Result': parameters['Eindresultaat'],
            'Stats_drinkwater': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_ve': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindresultaat'] = outputs['Stap3BerekenAfvalwaterprognose']['Result']
        results['Stap3_exafw_per_bem_id'] = outputs['Stap3BerekenAfvalwaterprognose']['Exafw_per_bem_id']
        results['Stap3_plancap_pc_id'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_pc_id']
        results['Stap3_bgt_intersect'] = outputs['Stap3BerekenAfvalwaterprognose']['Bgt_intersect']
        results['Stap3_meerdere_plancaps_in_bemalingsgebied'] = outputs['Stap3BerekenAfvalwaterprognose']['Meerdere_plancaps_in_bemalingsgebied']
        results['Stap3_plancap_in_meerdere_bemalingsgebieden'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_in_meerdere_bemalingsgebieden']

        # --- add below each alg_params {} 
        # alg_params['keepName'] = True

        # --- this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            results, context, feedback = rename_layers(results, context, feedback)
 

        return results

    def name(self):
        return 'Alle stappen achter elkaar'

    def displayName(self):
        return 'Alle stappen achter elkaar'

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