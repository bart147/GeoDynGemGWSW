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
                       QgsProcessingParameterBoolean,
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


class Stap3BerekenAfvalwaterprognose(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebiedenstats', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGT Inlooptabel', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputdrinkwater', 'Input Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputplancap', 'input Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputves', "Input VE's", optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterBoolean('vesmeenemen', "VE's meenemen", defaultValue=False))
        self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input fields csv', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue=default_inp_fields))
        self.addParameter(QgsProcessingParameterFeatureSink('Result', 'result', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_overlap', 'Plancap_overlap', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        feedback = QgsProcessingMultiStepFeedback(17, model_feedback)
        results = {}
        outputs = {}

        # koppel overige bronnen
        alg_params = {
            ##'hasve': parameters['vesmeenemen'],
            'input': parameters['bemalingsgebiedenstats'],
            'inputplancap': parameters['inputplancap'],
            'inputves': parameters['inputves'],
            'inputves (2)': parameters['inputdrinkwater'],
            'Bemalingsgebieden_joined_stats': QgsProcessing.TEMPORARY_OUTPUT,
            'Plancap_overlap': parameters['Plancap_overlap'],
            'Stats_drinkwater': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_plancap': QgsProcessing.TEMPORARY_OUTPUT,
            'Stats_ve': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_params['keepName'] = True
        outputs['KoppelOverigeBronnen'] = processing.run('GeoDynTools:koppel overige bronnen', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Plancap_overlap'] = outputs['KoppelOverigeBronnen']['Plancap_overlap']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # add fields from csv input fields st2a
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['KoppelOverigeBronnen']['Bemalingsgebieden_joined_stats'],
            'uittevoerenstapininputfields': 'st2a',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddFieldsFromCsvInputFieldsSt2a'] = processing.run('GeoDynTools:add fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # calc fields '01_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['AddFieldsFromCsvInputFieldsSt2a']['Output_layer'],
            'uittevoerenstapininputfields': '01_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields01_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # calc fields onderbemaling '03_obm'
        alg_params = {
            'alleendirecteonderbemaling': False,
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields01_ber']['Output_layer'],
            'uittevoerenstapininputfields': '03_obm',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFieldsOnderbemaling03_obm'] = processing.run('GeoDynTools:calc fields onderbemaling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # calc fields '04_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFieldsOnderbemaling03_obm']['Output_layer'],
            'uittevoerenstapininputfields': '04_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields04_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # calc fields '04a_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields04_ber']['Output_layer'],
            'uittevoerenstapininputfields': '04a_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields04a_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # calc fields '05_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields04a_ber']['Output_layer'],
            'uittevoerenstapininputfields': '05_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields05_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # koppel bgtInlooptabel
        alg_params = {
            'input': outputs['CalcFields05_ber']['Output_layer'],
            'inputves (2)': parameters['bgtinlooptabel'],
            'Bgt_intersect': QgsProcessing.TEMPORARY_OUTPUT,
            'Bgt_intersect_stats': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KoppelBgtinlooptabel'] = processing.run('GeoDynTools:koppel bgtInlooptabel', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # calc fields '06_bgt'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['KoppelBgtinlooptabel']['Bgt_intersect_stats'],
            'uittevoerenstapininputfields': '06_bgt',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields06_bgt'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # vervang alle None-waarden met 0 voor bgt velden
        alg_params = {
            'inputlayer': outputs['CalcFields06_bgt']['Output_layer'],
            'veldenlijst': 'HA_GEM_G;HA_HWA_G;HA_VGS_G;HA_VWR_G;HA_INF_G;HA_OPW_G;HA_MVD_G;HA_OBK_G;HA_BEM_G;HA_VER_G',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VervangAlleNonewaardenMet0VoorBgtVelden'] = processing.run('GeoDynTools:VervangNoneValuesMet0VoorVeldenlijst', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # calc fields '07_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['VervangAlleNonewaardenMet0VoorBgtVelden']['Output_layer'],
            'uittevoerenstapininputfields': '07_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields07_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # calc fields '08_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields07_ber']['Output_layer'],
            'uittevoerenstapininputfields': '08_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields08_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # calc fields onderbemaling '09_obm'
        alg_params = {
            'alleendirecteonderbemaling': False,
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields08_ber']['Output_layer'],
            'uittevoerenstapininputfields': '09_obm',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFieldsOnderbemaling09_obm'] = processing.run('GeoDynTools:calc fields onderbemaling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # calc fields onderbemaling '09_obm_1n'
        alg_params = {
            'alleendirecteonderbemaling': True,
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFieldsOnderbemaling09_obm']['Output_layer'],
            'uittevoerenstapininputfields': '09_obm_1n',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFieldsOnderbemaling09_obm_1n'] = processing.run('GeoDynTools:calc fields onderbemaling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # vervang alle None-waarden met 0 voor POC
        alg_params = {
            'inputlayer': outputs['CalcFieldsOnderbemaling09_obm_1n']['Output_layer'],
            'veldenlijst': 'POC_O_M3_O;POC_O_M3_G;IN_DWA_POC',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VervangAlleNonewaardenMet0VoorPoc'] = processing.run('GeoDynTools:VervangNoneValuesMet0VoorVeldenlijst', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # calc fields '10_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['VervangAlleNonewaardenMet0VoorPoc']['Output_layer'],
            'uittevoerenstapininputfields': '10_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields10_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # calc fields '11_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['CalcFields10_ber']['Output_layer'],
            'uittevoerenstapininputfields': '11_ber',
            'Output_layer': parameters['Result']
        }
        outputs['CalcFields11_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Result'] = outputs['CalcFields11_ber']['Output_layer']

        # this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            for key in results:
                random_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
                global_key = key + "_" + random_string 
                feedback.pushInfo("rename layer to {}".format(key))
                globals()[global_key] = Renamer(key) #create unique global renamer instances
                context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[global_key])

        return results

    def name(self):
        return 'stap 3.) bereken afvalwaterprognose'

    def displayName(self):
        return 'stap 3.) bereken afvalwaterprognose'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Stap3BerekenAfvalwaterprognose()        
    

        # ----- copy this code before returning results in algorithm class 
        # this is needed to rename layers. looks funky, but works!
        # if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
        #     feedback.pushInfo("keepName = True")
        # else:
        #     for key in results:
        #         feedback.pushInfo("rename layer to {}".format(key))
        #         globals()[key] = Renamer(key) #create unique global renamer instances
        #         context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[key])