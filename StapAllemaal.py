"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""
import string
import random
import processing
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProject)


class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()
        
    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)

        
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
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_tbv_stap2', 'bemalingsgebieden_tbv_stap2', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Leidingen_niet_meegenomen', 'leidingen_niet_meegenomen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolstelsel_buffer_10m_buffer', 'rioolstelsel_buffer_10m_buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelaties', 'afvoerrelaties', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'eindresultaat', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_overlap', 'plancap_overlap', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
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
            'Bemalingsgebieden_tbv_stap2': parameters['Bemalingsgebieden_tbv_stap2'],
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'GebiedsgegevensStap1AllAtt': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_puntStap1': QgsProcessing.TEMPORARY_OUTPUT,
            'GemengdeEnVuilwaterstelsels': QgsProcessing.TEMPORARY_OUTPUT,
            'LeidingenNietMeegenomen': parameters['Leidingen_niet_meegenomen'],
            'Rioolstelsel_buffer': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer_10m': parameters['Rioolstelsel_buffer_10m_buffer']
        }
        alg_params['keepName'] = True
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bemalingsgebieden_tbv_stap2'] = outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2']
        results['Leidingen_niet_meegenomen'] = outputs['Stap1GwswToGeodyn']['LeidingenNietMeegenomen']
        results['Rioolstelsel_buffer_10m_buffer'] = outputs['Stap1GwswToGeodyn']['Rioolstelsel_buffer_10m']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'Bemalingsgebieden_tbv_stap2': outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2'],
            'inputfieldscsv': 'G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv',
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2'],
            'Afvoerboom': QgsProcessing.TEMPORARY_OUTPUT,
            'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3': parameters['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten_in_eindgebied_selected': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_selectie': parameters['Afvoerrelaties'],
            'Van_naar': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar_sel': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'] = outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3']
        results['Afvoerrelaties'] = outputs['Stap2Genereer_afvoerrelaties']['Gebiedsgegevens_lijn_selectie']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # stap 3.) bereken afvalwaterprognose
        alg_params = {
            'bgtinlooptabel': parameters['inputbemalingsgebieden (2) (2) (2) (2)'],
            'input': outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'inputfieldscsv': 'G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv',
            'inputplancap': parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'],
            'inputves': parameters['inputbemalingsgebieden (2) (2) (3)'],
            'inputves (2)': parameters['inputbemalingsgebieden (2) (2) (3) (2)'],
            'Plancap_overlap': parameters['Plancap_overlap'],
            'Result': parameters['Eindresultaat'],
            'Stats_drinkwater': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_plancap': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_ve': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindresultaat'] = outputs['Stap3BerekenAfvalwaterprognose']['Result']
        results['Plancap_overlap'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_overlap']

        # --- add below each alg_params {} 
        # alg_params['keepName'] = True

        # --- this is needed to rename layers. looks funky, but works!
        for key in results:
            random_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
            global_key = key + "_" + random_string 
            feedback.pushInfo("rename layer to {}".format(key))
            globals()[global_key] = Renamer(key) #create unique global renamer instances
            context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[global_key])

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