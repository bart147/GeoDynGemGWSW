"""
Model exported as python.
Name : koppel overige bronnen
Group : 
With QGIS : 32207
"""

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean,
                       QgsProject)
import processing
import string
import random


class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()
        
    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)


class KoppelOverigeBronnen(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('input', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSource('inputplancap', 'Input Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputves', "Input VE's", optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputves (2)', 'Input Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_joined_stats', 'Bemalingsgebieden_joined_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Meerdere_plancaps_in_bemalingsgebied', 'meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Plancap_in_meerdere_bemalingsgebieden', 'plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_joined_stats', 'Bemalingsgebieden_joined_stats', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stats_drinkwater', 'STATS_DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stats_ve', 'STATS_VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stats_plancap', 'STATS_PLANCAP', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(13, model_feedback)
        results = {}
        outputs = {}

        # Conditional has ve
        alg_params = {
        }
        outputs['ConditionalHasVe'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) Drinkwater
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['input'],
            'JOIN': parameters['inputves (2)'],
            'JOIN_FIELDS': ['par_result','zak_result'],
            'PREDICATE': [0],  # intersects
            'SUMMARIES': [0,5],  # count,sum
            'OUTPUT': parameters['Stats_drinkwater']
        }
        outputs['JoinAttributesByLocationSummaryDrinkwater'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stats_drinkwater'] = outputs['JoinAttributesByLocationSummaryDrinkwater']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        

        # Join attributes SUM Drinkwater
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['par_result_sum','zak_result_sum','par_result_count','zak_result_count'],
            'FIELD_2': 'BEM_ID',
            'INPUT': parameters['input'],
            'INPUT_2': outputs['JoinAttributesByLocationSummaryDrinkwater']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesSumDrinkwater'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': parameters['inputplancap'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Field calc PC_ID
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'PC_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': '$id',
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalcPc_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) meerdere plancaps per bemalingsgebied
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['input'],
            'JOIN': outputs['FieldCalcPc_id']['OUTPUT'],
            'JOIN_FIELDS': ['PC_ID'],
            'PREDICATE': [0],  # intersects
            'SUMMARIES': [0],  # count
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryMeerderePlancapsPerBemalingsgebied'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) plancap in meerdere bemalingsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalcPc_id']['OUTPUT'],
            'JOIN': parameters['input'],
            'JOIN_FIELDS': ['BEM_ID'],
            'PREDICATE': [0],  # intersects
            'SUMMARIES': [0],  # count
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryPlancapInMeerdereBemalingsgebieden'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by Count > 2
        alg_params = {
            'FIELD': 'BEM_ID_count',
            'INPUT': outputs['JoinAttributesByLocationSummaryPlancapInMeerdereBemalingsgebieden']['OUTPUT'],
            'OPERATOR': 3,  # ≥
            'VALUE': '2',
            'OUTPUT': parameters['Plancap_in_meerdere_bemalingsgebieden']
        }
        outputs['ExtractByCount2'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Plancap_in_meerdere_bemalingsgebieden'] = outputs['ExtractByCount2']['OUTPUT']

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by Count > 2
        alg_params = {
            'FIELD': 'PC_ID_count',
            'INPUT': outputs['JoinAttributesByLocationSummaryMeerderePlancapsPerBemalingsgebied']['OUTPUT'],
            'OPERATOR': 3,  # ≥
            'VALUE': '2',
            'OUTPUT': parameters['Meerdere_plancaps_in_bemalingsgebied']
        }
        outputs['ExtractByCount2'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Meerdere_plancaps_in_bemalingsgebied'] = outputs['ExtractByCount2']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) stats_plancap
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['input'],
            'JOIN': outputs['FieldCalcPc_id']['OUTPUT'],
            'JOIN_FIELDS': ['ExAFW_2124','ExAFW_2529','ExAFW_3039','ExAFW_4050'],
            'PREDICATE': [0],  # intersects
            'SUMMARIES': [0,5],  # count,sum
            'OUTPUT': parameters['Stats_plancap']
        }
        outputs['JoinAttributesByLocationSummaryStats_plancap'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stats_plancap'] = outputs['JoinAttributesByLocationSummaryStats_plancap']['OUTPUT']

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes Plancap
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['ExAFW_2124_sum','ExAFW_2529_sum','ExAFW_3039_sum','ExAFW_4050_sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesSumDrinkwater']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocationSummaryStats_plancap']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesPlancap'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}
                
        if parameters['inputves']:
            # Join attributes by location (summary) VE's
            alg_params = {
                'DISCARD_NONMATCHING': False,
                'INPUT': parameters['input'],
                'JOIN': parameters['inputves'],
                'JOIN_FIELDS': ['GRONDSLAG'],
                'PREDICATE': [0],  # intersects
                'SUMMARIES': [0,5],  # count,sum
                'OUTPUT': parameters['Stats_ve']
            }
            outputs['JoinAttributesByLocationSummaryVes'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Stats_ve'] = outputs['JoinAttributesByLocationSummaryVes']['OUTPUT']

            feedback.setCurrentStep(4)
            if feedback.isCanceled():
                return {}

            # Join attributes VE
            alg_params = {
                'DISCARD_NONMATCHING': False,
                'FIELD': 'BEM_ID',
                'FIELDS_TO_COPY': ['GRONDSLAG_count','GRONDSLAG_sum'],
                'FIELD_2': 'BEM_ID',
                'INPUT': outputs['JoinAttributesPlancap']['OUTPUT'],
                'INPUT_2': outputs['JoinAttributesByLocationSummaryVes']['OUTPUT'],
                'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
                'PREFIX': '',
                'OUTPUT': parameters['Bemalingsgebieden_joined_stats']
            }
            outputs['JoinAttributesVe'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Bemalingsgebieden_joined_stats'] = outputs['JoinAttributesVe']['OUTPUT']

            feedback.setCurrentStep(14)
            if feedback.isCanceled():
                return {}
        else:
            # Raise warning
            alg_params = {
                'CONDITION': '',
                'MESSAGE': '"No source for VE\'s selected, skip join" '
            }
            outputs['RaiseWarning'] = processing.run('native:raisewarning', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

            feedback.setCurrentStep(2)
            if feedback.isCanceled():
                return {}

            # Add field GRONDSLAG_sum
            alg_params = {
                'FIELD_LENGTH': 10,
                'FIELD_NAME': 'GRONDSLAG_sum',
                'FIELD_PRECISION': 0,
                'FIELD_TYPE': 0,  # Integer
                'INPUT': outputs['JoinAttributesPlancap']['OUTPUT'],
                'OUTPUT': parameters['Bemalingsgebieden_joined_stats']
            }
            outputs['AddFieldGrondslag_sum'] = processing.run('native:addfieldtoattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Bemalingsgebieden_joined_stats'] = outputs['AddFieldGrondslag_sum']['OUTPUT']

        
        # --- this is needed to rename layers. looks funky, but works!
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
        return 'koppel overige bronnen'

    def displayName(self):
        return 'koppel overige bronnen'

    def group(self):
        return 'geodyn tools'

    def groupId(self):
        return 'geodyn_tools'

    def createInstance(self):
        return KoppelOverigeBronnen()
