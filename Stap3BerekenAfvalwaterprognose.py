"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""
import processing
from qgis.core import (QgsProcessing, 
                       QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProject)
from .custom_tools import rename_layers, default_inp_fields


class Stap3BerekenAfvalwaterprognose(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebiedenstats', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGT Inlooptabel', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputdrinkwater', 'Input Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input fields csv', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue='G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv'))
        self.addParameter(QgsProcessingParameterVectorLayer('inputplancap', 'input Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputves', "Input VE's", optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Result', 'result', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bgt_intersect', 'bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_joined_stats', 'Bemalingsgebieden_joined_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Exafw_per_bem_id', 'ExAFW_per_bem_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_pc_id', 'PLANCAP_PC_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stats_drinkwater', 'STATS_DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stats_ve', 'STATS_VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Meerdere_plancaps_in_bemalingsgebied', 'meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_in_meerdere_bemalingsgebieden', 'plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        parameters['inputfieldscsv'] = default_inp_fields
        QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        # let op: vanaf if parameters['bgtinlooptabel']: is het script afwijkend van model tbv optionaliteit bgt.
        feedback = QgsProcessingMultiStepFeedback(18, model_feedback)
        results = {}
        outputs = {}

        # koppel overige bronnen
        alg_params = {
            'input': parameters['bemalingsgebiedenstats'],
            'inputplancap': parameters['inputplancap'],
            'inputves': parameters['inputves'],
            'inputves (2)': parameters['inputdrinkwater'],
            'Bemalingsgebieden_joined_stats': parameters['Bemalingsgebieden_joined_stats'],
            'Exafw_per_bem_id': parameters['Exafw_per_bem_id'],
            'Meerdere_plancaps_in_bemalingsgebied': parameters['Meerdere_plancaps_in_bemalingsgebied'],
            'Plancap_in_meerdere_bemalingsgebieden': parameters['Plancap_in_meerdere_bemalingsgebieden'],
            'Plancap_pc_id': parameters['Plancap_pc_id'],
            'Stats_drinkwater': parameters['Stats_drinkwater'],
            'Stats_ve': parameters['Stats_ve']
        }
        outputs['KoppelOverigeBronnen'] = processing.run('GeoDynTools:koppel overige bronnen', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bemalingsgebieden_joined_stats'] = outputs['KoppelOverigeBronnen']['Bemalingsgebieden_joined_stats']
        results['Exafw_per_bem_id'] = outputs['KoppelOverigeBronnen']['Exafw_per_bem_id']
        results['Plancap_pc_id'] = outputs['KoppelOverigeBronnen']['Plancap_pc_id']
        results['Stats_drinkwater'] = outputs['KoppelOverigeBronnen']['Stats_drinkwater']
        results['Stats_ve'] = outputs['KoppelOverigeBronnen']['Stats_ve']
        results['Meerdere_plancaps_in_bemalingsgebied'] = outputs['KoppelOverigeBronnen']['Meerdere_plancaps_in_bemalingsgebied']
        results['Plancap_in_meerdere_bemalingsgebieden'] = outputs['KoppelOverigeBronnen']['Plancap_in_meerdere_bemalingsgebieden']

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

        # vervang alle None-waarden met 0 voor velden in lijst
        alg_params = {
            'inputlayer': outputs['CalcFieldsOnderbemaling03_obm']['Output_layer'],
            'veldenlijst': 'X_WON_ONBG;X_WON_GEB;X_VE_ONBG;X_VE_GEB;DWR_GEBIED;DWR_ONBG;PAR_RESULT;ZAK_RESULT;AW_21_24_G;AW_25_29_G;AW_30_39_G;AW_40_50_G;AW_21_24_O;AW_25_29_O;AW_30_39_O;AW_40_50_O;AantalPompen;AantalOverstorten;AantalDoorlaaten;AantalStrengen;AantalKnopen',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VervangAlleNonewaardenMet0VoorVeldenInLijst'] = processing.run('GeoDynTools:VervangNoneValuesMet0VoorVeldenlijst', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # calc fields '04_ber'
        alg_params = {
            'inputfields': parameters['inputfieldscsv'],
            'inputlayer': outputs['VervangAlleNonewaardenMet0VoorVeldenInLijst']['Output_layer'],
            'uittevoerenstapininputfields': '04_ber',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFields04_ber'] = processing.run('GeoDynTools:calc fields from csv input fields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
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

        feedback.setCurrentStep(7)
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

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # koppel bgtInlooptabel
        alg_params = {
            'input': outputs['CalcFields05_ber']['Output_layer'],
            'inputves (2)': parameters['bgtinlooptabel'],
            'Bgt_intersect': parameters['Bgt_intersect'],
            'Bgt_intersect_stats': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KoppelBgtinlooptabel'] = processing.run('GeoDynTools:koppel bgtInlooptabel', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bgt_intersect'] = outputs['KoppelBgtinlooptabel']['Bgt_intersect']

        feedback.setCurrentStep(9)
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

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # vervang alle None-waarden met 0 voor bgt velden
        alg_params = {
            'inputlayer': outputs['CalcFields06_bgt']['Output_layer'],
            'veldenlijst': 'HA_GEM_G;HA_HWA_G;HA_VGS_G;HA_VWR_G;HA_INF_G;HA_OPW_G;HA_MVD_G;HA_OBK_G;HA_BEM_G;HA_VER_G',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VervangAlleNonewaardenMet0VoorBgtVelden'] = processing.run('GeoDynTools:VervangNoneValuesMet0VoorVeldenlijst', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
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

        feedback.setCurrentStep(12)
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

        feedback.setCurrentStep(13)
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

        feedback.setCurrentStep(14)
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

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # vervang alle None-waarden met 0 voor POC
        alg_params = {
            'inputlayer': outputs['CalcFieldsOnderbemaling09_obm_1n']['Output_layer'],
            'veldenlijst': 'POC_O_M3_O;POC_O_M3_G;IN_DWA_POC',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VervangAlleNonewaardenMet0VoorPoc'] = processing.run('GeoDynTools:VervangNoneValuesMet0VoorVeldenlijst', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
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

        feedback.setCurrentStep(17)
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
        
        # --- this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            results, context, feedback = rename_layers(results, context, feedback)
 
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
