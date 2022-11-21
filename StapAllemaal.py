"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""

import processing
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean)


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
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelaties', 'afvoerrelaties', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'eindresultaat', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterBoolean('keepName', 'needs to be True', defaultValue=True))
    
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
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
            'BemalingsgebiedenTbvStap2Bem_id': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'GebiedsgegevensStap1AllAtt': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_puntStap1': QgsProcessing.TEMPORARY_OUTPUT,
            'GemengdeEnVuilwaterstelsels': QgsProcessing.TEMPORARY_OUTPUT,
            'LeidingenNietMeegenomen': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer': QgsProcessing.TEMPORARY_OUTPUT,
            'Rioolstelsel_buffer_10m': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'bemalingsgebieden': outputs['Stap1GwswToGeodyn']['BemalingsgebiedenTbvStap2Bem_id'],
            'inputfieldscsv': 'G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv',
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn'],
            'Afvoerboom': QgsProcessing.TEMPORARY_OUTPUT,
            'Bemalingsgebieden_met_afvoerrelaties': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten': QgsProcessing.TEMPORARY_OUTPUT,
            'Eindpunten_in_eindgebied_selected': QgsProcessing.TEMPORARY_OUTPUT,
            'Gebiedsgegevens_lijn_selectie': parameters['Afvoerrelaties'],
            'Van_naar': QgsProcessing.TEMPORARY_OUTPUT,
            'Van_naar_sel': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Afvoerrelaties'] = outputs['Stap2Genereer_afvoerrelaties']['Gebiedsgegevens_lijn_selectie']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # stap 3.) bereken afvalwaterprognose
        alg_params = {
            'bgtinlooptabel': parameters['inputbemalingsgebieden (2) (2) (2) (2)'],
            'input': outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties'],
            'inputfieldscsv': 'G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv',
            'inputplancap': parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'],
            'inputves': parameters['inputbemalingsgebieden (2) (2) (3)'],
            'inputves (2)': parameters['inputbemalingsgebieden (2) (2) (3) (2)'],
            'Plancap_overlap': QgsProcessing.TEMPORARY_OUTPUT,
            'Result': parameters['Eindresultaat'],
            'Stats_drinkwater': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_plancap': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_ve': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindresultaat'] = outputs['Stap3BerekenAfvalwaterprognose']['Result']

        # this is needed to rename layers. looks funky, but works!
        for key in results:
            feedback.pushInfo("rename layer to {}".format(key))
            globals()[key] = Renamer(key) #create unique global renamer instances
            context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[key])

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