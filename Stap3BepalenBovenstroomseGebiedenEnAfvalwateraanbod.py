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
from .custom_tools import default_inp_fields, default_layer, QgsProcessingAlgorithmPost, cmd_folder


class GeodynGwswStap3BepalenBovenstroomseGebiedenEnAfvalwateraanbod(QgsProcessingAlgorithmPost):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerboom', 'Resultaat_Stap1_Afvoerboom', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('resultaat_stap1_afvoerboom')))
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerpunten', 'Resultaat_Stap1_Afvoerpunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('resultaat_stap1_afvoerpunten')))
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerrelatie', 'Resultaat_Stap1_Afvoerrelatie', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('resultaat_stap1_afvoerrelatie')))
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat_stap_2_Rioleringsgebieden_Met_Afvalwateraanbod_Uit_Eigen_Gebied', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied')))
        self.addParameter(QgsProcessingParameterFeatureSink('CalcFieldsUpstream', 'calc fields upstream', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Lis2graph', 'lis2graph', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_afvoerrelatie', 'Resultaat_Stap3_Rioleringsgebieden_Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_afvoerboom', 'Resultaat_Stap3_Rioleringsgebieden_Afvoerboom', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_afvoerpunten_kengetallen', 'Resultaat_Stap3_Afvoerpunten_Kengetallen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit', 'Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bouwprojecten_ids', 'Bouwprojecten_IDs', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_kengetallen', 'Resultaat_Stap3_Rioleringsgebieden_Kengetallen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('CalcFieldsUpstreamInput', 'calc fields upstream input', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Calc_upstream_poc_praktijk_input', 'calc_upstream_POC_praktijk_input', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Retained_fields_for_testing_poc_calculation', 'retained_fields_for_testing_poc_calculation', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))        

        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerboom', 'Resultaat_Stap1_Afvoerboom', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('resultaat_stap1_afvoerboom')))
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerpunten', 'Resultaat_Stap1_Afvoerpunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('resultaat_stap1_afvoerpunten')))
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_afvoerrelatie', 'Resultaat_Stap1_Afvoerrelatie', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('resultaat_stap1_afvoerrelatie')))
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat_stap_2_Rioleringsgebieden_Met_Afvalwateraanbod_Uit_Eigen_Gebied', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied')))
        # self.addParameter(QgsProcessingParameterFeatureSink('CalcFieldsUpstream', 'calc fields upstream', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Lis2graph', 'lis2graph', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_afvoerrelatie', 'Resultaat_Stap3_Rioleringsgebieden_Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_afvoerboom', 'Resultaat_Stap3_Rioleringsgebieden_Afvoerboom', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_afvoerpunten_kengetallen', 'Resultaat_Stap3_Afvoerpunten_Kengetallen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit', 'Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Bouwprojecten_ids', 'Bouwprojecten_IDs', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap3_rioleringsgebieden_kengetallen', 'Resultaat_Stap3_Rioleringsgebieden_Kengetallen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('CalcFieldsUpstreamInput', 'calc fields upstream input', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Retained_fields_for_testing_poc_calculation', 'retained_fields_for_testing_poc_calculation', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Calc_upstream_poc_praktijk_input', 'calc_upstream_POC_praktijk_input', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))        
                
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        self.result_folder = parameters['result_folder']

        feedback = QgsProcessingMultiStepFeedback(85, model_feedback)
        results = {}
        outputs = {}

        # Field calculator Afvoerrelatie Stap3_datum
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Stap3_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': parameters['resultaat_stap1_afvoerrelatie'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerrelatieStap3_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Retain fields Bemalingsgebied_ID_Afvoerpunt
        alg_params = {
            'FIELDS': ['Bemalingsgebied_ID_Afvoerpunt'],
            'INPUT': parameters['resultaat_stap1_afvoerpunten'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsBemalingsgebied_id_afvoerpunt'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # retainfields Resultaat_Stap1_Afvoerrelatie
        alg_params = {
            'inputlayer': outputs['FieldCalculatorAfvoerrelatieStap3_datum']['OUTPUT'],
            'veldenlijst': 'Rioolgemaal;Beginpunt_Afvoerrelatie;Eindpunt_Afvoerrelatie;Bemalingsgebied_ID_Afvoerpunt;Bemalingsgebied_ID_Lozingspunt',
            'Output_layer': parameters['Resultaat_stap3_rioleringsgebieden_afvoerrelatie']
        }
        outputs['RetainfieldsResultaat_stap1_afvoerrelatie'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap3_rioleringsgebieden_afvoerrelatie'] = outputs['RetainfieldsResultaat_stap1_afvoerrelatie']['Output_layer']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Create spatial index
        alg_params = {
            'INPUT': parameters['resultaat_stap_2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied']
        }
        outputs['CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvoerboom Stap3_datum
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Stap3_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': parameters['resultaat_stap1_afvoerboom'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerboomStap3_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # retainfields Resultaat_Stap1_Afvoerboom
        alg_params = {
            'inputlayer': outputs['FieldCalculatorAfvoerboomStap3_datum']['OUTPUT'],
            'veldenlijst': 'Rioolgemaal;Beginpunt_Afvoerrelatie;Eindpunt_Afvoerrelatie;Bemalingsgebied_ID_Afvoerpunt;Bemalingsgebied_ID_Lozingspunt',
            'Output_layer': parameters['Resultaat_stap3_rioleringsgebieden_afvoerboom']
        }
        outputs['RetainfieldsResultaat_stap1_afvoerboom'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap3_rioleringsgebieden_afvoerboom'] = outputs['RetainfieldsResultaat_stap1_afvoerboom']['Output_layer']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Field calculator Stap3_datum
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Stap3_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['CreateSpatialIndex']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStap3_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(if("POC_Theorie_Totaal_m3h" IS NOT NULL AND "POC_Theorie_Totaal_m3h" > 0, if("Afvoercapaciteit_m3h" IS NOT NULL,"Afvoercapaciteit_m3h",NULL) ,"DWA_BAG_m3h"),2)',
            'INPUT': outputs['FieldCalculatorStap3_datum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Eigen_gebied_max_afvalwateraanbod_praktijk_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_Drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_Drinkwater_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(if("POC_Theorie_Totaal_m3h" IS NOT NULL AND "POC_Theorie_Totaal_m3h" > 0, if("Afvoercapaciteit_m3h" IS NOT NULL,"Afvoercapaciteit_m3h",NULL) ,"Drinkwater_Totaal_m3h"),2)',
            'INPUT': outputs['Eigen_gebied_max_afvalwateraanbod_praktijk_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEigen_gebied_max_afvalwateraanbod_praktijk_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_VE_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(if("POC_Theorie_Totaal_m3h" IS NOT NULL AND "POC_Theorie_Totaal_m3h" > 0, if("Afvoercapaciteit_m3h" IS NOT NULL,"Afvoercapaciteit_m3h",NULL) ,"DWA_VEs_m3h"),2)',
            'INPUT': outputs['FieldCalculatorEigen_gebied_max_afvalwateraanbod_praktijk_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEigen_gebied_max_afvalwateraanbod_praktijk_obv_ve_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Field calculator Onderbemalingsgeb_IDs_1_Niveau_Diep
        # Bovenstroomse BEM_ID's die direct op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Onderbemalingsgeb_IDs_1_Niveau_Diep',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorEigen_gebied_max_afvalwateraanbod_praktijk_obv_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorOnderbemalingsgeb_ids_1_niveau_diep'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator Onderbemalingsgebied_IDs
        # Bovenstroomse BEM_ID's die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Onderbemalingsgebied_IDs',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '"Onderbemalingsgebied_IDs"',
            'INPUT': outputs['FieldCalculatorOnderbemalingsgeb_ids_1_niveau_diep']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorOnderbemalingsgebied_ids'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvoerpunten_1_Niveau_Diep
        # Bovenstroomse afvoerpunten/rioolgemalen die direct op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvoerpunten_1_Niveau_Diep',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '"Afvoerpunten_1_Niveau_Diep"',
            'INPUT': outputs['FieldCalculatorOnderbemalingsgebied_ids']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerpunten_1_niveau_diep'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvoerpunten_Van_Onderbemalingen
        # Bovenstroomse afvoerpunten/rioolgemalen die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvoerpunten_Van_Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '"Afvoerpunten_Van_Onderbemalingen"',
            'INPUT': outputs['FieldCalculatorAfvoerpunten_1_niveau_diep']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerpunten_van_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_Onderbemalingen_1_Niveau_Diep
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_Onderbemalingen_1_Niveau_Diep',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorAfvoerpunten_van_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_onderbemalingen_1_niveau_diep'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_Onderbemalingen 
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorAantal_onderbemalingen_1_niveau_diep']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_Keer_Oppompen_Tot_En_Met_Afleverpunt
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_Keer_Oppompen_Tot_En_Met_Afleverpunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '0',
            'INPUT': outputs['FieldCalculatorAantal_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_keer_oppompen_tot_en_met_afleverpunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Field calculator Rioleringsgebied_ID_Overnamepunt
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Rioleringsgebied_ID_Overnamepunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorAantal_keer_oppompen_tot_en_met_afleverpunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorRioleringsgebied_id_overnamepunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculator Naam_Overnamepunt
        # Deze wordt nog niet bepaald.Kan eventueel een join zijn op basis van rioleringsgebied_ID
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Naam_Overnamepunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorRioleringsgebied_id_overnamepunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorNaam_overnamepunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Field calculator Bouwprojecten_IDs_Onderbemalingen
        # Bouwprojecten in bovenstroomse rioleringsgebieden die direct of indirect op rioleringsgebied lozen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Bouwprojecten_IDs_Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': '""',
            'INPUT': outputs['FieldCalculatorNaam_overnamepunt']['OUTPUT'],
            'OUTPUT': parameters['Bouwprojecten_ids']
        }
        outputs['FieldCalculatorBouwprojecten_ids_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bouwprojecten_ids'] = outputs['FieldCalculatorBouwprojecten_ids_onderbemalingen']['OUTPUT']

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # lis2graph
        # Onderbemalingsvelden worden hier gevuld.
        alg_params = {
            'inputlayer': outputs['FieldCalculatorBouwprojecten_ids_onderbemalingen']['OUTPUT'],
            'Output_layer': parameters['Lis2graph']
        }
        outputs['Lis2graph'] = processing.run('GeoDynTools:lis2graph', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lis2graph'] = outputs['Lis2graph']['Output_layer']

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_BAG_Onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'DWA_BAG_Onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['Lis2graph']['Output_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_bag_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Part_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Drinkwater_Part_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorDwa_bag_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_part_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Zak_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Drinkwater_Zak_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorDrinkwater_part_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_zak_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Totaal_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Drinkwater_Totaal_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorDrinkwater_zak_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_totaal_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_VEs_Onderbemalingen_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'DWA_VEs_Onderbemalingen_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorDrinkwater_totaal_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_ves_onderbemalingen_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_VEs_Onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_VEs_Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("DWA_VEs_Onderbemalingen_m3h"/(12/1000),0)',
            'INPUT': outputs['FieldCalculatorDwa_ves_onderbemalingen_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_ves_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_Onderbem_2124_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Extra_DWA_Periode_Onderbem_2124_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorAantal_ves_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_onderbem_2124_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_Onderbem_2529_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Extra_DWA_Periode_Onderbem_2529_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_onderbem_2124_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_onderbem_2529_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_Onderbem_3039_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Extra_DWA_Periode_Onderbem_3039_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_onderbem_2529_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_onderbem_3039_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_Onderbem_4050_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Extra_DWA_Periode_Onderbem_4050_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_onderbem_3039_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_onderbem_4050_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Gemengd_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Gemengd_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_onderbem_4050_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_gemengd_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_VGS_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_VGS_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_gemengd_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_vgs_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Onderbem_DWA_obv_BAG_m3h
        # Hier met Bart over sparren.
        # 
        # Als "POC_Theorie_Totaal_m3h" > 0, dan de afvoercapaciteit van het rioolgemaal meenenen in de optelling
        # Als "POC_Theorie_Totaal_m3h" = 0 of "POC_Theorie_Totaal_m3h" IS NULL, dan de droogweerafvoer van het rioolgemaal meenenen in de optelling
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Onderbem_DWA_obv_BAG_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_vgs_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Onderbem_DWA_obv_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Onderbem_DWA_obv_VEs_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': parameters['CalcFieldsUpstreamInput']
        }
        outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CalcFieldsUpstreamInput'] = outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_ves_m3h']['OUTPUT']

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # calc fields upstream
        alg_params = {
            'id_veld': 'Bemalingsgebied_ID',
            'inputlayer': outputs['FieldCalculatorPoc_praktijk_onderbem_dwa_obv_ves_m3h']['OUTPUT'],
            'ontvangt_van': 'Onderbemalingsgebied_IDs',
            'veldenlijst': 'POC_Theorie_Gemengd_m3h;POC_Theorie_Gemengd_Onderbem_m3h,POC_Theorie_VGS_m3h;POC_Theorie_VGS_Onderbem_m3h,DWA_BAG_m3h;DWA_BAG_Onderbemalingen_m3h,Drinkwater_Particulier_m3h;Drinkwater_Part_Onderbem_m3h,Drinkwater_Zakelijk_m3h;Drinkwater_Zak_Onderbem_m3h,Drinkwater_Totaal_m3h;Drinkwater_Totaal_Onderbem_m3h,DWA_VEs_m3h;DWA_VEs_Onderbemalingen_m3h,Extra_DWA_Periode_2124_m3h;Extra_DWA_Periode_Onderbem_2124_m3h,Extra_DWA_Periode_2529_m3h;Extra_DWA_Periode_Onderbem_2529_m3h,Extra_DWA_Periode_3039_m3h;Extra_DWA_Periode_Onderbem_3039_m3h,Extra_DWA_Periode_4050_m3h;Extra_DWA_Periode_Onderbem_4050_m3h',
            'Output_layer': parameters['CalcFieldsUpstream']
        }
        outputs['CalcFieldsUpstream'] = processing.run('GeoDynTools:calc fields upstream', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CalcFieldsUpstream'] = outputs['CalcFieldsUpstream']['Output_layer']

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_Adressen_In_Onderbemalingen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_Adressen_In_Onderbemalingen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("DWA_BAG_onderbemalingen_m3h"/(12/1000),0)',
            'INPUT': outputs['CalcFieldsUpstream']['Output_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_adressen_in_onderbemalingen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Totaal_Onderbem_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Totaal_Onderbem_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("POC_Theorie_Gemengd_Onderbem_m3h"+"POC_Theorie_VGS_Onderbem_m3h",2)',
            'INPUT': outputs['FieldCalculatorAantal_adressen_in_onderbemalingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_totaal_onderbem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Theorie_Gemengd_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Theorie_Gemengd_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("POC_Theorie_Gemengd_m3h"+"POC_Theorie_Gemengd_Onderbem_m3h",2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_totaal_onderbem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_poc_theorie_gemengd_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Theorie_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Theorie_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("POC_Theorie_VGS_m3h"+"POC_Theorie_VGS_Onderbem_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_poc_theorie_gemengd_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_poc_theorie_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Theorie_Totaal_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Theorie_Totaal_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Sommatie_POC_Theorie_Gemengd_m3h"+"Sommatie_POC_Theorie_VGS_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_poc_theorie_vgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_poc_theorie_totaal_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_DWA_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("DWA_BAG_m3h"+"DWA_BAG_Onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_poc_theorie_totaal_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_dwa_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Adressen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Adressen',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '"Aantal_Adressen_Eigen_Rioleringsgebied"+"Aantal_Adressen_In_Onderbemalingen"',
            'INPUT': outputs['FieldCalculatorSommatie_dwa_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_adressen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Drinkwater_Part_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Drinkwater_Part_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Drinkwater_Particulier_m3h"+"Drinkwater_Part_Onderbem_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_adressen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_drinkwater_part_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Drinkwater_Zak_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Drinkwater_Zak_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Drinkwater_Zakelijk_m3h"+"Drinkwater_Zak_Onderbem_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_drinkwater_part_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_drinkwater_zak_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Drinkwater_Totaal_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Drinkwater_Totaal_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Drinkwater_Totaal_m3h"+"Drinkwater_Totaal_Onderbem_m3h" ,2)',
            'INPUT': outputs['FieldCalculatorSommatie_drinkwater_zak_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_drinkwater_totaal_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_DWA_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_DWA_VEs_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("DWA_VEs_m3h"+"DWA_VEs_Onderbemalingen_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_drinkwater_totaal_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_dwa_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Aantal_VEs
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Aantal_VEs',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Aantal_VEs_Eigen_Rioleringsgebied"+"Aantal_VEs_Onderbemalingen",0)',
            'INPUT': outputs['FieldCalculatorSommatie_dwa_ves_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_aantal_ves'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Extra_DWA_Periode_2124_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Extra_DWA_Periode_2124_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Extra_DWA_Periode_2124_m3h"+"Extra_DWA_Periode_Onderbem_2124_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_aantal_ves']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_extra_dwa_periode_2124_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Extra_DWA_Periode_2529_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Extra_DWA_Periode_2529_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Extra_DWA_Periode_2529_m3h"+"Extra_DWA_Periode_Onderbem_2529_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_extra_dwa_periode_2124_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_extra_dwa_periode_2529_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Extra_DWA_Periode_3039_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Extra_DWA_Periode_3039_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Extra_DWA_Periode_3039_m3h"+"Extra_DWA_Periode_Onderbem_3039_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_extra_dwa_periode_2529_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_extra_dwa_periode_3039_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_Extra_DWA_Periode_4050_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_Extra_DWA_Periode_4050_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Extra_DWA_Periode_4050_m3h"+"Extra_DWA_Periode_Onderbem_4050_m3h",2)',
            'INPUT': outputs['FieldCalculatorSommatie_extra_dwa_periode_3039_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_extra_dwa_periode_4050_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_BAG_En_POC_Theorie_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_BAG_En_POC_Theorie_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Sommatie_DWA_BAG_m3h"=>0,round("Sommatie_POC_Theorie_Totaal_m3h"+"Sommatie_DWA_BAG_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorSommatie_extra_dwa_periode_4050_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_bag_en_poc_theorie_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Sommatie_Drinkwater_Totaal_m3h">0,round("Sommatie_POC_Theorie_Totaal_m3h"+"Sommatie_Drinkwater_Totaal_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_bag_en_poc_theorie_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_en_poc_theorie_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Sommatie_DWA_VEs_m3h">0,round("Sommatie_POC_Theorie_Totaal_m3h"+"Sommatie_DWA_VEs_m3h",2),0)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_en_poc_theorie_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_ves_en_poc_theorie_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_ves_en_poc_theorie_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_bag_en_poc_praktijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_bag_en_poc_praktijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_en_poc_praktijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_drinkwater_en_poc_praktijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvalwateraanbod_obv_ves_en_poc_praktijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorAfvalwateraanbod_obv_ves_en_poc_praktijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Praktijk_DWA_obv_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Praktijk_DWA_obv_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)\r\n',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_ves_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(0,2)',
            'INPUT': outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Field calculator Sommatie_POC_Praktijk_DWA_obv_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Sommatie_POC_Praktijk_DWA_obv_VEs_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(if("POC_Theorie_Totaal_m3h"=0,0,\r\n"Afvoercapaciteit_m3h" - \r\n"POC_Praktijk_Onderbem_DWA_obv_VEs_m3h" -\r\n"Sommatie_DWA_VEs_m3h")\r\n,2)\r\n',
            'INPUT': outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': parameters['Calc_upstream_poc_praktijk_input']
        }
        outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Calc_upstream_poc_praktijk_input'] = outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_ves_m3h']['OUTPUT']

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # calc fields upstream POC with iteration
        # input required: 
        # id_veld, ontvangt_van, Aantal_Keer_Oppompen_Tot_En_Met_Afleverpunt, Afvoercapaciteit_m3h, POC_Theorie_Totaal_m3h, 
        # Sommatie_DWA_BAG_m3h, 
        # Sommatie_Drinkwater_Totaal_m3h, 
        # Sommatie_DWA_VEs_m3h,
        # 
        # output BAG: 
        # POC_Praktijk_Onderbem_DWA_obv_BAG_m3h, 
        # Sommatie_POC_Praktijk_DWA_obv_BAG_m3h, 
        # POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h, 
        # Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h,
        # 
        # output Drinktwater:
        # POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h, 
        # Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h, 
        # POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h, 
        # Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h,
        # 
        # output VE's:
        # POC_Praktijk_Onderbem_DWA_obv_VEs_m3h, 
        # Sommatie_POC_Praktijk_DWA_obv_VEs_m3h, 
        # POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h, 
        # Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h,
        alg_params = {
            'id_veld': 'Bemalingsgebied_ID',
            'inputlayer': outputs['FieldCalculatorSommatie_poc_praktijk_dwa_obv_ves_m3h']['OUTPUT'],
            'ontvangt_van': 'Onderbemalingsgeb_IDs_1_Niveau_Diep',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalcFieldsUpstreamPocWithIteration'] = processing.run('GeoDynTools:calc fields upstream POC with iteration', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Extract by expression Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit
        alg_params = {
            'EXPRESSION': '(("Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h" OR "Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h" OR "Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h") > "Afvoercapaciteit_m3h") OR "Afvoercapaciteit_m3h" IS NULL',
            'INPUT': outputs['CalcFieldsUpstreamPocWithIteration']['Output_layer'],
            'OUTPUT': parameters['Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit']
        }
        outputs['ExtractByExpressionGebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Gebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit'] = outputs['ExtractByExpressionGebieden_waar_afvalwateraanbod_groter_is_dan_afvoercapaciteit']['OUTPUT']

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # Retain fields
        alg_params = {
            'FIELDS': ['Bemalingsgebied_ID','Afvoercapaciteit_m3h','Bemalingsgebied_ID_Lozingspunt','POC_Theorie_Totaal_m3h','DWA_BAG_m3h','Onderbemalingsgeb_IDs_1_Niveau_Diep','Onderbemalingsgebied_IDs','DWA_BAG_Onderbemalingen_m3h','POC_Praktijk_Onderbem_DWA_obv_BAG_m3h','POC_Praktijk_Onderbem_DWA_obv_Drinkwater_m3h','POC_Praktijk_Onderbem_DWA_obv_VEs_m3h','Sommatie_DWA_BAG_m3h','Sommatie_Drinkwater_Totaal_m3h','Sommatie_DWA_VEs_m3h','POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h','POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h','Sommatie_POC_Praktijk_DWA_obv_BAG_m3h','Sommatie_POC_Praktijk_DWA_obv_Drinkwater_m3h','Sommatie_POC_Praktijk_DWA_obv_VEs_m3h','Afvalwateraanbod_obv_BAG_En_POC_Praktijk_m3h','Afvalwateraanbod_obv_Drinkwater_En_POC_Praktijk_m3h','Afvalwateraanbod_obv_VEs_En_POC_Praktijk_m3h','POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h'],
            'INPUT': outputs['CalcFieldsUpstreamPocWithIteration']['Output_layer'],
            'OUTPUT': parameters['Retained_fields_for_testing_poc_calculation']
        }
        outputs['RetainFields'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Retained_fields_for_testing_poc_calculation'] = outputs['RetainFields']['OUTPUT']

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # Field calculator Leidingberging_mm
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Leidingberging_mm',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"Leidingberging_m3"/("Aangesloten_Oppervlak_Stelsel_ha"*10000)*1000\r\n,2)',
            'INPUT': outputs['CalcFieldsUpstreamPocWithIteration']['Output_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLeidingberging_mm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Field calculator Knooppuntberging_mm
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Knooppuntberging_mm',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"Knooppuntberging_m3"/\r\n("Aangesloten_Oppervlak_Stelsel_ha"*10000)*1000\r\n,2)',
            'INPUT': outputs['FieldCalculatorLeidingberging_mm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorKnooppuntberging_mm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # Field calculator Stelselberging_mm
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Stelselberging_mm',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"Stelselberging_m3"/\r\n("Aangesloten_Oppervlak_Stelsel_ha"*10000)*1000\r\n,2)',
            'INPUT': outputs['FieldCalculatorKnooppuntberging_mm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStelselberging_mm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Field calculator Maximale_Vultijd_Droogweer_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Maximale_Vultijd_Droogweer_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Sommatie_Drinkwater_Totaal_m3h" = 0 AND "Sommatie_DWA_VEs_m3h" = 0,\r\nround("Stelselberging_m3"/"Sommatie_DWA_BAG_m3h",2),\r\nif("Sommatie_Drinkwater_Totaal_m3h" > 0 AND "Sommatie_DWA_VEs_m3h" = 0,\r\nround("Stelselberging_m3"/min("Sommatie_DWA_BAG_m3h","Sommatie_Drinkwater_Totaal_m3h"),2),\r\nif("Sommatie_Drinkwater_Totaal_m3h" = 0 AND "Sommatie_DWA_VEs_m3h" > 0,\r\nround("Stelselberging_m3"/min("Sommatie_DWA_BAG_m3h","Sommatie_DWA_VEs_m3h"),2),\r\nif("Sommatie_Drinkwater_Totaal_m3h" > 0 AND "Sommatie_DWA_VEs_m3h" > 0,\r\nround("Stelselberging_m3"/min("Sommatie_DWA_BAG_m3h","Sommatie_Drinkwater_Totaal_m3h","Sommatie_DWA_VEs_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorStelselberging_mm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMaximale_vultijd_droogweer_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # Field calculator Minimale_Vultijd_Droogweer_h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Minimale_Vultijd_Droogweer_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Stelselberging_m3"/max("Sommatie_DWA_BAG_m3h","Sommatie_Drinkwater_Totaal_m3h","Sommatie_DWA_VEs_m3h"),2)',
            'INPUT': outputs['FieldCalculatorMaximale_vultijd_droogweer_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMinimale_vultijd_droogweer_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # Field calculator Maximale_Ledigingstijd_h
        # 20240918 aangepast
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Maximale_Ledigingstijd_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" = 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" = 0,\r\nround("Stelselberging_m3"/"Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h",2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" > 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" = 0,\r\nround("Stelselberging_m3"/min("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_Drinkwater_Totaal_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" = 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" > 0,\r\nround("Stelselberging_m3"/min("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_DWA_VEs_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" > 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" > 0,\r\nround("Stelselberging_m3"/min("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_DWA_VEs_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_Drinkwater_Totaal_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorMinimale_vultijd_droogweer_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMaximale_ledigingstijd_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # Field calculator Minimale_Ledigingstijd_h
        # 20240918 aangepast
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Minimale_Ledigingstijd_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'if("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" = 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" = 0,\r\nround("Stelselberging_m3"/"Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h",2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" > 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" = 0,\r\nround("Stelselberging_m3"/max("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_Drinkwater_Totaal_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" = 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" > 0,\r\nround("Stelselberging_m3"/max("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_DWA_VEs_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),\r\nif("Afvalwateraanbod_obv_Drinkwater_En_POC_Theorie_m3h" > 0 AND "Afvalwateraanbod_obv_VEs_En_POC_Theorie_m3h" > 0,\r\nround("Stelselberging_m3"/max("Afvoercapaciteit_m3h"-"Sommatie_DWA_BAG_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_DWA_VEs_m3h"-"POC_Theorie_Totaal_Onderbem_m3h","Afvoercapaciteit_m3h"-"Sommatie_Drinkwater_Totaal_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"),2),0))))',
            'INPUT': outputs['FieldCalculatorMaximale_ledigingstijd_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMinimale_ledigingstijd_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Beschikbaar_DWA_obv_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Beschikbaar_DWA_obv_BAG_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Afvoercapaciteit_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"-"DWA_BAG_Onderbemalingen_m3h"-"DWA_BAG_m3h",2)',
            'INPUT': outputs['FieldCalculatorMinimale_ledigingstijd_h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Beschikbaar_DWA_obv_Drinkwater_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Beschikbaar_DWA_obv_Drinkwater_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Afvoercapaciteit_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"-"Drinkwater_Totaal_Onderbem_m3h"-"Drinkwater_Totaal_m3h",2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Beschikbaar_DWA_obv_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Beschikbaar_DWA_obv_VEs_m3h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round("Afvoercapaciteit_m3h"-"POC_Theorie_Totaal_Onderbem_m3h"-"DWA_VEs_Onderbemalingen_m3h"-"DWA_VEs_m3h",2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_mmh
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_mmh',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_BAG_m3h"/\r\n"Aangesloten_Oppervlak_Stelsel_ha",2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_beschikbaar_dwa_obv_ves_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_bag_mmh'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_mmh
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_mmh',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_Drinkwater_m3h"/\r\n"Aangesloten_Oppervlak_Stelsel_ha",2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_bag_mmh']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_drinkwater_mmh'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_mmh
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_mmh',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimaal (double)
            'FORMULA': 'round(\r\n"POC_Praktijk_Eigen_Rioleringsgeb_DWA_obv_VEs_m3h"/\r\n"Aangesloten_Oppervlak_Stelsel_ha",2)',
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_drinkwater_mmh']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_ves_mmh'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Drop field(s) overbodige velden
        alg_params = {
            'COLUMN': ['Bemalingsgebied_ID_2','Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_BAG_m3h','Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_Drinkwater_m3h','Eigen_Gebied_Max_Afvalwateraanbod_praktijk_obv_VE_m3h'],
            'INPUT': outputs['FieldCalculatorPoc_praktijk_eigen_rioleringsgeb_dwa_obv_ves_mmh']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsOverbodigeVelden'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(82)
        if feedback.isCanceled():
            return {}

        # Field calculator Order
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Order',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '1',
            'INPUT': outputs['DropFieldsOverbodigeVelden']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap3_rioleringsgebieden_kengetallen']
        }
        outputs['FieldCalculatorOrder'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap3_rioleringsgebieden_kengetallen'] = outputs['FieldCalculatorOrder']['OUTPUT']

        feedback.setCurrentStep(83)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Bemalingsgebied_ID_Afvoerpunt',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'Bemalingsgebied_ID',
            'INPUT': outputs['RetainFieldsBemalingsgebied_id_afvoerpunt']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorOrder']['OUTPUT'],
            'METHOD': 1,  # Alleen attributen gebruiken van eerste overeenkomende object (één-tot-één)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(84)
        if feedback.isCanceled():
            return {}

        # Drop field(s) Bemalingsgebied_ID_2
        # Data aan afvoerpunten plakken, omdat GWSW-kengetallen de kengetallen aan afvoerpunten hangt.
        alg_params = {
            'COLUMN': ['Bemalingsgebied_ID_2'],
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap3_afvoerpunten_kengetallen']
        }
        outputs['DropFieldsBemalingsgebied_id_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap3_afvoerpunten_kengetallen'] = outputs['DropFieldsBemalingsgebied_id_2']['OUTPUT']

        
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
