"""
Model exported as python.
Name : GeoDyn GWSW stap 1 - Bepalen assetkenmerken afvoerpunten rioleringsgebieden
Group : Geodyn cheat
With QGIS : 32207
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProject, QgsProcessingUtils, QgsProcessingParameterFile
from qgis.core import QgsCoordinateReferenceSystem
import processing
import os
from .custom_tools import rename_layers, default_layer, QgsProcessingAlgorithmPost, cmd_folder

        
class GeodynGwswStap1BepalenAssetkenmerkenAfvoerpuntenRioleringsgebieden(QgsProcessingAlgorithmPost):
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_knooppunt', 'Netwerk_knooppunt', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_knooppunt',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_kunstwerk', 'Netwerk_kunstwerk', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_kunstwerk',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_verbinding', 'Netwerk_verbinding', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('netwerk_verbinding',geometryType=1)))
        self.addParameter(QgsProcessingParameterVectorLayer('rioleringsgebieden', 'Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Input bemalingsgebieden',geometryType=2)))
        self.addParameter(QgsProcessingParameterFeatureSink('RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel', 'retainfields afvoerpunt rioleringsgebieden zonder rioolstelsel', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_Afvoerboom', 'Resultaat_stap1_ Afvoerboom', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('RioolstelselsVanEindgebiedenOvernamepunten', 'Rioolstelsels van eindgebieden / overnamepunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('AfvoerpuntenEindgebiedenMetRioolstelsels', 'Afvoerpunten eindgebieden met rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolgemalen_met_kenmerken', 'rioolgemalen_met_kenmerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Rioolstelsels', 'Resultaat stap 1: Rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Dwa_en_gemengde_riolen_die_niet_meedoen_in_bergingsberekening', 'DWA_en_Gemengde_riolen_die_niet_meedoen_in_bergingsberekening', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('RioleringsgebiedenBem_id', 'Rioleringsgebieden BEM_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_1_afvoerrelatie', 'Resultaat_stap_1_Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_1_afvoerpunten', 'Resultaat_stap_1_Afvoerpunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap_1_rioleringsgebieden', 'Resultaat_stap_1_Rioleringsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Bem_idEnStelsel_id', 'BEM_ID en STELSEL_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('StelselsKunstwerkEnMaaiveldstats', 'STELSELS kunstwerk en maaiveldstats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Diameters_en_leidingberging', 'diameters_en_leidingberging', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Knoopberging', 'knoopberging', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('M3_stelselberging', 'M3_StelselBerging', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelatie_rioolgemalen', 'afvoerrelatie_rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('KunstwerkBem_idEnStelsel_id', 'kunstwerk BEM_ID en STELSEL_ID', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('KnpStelselIdEnBobs', 'knp stelsel id en bobs', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('RioleringsgebiedenAllData', 'rioleringsgebieden all data', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('KnpMetKunstwerkdata', 'knp met kunstwerkdata', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
       

        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_knooppunt', 'Netwerk_knooppunt', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_knooppunt',geometryType=0)))
        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_kunstwerk', 'Netwerk_kunstwerk', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_kunstwerk',geometryType=0)))
        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_verbinding', 'Netwerk_verbinding', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('netwerk_verbinding',geometryType=1)))
        # self.addParameter(QgsProcessingParameterVectorLayer('rioleringsgebieden', 'Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Input bemalingsgebieden',geometryType=2)))
        # self.addParameter(QgsProcessingParameterFeatureSink('RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel', 'retainfields afvoerpunt rioleringsgebieden zonder rioolstelsel', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Afvoerboom', 'Resultaat stap1: Afvoerboom', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('RioolstelselsVanEindgebiedenOvernamepunten', 'Rioolstelsels van eindgebieden / overnamepunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('AfvoerpuntenEindgebiedenMetRioolstelsels', 'Afvoerpunten eindgebieden met rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('RioolgemalenMetKenmerken', 'rioolgemalen met kenmerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Rioolstelsels', 'Resultaat stap 1: Rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('DwaEnGemengdeRiolenDieNietMeedoenInBergingsberekening', 'DWA en Gemengde riolen die niet meedoen in bergingsberekening', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('RioleringsgebiedenBem_id', 'Rioleringsgebieden BEM_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Afvoerrelatie', 'Resultaat stap 1: Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Afvoerpunten', 'Resultaat stap 1: Afvoerpunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('ResultaatStap1Rioleringsgebieden', 'Resultaat stap 1: Rioleringsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Bem_idEnStelsel_id', 'BEM_ID en STELSEL_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('StelselsKunstwerkEnMaaiveldstats', 'STELSELS kunstwerk en maaiveldstats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('BergingLeidingEnDiameters', 'BERGING LEIDING - en diameters', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('BergingKnoop', 'BERGING KNOOP', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('M3_stelselberging', 'M3_StelselBerging', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('AfvoerrelatieRioolgemalen', 'afvoerrelatie rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('KunstwerkBem_idEnStelsel_id', 'kunstwerk BEM_ID en STELSEL_ID', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))
       
        

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        #QgsProject.instance().reloadAllLayers() 
        self.result_folder = parameters['result_folder']
        
        feedback = QgsProcessingMultiStepFeedback(111, model_feedback)
        results = {}
        outputs = {}

        # Create spatial index knooppunt
        alg_params = {
            'INPUT': parameters['netwerk_knooppunt']
        }
        outputs['CreateSpatialIndexKnooppunt'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Create spatial index kunstwerk
        alg_params = {
            'INPUT': parameters['netwerk_kunstwerk']
        }
        outputs['CreateSpatialIndexKunstwerk'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Create spatial index verbinding
        alg_params = {
            'INPUT': parameters['netwerk_verbinding']
        }
        outputs['CreateSpatialIndexVerbinding'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Fix geometries rioleringsgebieden
        alg_params = {
            'INPUT': parameters['rioleringsgebieden'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesRioleringsgebieden'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Create spatial index rioleringsgebieden
        alg_params = {
            'INPUT': outputs['FixGeometriesRioleringsgebieden']['OUTPUT']
        }
        outputs['CreateSpatialIndexRioleringsgebieden'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "'BEM' || lpad( $id ,3,0)",
            'INPUT': outputs['CreateSpatialIndexRioleringsgebieden']['OUTPUT'],
            'OUTPUT': parameters['RioleringsgebiedenBem_id']
        }
        outputs['FieldCalculatorBem_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RioleringsgebiedenBem_id'] = outputs['FieldCalculatorBem_id']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # retainfields verbinding
        # alleen relevante attributen behouden
        alg_params = {
            'inputlayer': outputs['CreateSpatialIndexVerbinding']['OUTPUT'],
            'veldenlijst': 'geo_id;Stelsel;naam;type;beginpunt;eindpunt;VormLeiding;BreedteLeiding;HoogteLeiding;LengteLeiding;BobBeginpuntLeiding;BobEindpuntLeiding',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainfieldsVerbinding'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Join attributes by location BEM_ID aan kunstwerk
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexKunstwerk']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID','STELSEL_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBem_idAanKunstwerk'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value KNOOPPUNT - BobBeginpuntLeiding
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['BobBeginpuntLeiding'],
            'FIELD_2': 'beginpunt',
            'INPUT': outputs['CreateSpatialIndexKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['CreateSpatialIndexVerbinding']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKnooppuntBobbeginpuntleiding'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value KNOOPPUNT - BobEindpuntLeiding
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['BobEindpuntLeiding'],
            'FIELD_2': 'eindpunt',
            'INPUT': outputs['JoinAttributesByFieldValueKnooppuntBobbeginpuntleiding']['OUTPUT'],
            'INPUT_2': outputs['CreateSpatialIndexVerbinding']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKnooppuntBobeindpuntleiding'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Join attributes by location BEM_ID aan verbinding
        # Hier kan je de leidingen exporteren die geen BEM_ID hebben (de leidingen die niet volledig binnen één rioleringsgebied liggen)
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['RetainfieldsVerbinding']['Output_layer'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBem_idAanVerbinding'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Extract by expression DWA en Gemengde riolen die niet meedoen in bergingsberekening
        alg_params = {
            'EXPRESSION': '("type" LIKE \'%erg%\' OR\r\n"type" LIKE \'%emengd%\' OR\r\n"type" LIKE \'%uilwate%\' ) AND "BEM_ID" IS NULL',
            'INPUT': outputs['JoinAttributesByLocationBem_idAanVerbinding']['OUTPUT'],
            'OUTPUT': parameters['Dwa_en_gemengde_riolen_die_niet_meedoen_in_bergingsberekening']
        }
        outputs['ExtractByExpressionDwaEnGemengdeRiolenDieNietMeedoenInBergingsberekening'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Dwa_en_gemengde_riolen_die_niet_meedoen_in_bergingsberekening'] = outputs['ExtractByExpressionDwaEnGemengdeRiolenDieNietMeedoenInBergingsberekening']['OUTPUT']

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Merge vector layers US en DS bobs
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:28992'),
            'LAYERS': [outputs['JoinAttributesByFieldValueKnooppuntBobbeginpuntleiding']['OUTPUT'],outputs['JoinAttributesByFieldValueKnooppuntBobeindpuntleiding']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersUsEnDsBobs'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Extract by expression DWA en Gemengde riolen
        alg_params = {
            'EXPRESSION': '("type" LIKE \'%erg%\' OR\r\n"type" LIKE \'%emengd%\' OR\r\n"type" LIKE \'%uilwate%\' ) AND "BEM_ID" IS NOT NULL',
            'INPUT': outputs['JoinAttributesByLocationBem_idAanVerbinding']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionDwaEnGemengdeRiolen'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value US_MV
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'beginpunt',
            'FIELDS_TO_COPY': ['Maaiveldhoogte'],
            'FIELD_2': 'naam',
            'INPUT': outputs['ExtractByExpressionDwaEnGemengdeRiolen']['OUTPUT'],
            'INPUT_2': outputs['CreateSpatialIndexKnooppunt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'US_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUs_mv'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Field calculator laagste bob per object "Min_Bob"
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Min_Bob',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(min("BobBeginpuntLeiding","BobEindpuntLeiding"),2)',
            'INPUT': outputs['MergeVectorLayersUsEnDsBobs']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLaagsteBobPerObjectMin_bob'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Aggregate laagste Bob per naam - "Min_Bob"
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'naam','length': 50,'name': 'naam','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'Min_Bob','length': 0,'name': 'Min_Bob','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'naam',
            'INPUT': outputs['FieldCalculatorLaagsteBobPerObjectMin_bob']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateLaagsteBobPerNaamMin_bob'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value DS_MV
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'eindpunt',
            'FIELDS_TO_COPY': ['Maaiveldhoogte'],
            'FIELD_2': 'naam',
            'INPUT': outputs['JoinAttributesByFieldValueUs_mv']['OUTPUT'],
            'INPUT_2': outputs['CreateSpatialIndexKnooppunt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'DS_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueDs_mv'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - "Min_Bob"
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Min_Bob'],
            'FIELD_2': 'naam',
            'INPUT': outputs['CreateSpatialIndexKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['AggregateLaagsteBobPerNaamMin_bob']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMin_bob'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join attributes by location BEM_ID aan knooppunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['JoinAttributesByFieldValueMin_bob']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBem_idAanKnooppunt'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Buffer 20 cm en dissolve
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 0.2,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['JoinAttributesByFieldValueDs_mv']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 1,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer20CmEnDissolve'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts - naar losse stelsel polygonen
        alg_params = {
            'INPUT': outputs['Buffer20CmEnDissolve']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsNaarLosseStelselPolygonen'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator POLY_ID
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'POLY_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'lpad( $id+1 ,3,0)',
            'INPUT': outputs['MultipartToSinglepartsNaarLosseStelselPolygonen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPoly_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # retainfields POLY_ID
        alg_params = {
            'inputlayer': outputs['FieldCalculatorPoly_id']['OUTPUT'],
            'veldenlijst': 'POLY_ID',
            'Output_layer': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainfieldsPoly_id'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Create spatial index POLY_ID
        alg_params = {
            'INPUT': outputs['RetainfieldsPoly_id']['Output_layer']
        }
        outputs['CreateSpatialIndexPoly_id'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Join attributes by location BEM_ID aan POLY_ID
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexPoly_id']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'JOIN_FIELDS': ['BEM_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBem_idAanPoly_id'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator STELSEL_ID
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'STELSEL_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"BEM_ID" || \'-\' || "POLY_ID"',
            'INPUT': outputs['JoinAttributesByLocationBem_idAanPoly_id']['OUTPUT'],
            'OUTPUT': parameters['Bem_idEnStelsel_id']
        }
        outputs['FieldCalculatorStelsel_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Bem_idEnStelsel_id'] = outputs['FieldCalculatorStelsel_id']['OUTPUT']

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Join attributes by location STELSEL_ID aan kunstwerk
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['JoinAttributesByLocationBem_idAanKunstwerk']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'JOIN_FIELDS': ['STELSEL_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': parameters['KunstwerkBem_idEnStelsel_id']
        }
        outputs['JoinAttributesByLocationStelsel_idAanKunstwerk'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['KunstwerkBem_idEnStelsel_id'] = outputs['JoinAttributesByLocationStelsel_idAanKunstwerk']['OUTPUT']

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Join attributes by location STELSEL_ID aan knooppunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['JoinAttributesByLocationBem_idAanKnooppunt']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'JOIN_FIELDS': ['STELSEL_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': parameters['KnpStelselIdEnBobs']
        }
        outputs['JoinAttributesByLocationStelsel_idAanKnooppunt'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['KnpStelselIdEnBobs'] = outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT']

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Statistics by categories maaiveldhoogte stats per stelsel
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['STELSEL_ID'],
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'VALUES_FIELD_NAME': 'Maaiveldhoogte',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMaaiveldhoogteStatsPerStelsel'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Extract by expression pompen
        alg_params = {
            'EXPRESSION': '"type"=\'Pomp\'',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKunstwerk']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionPompen'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Aggregate kunstwerk stats per STELSEL_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'STELSEL_ID','length': 50,'name': 'STELSEL_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'Doorlaatniveau','length': 0,'name': 'Min_Doorlaatniveau','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'minimum','delimiter': ',','input': 'Drempelniveau','length': 0,'name': 'Min_Drempelniveau','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'count','delimiter': ',','input': 'Doorlaatniveau','length': 0,'name': 'Count_Doorlaatniveau','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'aggregate': 'count','delimiter': ',','input': 'Drempelniveau','length': 0,'name': 'Count_Drempelniveau','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'}],
            'GROUP_BY': 'STELSEL_ID',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKunstwerk']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateKunstwerkStatsPerStelsel_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value kunstwerk stats aan stelsel_polygonen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'INPUT_2': outputs['AggregateKunstwerkStatsPerStelsel_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKunstwerkStatsAanStelsel_polygonen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value maaiveld stats aan stelsel polygonen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': ['q1'],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['JoinAttributesByFieldValueKunstwerkStatsAanStelsel_polygonen']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesMaaiveldhoogteStatsPerStelsel']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'MV_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMaaiveldStatsAanStelselPolygonen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - laagste bob bij knooppunt rioolstelsel
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['STELSEL_ID'],
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'VALUES_FIELD_NAME': 'Min_Bob',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesLaagsteBobBijKnooppuntRioolstelsel'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Aggregate kenmerken afvoerpunt
        # Van alle pompen afvoerpunten gemaakt. Rioolgemalen kunnen meerdere pompen hebben, maar het rioolgemaal is het afvoerpunt waar de gebiedskenmerken aan komen te hangen. Dit is één geografisch punt per rioleringsgebied. In deze stap wordt per knoop-id bepaald: type (altijd pomp binnen deze tool); beginpunt; eindpunt (lozingspunt van het rioolgemaal, daar waar het afvalwater weer in atmosferische druk komt); hoogste inslagpeil dat bij de pompen van het rioolgemaal is geregistreerd; laagste uitslagpeil dat bij de pompen van het rioolgemaal is geregistreerd; aantal pompen in het rioolgemaal; BEM_ID van het rioleringsgebied waar het afvoerpunt het afvalwater van verpompt. LET OP: er wordt in de tool niet gerekend met samenloop van pompen (waardoor een hoger afvoerdebiet mogelijk is). Tool gaat uit van alternerende pompen.

        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'naam','length': 80,'name': 'naam','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'type','length': 80,'name': 'type','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'begin','length': 80,'name': 'begin','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'eind','length': 80,'name': 'eind','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'maximum','delimiter': ',','input': 'Pompcapaciteit','length': 0,'name': 'Pompcapaciteit','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'maximum','delimiter': ',','input': 'AanslagniveauBoven','length': 0,'name': 'AanslagniveauBoven','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'minimum','delimiter': ',','input': 'AfslagniveauBoven','length': 0,'name': 'AfslagniveauBoven','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'count','delimiter': ',','input': 'naam','length': 0,'name': 'Aantalpompen','precision': 0,'sub_type': 0,'type': 4,'type_name': 'int8'},{'aggregate': 'first_value','delimiter': ',','input': 'BEM_ID','length': 20,'name': 'US_BEM_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'STELSEL_ID','length': 50,'name': 'US_STELSEL_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'GROUP_BY': 'naam',
            'INPUT': outputs['ExtractByExpressionPompen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateKenmerkenAfvoerpunt'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value DS_BEM_ID
        # Toevoegen benedenstrooms BEM_ID.
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'eind',
            'FIELDS_TO_COPY': ['BEM_ID','STELSEL_ID'],
            'FIELD_2': 'naam',
            'INPUT': outputs['AggregateKenmerkenAfvoerpunt']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'DS_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueDs_bem_id'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator MV_q1 2 decimalen
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'MV_q1',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("MV_q1",2)',
            'INPUT': outputs['JoinAttributesByFieldValueMaaiveldStatsAanStelselPolygonen']['OUTPUT'],
            'OUTPUT': parameters['StelselsKunstwerkEnMaaiveldstats']
        }
        outputs['FieldCalculatorMv_q12Decimalen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['StelselsKunstwerkEnMaaiveldstats'] = outputs['FieldCalculatorMv_q12Decimalen']['OUTPUT']

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - laagste bob per stelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesLaagsteBobBijKnooppuntRioolstelsel']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueLaagsteBobPerStelsel'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Extract by expression - "STELSEL_ID" = "STELSEL_ID_2"  AND "min" = "Min_Bob"
        alg_params = {
            'EXPRESSION': '"STELSEL_ID" = "STELSEL_ID_2"  AND "min" = "Min_Bob"',
            'INPUT': outputs['JoinAttributesByFieldValueLaagsteBobPerStelsel']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionStelsel_idStelsel_id_2AndMinMin_bob'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Delete duplicates by attribute - 1 laagste punt overhouden
        alg_params = {
            'FIELDS': ['STELSEL_ID'],
            'INPUT': outputs['ExtractByExpressionStelsel_idStelsel_id_2AndMinMin_bob']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicatesByAttribute1LaagstePuntOverhouden'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value knooppunt stats kunstwerken en maaiveldhoogte
        # plakken van kunstwerkkenmerken en maaiveldhoogtes aan knopen t.b.v. bergingsberekening
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': ['Min_Doorlaatniveau','Min_Drempelniveau','Count_Doorlaatniveau','Count_Drempelniveau','MV_q1'],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorMv_q12Decimalen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': parameters['KnpMetKunstwerkdata']
        }
        outputs['JoinAttributesByFieldValueKnooppuntStatsKunstwerkenEnMaaiveldhoogte'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['KnpMetKunstwerkdata'] = outputs['JoinAttributesByFieldValueKnooppuntStatsKunstwerkenEnMaaiveldhoogte']['OUTPUT']

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Join attributes by location verbinding BEM_ID en STELSEL_ID en stats
        # plakken van kunstwerkkenmerken en maaiveldhoogtes aan leidingen t.b.v. bergingsberekening
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractByExpressionDwaEnGemengdeRiolen']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorMv_q12Decimalen']['OUTPUT'],
            'JOIN_FIELDS': ['STELSEL_ID','Min_Doorlaatniveau','Min_Drempelniveau','Count_Doorlaatniveau','Count_Drempelniveau','MV_q1'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationVerbindingBem_idEnStelsel_idEnStats'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Field calculator BERGING LEIDING
        # Voor de volgende leidingen wordt berging betekend: Alle leidingen waarvan de gemiddelde bovenkantbuis onder overstortdrempel ligt; Indien geen dremepelniveau aanwezig is dan alle leidingen waarvan de gemiddelde bovenkantbuis onder MV_q1 minus 60 cm ligt; Kan ook een diameterplaatje van worden gemaakt
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'B_M3_LEI',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if(mean( "BobBeginpuntLeiding" , "BobEindpuntLeiding" ) +  ("HoogteLeiding"/1000) > if( "Min_Drempelniveau" IS NOT NULL,  "Min_Drempelniveau" , "MV_q1"-0.6 ), 0,\r\nif("VormLeiding" LIKE \'%Ei%\' , round((((0.25 * pi()*((("BreedteLeiding"/1000)^2))/2))+(((("BreedteLeiding"/1000)+(("HoogteLeiding"-"BreedteLeiding")/1000))/2)*(("BreedteLeiding"/1000/2)+(("HoogteLeiding"-"BreedteLeiding")/1000/2)))+((0.25*pi()*(("HoogteLeiding"-"BreedteLeiding")/1000)^2/2))) *  "LengteLeiding" ,2),\r\nif("VormLeiding" = \'Rechthoekig\' , round( ("BreedteLeiding" /1000) * ("HoogteLeiding" /1000) *  "LengteLeiding" ,2),\r\nround( ("BreedteLeiding" /1000 /2) * ("BreedteLeiding" /1000 /2) * pi() *  "LengteLeiding" ,2 ))))',
            'INPUT': outputs['JoinAttributesByLocationVerbindingBem_idEnStelsel_idEnStats']['OUTPUT'],
            'OUTPUT': parameters['Diameters_en_leidingberging']
        }
        outputs['FieldCalculatorBergingLeiding'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Diameters_en_leidingberging'] = outputs['FieldCalculatorBergingLeiding']['OUTPUT']

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Aggregate leidingberging per stelsel
        # Hier zitten ook de voorkomende leidingtypen in, bijv.: vuilwaterriool en gemengd riool
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'STELSEL_ID','length': 50,'name': 'STELSEL_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'type','length': 200,'name': 'typen','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'Stelsel','length': 200,'name': 'Stelselnamen','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'B_M3_LEI','length': 0,'name': 'SUM_M3_LEI','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'STELSEL_ID',
            'INPUT': outputs['FieldCalculatorBergingLeiding']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateLeidingbergingPerStelsel'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Field calculator BERGING KNOOP
        # Berging in knoop oppervlak * hoogteverschil tussen laagste bob en: laagste overstortdrempel (als deze aanwezig is anders:); MV_q1 minus 60 cm (nooduitlaatpeil); (kunnen we eventueel ook bijv 1 m putschacht van maken)
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'B_M3_KNP',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(\r\nif( "VormPut" LIKE \'%Rond%\',  (("BreedtePut" /1000/2) * ("BreedtePut" /1000/2) * pi()) * \r\n(if( "Drempelniveau_min" IS NULL,  abs(("MV_q1"-0.6) - Min_Bob),  abs("Drempelniveau_min" - Min_Bob))),\r\n("BreedtePut" /1000) * ("Lengteput" /1000) * if( "Drempelniveau_min" IS NULL,  abs(("MV_q1"-0.6) - Min_Bob),  abs("Drempelniveau_min" - Min_Bob)))\r\n, 2)',
            'INPUT': outputs['JoinAttributesByFieldValueKnooppuntStatsKunstwerkenEnMaaiveldhoogte']['OUTPUT'],
            'OUTPUT': parameters['Knoopberging']
        }
        outputs['FieldCalculatorBergingKnoop'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Knoopberging'] = outputs['FieldCalculatorBergingKnoop']['OUTPUT']

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Aggregate knoopberging per stelsel
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'STELSEL_ID','length': 50,'name': 'STELSEL_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'B_M3_KNP','length': 0,'name': 'SUM_M3_KNP','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'STELSEL_ID',
            'INPUT': outputs['FieldCalculatorBergingKnoop']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateKnoopbergingPerStelsel'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - leidingberging aan stelselpolygonen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'INPUT_2': outputs['AggregateLeidingbergingPerStelsel']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueLeidingbergingAanStelselpolygonen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - knoopberging aan stelselpolygonen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': ['SUM_M3_KNP'],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['JoinAttributesByFieldValueLeidingbergingAanStelselpolygonen']['OUTPUT'],
            'INPUT_2': outputs['AggregateKnoopbergingPerStelsel']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKnoopbergingAanStelselpolygonen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Field calculator - stelselberging
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'M3_StelselBerging',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round("SUM_M3_LEI" + "SUM_M3_KNP",2)',
            'INPUT': outputs['JoinAttributesByFieldValueKnoopbergingAanStelselpolygonen']['OUTPUT'],
            'OUTPUT': parameters['M3_stelselberging']
        }
        outputs['FieldCalculatorStelselberging'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['M3_stelselberging'] = outputs['FieldCalculatorStelselberging']['OUTPUT']

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - berging en kunstwerk stats aan stelsels
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': ['Min_Doorlaatniveau','Min_Drempelniveau','Count_Doorlaatniveau','Count_Drempelniveau','MV_q1'],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['FieldCalculatorStelselberging']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorMv_q12Decimalen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBergingEnKunstwerkStatsAanStelsels'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - berging en kunstwerkstats aan rioolgemalen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['typen','Stelselnamen','SUM_M3_LEI','SUM_M3_KNP','M3_StelselBerging','Min_Doorlaatniveau','Min_Drempelniveau','Count_Doorlaatniveau','Count_Drempelniveau','MV_q1'],
            'INPUT': outputs['JoinAttributesByFieldValueDs_bem_id']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValueBergingEnKunstwerkStatsAanStelsels']['OUTPUT'],
            'MAX_DISTANCE': 3,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestBergingEnKunstwerkstatsAanRioolgemalen'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - rioolgemalen zonder rioolstelsel en rioolgemalen met rioolstelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'begin',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'begin',
            'INPUT': outputs['JoinAttributesByFieldValueDs_bem_id']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByNearestBergingEnKunstwerkstatsAanRioolgemalen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueRioolgemalenZonderRioolstelselEnRioolgemalenMetRioolstelsel'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Drop field(s) _2
        alg_params = {
            'COLUMN': ['naam_2','type_2','begin_2','eind_2','Pompcapaciteit_2','AanslagniveauBoven_2','AfslagniveauBoven_2','Aantalpompen_2','US_BEM_ID_2','US_STELSEL_ID_2','DS_BEM_ID_2','DS_STELSEL_ID_2','n','distance','feature_x','feature_y','nearest_x','nearest_y'],
            'INPUT': outputs['JoinAttributesByFieldValueRioolgemalenZonderRioolstelselEnRioolgemalenMetRioolstelsel']['OUTPUT'],
            'OUTPUT': parameters['Rioolgemalen_met_kenmerken']
        }
        outputs['DropFields_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Rioolgemalen_met_kenmerken'] = outputs['DropFields_2']['OUTPUT']

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines) - afvoerrelatie (lijn) maken
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['DropFields_2']['OUTPUT'],
            'HUB_FIELD': 'eind',
            'HUB_FIELDS': ['begin','eind','US_BEM_ID','US_STELSEL_ID','DS_BEM_ID','DS_STELSEL_ID'],
            'SPOKES': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'SPOKE_FIELD': 'naam',
            'SPOKE_FIELDS': ['naam'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinByLinesHubLinesAfvoerrelatieLijnMaken'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Drop field(s) naam bij afvoerrelatie
        alg_params = {
            'COLUMN': ['naam'],
            'INPUT': outputs['JoinByLinesHubLinesAfvoerrelatieLijnMaken']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsNaamBijAfvoerrelatie'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Field calculator lengte afvoerrelatie
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Lengte',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( $length ,2)',
            'INPUT': outputs['DropFieldsNaamBijAfvoerrelatie']['OUTPUT'],
            'OUTPUT': parameters['Afvoerrelatie_rioolgemalen']
        }
        outputs['FieldCalculatorLengteAfvoerrelatie'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Afvoerrelatie_rioolgemalen'] = outputs['FieldCalculatorLengteAfvoerrelatie']['OUTPUT']

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Field calculator USDS_BEM_ID
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'USDS_BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"US_BEM_ID" || \'/\' || "DS_BEM_ID"',
            'INPUT': outputs['FieldCalculatorLengteAfvoerrelatie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUsds_bem_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Extract by expression US_BEM_ID <> DS_BEM_ID
        alg_params = {
            'EXPRESSION': '"US_BEM_ID" <> "DS_BEM_ID"',
            'INPUT': outputs['FieldCalculatorUsds_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionUs_bem_idDs_bem_id'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Aggregate USDS_BEM_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'USDS_BEM_ID','length': 50,'name': 'USDS_BEM_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'Lengte','length': 0,'name': 'Min_Lengte','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'USDS_BEM_ID',
            'INPUT': outputs['ExtractByExpressionUs_bem_idDs_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateUsds_bem_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts - van multilijn naar enkele lijnen
        alg_params = {
            'INPUT': outputs['AggregateUsds_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsVanMultilijnNaarEnkeleLijnen'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Field calculator lengte afvoerrelatie t.b.v. selectie
        # Stap wordt alleen gedaan om vervolgens op te kunnen selecteren
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Lengte',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round( $length ,2)',
            'INPUT': outputs['MultipartToSinglepartsVanMultilijnNaarEnkeleLijnen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLengteAfvoerrelatieTbvSelectie'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Extract by expression - afoerrelatie kortste lijn exporteren
        alg_params = {
            'EXPRESSION': '"Min_Lengte" = "Lengte"',
            'INPUT': outputs['FieldCalculatorLengteAfvoerrelatieTbvSelectie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionAfoerrelatieKortsteLijnExporteren'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices - extract beginpunt afvoerrelatie van afvoerpunt
        alg_params = {
            'INPUT': outputs['ExtractByExpressionAfoerrelatieKortsteLijnExporteren']['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSpecificVerticesExtractBeginpuntAfvoerrelatieVanAfvoerpunt'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - kenmerken afvoerrelatie koppelen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractByExpressionAfoerrelatieKortsteLijnExporteren']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorLengteAfvoerrelatie']['OUTPUT'],
            'JOIN_FIELDS': ['begin','eind','US_BEM_ID','US_STELSEL_ID','DS_BEM_ID','DS_STELSEL_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [2],  # equal
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationKenmerkenAfvoerrelatieKoppelen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # Drop field(s)- afvoerrelatie van afvoerpunten - verwijderen irrelevante attributen
        # Min_Lengte en Lengte zijn niet relevant, zegt niets over de lengte van de persleiding
        alg_params = {
            'COLUMN': ['Min_Lengte','Lengte'],
            'INPUT': outputs['JoinAttributesByLocationKenmerkenAfvoerrelatieKoppelen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsAfvoerrelatieVanAfvoerpuntenVerwijderenIrrelevanteAttributen'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - join kenmerken afvoerpunten
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['JoinAttributesByFieldValueRioolgemalenZonderRioolstelselEnRioolgemalenMetRioolstelsel']['OUTPUT'],
            'JOIN': outputs['ExtractSpecificVerticesExtractBeginpuntAfvoerrelatieVanAfvoerpunt']['OUTPUT'],
            'JOIN_FIELDS': ['Lengte'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [2],  # equal
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationJoinKenmerkenAfvoerpunten'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # Field calculator stap1_datum - AFVOERRELATIE
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'stap1_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['DropFieldsAfvoerrelatieVanAfvoerpuntenVerwijderenIrrelevanteAttributen']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_1_afvoerrelatie']
        }
        outputs['FieldCalculatorStap1_datumAfvoerrelatie'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_1_afvoerrelatie'] = outputs['FieldCalculatorStap1_datumAfvoerrelatie']['OUTPUT']

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # Drop field(s) - afvoerpunten - verwijderen irrelevante attributen
        alg_params = {
            'COLUMN': ['Naam_2','Lengte'],
            'INPUT': outputs['JoinAttributesByLocationJoinKenmerkenAfvoerpunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsAfvoerpuntenVerwijderenIrrelevanteAttributen'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - rioolgemalen aan rioolstelsels
        # Even controleren of dit goed gaat. Hier kan je de 'eindgebieden' uit filteren dit zijn de rioolstelsels zonder pomprelatie
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['naam','type','begin','eind','Pompcapaciteit','AanslagniveauBoven','AfslagniveauBoven','Aantalpompen','US_BEM_ID','US_STELSEL_ID','DS_BEM_ID','DS_STELSEL_ID'],
            'INPUT': outputs['JoinAttributesByFieldValueBergingEnKunstwerkStatsAanStelsels']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsAfvoerpuntenVerwijderenIrrelevanteAttributen']['OUTPUT'],
            'MAX_DISTANCE': 3,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestRioolgemalenAanRioolstelsels'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - stelsels in rioleringsgebieden zonder afvoerpunt
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['BEM_ID'],
            'INPUT': outputs['JoinAttributesByNearestRioolgemalenAanRioolstelsels']['OUTPUT'],
            'VALUES_FIELD_NAME': 'DS_BEM_ID',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesStelselsInRioleringsgebiedenZonderAfvoerpunt'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - statistics aan rioolstelsels
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['min'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByNearestRioolgemalenAanRioolstelsels']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesStelselsInRioleringsgebiedenZonderAfvoerpunt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStatisticsAanRioolstelsels'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # Drop field(s) STELSEL_ID_2
        alg_params = {
            'COLUMN': ['STELSEL_ID_2','n','distance','feature_x','feature_y','nearest_x','nearest_y'],
            'INPUT': outputs['JoinAttributesByNearestRioolgemalenAanRioolstelsels']['OUTPUT'],
            'OUTPUT': parameters['ResultaatStap1Rioolstelsels']
        }
        outputs['DropFieldsStelsel_id_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ResultaatStap1Rioolstelsels'] = outputs['DropFieldsStelsel_id_2']['OUTPUT']

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # Field calculator - lengte_txt tbv extract
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'lengte_txt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': 'length("min")',
            'INPUT': outputs['JoinAttributesByFieldValueStatisticsAanRioolstelsels']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLengte_txtTbvExtract'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # Extract by expression - rioolstelsels van eindrioolgemalen / overnamepunten
        alg_params = {
            'EXPRESSION': '"lengte_txt" = 0',
            'INPUT': outputs['FieldCalculatorLengte_txtTbvExtract']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionRioolstelselsVanEindrioolgemalenOvernamepunten'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Drop field(s) - rioolstelsels eindrioleringsgebieden
        alg_params = {
            'COLUMN': ['min','lengte_txt'],
            'INPUT': outputs['ExtractByExpressionRioolstelselsVanEindrioolgemalenOvernamepunten']['OUTPUT'],
            'OUTPUT': parameters['RioolstelselsVanEindgebiedenOvernamepunten']
        }
        outputs['DropFieldsRioolstelselsEindrioleringsgebieden'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RioolstelselsVanEindgebiedenOvernamepunten'] = outputs['DropFieldsRioolstelselsEindrioleringsgebieden']['OUTPUT']

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['DeleteDuplicatesByAttribute1LaagstePuntOverhouden']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsRioolstelselsEindrioleringsgebieden']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValue'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # Retain fields eindknoop rioolstelsel eindgebied
        alg_params = {
            'FIELDS': ['naam','BEM_ID','STELSEL_ID'],
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsEindknoopRioolstelselEindgebied'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - stelselkenmerken aan afvoerpunten van eindrioolstelsels / overnamepunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'STELSEL_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'STELSEL_ID',
            'INPUT': outputs['RetainFieldsEindknoopRioolstelselEindgebied']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsRioolstelselsEindrioleringsgebieden']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStelselkenmerkenAanAfvoerpuntenVanEindrioolstelselsOvernamepunten'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Drop field(s) afvoerpunt - BEM_ID_2;STELSEL_ID_2;naam_2
        alg_params = {
            'COLUMN': ['BEM_ID_2','STELSEL_ID_2','naam_2'],
            'INPUT': outputs['JoinAttributesByFieldValueStelselkenmerkenAanAfvoerpuntenVanEindrioolstelselsOvernamepunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsAfvoerpuntBem_id_2stelsel_id_2naam_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Aggregate BEM_ID maximale berging
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'BEM_ID','length': 20,'name': 'BEM_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'maximum','delimiter': ',','input': 'M3_StelselBerging','length': 0,'name': 'M3_StelselBerging','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'BEM_ID',
            'INPUT': outputs['DropFieldsAfvoerpuntBem_id_2stelsel_id_2naam_2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateBem_idMaximaleBerging'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Field calculator - att tbv selectie
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Select',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "'Select'",
            'INPUT': outputs['AggregateBem_idMaximaleBerging']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAttTbvSelectie'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(82)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - selctie aan stelsels plakken
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'M3_StelselBerging',
            'FIELDS_TO_COPY': ['Select'],
            'FIELD_2': 'M3_StelselBerging',
            'INPUT': outputs['DropFieldsAfvoerpuntBem_id_2stelsel_id_2naam_2']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorAttTbvSelectie']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueSelctieAanStelselsPlakken'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(83)
        if feedback.isCanceled():
            return {}

        # Drop field(s) - select
        alg_params = {
            'COLUMN': ['Select','layer','path'],
            'INPUT': outputs['JoinAttributesByFieldValueSelctieAanStelselsPlakken']['OUTPUT'],
            'OUTPUT': parameters['AfvoerpuntenEindgebiedenMetRioolstelsels']
        }
        outputs['DropFieldsSelect'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['AfvoerpuntenEindgebiedenMetRioolstelsels'] = outputs['DropFieldsSelect']['OUTPUT']

        feedback.setCurrentStep(84)
        if feedback.isCanceled():
            return {}

        # Merge vector layers - afvoerpunten samenvoegen
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['DropFieldsAfvoerpuntenVerwijderenIrrelevanteAttributen']['OUTPUT'],outputs['DropFieldsSelect']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersAfvoerpuntenSamenvoegen'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(85)
        if feedback.isCanceled():
            return {}

        # Field calculator US_BEM_ID where NULL
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'US_BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("US_BEM_ID" IS NULL, "BEM_ID", "US_BEM_ID")',
            'INPUT': outputs['MergeVectorLayersAfvoerpuntenSamenvoegen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_bem_idWhereNull'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(86)
        if feedback.isCanceled():
            return {}

        # Field calculator US_STELSEL_ID where NULL
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'US_STELSEL_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("US_STELSEL_ID" IS NULL, "STELSEL_ID", "US_STELSEL_ID")',
            'INPUT': outputs['FieldCalculatorUs_bem_idWhereNull']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_stelsel_idWhereNull'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(87)
        if feedback.isCanceled():
            return {}

        # Field calculator begin where NULL
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'begin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("begin" IS NULL, "naam","begin")',
            'INPUT': outputs['FieldCalculatorUs_stelsel_idWhereNull']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBeginWhereNull'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(88)
        if feedback.isCanceled():
            return {}

        # Drop field(s) BEM_ID;STELSEL_ID;POLY_ID
        # afvoerpunten van rioleringsgebieden met rioolstelsels
        alg_params = {
            'COLUMN': ['BEM_ID','STELSEL_ID','POLY_ID','layer','path','naam_2','type_2','begin_2','eind_2','Pompcapaciteit_2','AanslagniveauBoven_2','AfslagniveauBoven_2','Aantalpompen_2','US_BEM_ID_2','US_STELSEL_ID_2','DS_BEM_ID_2','DS_STELSEL_ID_2','STELSEL_ID_3'],
            'INPUT': outputs['FieldCalculatorBeginWhereNull']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsBem_idstelsel_idpoly_id'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(89)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Kenmerken afvoerpunten aan Rioleringsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'US_BEM_ID',
            'INPUT': outputs['FieldCalculatorBem_id']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsBem_idstelsel_idpoly_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': parameters['RioleringsgebiedenAllData']
        }
        outputs['JoinAttributesByFieldValueKenmerkenAfvoerpuntenAanRioleringsgebieden'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RioleringsgebiedenAllData'] = outputs['JoinAttributesByFieldValueKenmerkenAfvoerpuntenAanRioleringsgebieden']['OUTPUT']

        feedback.setCurrentStep(90)
        if feedback.isCanceled():
            return {}

        # Drop field(s) - naam_2;type_2;begin_2;eind_2;Pompcapaciteit_2;AanslagniveauBoven_2;AfslagniveauBoven_2;Aantalpompen_2;US_BEM_ID_2;US_STELSEL_ID_2;DS_BEM_ID_2;DS_STELSEL_ID_2;DS_STELSEL_ID_3
        alg_params = {
            'COLUMN': ['naam_2','type_2','begin_2','eind_2','Pompcapaciteit_2','AanslagniveauBoven_2','AfslagniveauBoven_2','Aantalpompen_2','US_BEM_ID_2','US_STELSEL_ID_2','DS_BEM_ID_2','DS_STELSEL_ID_2','DS_STELSEL_ID_3'],
            'INPUT': outputs['JoinAttributesByFieldValueKenmerkenAfvoerpuntenAanRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsNaam_2type_2begin_2eind_2pompcapaciteit_2aanslagniveauboven_2afslagniveauboven_2aantalpompen_2us_bem_id_2us_stelsel_id_2ds_bem_id_2ds_stelsel_id_2ds_stelsel_id_3'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(91)
        if feedback.isCanceled():
            return {}

        # Extract by expression BEM_ID waar "naam" leeg is
        alg_params = {
            'EXPRESSION': '"naam" IS NULL',
            'INPUT': outputs['DropFieldsNaam_2type_2begin_2eind_2pompcapaciteit_2aanslagniveauboven_2afslagniveauboven_2aantalpompen_2us_bem_id_2us_stelsel_id_2ds_bem_id_2ds_stelsel_id_2ds_stelsel_id_3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionBem_idWaarNaamLeegIs'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(92)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value knoopnummer aan leeg rioleringsgebied
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['naam'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['ExtractByExpressionBem_idWaarNaamLeegIs']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocationBem_idAanKnooppunt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKnoopnummerAanLeegRioleringsgebied'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(93)
        if feedback.isCanceled():
            return {}

        # Join attributes by field - vullen lege rioleringsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['naam_2'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['DropFieldsNaam_2type_2begin_2eind_2pompcapaciteit_2aanslagniveauboven_2afslagniveauboven_2aantalpompen_2us_bem_id_2us_stelsel_id_2ds_bem_id_2ds_stelsel_id_2ds_stelsel_id_3']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValueKnoopnummerAanLeegRioleringsgebied']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldVullenLegeRioleringsgebieden'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(94)
        if feedback.isCanceled():
            return {}

        # Field calculator BEM_ID "naam" vullen
        alg_params = {
            'FIELD_LENGTH': 80,
            'FIELD_NAME': 'naam',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("naam" IS NULL,"naam_2","naam")',
            'INPUT': outputs['JoinAttributesByFieldVullenLegeRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBem_idNaamVullen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(95)
        if feedback.isCanceled():
            return {}

        # Field calculator "US_BEM_ID" vullen
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'US_BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("US_BEM_ID" IS NULL,"BEM_ID","US_BEM_ID")',
            'INPUT': outputs['FieldCalculatorBem_idNaamVullen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_bem_idVullen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(96)
        if feedback.isCanceled():
            return {}

        # Field calculator "begin" in leeg rioleringsgebied vullen
        alg_params = {
            'FIELD_LENGTH': 80,
            'FIELD_NAME': 'begin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("begin" IS NULL,"naam","begin")',
            'INPUT': outputs['FieldCalculatorUs_bem_idVullen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBeginInLeegRioleringsgebiedVullen'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(97)
        if feedback.isCanceled():
            return {}

        # Drop field(s) "naam_2"
        alg_params = {
            'COLUMN': ['naam_2','n','distance','feature_x','feature_y','nearest_x','nearest_y'],
            'INPUT': outputs['FieldCalculatorBeginInLeegRioleringsgebiedVullen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsNaam_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(98)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - opzoeken afvoerpunt van rioleringsgebieden zonder rioolstelsel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'BEM_ID',
            'FIELDS_TO_COPY': ['naam_2'],
            'FIELD_2': 'BEM_ID',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunt']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorBeginInLeegRioleringsgebiedVullen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueOpzoekenAfvoerpuntVanRioleringsgebiedenZonderRioolstelsel'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(99)
        if feedback.isCanceled():
            return {}

        # Field calculator stap1_datum - Rioleringsgebieden
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'stap1_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['DropFieldsNaam_2']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_1_rioleringsgebieden']
        }
        outputs['FieldCalculatorStap1_datumRioleringsgebieden'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_1_rioleringsgebieden'] = outputs['FieldCalculatorStap1_datumRioleringsgebieden']['OUTPUT']

        feedback.setCurrentStep(100)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '"naam" = "naam_2"',
            'INPUT': outputs['JoinAttributesByFieldValueOpzoekenAfvoerpuntVanRioleringsgebiedenZonderRioolstelsel']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(101)
        if feedback.isCanceled():
            return {}

        # Point on surface - rioleringsgebieden US_BEM_ID
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['FieldCalculatorStap1_datumRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointOnSurfaceRioleringsgebiedenUs_bem_id'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(102)
        if feedback.isCanceled():
            return {}

        # retainfields afvoerpunt rioleringsgebieden zonder rioolstelsel
        alg_params = {
            'inputlayer': outputs['ExtractByExpression']['OUTPUT'],
            'veldenlijst': 'naam;type;BEM_ID',
            'Output_layer': parameters['RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel']
        }
        outputs['RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel'] = outputs['RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel']['Output_layer']

        feedback.setCurrentStep(103)
        if feedback.isCanceled():
            return {}

        # Field calculator DS_BEM_ID - POS
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'POS',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"POS"',
            'INPUT': outputs['PointOnSurfaceRioleringsgebiedenUs_bem_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDs_bem_idPos'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(104)
        if feedback.isCanceled():
            return {}

        # Merge vector layers - afvoerpunten
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['RetainfieldsAfvoerpuntRioleringsgebiedenZonderRioolstelsel']['Output_layer'],outputs['DropFieldsBem_idstelsel_idpoly_id']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersAfvoerpunten'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(105)
        if feedback.isCanceled():
            return {}

        # Field calculator "begin" samenvoeging afvoerpunten
        alg_params = {
            'FIELD_LENGTH': 80,
            'FIELD_NAME': 'begin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("begin" IS NULL,"naam","begin")',
            'INPUT': outputs['MergeVectorLayersAfvoerpunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBeginSamenvoegingAfvoerpunten'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(106)
        if feedback.isCanceled():
            return {}

        # Field calculator "US_BEM_ID" samenvoeging afvoerpunten
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'US_BEM_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("US_BEM_ID" IS NULL,"BEM_ID","US_BEM_ID")',
            'INPUT': outputs['FieldCalculatorBeginSamenvoegingAfvoerpunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUs_bem_idSamenvoegingAfvoerpunten'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(107)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines) - afvoerboom maken
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['PointOnSurfaceRioleringsgebiedenUs_bem_id']['OUTPUT'],
            'HUB_FIELD': 'DS_BEM_ID',
            'HUB_FIELDS': [''],
            'SPOKES': outputs['FieldCalculatorDs_bem_idPos']['OUTPUT'],
            'SPOKE_FIELD': 'US_BEM_ID',
            'SPOKE_FIELDS': ['X'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinByLinesHubLinesAfvoerboomMaken'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(108)
        if feedback.isCanceled():
            return {}

        # Drop field(s) BEM_ID;layer;path
        alg_params = {
            'COLUMN': ['BEM_ID','layer','path'],
            'INPUT': outputs['FieldCalculatorUs_bem_idSamenvoegingAfvoerpunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsBem_idlayerpath'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(109)
        if feedback.isCanceled():
            return {}

        # retainfields afvoerboom
        alg_params = {
            'inputlayer': outputs['JoinByLinesHubLinesAfvoerboomMaken']['OUTPUT'],
            'veldenlijst': 'naam;begin;eind;US_BEM_ID;DS_BEM_ID',
            'Output_layer': parameters['Resultaat_stap1_Afvoerboom']
        }
        outputs['RetainfieldsAfvoerboom'] = processing.run('GeoDynTools:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_Afvoerboom'] = outputs['RetainfieldsAfvoerboom']['Output_layer']

        feedback.setCurrentStep(110)
        if feedback.isCanceled():
            return {}

        # Field calculator stap1_datum - Afvoerpunt
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'stap1_datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['DropFieldsBem_idlayerpath']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap_1_afvoerpunten']
        }
        outputs['FieldCalculatorStap1_datumAfvoerpunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap_1_afvoerpunten'] = outputs['FieldCalculatorStap1_datumAfvoerpunt']['OUTPUT']

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
        return 'GeoDyn GWSW stap 1 - Bepalen assetkenmerken afvoerpunten rioleringsgebieden'

    def displayName(self):
        return 'GeoDyn GWSW stap 1 - Bepalen assetkenmerken afvoerpunten rioleringsgebieden'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return GeodynGwswStap1BepalenAssetkenmerkenAfvoerpuntenRioleringsgebieden()
