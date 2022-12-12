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

# set defaults
import os, inspect
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
default_inp_fields = os.path.join(cmd_folder, 'inp_fields.csv')


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
        self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input_fields_csv', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue='G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv'))
        self.addParameter(QgsProcessingParameterFeatureSink('Leidingen_niet_meegenomen', 'leidingen_niet_meegenomen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolstelsel_buffer_10m_buffer', 'rioolstelsel_buffer_10m_buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelaties_bemalingsgebieden', 'afvoerrelaties_bemalingsgebieden', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelaties_knooppunten', 'afvoerrelaties_knooppunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolgemalen_gekoppeld', 'rioolgemalen_gekoppeld', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bgt_intersect', 'bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'eindresultaat', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Meerdere_plancaps_in_bemalingsgebied', 'meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_in_meerdere_bemalingsgebieden', 'plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

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
            'Bemalingsgebieden_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'GebiedsgegevensStap1AllAtt': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_punt_tbv_stap2': QgsProcessing.TEMPORARY_OUTPUT,
            'GemengdeEnVuilwaterstelsels': QgsProcessing.TEMPORARY_OUTPUT,
            'LeidingenNietMeegenomen': parameters['Leidingen_niet_meegenomen'],
            'Rioolstelsel_buffer': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer_10m': parameters['Rioolstelsel_buffer_10m_buffer']
        }
        alg_params['keepName'] = True
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Leidingen_niet_meegenomen'] = outputs['Stap1GwswToGeodyn']['LeidingenNietMeegenomen']
        results['Rioolstelsel_buffer_10m_buffer'] = outputs['Stap1GwswToGeodyn']['Rioolstelsel_buffer_10m']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'bemalingsgebieden': outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2'],
            'gebiedsgegevenspunttbvstap2': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_punt_tbv_stap2'],
            'inputfieldscsv': parameters['inputfieldscsv'],
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2'],
            'Afvoerboom': parameters['Afvoerrelaties_bemalingsgebieden'],
            'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten_in_eindgebied_selected': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_selectie': parameters['Afvoerrelaties_knooppunten'],
            'Van_naar': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar_sel': parameters['Rioolgemalen_gekoppeld']
        }
        alg_params['keepName'] = True
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Afvoerrelaties_bemalingsgebieden'] = outputs['Stap2Genereer_afvoerrelaties']['Afvoerboom']
        results['Afvoerrelaties_knooppunten'] = outputs['Stap2Genereer_afvoerrelaties']['Gebiedsgegevens_lijn_selectie']
        results['Rioolgemalen_gekoppeld'] = outputs['Stap2Genereer_afvoerrelaties']['Van_naar_sel']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # stap 3.) bereken afvalwaterprognose
        alg_params = {
            'bemalingsgebiedenstats': outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'bgtinlooptabel': parameters['inputbemalingsgebieden (2) (2) (2) (2)'],
            'inputdrinkwater': parameters['inputbemalingsgebieden (2) (2) (3) (2)'],
            'inputfieldscsv': parameters['inputfieldscsv'],
            'inputplancap': parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'],
            'inputves': parameters['inputbemalingsgebieden (2) (2) (3)'],
            'Bgt_intersect': parameters['Bgt_intersect'],
            'Meerdere_plancaps_in_bemalingsgebied': parameters['Meerdere_plancaps_in_bemalingsgebied'],
            'Plancap_in_meerdere_bemalingsgebieden': parameters['Plancap_in_meerdere_bemalingsgebieden'],
            'Result': parameters['Eindresultaat']
        }
        alg_params['keepName'] = True
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bgt_intersect'] = outputs['Stap3BerekenAfvalwaterprognose']['Bgt_intersect']
        results['Eindresultaat'] = outputs['Stap3BerekenAfvalwaterprognose']['Result']
        results['Meerdere_plancaps_in_bemalingsgebied'] = outputs['Stap3BerekenAfvalwaterprognose']['Meerdere_plancaps_in_bemalingsgebied']
        results['Plancap_in_meerdere_bemalingsgebieden'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_in_meerdere_bemalingsgebieden']


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