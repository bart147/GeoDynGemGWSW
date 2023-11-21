"""
Model exported as python.
Name : GeoDyn GWSW stap 3 - Bepalen bovenstroomse gebieden en afvalwateraanbod
Group : GeoDyn GWSW
With QGIS : 32805
"""
import os
import processing
from qgis.core import (QgsProcessing, 
                       QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingUtils,
                       QgsProject,
                       QgsVectorLayer,
                       QgsProcessingParameterNumber)
from .custom_tools import rename_layers, default_inp_fields, default_layer, QgsProcessingAlgorithmPost, cmd_folder


class GeodynGwswStap3BepalenBovenstroomseGebiedenEnAfvalwateraanbod(QgsProcessingAlgorithmPost):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_1_afvoerpunten', 'Resultaat stap 1: Afvoerpunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('Resultaat_stap_1_afvoerpunten')))
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat stap 2: Rioleringsgebieden met afvalwateraanbod uit eigen gebied', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied')))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_3_afvoerpunten_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd', 'Resultaat_stap_3_Afvoerpunten_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_3_rioleringsgebieden_toekomstige_situatie_extra_afvalwateraanbod_tot_2050', 'Resultaat_stap_3_Rioleringsgebieden_toekomstige_situatie_extra_afvalwateraanbod_tot_2050', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_3_rioleringsgebieden_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd', 'Resultaat_stap_3_Rioleringsgebieden_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
      
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_1_afvoerpunten', 'Resultaat stap 1: Afvoerpunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('ResultaatStap1Afvoerpunten')))
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat stap 2: Rioleringsgebieden met afvalwateraanbod uit eigen gebied', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('ResultaatStap2RioleringsgebiedenMetAfvalwateraanbodUitEigenGebied')))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap3AfvoerpuntenRioleringsgebiedenKenmerkenSommatieAfvalwateraanbodBergingVultijdLedigingstijd', 'Resultaat stap 3: Afvoerpunten rioleringsgebieden kenmerken, sommatie afvalwateraanbod, berging, vultijd, ledigingstijd', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Onderbemaling_test', 'onderbemaling_test', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('TussenresultaatHuidigeSituatieAfvalwateraanbod', 'Tussenresultaat: huidige situatie afvalwateraanbod', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap3RioleringsgebiedenToekomstigeSituatieAfvalwateraanbod2050', 'Resultaat stap 3: Rioleringsgebieden toekomstige situatie afvalwateraanbod 2050', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap3RioleringsgebiedenSommatieAfvalwateraanbodBergingVultijdLedigingstijd', 'Resultaat stap 3: Rioleringsgebieden sommatie afvalwateraanbod, berging, vultijd, ledigingstijd', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
      
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        self.result_folder = parameters['result_folder']

        feedback = QgsProcessingMultiStepFeedback(60, model_feedback)
        results = {}
        outputs = {}

        # Create spatial index
        alg_params = {
            'INPUT': parameters['resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied']
        }
        outputs['CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Retain fields US_BEM_ID
        alg_params = {
            'FIELDS': ['US_BEM_ID'],
            'INPUT': parameters['resultaat_stap_1_afvoerpunten'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsUs_bem_id'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator stap3_datum
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'stap3_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['CreateSpatialIndex']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStap3_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator N1_onderbemalingen
        # Bovenstroomse BEM_ID's die direct op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 1000,
            'FIELD_NAME': 'N1_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Onderbemalingen niveau 1"',
            'INPUT': outputs['FieldCalculatorStap3_datum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorN1_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator Onderbemalingen
        # Bovenstroomse BEM_ID's die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 1000,
            'FIELD_NAME': 'Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Onderbemalingen alles niveaus"',
            'INPUT': outputs['FieldCalculatorN1_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorOnderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator N1_afvoerpunten_onderbemalingen
        # Bovenstroomse afvoerpunten/rioolgemalen die direct op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 1000,
            'FIELD_NAME': 'N1_afvoerpunten_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Afvoerpunten onderbemalingen niveau 1"',
            'INPUT': outputs['FieldCalculatorOnderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorN1_afvoerpunten_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvoerpunten_onderbemalingen
        # Bovenstroomse afvoerpunten/rioolgemalen die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 1000,
            'FIELD_NAME': 'Afvoerpunten_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Afvoerpunten ondrbemalingen"',
            'INPUT': outputs['FieldCalculatorN1_afvoerpunten_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerpunten_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorAfvoerpunten_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator N1_aantal_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'N1_aantal_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorAantal_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorN1_aantal_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator X_OPPOMP
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'X_OPPOMP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorN1_aantal_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorX_oppomp'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID_afleveringspunt
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'BEM_ID_afleveringspunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorX_oppomp']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBem_id_afleveringspunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator Naam_afleveringspunt
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Naam_afleveringspunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorBem_id_afleveringspunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNaam_afleveringspunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Field calculator PC_IDs_onderbemalingen
        # Bouwprojecten in bovenstroomse rioleringsgebieden die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 500,
            'FIELD_NAME': 'PC_IDs_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorNaam_afleveringspunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPc_ids_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # lis2graph
        alg_params = {
            'inputlayer': outputs['FieldCalculatorPc_ids_onderbemalingen']['OUTPUT'],
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Lis2graph'] = processing.run('GeoDynTools:lis2graph', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_GEM_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_GEM_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['Lis2graph']['Output_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_gem_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_VGS_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_VGS_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_gem_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_vgs_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_GEM+VGS_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_GEM+VGS_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorPoc_vgs_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_gemvgs_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_BAG_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'DWA_BAG_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_gemvgs_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_bag_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculator BAG_count_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'BAG_count_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("DWA_BAG_onderbemalingen_m3h"/(12/1000),0)',
            'INPUT': outputs['FieldCalculatorDwa_bag_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBag_count_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Field calculator PAR_DRINKWATER_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'PAR_DRINKWATER_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorBag_count_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPar_drinkwater_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Field calculator ZAK_DRINKWATER_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ZAK_DRINKWATER_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPar_drinkwater_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorZak_drinkwater_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Field calculator TOT_DRINKWATER_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'TOT_DRINKWATER_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorZak_drinkwater_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTot_drinkwater_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator VE_onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'VE_onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorTot_drinkwater_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVe_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator VE_onderbemalingen_count
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'VE_onderbemalingen_count',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("VE_onderbemalingen_m3h"/(12/1000),0)',
            'INPUT': outputs['FieldCalculatorVe_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVe_onderbemalingen_count'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator ExAFW_2124_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ExAFW_2124_onderbemalingen',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorVe_onderbemalingen_count']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExafw_2124_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator ExAFW_2529_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ExAFW_2529_onderbemalingen',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExafw_2124_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExafw_2529_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator ExAFW_3039_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ExAFW_3039_onderbemalingen',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExafw_2529_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExafw_3039_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Field calculator ExAFW_4050_onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ExAFW_4050_onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExafw_3039_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExafw_4050_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # calc fields upstream
        alg_params = {
            'id_veld': 'BEM_ID',
            'inputlayer': outputs['FieldCalculatorExafw_4050_onderbemalingen']['OUTPUT'],
            'ontvangt_van': 'Onderbemalingen',
            'veldenlijst': 'POC_GEM_m3h;POC_GEM_onderbemalingen_m3h,POC_VGS_m3h;POC_VGS_onderbemalingen_m3h,DWA_BAG_m3h;DWA_BAG_onderbemalingen_m3h,PAR_DRINKWATER_m3h;PAR_DRINKWATER_onderbemalingen_m3h,ZAK_DRINKWATER_m3h;ZAK_DRINKWATER_onderbemalingen_m3h,TOT_DRINKWATER_m3h;TOT_DRINKWATER_onderbemalingen_m3h,VE_m3h;VE_onderbemalingen_m3h,ExAFW_2124;ExAFW_2124_onderbemalingen,ExAFW_3039;ExAFW_3039_onderbemalingen,ExAFW_4050;ExAFW_4050_onderbemalingen',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFieldsUpstream'] = processing.run('GeoDynTools:calc fields upstream', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_POC_GEM_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_POC_GEM_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_GEM_m3h"+"POC_GEM_onderbemalingen_m3h",2)',
            'INPUT': outputs['CalcFieldsUpstream']['Output_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_poc_gem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_POC_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_POC_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_VGS_m3h"+"POC_VGS_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_poc_gem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_poc_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_POC_GEM+VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_POC_GEM+VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_GEM_m3h"+"POC_VGS_m3h"+"POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_poc_vgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_poc_gemvgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_DWA_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("DWA_BAG_m3h"+"DWA_BAG_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_poc_gemvgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_dwa_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_BAG_count
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_BAG_count',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(("DWA_BAG_m3h"+"DWA_BAG_onderbemalingen_m3h")/(12/1000),0)',
            'INPUT': outputs['FieldCalculatorSom_dwa_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_bag_count'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_PAR_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_PAR_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("PAR_DRINKWATER_m3h"+"PAR_DRINKWATER_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_bag_count']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_par_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_ZAK_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_ZAK_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("ZAK_DRINKWATER_m3h"+"ZAK_DRINKWATER_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_par_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_zak_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_TOT_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_TOT_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("TOT_DRINKWATER_m3h"+"TOT_DRINKWATER_onderbemalingen_m3h" ,2)',
            'INPUT': outputs['FieldCalculatorSom_zak_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_tot_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_VE_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("VE_m3h"+"VE_onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_tot_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_ve_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_VE_count
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_VE_count',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("VE_count"+"VE_onderbemalingen_count",0)',
            'INPUT': outputs['FieldCalculatorSom_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_ve_count'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_ExAFW_2124
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_ExAFW_2124',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("ExAFW_2124"+"ExAFW_2124_onderbemalingen",2)',
            'INPUT': outputs['FieldCalculatorSom_ve_count']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_exafw_2124'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_ExAFW_2529
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_ExAFW_2529',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("ExAFW_2529"+"ExAFW_2529_onderbemalingen",2)',
            'INPUT': outputs['FieldCalculatorSom_exafw_2124']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_exafw_2529'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_ExAFW_3039
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_ExAFW_3039',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("ExAFW_3039"+"ExAFW_3039_onderbemalingen",2)',
            'INPUT': outputs['FieldCalculatorSom_exafw_2529']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_exafw_3039'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_ExAFW_4050
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SOM_ExAFW_4050',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("ExAFW_4050"+"ExAFW_4050_onderbemalingen",2)',
            'INPUT': outputs['FieldCalculatorSom_exafw_3039']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_exafw_4050'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_DWA_BAG_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_DWA_BAG_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorSom_exafw_4050']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_drinkwater_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_TOT_DRINKWATER_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_TOT_DRINKWATER_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_VE_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_VE_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_VE_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_ve_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Field calculator mm_Berging
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'mm_Berging',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(("M3_StelselBerging"/((("GEM_ha"+"VGS_ha")*10000)+(("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h")/(0.7/1000))))*1000,2)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMm_berging'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Field calculator MAX_VULTIJD_DWA_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MAX_VULTIJD_DWA_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_TOT_DRINKWATER_m3h" = 0 AND "SOM_VE_m3h" = 0,\r\nround("M3_StelselBerging"/"SOM_DWA_BAG_m3h",2),\r\nif("SOM_TOT_DRINKWATER_m3h" > 0 AND "SOM_VE_m3h" = 0,\r\nround("M3_StelselBerging"/min("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h"),2),\r\nif("SOM_TOT_DRINKWATER_m3h" = 0 AND "SOM_VE_m3h" > 0,\r\nround("M3_StelselBerging"/min("SOM_DWA_BAG_m3h","SOM_VE_m3h"),2),\r\nif("SOM_TOT_DRINKWATER_m3h" > 0 AND "SOM_VE_m3h" > 0,\r\nround("M3_StelselBerging"/min("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h","SOM_VE_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorMm_berging']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMax_vultijd_dwa_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Field calculator MIN_VULTIJD_DWA_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MIN_VULTIJD_DWA_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("M3_StelselBerging"/max("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h","SOM_VE_m3h"),2)',
            'INPUT': outputs['FieldCalculatorMax_vultijd_dwa_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMin_vultijd_dwa_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Field calculator MAX_LEDIGINGSTIJD_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MAX_LEDIGINGSTIJD_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("Afvalwateraanbod_obv_drinkwater_m3h" = 0 AND "Afvalwateraanbod_obv_VE_m3h" = 0,\r\nround("M3_StelselBerging"/"Afvalwateraanbod_obv_BAG_m3h",2),\r\nif("Afvalwateraanbod_obv_drinkwater_m3h" > 0 AND "Afvalwateraanbod_obv_VE_m3h" = 0,\r\nround("M3_StelselBerging"/min("Afvalwateraanbod_obv_BAG_m3h","Afvalwateraanbod_obv_drinkwater_m3h"),2),\r\nif("Afvalwateraanbod_obv_drinkwater_m3h" = 0 AND "Afvalwateraanbod_obv_VE_m3h" > 0,\r\nround("M3_StelselBerging"/min("Afvalwateraanbod_obv_BAG_m3h","Afvalwateraanbod_obv_VE_m3h"),2),\r\nif("Afvalwateraanbod_obv_drinkwater_m3h" > 0 AND "Afvalwateraanbod_obv_VE_m3h" > 0,\r\nround("M3_StelselBerging"/min("Afvalwateraanbod_obv_BAG_m3h","Afvalwateraanbod_obv_drinkwater_m3h","Afvalwateraanbod_obv_VE_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorMin_vultijd_dwa_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMax_ledigingstijd_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Field calculator MIN_LEDIGINGSTIJD_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MIN_LEDIGINGSTIJD_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("M3_StelselBerging"/max("Afvalwateraanbod_obv_BAG_m3h","Afvalwateraanbod_obv_drinkwater_m3h","Afvalwateraanbod_obv_VE_m3h"),2)',
            'INPUT': outputs['FieldCalculatorMax_ledigingstijd_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMin_ledigingstijd_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Field calculator MIN_POC_PRAKTIJK_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MIN_POC_PRAKTIJK_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("Pompcapaciteit"-max("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h","SOM_VE_m3h")-("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h"),2)',
            'INPUT': outputs['FieldCalculatorMin_ledigingstijd_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMin_poc_praktijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Field calculator MAX_POC_PRAKTIJK_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MAX_POC_PRAKTIJK_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_TOT_DRINKWATER_m3h" = 0 AND "SOM_VE_m3h" = 0,\r\nround("Pompcapaciteit"-"SOM_DWA_BAG_m3h"-("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h"),2),\r\n\r\nif("SOM_TOT_DRINKWATER_m3h" > 0 AND "SOM_VE_m3h" = 0,\r\nround("Pompcapaciteit"-min("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h")-("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h"),2),\r\n\r\nif("SOM_TOT_DRINKWATER_m3h" = 0 AND "SOM_VE_m3h" > 0,\r\nround("Pompcapaciteit"-min("SOM_DWA_BAG_m3h","SOM_VE_m3h")-("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h"),2),\r\n\r\nif("SOM_TOT_DRINKWATER_m3h" > 0 AND "SOM_VE_m3h" > 0,\r\nround("Pompcapaciteit"-min("SOM_DWA_BAG_m3h","SOM_TOT_DRINKWATER_m3h","SOM_VE_m3h")-("POC_GEM_onderbemalingen_m3h"+"POC_VGS_onderbemalingen_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorMin_poc_praktijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMax_poc_praktijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Field calculator MIN_POC_PRAKTIJK_mmh
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MIN_POC_PRAKTIJK_mmh',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(("MIN_POC_PRAKTIJK_m3h"/(("GEM_ha"+"VGS_ha")*10000))*1000,2)',
            'INPUT': outputs['FieldCalculatorMax_poc_praktijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMin_poc_praktijk_mmh'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Field calculator MAX_POC_PRAKTIJK_mmh
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MAX_POC_PRAKTIJK_mmh',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(("MAX_POC_PRAKTIJK_m3h"/(("GEM_ha"+"VGS_ha")*10000))*1000,2)',
            'INPUT': outputs['FieldCalculatorMin_poc_praktijk_mmh']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_3_rioleringsgebieden_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd']
        }
        outputs['FieldCalculatorMax_poc_praktijk_mmh'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_3_rioleringsgebieden_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd'] = outputs['FieldCalculatorMax_poc_praktijk_mmh']['OUTPUT']

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'US_BEM_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['RetainFieldsUs_bem_id']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorMax_poc_praktijk_mmh']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_BAG+PC_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_BAG+PC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_DWA_BAG_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_DWA_BAG_m3h"+"SOM_ExAFW_2124"+"SOM_ExAFW_2529"+"SOM_ExAFW_3039"+"SOM_ExAFW_4050",2),0)',
            'INPUT': outputs['FieldCalculatorMax_poc_praktijk_mmh']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_bagpc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_drinkwater+PC_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_drinkwater+PC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_TOT_DRINKWATER_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_TOT_DRINKWATER_m3h"+"SOM_ExAFW_2124"+"SOM_ExAFW_2529"+"SOM_ExAFW_3039"+"SOM_ExAFW_4050",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_bagpc_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwaterpc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_VE+PC_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_VE+PC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("SOM_VE_m3h">0,round("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"+"SOM_VE_m3h"+"SOM_ExAFW_2124"+"SOM_ExAFW_2529"+"SOM_ExAFW_3039"+"SOM_ExAFW_4050",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwaterpc_m3h']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_3_rioleringsgebieden_toekomstige_situatie_extra_afvalwateraanbod_tot_2050']
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_vepc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_3_rioleringsgebieden_toekomstige_situatie_extra_afvalwateraanbod_tot_2050'] = outputs['FieldCalculatorAfvalwateraanbod_obv_vepc_m3h']['OUTPUT']

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_BEM_ID_2
        # Data aan afvoerpunten plakken, omdat GWSW-kengetallen de kengetallen aan afvoerpunten hangt.
        alg_params = {
            'COLUMN': ['US_BEM_ID_2'],
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_3_afvoerpunten_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd']
        }
        outputs['DropFieldsUs_bem_id_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_3_afvoerpunten_sommatie_afvalwateraanbod_berging_vultijd_ledigingstijd'] = outputs['DropFieldsUs_bem_id_2']['OUTPUT']
        
        # --- this is needed to rename layers. looks funky, but works!
        if parameters.get('keepName', False): # skip Rename if parameter 'keepName' = True.
            feedback.pushInfo("keepName = True")
        else:
            #results, context, feedback = rename_layers(results, context, feedback)
            context.setLayersToLoadOnCompletion({})
            for key in results:
                self.final_layers[key] = QgsProcessingUtils.mapLayerFromString(results[key], context)        

        return results

    def name(self):
        return 'GeoDyn GWSW stap 3 - Bepalen bovenstroomse gebieden en afvalwateraanbod'

    def displayName(self):
        return 'GeoDyn GWSW stap 3 - Bepalen bovenstroomse gebieden en afvalwateraanbod'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return GeodynGwswStap3BepalenBovenstroomseGebiedenEnAfvalwateraanbod()        
