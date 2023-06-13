"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
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


class Stap3BerekenAfvalwaterprognoseAlt(QgsProcessingAlgorithmPost):

    def initAlgorithm(self, config=None):
        # inputs
        self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebiedenstats', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('tbv_stap3')))
        self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGT Inlooptabel', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('inlooptabel', geometryType=2)))
        self.addParameter(QgsProcessingParameterVectorLayer('drinkwater', 'Input Drinkwater', optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('drinkwater', geometryType=0)))
        self.addParameter(QgsProcessingParameterNumber('inw_per_adres', 'inw_per_adres', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=2.5))
        self.addParameter(QgsProcessingParameterVectorLayer('bag_verblijfsobject', 'Input BAG Verblijfsobjecten', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('vbo', geometryType=0)))
        ##self.addParameter(QgsProcessingParameterFile('inputfieldscsv', 'input fields csv', behavior=QgsProcessingParameterFile.File, fileFilter='CSV Files (*.csv)', defaultValue='G:\\02_Werkplaatsen\\07_IAN\\bk\\projecten\\GeoDynGem\\2022\\inp_fields.csv'))
        # TODO inputplancap niet inbegrepen  
        ##self.addParameter(QgsProcessingParameterVectorLayer('inputplancap', 'input Plancap', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('plancap', geometryType=2)))
        self.addParameter(QgsProcessingParameterVectorLayer('ve', "Input VE's", optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('ve_', geometryType=0)))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
        # outputs ori
        # self.addParameter(QgsProcessingParameterFeatureSink('Result_all_fields', 'result_all_fields', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'Eindresultaat', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Bgt_intersect', 'bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Bemalingsgebieden_joined_stats', 'Bemalingsgebieden_joined_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Exafw_per_bem_id', 'ExAFW_per_bem_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Plancap_pc_id', 'PLANCAP_PC_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stats_drinkwater', 'STATS_DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stats_vbo', 'STATS_VBO', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stats_ve', 'STATS_VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Meerdere_plancaps_in_bemalingsgebied', 'meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Plancap_in_meerdere_bemalingsgebieden', 'plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # outputs new
        self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwater', 'POC BAG DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwaterVe', 'POC BAG DRINKWATER VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Poc_gem_m3h', 'POC_GEM_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Poc_vgs_m3h', 'POC_VGS_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Dwa_bag_m3h', 'DWA_BAG_m3/h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat_huidige_situatie', 'EINDRESULTAAT_HUIDIGE_SITUATIE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

        # inputs script generated
        ##self.addParameter(QgsProcessingParameterVectorLayer('bag_verblijfsobject', 'BAG verblijfsobject', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterVectorLayer('bemalingsgebiedenstats', 'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterVectorLayer('bgtinlooptabel', 'BGTinlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterVectorLayer('drinkwater', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        ##self.addParameter(QgsProcessingParameterNumber('inw_per_adres', 'inw_per_adres', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=2.5))
        ##self.addParameter(QgsProcessingParameterVectorLayer('ve', 'VE', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        # outputs script generated
        ##self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwater', 'POC BAG DRINKWATER', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFeatureSink('PocBagDrinkwaterVe', 'POC BAG DRINKWATER VE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFeatureSink('Poc_gem_m3h', 'POC_GEM_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFeatureSink('Poc_vgs_m3h', 'POC_VGS_m3h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFeatureSink('Dwa_bag_m3h', 'DWA_BAG_m3/h', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        ##self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat_huidige_situatie', 'EINDRESULTAAT_HUIDIGE_SITUATIE', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))



    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        parameters['inputfieldscsv'] = default_inp_fields
        dummy_folder = "dummy_gpkg"
        if not parameters['ve']:
            parameters['ve'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "ve_empty.gpkg"), "ve_empty", "ogr")
        if not parameters['bgtinlooptabel']:
            parameters['bgtinlooptabel'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "bgt_inlooptabel_empty.gpkg"), "bgt_inlooptabel_empty", "ogr")
        # TODO input plancap niet inbegrepen in dit alternatief
        # if not parameters['inputplancap']:
        #     parameters['inputplancap'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "plancap_empty.gpkg"), "plancap_empty", "ogr")
        if not parameters['drinkwater']:
            parameters['drinkwater'] = QgsVectorLayer(os.path.join(cmd_folder, dummy_folder, "drinkwater_empty.gpkg"), "drinkwater_empty", "ogr")
        #QgsProject.instance().reloadAllLayers() # this is very important to prevent mix ups with 'in memory' layers
        # let op: vanaf if parameters['bgtinlooptabel']: is het script afwijkend van model tbv optionaliteit bgt.
        self.result_folder = parameters['result_folder']


        feedback = QgsProcessingMultiStepFeedback(82, model_feedback)
        results = {}
        outputs = {}

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

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Create spatial index BAG
        alg_params = {
            'INPUT': outputs['FieldCalculatorBag']['OUTPUT']
        }
        outputs['CreateSpatialIndexBag'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Create spatial index BGTinlooptabel
        alg_params = {
            'INPUT': parameters['bgtinlooptabel']
        }
        outputs['CreateSpatialIndexBgtinlooptabel'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Create spatial index Drinkwater
        alg_params = {
            'INPUT': parameters['drinkwater']
        }
        outputs['CreateSpatialIndexDrinkwater'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Create spatial index VE
        alg_params = {
            'INPUT': parameters['ve']
        }
        outputs['CreateSpatialIndexVe'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Create spatial index Rioleringsgebieden tbv stap 3
        alg_params = {
            'INPUT': parameters['bemalingsgebiedenstats']
        }
        outputs['CreateSpatialIndexRioleringsgebiedenTbvStap3'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Intersection BGT inlooptabel met rioleringsgebieden tbv stap 3
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['CreateSpatialIndexBgtinlooptabel']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['CreateSpatialIndexRioleringsgebiedenTbvStap3']['OUTPUT'],
            'OVERLAY_FIELDS': ['BEM_ID'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IntersectionBgtInlooptabelMetRioleringsgebiedenTbvStap3'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
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
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBgtinlooptabelOppv'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator GEM_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'GEM_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("gemengd_riool"/100)',
            'INPUT': outputs['FieldCalculatorBgtinlooptabelOppv']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorGem_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Statistics by categories GEM_m2
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorGem_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'GEM_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesGem_m2'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Field calculator GEM_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'GEM_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesGem_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorGem_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator HWA_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'HWA_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("hemelwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorGem_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorHwa_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Statistics by categories HWA_m2
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorHwa_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'HWA_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesHwa_m2'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Field calculator VGS_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VGS_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("vgs_hemelwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorHwa_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVgs_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID GEM_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['GEM_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['CreateSpatialIndexRioleringsgebiedenTbvStap3']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorGem_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idGem_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Statistics by categories VGS_m2_BEM_ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorVgs_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'VGS_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesVgs_m2_bem_id'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Field calculator HWA_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'HWA_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesHwa_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorHwa_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("vuilwaterriool"/100)',
            'INPUT': outputs['FieldCalculatorVgs_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Field calculator VGS_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VGS_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesVgs_m2_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVgs_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID HWA_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['HWA_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idGem_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorHwa_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idHwa_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Field calculator DIT_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DIT_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("infiltratievoorziening"/100)',
            'INPUT': outputs['FieldCalculatorDwa_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDit_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Statistics by categories DWA_m2_BEM_ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorDwa_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DWA_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesDwa_m2_bem_id'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID VGS_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['VGS_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idHwa_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorVgs_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idVgs_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Statistics by categories DIT_m2_BEM_ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorDit_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DIT_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesDit_m2_bem_id'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator WATER_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'WATER_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("open_water"/100)',
            'INPUT': outputs['FieldCalculatorDit_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorWater_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator DIT_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DIT_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesDit_m2_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDit_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesDwa_m2_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwa_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Statistics by categories WATER_m2_BEM_ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorWater_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'WATER_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesWater_m2_bem_id'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Field calculator MV_m2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'MV_m2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"oppv" * ("graad_verharding"/100) * ("maaiveld"/100)',
            'INPUT': outputs['FieldCalculatorWater_m2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMv_m2'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Statistics by categories MV_m2_BEM_ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['FieldCalculatorMv_m2']['OUTPUT'],
            'VALUES_FIELD_NAME': 'MV_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMv_m2_bem_id'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID DWA_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['DWA_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idVgs_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorDwa_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idDwa_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID DIT_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['DIT_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idDwa_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorDit_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idDit_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Field calculator WATER_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'WATER_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesWater_m2_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorWater_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Field calculator MV_ha
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'MV_ha',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("sum"/10000,4)',
            'INPUT': outputs['StatisticsByCategoriesMv_m2_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMv_ha'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID WATER_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['WATER_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idDit_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorWater_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idWater_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value BEM_ID MV_ha
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['MV_ha'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idWater_ha']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorMv_ha']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBem_idMv_ha'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator Berging_mm
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Berging_mm',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(("BERGING_M3"/("GEM_ha"*10000))*1000,2)',
            'INPUT': outputs['JoinAttributesByFieldValueBem_idMv_ha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBerging_mm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_GEM_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'POC_GEM_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("GEM_ha" IS NULL, 0, ("GEM_ha"*10000) * (0.7/1000))',
            'INPUT': outputs['FieldCalculatorBerging_mm']['OUTPUT'],
            'OUTPUT': parameters['Poc_gem_m3h']
        }
        outputs['FieldCalculatorPoc_gem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Poc_gem_m3h'] = outputs['FieldCalculatorPoc_gem_m3h']['OUTPUT']

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Field calculator POC_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'POC_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("VGS_ha" IS NULL, 0, ("VGS_ha"*10000) * (0.7/1000))',
            'INPUT': outputs['FieldCalculatorPoc_gem_m3h']['OUTPUT'],
            'OUTPUT': parameters['Poc_vgs_m3h']
        }
        outputs['FieldCalculatorPoc_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Poc_vgs_m3h'] = outputs['FieldCalculatorPoc_vgs_m3h']['OUTPUT']

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Create spatial index POC_VGS_m3h
        alg_params = {
            'INPUT': outputs['FieldCalculatorPoc_vgs_m3h']['OUTPUT']
        }
        outputs['CreateSpatialIndexPoc_vgs_m3h'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) - aantal BAG objecten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexPoc_vgs_m3h']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexBag']['OUTPUT'],
            'JOIN_FIELDS': ['BAG'],
            'PREDICATE': [0],  # intersect
            'SUMMARIES': [0],  # count
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryAantalBagObjecten'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA_BAG
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'IF("BAG_count" IS NULL, 0, @inw_per_adres * (12/1000) * "BAG_count")',
            'INPUT': outputs['JoinAttributesByLocationSummaryAantalBagObjecten']['OUTPUT'],
            'OUTPUT': parameters['Dwa_bag_m3h']
        }
        outputs['FieldCalculatorDwa_bag'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Dwa_bag_m3h'] = outputs['FieldCalculatorDwa_bag']['OUTPUT']

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Create spatial index DWA_BAG
        alg_params = {
            'INPUT': outputs['FieldCalculatorDwa_bag']['OUTPUT']
        }
        outputs['CreateSpatialIndexDwa_bag'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Join attributes by location (summary) DRINKWATER
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexDwa_bag']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexDrinkwater']['OUTPUT'],
            'JOIN_FIELDS': ['PAR_RESULT','ZAK_RESULT'],
            'PREDICATE': [0],  # intersect
            'SUMMARIES': [5],  # sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationSummaryDrinkwater'] = processing.run('qgis:joinbylocationsummary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Field calculator PAR_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'PAR_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("PAR_RESULT_sum" IS NULL, 0, round("PAR_RESULT_sum"/1000,2))',
            'INPUT': outputs['JoinAttributesByLocationSummaryDrinkwater']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPar_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Field calculator ZAK_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'ZAK_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("ZAK_RESULT_sum" IS NULL, 0, round("ZAK_RESULT_sum"/1000,2))',
            'INPUT': outputs['FieldCalculatorPar_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorZak_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Field calculator TOT_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'TOT_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"PAR_DRINKWATER_m3h" + "ZAK_DRINKWATER_m3h"',
            'INPUT': outputs['FieldCalculatorZak_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTot_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Drop field(s) PAR_sum en ZAK_sum
        alg_params = {
            'COLUMN': ['PAR_RESULT_sum','ZAK_RESULT_sum'],
            'INPUT': outputs['FieldCalculatorTot_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': parameters['PocBagDrinkwater']
        }
        outputs['DropFieldsPar_sumEnZak_sum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PocBagDrinkwater'] = outputs['DropFieldsPar_sumEnZak_sum']['OUTPUT']

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Create spatial index POC BAG DRINKWATER
        alg_params = {
            'INPUT': outputs['DropFieldsPar_sumEnZak_sum']['OUTPUT']
        }
        outputs['CreateSpatialIndexPocBagDrinkwater'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
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

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Field calculator VE_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("GRONDSLAG_sum" * (12/1000),2)',
            'INPUT': outputs['JoinAttributesByLocationSummaryVe']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVe_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Drop field(s) GRONDSLAG_sum
        alg_params = {
            'COLUMN': ['GRONDSLAG_sum'],
            'INPUT': outputs['FieldCalculatorVe_m3h']['OUTPUT'],
            'OUTPUT': parameters['PocBagDrinkwaterVe']
        }
        outputs['DropFieldsGrondslag_sum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PocBagDrinkwaterVe'] = outputs['DropFieldsGrondslag_sum']['OUTPUT']

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Statistics by categories US_VE_m3h
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['NAAR_BEM_ID'],
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'VALUES_FIELD_NAME': 'VE_m3h',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUs_ve_m3h'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Statistics by categories US_DWA_BAG_m3h
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['NAAR_BEM_ID'],
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DWA_BAG_m3h',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUs_dwa_bag_m3h'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Statistics by categories US_POC_GEM_m3h
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['NAAR_BEM_ID'],
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'VALUES_FIELD_NAME': 'POC_GEM_m3h',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUs_poc_gem_m3h'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Statistics by categories US_TOT_DRINKWATER_m3h
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['NAAR_BEM_ID'],
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'VALUES_FIELD_NAME': 'TOT_DRINKWATER_m3h',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUs_tot_drinkwater_m3h'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_DWA_BAG_m3h
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'NAAR_BEM_ID',
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUs_dwa_bag_m3h']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_dwa_bag_m3h'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Statistics by categories US_POC_VGS_m3h
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['NAAR_BEM_ID'],
            'INPUT': outputs['DropFieldsGrondslag_sum']['OUTPUT'],
            'VALUES_FIELD_NAME': 'POC_VGS_m3h',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUs_poc_vgs_m3h'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Field calculator US_DWA_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'US_DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("sum" IS NULL, 0, round("sum",2))',
            'INPUT': outputs['JoinAttributesByFieldValueUs_dwa_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_dwa_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_DWA_BAG_m3h - sum
        alg_params = {
            'COLUMN': ['sum'],
            'INPUT': outputs['FieldCalculatorUs_dwa_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsUs_dwa_bag_m3hSum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_TOT_DRINKWATER_m3h
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'NAAR_BEM_ID',
            'INPUT': outputs['DropFieldsUs_dwa_bag_m3hSum']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUs_tot_drinkwater_m3h']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_tot_drinkwater_m3h'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Field calculator US_TOT_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'US_TOT_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("sum" IS NULL, 0, round("sum",2))',
            'INPUT': outputs['JoinAttributesByFieldValueUs_tot_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_tot_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_TOT_DRINKWATER_m3h
        alg_params = {
            'COLUMN': ['sum'],
            'INPUT': outputs['FieldCalculatorUs_tot_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsUs_tot_drinkwater_m3h'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_VE_m3h
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'NAAR_BEM_ID',
            'INPUT': outputs['DropFieldsUs_tot_drinkwater_m3h']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUs_ve_m3h']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_ve_m3h'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Field calculator US_VE_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'US_VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("sum" IS NULL, 0, round("sum",2))',
            'INPUT': outputs['JoinAttributesByFieldValueUs_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_ve_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_VE_m3h - sum
        alg_params = {
            'COLUMN': ['sum'],
            'INPUT': outputs['FieldCalculatorUs_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsUs_ve_m3hSum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_POC_GEM_m3h
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'NAAR_BEM_ID',
            'INPUT': outputs['DropFieldsUs_ve_m3hSum']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUs_poc_gem_m3h']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_poc_gem_m3h'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # Field calculator US_POC_GEM_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'US_POC_GEM_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("sum" IS NULL, 0, round("sum",2))',
            'INPUT': outputs['JoinAttributesByFieldValueUs_poc_gem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_poc_gem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_POC_GEM_m3h - sum
        alg_params = {
            'COLUMN': ['sum'],
            'INPUT': outputs['FieldCalculatorUs_poc_gem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsUs_poc_gem_m3hSum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_POC_VGS_m3h
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': 'NAAR_BEM_ID',
            'INPUT': outputs['DropFieldsUs_poc_gem_m3hSum']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUs_poc_vgs_m3h']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_poc_vgs_m3h'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # Field calculator US_POC_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'US_POC_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if( "sum" IS NULL, 0, round("sum",2))',
            'INPUT': outputs['JoinAttributesByFieldValueUs_poc_vgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_poc_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Drop field(s) US_POC_VGS_m3h - sum
        alg_params = {
            'COLUMN': ['sum'],
            'INPUT': outputs['FieldCalculatorUs_poc_vgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsUs_poc_vgs_m3hSum'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_DWA_BAG_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'SOM_DWA_BAG_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("DWA_BAG_m3h" + "US_DWA_BAG_m3h" , 2)',
            'INPUT': outputs['DropFieldsUs_poc_vgs_m3hSum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_dwa_bag_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_DRINKWATER_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'SOM_DRINKWATER_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( "TOT_DRINKWATER_m3h" + "US_TOT_DRINKWATER_m3h" , 2)',
            'INPUT': outputs['FieldCalculatorSom_dwa_bag_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_drinkwater_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_VE_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'SOM_VE_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( "VE_m3h" + "US_VE_m3h",2)',
            'INPUT': outputs['FieldCalculatorSom_drinkwater_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_ve_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_POC_GEM_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'SOM_POC_GEM_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( "POC_GEM_m3h" + "US_POC_GEM_m3h" , 2)',
            'INPUT': outputs['FieldCalculatorSom_ve_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_poc_gem_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # Field calculator SOM_POC_VGS_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'SOM_POC_VGS_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("POC_VGS_m3h" + "US_POC_VGS_m3h", 2)',
            'INPUT': outputs['FieldCalculatorSom_poc_gem_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSom_poc_vgs_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # Field calculator DWA+POC_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DWA+POC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"SOM_DWA_BAG_m3h" + "SOM_POC_GEM_m3h" + "SOM_POC_VGS_m3h"',
            'INPUT': outputs['FieldCalculatorSom_poc_vgs_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDwapoc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Field calculator DRINKWATER+POC_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'DRINKWATER+POC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"SOM_DRINKWATER_m3h" + "SOM_POC_GEM_m3h" + "SOM_POC_VGS_m3h"',
            'INPUT': outputs['FieldCalculatorDwapoc_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDrinkwaterpoc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Field calculator VE+POC_m3h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VE+POC_m3h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"SOM_VE_m3h" + "SOM_POC_GEM_m3h" + "SOM_POC_VGS_m3h"',
            'INPUT': outputs['FieldCalculatorDrinkwaterpoc_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVepoc_m3h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Field calculator VULTIJD_DWA_MIN_h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'VULTIJD_DWA_MIN_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("BERGING_M3"/max("SOM_DWA_BAG_m3h","SOM_DRINKWATER_m3h","SOM_VE_m3h"),2)',
            'INPUT': outputs['FieldCalculatorVepoc_m3h']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorVultijd_dwa_min_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Field calculator LEDIGINGSTIJD_h
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'LEDIGINGSTIJD_h',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("BERGING_M3"/("SOM_POC_GEM_m3h"+"SOM_POC_VGS_m3h"),2)',
            'INPUT': outputs['FieldCalculatorVultijd_dwa_min_h']['OUTPUT'],
            'OUTPUT': parameters['Eindresultaat_huidige_situatie']
        }
        outputs['FieldCalculatorLedigingstijd_h'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindresultaat_huidige_situatie'] = outputs['FieldCalculatorLedigingstijd_h']['OUTPUT']

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
        return 'stap 3.) bereken afvalwaterprognose 2'

    def displayName(self):
        return 'stap 3.) Bereken afvalwaterprognose 2'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Stap3BerekenAfvalwaterprognoseAlt()        
