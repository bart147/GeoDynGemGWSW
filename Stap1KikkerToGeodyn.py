"""
Model exported as python.
Name : GWSW Geodyn - stap 1 met rioolstelsel
Group : Geodyn cheat
With QGIS : 32207
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProject
import processing
from .custom_tools import rename_layers

        
class Stap1KikkerToGeodyn(QgsProcessingAlgorithm):
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebieden', 'bemalingsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('kikkerlijnen', 'Kikker_lijnen', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('kikkerpunten', 'Kikker_punten', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_tbv_stap2_kikker', 'Bemalingsgebieden_tbv_stap2_kikker', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebiedsgegevens_punt_tbv_stap2_kikker', 'Gebiedsgegevens_punt_tbv_stap2_kikker', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebiedsgegevens_lijn_tbv_stap2_kikker', 'Gebiedsgegevens_lijn_tbv_stap2_kikker', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        QgsProject.instance().reloadAllLayers() 
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Fix geometries BEMALINGSGEBIEDEN
        alg_params = {
            'INPUT': parameters['bemalingsgebieden'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesBemalingsgebieden'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': "'BEM' || lpad( $id ,3,0)",
            'INPUT': outputs['FixGeometriesBemalingsgebieden']['OUTPUT'],
            'OUTPUT': parameters['Bemalingsgebieden_tbv_stap2_kikker']
        }
        outputs['FieldCalculatorBem_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bemalingsgebieden_tbv_stap2_kikker'] = outputs['FieldCalculatorBem_id']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Retain fields lijnen
        alg_params = {
            'FIELDS': ['NUMMER','VAN_KNOOPN','NAAR_KNOOP','TTOTAAL_M3'],
            'INPUT': parameters['kikkerlijnen'],
            'OUTPUT': parameters['Gebiedsgegevens_lijn_tbv_stap2_kikker']
        }
        outputs['RetainFieldsLijnen'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebiedsgegevens_lijn_tbv_stap2_kikker'] = outputs['RetainFieldsLijnen']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['kikkerpunten'],
            'JOIN': parameters['bemalingsgebieden'],
            'JOIN_FIELDS': [''],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Retain fields punten
        alg_params = {
            'FIELDS': ['BEM_ID','BEM_ID_SP','BERGING_M3','POMPEN_ST','OVERSTORT_','DOORLAAT_S','NUMMER','NAAM','VAN_KNOOPN','NAAR_KNOOP','CAP_INST_M','LAAGSTE_OS','STRENGEN_S','KNOPEN_ST'],
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsPunten'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculater BEM_ID_SP
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'BEM_ID_SP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': '"BEM_ID"',
            'INPUT': outputs['RetainFieldsPunten']['OUTPUT'],
            'OUTPUT': parameters['Gebiedsgegevens_punt_tbv_stap2_kikker']
        }
        outputs['FieldCalculaterBem_id_sp'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebiedsgegevens_punt_tbv_stap2_kikker'] = outputs['FieldCalculaterBem_id_sp']['OUTPUT']

        # --- this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            results, context, feedback = rename_layers(results, context, feedback)
 
        return results

    def name(self):
        return 'stap 1.) Kikker to Geodyn'

    def displayName(self):
        return 'stap 1.) Kikker to Geodyn'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Stap1KikkerToGeodyn()
