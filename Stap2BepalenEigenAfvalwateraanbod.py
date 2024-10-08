"""
Model exported as python.
Name : GeoDyn GWSW stap 2 - Bepalen eigen afvalwateraanbod
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


class GeodynGwswStap2BepalenEigenAfvalwateraanbod(QgsProcessingAlgorithmPost):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bag_verblijfsobject', 'BAG verblijfsobject', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('bag_vbo', geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGTinlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('inlooptabel', geometryType=2), optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer('drinkwater', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('drinkwater', geometryType=0), optional=True))
        self.addParameter(QgsProcessingParameterNumber('inw_per_adres', 'inw_per_adres', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=2.5))
        self.addParameter(QgsProcessingParameterVectorLayer('plancap', 'Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('plancap', geometryType=2), optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_rioleringsgebieden', 'Resultaat stap 1: Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Resultaat_stap1_rioleringsgebieden')))
        self.addParameter(QgsProcessingParameterVectorLayer('ve', 'VE', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('ve_', geometryType=0), optional=True))
        self.addParameter(QgsProcessingParameterFeatureSink('PlancapPerBem_id', 'Plancap per BEM_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwater', 'POC BAG DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwaterVe', 'POC BAG DRINKWATER VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Dwa_bag_m3h', 'DWA_BAG_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat_Stap2_Rioleringsgebieden_Met_Afvalwateraanbod_Uit_Eigen_Gebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Aangesloten_oppervlak_en_poc_eigen_gebied', 'Aangesloten_oppervlak_en_POC_eigen_gebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('BgtIntersectEnOppervlakteAttribuut', 'BGT intersect en oppervlakte attribuut', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))

        # self.addParameter(QgsProcessingParameterVectorLayer('bag_verblijfsobject', 'BAG verblijfsobject', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('bag_vbo', geometryType=0)))
        # self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGTinlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('inlooptabel', geometryType=2)))
        # self.addParameter(QgsProcessingParameterVectorLayer('drinkwater', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('drinkwater', geometryType=0)))
        # self.addParameter(QgsProcessingParameterNumber('inw_per_adres', 'inw_per_adres', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=2.5))
        # self.addParameter(QgsProcessingParameterVectorLayer('plancap', 'Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('plancap', geometryType=2)))
        # self.addParameter(QgsProcessingParameterVectorLayer('resultaat_stap1_rioleringsgebieden', 'Resultaat stap 1: Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Resultaat_stap1_rioleringsgebieden')))
        # self.addParameter(QgsProcessingParameterVectorLayer('ve', 'VE', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('ve_', geometryType=0)))
        # self.addParameter(QgsProcessingParameterFeatureSink('PlancapPerBem_id', 'Plancap per BEM_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwater', 'POC BAG DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwaterVe', 'POC BAG DRINKWATER VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Dwa_bag_m3h', 'DWA_BAG_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied', 'Resultaat_Stap2_Rioleringsgebieden_Met_Afvalwateraanbod_Uit_Eigen_Gebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        # self.addParameter(QgsProcessingParameterFeatureSink('Aangesloten_oppervlak_en_poc_eigen_gebied', 'Aangesloten_oppervlak_en_POC_eigen_gebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('BgtIntersectEnOppervlakteAttribuut', 'BGT intersect en oppervlakte attribuut', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        # self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
        
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        inw_per_adres = parameters['inw_per_adres'] 
        parameters['input_fields_csv'] = default_inp_fields
        dummy_folder = "dummy_gpkg"
        if not parameters['ve']:
            parameters['ve'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "ve_empty.gpkg"), "ve_empty", "ogr")
            QgsProject.instance().addMapLayer(parameters['ve'], False)
        if not parameters['bgtinlooptabel']:
            parameters['bgtinlooptabel'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "bgtinlooptabel_empty.gpkg"), "bgtinlooptabel_empty", "ogr")
            QgsProject.instance().addMapLayer(parameters['bgtinlooptabel'], False) # addMapLayer seems to be necessary to load layer but only for bgtinlooptabel? why?
        if not parameters['plancap']:
            parameters['plancap'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "plancap_empty.gpkg"), "plancap_empty", "ogr")
            QgsProject.instance().addMapLayer(parameters['plancap'], False)
        if not parameters['drinkwater']:
            parameters['drinkwater'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "drinkwater_empty.gpkg"), "drinkwater_empty", "ogr")
            QgsProject.instance().addMapLayer(parameters['drinkwater'], False)
        #QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        self.result_folder = parameters['result_folder']
        
        ################################ IMPORTANT! ####################################
        # after pasting also replace text below for the Field calculator DWA_BAG
        # 'FORMULA':  'round(IF("Aantal_Adressen_Eigen_Rioleringsgebied" IS NULL, 0, @inw_per_adres * (12/1000) * "Aantal_Adressen_Eigen_Rioleringsgebied"),2)',
        # by
        # 'FORMULA': f'round(IF("Aantal_Adressen_Eigen_Rioleringsgebied" IS NULL, 0, {inw_per_adres} * (12/1000) * "Aantal_Adressen_Eigen_Rioleringsgebied"),2)',
        ################################ IMPORTANT! ####################################

        feedback = QgsProcessingMultiStepFeedback(55, model_feedback)
        results = {}
        outputs = {}

        # Create spatial index Resultaat stap 1: Rioleringsgebieden
        alg_params = {
            'INPUT': parameters['resultaat_stap1_rioleringsgebieden']
        }
        outputs['CreateSpatialIndexResultaatStap1Rioleringsgebieden'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Field calculator Stap2_datum
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'Stap2_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['CreateSpatialIndexResultaatStap1Rioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStap2_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator BAG
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'BAG',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '1',
            'INPUT': parameters['bag_verblijfsobject'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBag'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Fix geometries Plancap
        alg_params = {
            'INPUT': parameters['plancap'],
            'METHOD': 0,  # Linework
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesPlancap'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Fix geometries BGT-inlooptabel
        alg_params = {
            'INPUT': parameters['bgtinlooptabel'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesBgtinlooptabel'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Create spatial index VE
        alg_params = {
            'INPUT': parameters['ve']
        }
        outputs['CreateSpatialIndexVe'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # retainfields Bemalingsgebied_ID
        alg_params = {
            'inputlayer': outputs['FieldCalculatorStap2_datum']['OUTPUT'],
            'veldenlijst': 'Bemalingsgebied_ID',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainfieldsBemalingsgebied_id'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Create spatial index Drinkwater
        alg_params = {
            'INPUT': parameters['drinkwater']
        }
        outputs['CreateSpatialIndexDrinkwater'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Create spatial index BAG
        alg_params = {
            'INPUT': outputs['FieldCalculatorBag']['OUTPUT']
        }
        outputs['CreateSpatialIndexBag'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator Plancap ID
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'PC_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"PLANID"',
            'INPUT': outputs['FixGeometriesPlancap']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPlancapId'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Create spatial index BGTinlooptabel
        alg_params = {
            'INPUT': outputs['FixGeometriesBgtinlooptabel']['OUTPUT']
        }
        outputs['CreateSpatialIndexBgtinlooptabel'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Create spatial index PlanCap
        alg_params = {
            'INPUT': outputs['FieldCalculatorPlancapId']['OUTPUT']
        }
        outputs['CreateSpatialIndexPlancap'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Intersection rioleringsgebieden met plancap
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['RetainfieldsBemalingsgebied_id']['Output_layer'],
            'INPUT_FIELDS': ['Bemalingsgebied_ID'],
            'OVERLAY': outputs['CreateSpatialIndexPlancap']['OUTPUT'],
            'OVERLAY_FIELDS': ['ExAFW_2124','ExAFW_2529','ExAFW_3039','ExAFW_4050','PC_ID'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IntersectionRioleringsgebiedenMetPlancap'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Add geometry attributes
        alg_params = {
            'CALC_METHOD': 0,  # Layer CRS
            'INPUT': outputs['IntersectionRioleringsgebiedenMetPlancap']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddGeometryAttributes'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Order by expression Plancap area van hoog naar laag
        alg_params = {
            'ASCENDING': False,
            'EXPRESSION': 'area',
            'INPUT': outputs['AddGeometryAttributes']['OUTPUT'],
            'NULLS_FIRST': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['OrderByExpressionPlancapAreaVanHoogNaarLaag'] = processing.run('native:orderbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Delete duplicates by attribute kleinste Plancap-polygonen per PC_ID verwijderen
        alg_params = {
            'FIELDS': ['PC_ID'],
            'INPUT': outputs['OrderByExpressionPlancapAreaVanHoogNaarLaag']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicatesByAttributeKleinstePlancappolygonenPerPc_idVerwijderen'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Aggregate plancap hoeveelheden per jaartal per rioleringsgebied
        # PlanCap wordt aan het rioleringsgebied met grootste overlap gehangen
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Bemalingsgebied_ID','length': 50,'name': 'Bemalingsgebied_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'ExAFW_2124','length': 0,'name': 'Extra_DWA_Periode_2124_m3h','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'ExAFW_2529','length': 0,'name': 'Extra_DWA_Periode_2529_m3h','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'ExAFW_3039','length': 0,'name': 'Extra_DWA_Periode_3039_m3h','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ', ','input': 'ExAFW_4050','length': 0,'name': 'Extra_DWA_Periode_4050_m3h','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'PC_ID','length': 500,'name': 'Bouwprojecten_Eigen_Rioleringsgeb_IDs','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'GROUP_BY': 'Bemalingsgebied_ID',
            'INPUT': outputs['DeleteDuplicatesByAttributeKleinstePlancappolygonenPerPc_idVerwijderen']['OUTPUT'],
            'OUTPUT': parameters['PlancapPerBem_id']
        }
        outputs['AggregatePlancapHoeveelhedenPerJaartalPerRioleringsgebied'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PlancapPerBem_id'] = outputs['AggregatePlancapHoeveelhedenPerJaartalPerRioleringsgebied']['OUTPUT']

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Intersection BGT inlooptabel met rioleringsgebieden tbv stap 3
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['CreateSpatialIndexBgtinlooptabel']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['FieldCalculatorStap2_datum']['OUTPUT'],
            'OVERLAY_FIELDS': ['Bemalingsgebied_ID'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IntersectionBgtInlooptabelMetRioleringsgebiedenTbvStap3'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculator BGT-inlooptabel - oppv
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'oppv',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( $area ,2)',
            'INPUT': outputs['IntersectionBgtInlooptabelMetRioleringsgebiedenTbvStap3']['OUTPUT'],
            'OUTPUT': parameters['BgtIntersectEnOppervlakteAttribuut']
        }
        outputs['FieldCalculatorBgtinlooptabelOppv'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BgtIntersectEnOppervlakteAttribuut'] = outputs['FieldCalculatorBgtinlooptabelOppv']['OUTPUT']

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Field calculator GEM_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'GEM_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("gemengd_riool"/100)',
            'INPUT': outputs['FieldCalculatorBgtinlooptabelOppv']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorGem_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Field calculator HWA_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'HWA_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("hemelwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorGem_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorHwa_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Field calculator VGS_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VGS_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("vgs_hemelwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorHwa_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVgs_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("vuilwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorVgs_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator DIT_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DIT_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("infiltratievoorziening"/100)',
            'INPUT': outputs['FieldCalculatorDwa_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDit_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator WATER_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'WATER_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("open_water"/100)',
            'INPUT': outputs['FieldCalculatorDit_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorWater_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator MV_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'MV_ha',
            'FIELD_PRECISION': 5,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '("oppv"/10000) * ("graad_verharding"/100) * ("maaiveld"/100)',
            'INPUT': outputs['FieldCalculatorWater_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMv_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Aggregate BGT-oppervlakken per rioleringsgebied
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Bemalingsgebied_ID','length': 50,'name': 'Bemalingsgebied_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'GEM_ha','length': 0,'name': 'Gemengd_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'HWA_ha','length': 0,'name': 'Hemelwater_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'VGS_ha','length': 0,'name': 'Verbeterd_Hemelwater_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'DWA_ha','length': 0,'name': 'Vuilwater_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'DIT_ha','length': 0,'name': 'DIT_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'sum','delimiter': ',','input': 'WATER_ha','length': 0,'name': 'Oppervlaktewater_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 4,'type_name': 'int8'},{'aggregate': 'sum','delimiter': ',','input': 'MV_ha','length': 0,'name': 'Maaiveld_Aangesloten_ha','precision': 3,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'Bemalingsgebied_ID',
            'INPUT': outputs['FieldCalculatorMv_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateBgtoppervlakkenPerRioleringsgebied'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value aangesloten oppervlak aan rioleringsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Bemalingsgebied_ID',
            'FIELDS_TO_COPY': ['Gemengd_Aangesloten_ha','Hemelwater_Aangesloten_ha','Verbeterd_Hemelwater_Aangesloten_ha','Vuilwater_Aangesloten_ha','DIT_Aangesloten_ha','Oppervlaktewater_Aangesloten_ha','Maaiveld_Aangesloten_ha'],
            'FIELD_2': 'Bemalingsgebied_ID',
            'INPUT': outputs['FieldCalculatorStap2_datum']['OUTPUT'],
            'INPUT_2': outputs['AggregateBgtoppervlakkenPerRioleringsgebied']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueAangeslotenOppervlakAanRioleringsgebieden'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Field calculator Aangesloten_Oppervlak_Stelsel_ha
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aangesloten_Oppervlak_Stelsel_ha',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("Gemengd_Aangesloten_ha"+"Verbeterd_Hemelwater_Aangesloten_ha",2)',
            'INPUT': outputs['JoinAttributesByFieldValueAangeslotenOppervlakAanRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAangesloten_oppervlak_stelsel_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Gemengd_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'POC_Theorie_Gemengd_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Gemengd_Aangesloten_ha" IS NULL, 0, ("Gemengd_Aangesloten_ha"*10000) * (0.7/1000)),2)',
            'INPUT': outputs['FieldCalculatorAangesloten_oppervlak_stelsel_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_gemengd_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'POC_Theorie_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Verbeterd_Hemelwater_Aangesloten_ha" IS NULL, 0, ("Verbeterd_Hemelwater_Aangesloten_ha"*10000) * (0.3/1000)),2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_gemengd_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoc_theorie_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_Theorie_Totaal_m3h
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'POC_Theorie_Totaal_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_Theorie_Gemengd_m3h"+"POC_Theorie_VGS_m3h",2)',
            'INPUT': outputs['FieldCalculatorPoc_theorie_vgs_m3h']['OUTPUT'],
            'OUTPUT': parameters['Aangesloten_oppervlak_en_poc_eigen_gebied']
        }
        outputs['FieldCalculatorPoc_theorie_totaal_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Aangesloten_oppervlak_en_poc_eigen_gebied'] = outputs['FieldCalculatorPoc_theorie_totaal_m3h']['OUTPUT']

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Create spatial index aangesloten oppervlak rioleringsgebieden
        alg_params = {
            'INPUT': outputs['FieldCalculatorPoc_theorie_totaal_m3h']['OUTPUT']
        }
        outputs['CreateSpatialIndexAangeslotenOppervlakRioleringsgebieden'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) - aantal BAG objecten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexAangeslotenOppervlakRioleringsgebieden']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexBag']['OUTPUT'],
            'JOIN_FIELDS': ['BAG'],
            'PREDICATE': [0],  # intersect
            'SUMMARIES': [0],  # count
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryAantalBagObjecten'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Field calculator BAG_count NULL = 0 / Aantal_Adressen_Eigen_Rioleringsgebied
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_Adressen_Eigen_Rioleringsgebied',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("BAG_count" IS NULL, 0, "BAG_count")',
            'INPUT': outputs['JoinAttributesByLocationSummaryAantalBagObjecten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBag_countNull0Aantal_adressen_eigen_rioleringsgebied'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Field calculator Aangesloten_Oppervlak_Per_Woning_m2
        # Berekening aangesloten oppervlak per adres. "Gemengd_Aangesloten_ha"+"Verbeterd_Hemelwater_Aangesloten_ha"*10000 / "BAG_count"
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aangesloten_Oppervlak_Per_Woning_m2',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round((("Gemengd_Aangesloten_ha"+"Verbeterd_Hemelwater_Aangesloten_ha")*10000)/"BAG_count",0)',
            'INPUT': outputs['FieldCalculatorBag_countNull0Aantal_adressen_eigen_rioleringsgebied']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAangesloten_oppervlak_per_woning_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator Aangesloten_Oppervlak_Per_Woning_m2 NULL = 0
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Aangesloten_Oppervlak_Per_Woning_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("Aangesloten_Oppervlak_Per_Woning_m2" IS NULL, 0, "Aangesloten_Oppervlak_Per_Woning_m2")',
            'INPUT': outputs['FieldCalculatorAangesloten_oppervlak_per_woning_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAangesloten_oppervlak_per_woning_m2Null0'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': f'round(IF("Aantal_Adressen_Eigen_Rioleringsgebied" IS NULL, 0, {inw_per_adres} * (12/1000) * "Aantal_Adressen_Eigen_Rioleringsgebied"),2)',
            'INPUT': outputs['FieldCalculatorAangesloten_oppervlak_per_woning_m2Null0']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Drop field(s) BAG_count
        alg_params = {
            'COLUMN': ['BAG_count'],
            'INPUT': outputs['FieldCalculatorDwa_bag_m3h']['OUTPUT'],
            'OUTPUT': parameters['Dwa_bag_m3h']
        }
        outputs['DropFieldsBag_count'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Dwa_bag_m3h'] = outputs['DropFieldsBag_count']['OUTPUT']

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Create spatial index DWA_BAG_m3h
        alg_params = {
            'INPUT': outputs['DropFieldsBag_count']['OUTPUT']
        }
        outputs['CreateSpatialIndexDwa_bag_m3h'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) DRINKWATER
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexDwa_bag_m3h']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexDrinkwater']['OUTPUT'],
            'JOIN_FIELDS': ['PAR_RESULT','ZAK_RESULT'],
            'PREDICATE': [0],  # intersect
            'SUMMARIES': [5],  # sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryDrinkwater'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Particulier_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Drinkwater_Particulier_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("PAR_RESULT_sum" IS NULL, 0, round("PAR_RESULT_sum"/1000,2))',
            'INPUT': outputs['JoinAttributesByLocationSummaryDrinkwater']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_particulier_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Zakelijk_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Drinkwater_Zakelijk_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("ZAK_RESULT_sum" IS NULL, 0, round("ZAK_RESULT_sum"/1000,2))',
            'INPUT': outputs['FieldCalculatorDrinkwater_particulier_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_zakelijk_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Field calculator Drinkwater_Totaal_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Drinkwater_Totaal_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("Drinkwater_Particulier_m3h" + "Drinkwater_Zakelijk_m3h",2)',
            'INPUT': outputs['FieldCalculatorDrinkwater_zakelijk_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwater_totaal_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Drop field(s) PAR_sum en ZAK_sum
        alg_params = {
            'COLUMN': ['PAR_RESULT_sum','ZAK_RESULT_sum'],
            'INPUT': outputs['FieldCalculatorDrinkwater_totaal_m3h']['OUTPUT'],
            'OUTPUT': parameters['PocBagDrinkwater']
        }
        outputs['DropFieldsPar_sumEnZak_sum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PocBagDrinkwater'] = outputs['DropFieldsPar_sumEnZak_sum']['OUTPUT']

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Create spatial index POC BAG DRINKWATER
        alg_params = {
            'INPUT': outputs['DropFieldsPar_sumEnZak_sum']['OUTPUT']
        }
        outputs['CreateSpatialIndexPocBagDrinkwater'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) VE
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexPocBagDrinkwater']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexVe']['OUTPUT'],
            'JOIN_FIELDS': ['GRONDSLAG'],
            'PREDICATE': [0],  # intersect
            'SUMMARIES': [5],  # sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryVe'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Field calculator Aantal_VEs_Eigen_Rioleringsgebied
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Aantal_VEs_Eigen_Rioleringsgebied',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("GRONDSLAG_sum" IS NULL, 0,round("GRONDSLAG_sum",2))',
            'INPUT': outputs['JoinAttributesByLocationSummaryVe']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAantal_ves_eigen_rioleringsgebied'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_VEs_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_VEs_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("GRONDSLAG_sum" IS NULL, 0,"GRONDSLAG_sum" * (12/1000)),2)',
            'INPUT': outputs['FieldCalculatorAantal_ves_eigen_rioleringsgebied']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_ves_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Drop field(s) GRONDSLAG_sum
        alg_params = {
            'COLUMN': ['GRONDSLAG_sum'],
            'INPUT': outputs['FieldCalculatorDwa_ves_m3h']['OUTPUT'],
            'OUTPUT': parameters['PocBagDrinkwaterVe']
        }
        outputs['DropFieldsGrondslag_sum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PocBagDrinkwaterVe'] = outputs['DropFieldsGrondslag_sum']['OUTPUT']

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value PlanCap aan Rioleringsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Bemalingsgebied_ID',
            'FIELDS_TO_COPY': ['Extra_DWA_Periode_2124_m3h','Extra_DWA_Periode_2529_m3h','Extra_DWA_Periode_3039_m3h','Extra_DWA_Periode_4050_m3h','Bouwprojecten_Eigen_Rioleringsgeb_IDs'],
            'FIELD_2': 'Bemalingsgebied_ID',
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'INPUT_2': outputs['AggregatePlancapHoeveelhedenPerJaartalPerRioleringsgebied']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValuePlancapAanRioleringsgebieden'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_2124_m3h NULL = 0
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Extra_DWA_Periode_2124_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Extra_DWA_Periode_2124_m3h" IS NULL, 0, "Extra_DWA_Periode_2124_m3h"),2)',
            'INPUT': outputs['JoinAttributesByFieldValuePlancapAanRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_2124_m3hNull0'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_2529_m3h = 0
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Extra_DWA_Periode_2529_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Extra_DWA_Periode_2529_m3h" IS NULL, 0, "Extra_DWA_Periode_2529_m3h" ),2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_2124_m3hNull0']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_2529_m3h0'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_3039_m3h NULL = 0
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Extra_DWA_Periode_3039_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Extra_DWA_Periode_3039_m3h" IS NULL, 0,"Extra_DWA_Periode_3039_m3h"),2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_2529_m3h0']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorExtra_dwa_periode_3039_m3hNull0'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Field calculator Extra_DWA_Periode_4050_m3h NULL = 0
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Extra_DWA_Periode_4050_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(if("Extra_DWA_Periode_4050_m3h" IS NULL, 0, "Extra_DWA_Periode_4050_m3h"),2)',
            'INPUT': outputs['FieldCalculatorExtra_dwa_periode_3039_m3hNull0']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied']
        }
        outputs['FieldCalculatorExtra_dwa_periode_4050_m3hNull0'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap2_rioleringsgebieden_met_afvalwateraanbod_uit_eigen_gebied'] = outputs['FieldCalculatorExtra_dwa_periode_4050_m3hNull0']['OUTPUT']
        
        # Reminder: Did you replace de DWA_BAG calculation? See line 77

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
        return 'GeoDyn GWSW stap 2 - Bepalen eigen afvalwateraanbod'

    def displayName(self):
        return 'GeoDyn GWSW stap 2 - Bepalen eigen afvalwateraanbod'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return GeodynGwswStap2BepalenEigenAfvalwateraanbod()        
