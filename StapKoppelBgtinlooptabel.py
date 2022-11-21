"""
Model exported as python.
Name : koppel bgtInlooptabel
Group : 
With QGIS : 32207
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class KoppelBgtinlooptabel(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('input', 'Bemalingsgebieden tbv stap 2', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputves (2)', 'BGT Inlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bgt_intersect', 'bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bgt_intersect_stats', 'bgt_intersect_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(33, model_feedback)
        results = {}
        outputs = {}

        # Intersection
        alg_params = {
            'INPUT': parameters['inputves (2)'],
            'INPUT_FIELDS': [''],
            'OVERLAY': parameters['input'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Add geometry attributes
        alg_params = {
            'CALC_METHOD': 0,  # Layer CRS
            'INPUT': outputs['Intersection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddGeometryAttributes'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator GEM_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'GEM_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"gemengd_riool"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['AddGeometryAttributes']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorGem_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator HWA_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'HWA_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"hemelwaterriool"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorGem_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorHwa_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator VGS_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'VGS_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"vgs_hemelwaterriool"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorHwa_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVgs_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator VWR_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'VWR_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"vuilwaterriool"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorVgs_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVwr_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Field calculator INF_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'INF_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"infiltratievoorziening"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorVwr_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorInf_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Field calculator OPW_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'OPW_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"open_water"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorInf_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorOpw_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator MVD_HA
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MVD_HA',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"maaiveld"/100 * "graad_verharding"/100 * "area"/10000',
            'INPUT': outputs['FieldCalculatorOpw_ha']['OUTPUT'],
            'OUTPUT': parameters['Bgt_intersect']
        }
        outputs['FieldCalculatorMvd_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bgt_intersect'] = outputs['FieldCalculatorMvd_ha']['OUTPUT']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by attribute MVD_HA > 0
        alg_params = {
            'FIELD': 'MVD_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeMvd_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by attribute INF_HA > 0
        alg_params = {
            'FIELD': 'INF_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeInf_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extract by attribute VWR_HA > 0
        alg_params = {
            'FIELD': 'VWR_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeVwr_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary)
        # Helaas, resultaat van deze join by location is onbetrouwbaar. :-( Dan maar Statistics by category met veel meer stappen...
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['input'],
            'JOIN': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'JOIN_FIELDS': ['GEM_HA','HWA_HA','VGS_HA','VWR_HA','INF_HA','OPW_HA','MVD_HA'],
            'PREDICATE': [0],  # intersects
            'SUMMARIES': [0,5],  # count,sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummary'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract by attribute VGS_HA > 0
        alg_params = {
            'FIELD': 'VGS_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeVgs_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Extract by attribute HWA_HA > 0
        alg_params = {
            'FIELD': 'HWA_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeHwa_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Extract by attribute GEM_HA > 0
        alg_params = {
            'FIELD': 'GEM_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeGem_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Extract by attribute OPW_HA > 0
        alg_params = {
            'FIELD': 'OPW_HA',
            'INPUT': outputs['FieldCalculatorMvd_ha']['OUTPUT'],
            'OPERATOR': 2,  # >
            'VALUE': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeOpw_ha0'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Statistics by categories INF_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeInf_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'INF_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesInf_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Statistics by categories VGS_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeVgs_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'VGS_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesVgs_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Statistics by categories HWA_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeHwa_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'HWA_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesHwa_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Statistics by categories MVD_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeMvd_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'MVD_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMvd_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Statistics by categories VWR_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeVwr_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'VWR_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesVwr_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Statistics by categories OPW_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeOpw_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'OPW_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesOpw_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Statistics by categories GEM_HA
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['ExtractByAttributeGem_ha0']['OUTPUT'],
            'VALUES_FIELD_NAME': 'GEM_HA',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesGem_ha'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Join attributes GEM_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': parameters['input'],
            'INPUT_2': outputs['StatisticsByCategoriesGem_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'GEM_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesGem_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Join attributes HWA_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesGem_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesHwa_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'HWA_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesHwa_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Join attributes VGS_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesHwa_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesVgs_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'VGS_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesVgs_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Join attributes VWR_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesVgs_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesVwr_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'VWR_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesVwr_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Join attributes INF_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesVwr_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesInf_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'INF_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesInf_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Join attributes OPW_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesInf_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesOpw_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'OPW_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesOpw_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Join attributes MVD_HA
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['count','sum'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesOpw_ha']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesMvd_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'MVD_HA_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesMvd_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator BGT_HA_TOT
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'BGT_HA_TOT',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'if ("GEM_HA_sum"  IS NOT Null, "GEM_HA_sum", 0) +\r\nif ("HWA_HA_sum"  IS NOT Null, "HWA_HA_sum", 0) +\r\nif ("VGS_HA_sum"  IS NOT Null, "VGS_HA_sum", 0) +\r\nif ("VWR_HA_sum"  IS NOT Null, "VWR_HA_sum", 0) +\r\nif ("INF_HA_sum"  IS NOT Null, "INF_HA_sum", 0) +\r\nif ("OPW_HA_sum"  IS NOT Null, "OPW_HA_sum", 0) +\r\nif ("MVD_HA_sum"  IS NOT Null, "MVD_HA_sum", 0)',
            'INPUT': outputs['JoinAttributesMvd_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBgt_ha_tot'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Add geometry attributes
        alg_params = {
            'CALC_METHOD': 0,  # Layer CRS
            'INPUT': outputs['FieldCalculatorBgt_ha_tot']['OUTPUT'],
            'OUTPUT': parameters['Bgt_intersect_stats']
        }
        outputs['AddGeometryAttributes'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bgt_intersect_stats'] = outputs['AddGeometryAttributes']['OUTPUT']
        return results

    def name(self):
        return 'koppel bgtInlooptabel'

    def displayName(self):
        return 'koppel bgtInlooptabel'

    def group(self):
        return 'geodyn tools'

    def groupId(self):
        return 'geodyn_tools'

    def createInstance(self):
        return KoppelBgtinlooptabel()
