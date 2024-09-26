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
from qgis.core import QgsCoordinateReferenceSystem, QgsProcessingParameterDefinition
import processing
import os
from .custom_tools import default_layer, QgsProcessingAlgorithmPost, cmd_folder

        
class GeodynGwswStap1BepalenAssetkenmerkenAfvoerpuntenRioleringsgebieden(QgsProcessingAlgorithmPost):
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('buffer_rioolstelsel', 'Buffer_Rioolstelsel', type=QgsProcessingParameterNumber.Double, minValue=0.1, maxValue=5, defaultValue=0.2))
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_knooppunt', 'Netwerk_knooppunt', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_knooppunt',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_kunstwerk', 'Netwerk_kunstwerk', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_kunstwerk',geometryType=0)))
        self.addParameter(QgsProcessingParameterVectorLayer('netwerk_verbinding', 'Netwerk_verbinding', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('netwerk_verbinding',geometryType=1)))
        self.addParameter(QgsProcessingParameterVectorLayer('rioleringsgebieden', 'Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Rioleringsgebieden',geometryType=2)))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolgemalen', 'Rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id_kenmerken_kunstwerken', 'Stelsel_ID_kenmerken_kunstwerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id_leidingberging_m3', 'Stelsel_ID_Leidingberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_idKnooppuntberging_m3', 'Stelsel_ID Knooppuntberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerrelatie', 'Resultaat_Stap1_Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_rioolstelsels', 'Resultaat_Stap1_Rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerpunten', 'Resultaat_Stap1_Afvoerpunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Knooppuntberging_m3', 'Knooppuntberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Vuilwaterriolen_en_gemengd_riolen_die_niet_meedoen_in_bergingsberekening', 'Vuilwaterriolen_en_Gemengd_riolen_die_niet_meedoen_in_bergingsberekening', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('Lozingspunten_rioolgemalen', 'Lozingspunten_Rioolgemalen', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Controle_kunstwerken', 'Controle_Kunstwerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Leidingberging_m3', 'Leidingberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id', 'Stelsel_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelatie_rioolgemalen', 'Afvoerrelatie_Rioolgemalen', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerboom', 'Resultaat_Stap1_Afvoerboom', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_rioleringsgebieden', 'Resultaat_Stap1_Rioleringsgebieden', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Rioolgemalen_zonder_afvoerrelatie', 'Rioolgemalen_zonder_afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))     

        # self.addParameter(QgsProcessingParameterNumber('buffer_rioolstelsel', 'Buffer_Rioolstelsel', type=QgsProcessingParameterNumber.Double, minValue=0.1, maxValue=5, defaultValue=0.2))
        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_knooppunt', 'Netwerk_knooppunt', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_knooppunt',geometryType=0)))
        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_kunstwerk', 'Netwerk_kunstwerk', types=[QgsProcessing.TypeVectorPoint], defaultValue=default_layer('netwerk_kunstwerk',geometryType=0)))
        # self.addParameter(QgsProcessingParameterVectorLayer('netwerk_verbinding', 'Netwerk_verbinding', types=[QgsProcessing.TypeVectorLine], defaultValue=default_layer('netwerk_verbinding',geometryType=1)))
        # self.addParameter(QgsProcessingParameterVectorLayer('rioleringsgebieden', 'Rioleringsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=default_layer('Rioleringsgebieden',geometryType=2)))
        # self.addParameter(QgsProcessingParameterFeatureSink('Rioolgemalen', 'Rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id_kenmerken_kunstwerken', 'Stelsel_ID_kenmerken_kunstwerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id_leidingberging_m3', 'Stelsel_ID_Leidingberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_idKnooppuntberging_m3', 'Stelsel_ID Knooppuntberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerrelatie', 'Resultaat_Stap1_Afvoerrelatie', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_rioolstelsels', 'Resultaat_Stap1_Rioolstelsels', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerpunten', 'Resultaat_Stap1_Afvoerpunten', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Knooppuntberging_m3', 'Knooppuntberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('VuilwaterrioolEnGemengdRioolDieNietMeedoenInBergingsberekening', 'Vuilwaterriool en Gemengd riool die niet meedoen in bergingsberekening', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Lozingspunten_rioolgemalen', 'Lozingspunten_Rioolgemalen', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Controle_kunstwerken', 'Controle_Kunstwerken', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Leidingberging_m3', 'Leidingberging_m3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Stelsel_id', 'Stelsel_ID', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Afvoerrelatie_rioolgemalen', 'Afvoerrelatie_Rioolgemalen', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_afvoerboom', 'Resultaat_Stap1_Afvoerboom', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFeatureSink('Resultaat_stap1_rioleringsgebieden', 'Resultaat_Stap1_Rioleringsgebieden', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        # self.addParameter(QgsProcessingParameterFile('result_folder', 'resultaatmap', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=os.path.join(cmd_folder, "results")))     

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        #QgsProject.instance().reloadAllLayers() 
        self.result_folder = parameters['result_folder']
        
        feedback = QgsProcessingMultiStepFeedback(90, model_feedback)
        results = {}
        outputs = {}

        # Create spatial index Netwerk_Knooppunt
        alg_params = {
            'INPUT': parameters['netwerk_knooppunt']
        }
        outputs['CreateSpatialIndexNetwerk_knooppunt'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Fix geometries rioleringsgebieden
        alg_params = {
            'INPUT': parameters['rioleringsgebieden'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesRioleringsgebieden'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Retain fields verbinding
        alg_params = {
            'FIELDS': ['geo_id','Stelsel','naam','type','beginpunt','eindpunt','VormLeiding','BreedteLeiding','HoogteLeiding','LengteLeiding','BobBeginpuntLeiding','BobEindpuntLeiding'],
            'INPUT': parameters['netwerk_verbinding'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsVerbinding'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Create spatial index verbinding
        alg_params = {
            'INPUT': outputs['RetainFieldsVerbinding']['OUTPUT']
        }
        outputs['CreateSpatialIndexVerbinding'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator Bemalingsgebied_ID
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Bemalingsgebied_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "'Rioleringsgebied' || lpad( $id ,3,0)",
            'INPUT': outputs['FixGeometriesRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBemalingsgebied_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator Bemalingsgebied_ID Stap1_Datum
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Stap1_Datum',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "format_date(now(),\r\n'yyyy-MM-dd hh:mm:ss')",
            'INPUT': outputs['FieldCalculatorBemalingsgebied_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBemalingsgebied_idStap1_datum'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Create spatial index Bemalingsgebied_ID
        alg_params = {
            'INPUT': outputs['FieldCalculatorBemalingsgebied_idStap1_datum']['OUTPUT']
        }
        outputs['CreateSpatialIndexBemalingsgebied_id'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Bemalingsgebied_ID aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexVerbinding']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexBemalingsgebied_id']['OUTPUT'],
            'JOIN_FIELDS': ['Bemalingsgebied_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBemalingsgebied_idAanLeidingen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Bemalingsgebied_ID aan knooppunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexNetwerk_knooppunt']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexBemalingsgebied_id']['OUTPUT'],
            'JOIN_FIELDS': ['Bemalingsgebied_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBemalingsgebied_idAanKnooppunten'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by expression Vuilwaterriolen_en_Gemengd_riolen_die_niet_meedoen_in_bergingsberekening
        alg_params = {
            'EXPRESSION': '("type" LIKE \'%erg%\' OR\r\n"type" LIKE \'%emengd%\' OR\r\n"type" LIKE \'%uilwate%\' ) AND "Bemalingsgebied_ID" IS NULL',
            'INPUT': outputs['JoinAttributesByLocationBemalingsgebied_idAanLeidingen']['OUTPUT'],
            'OUTPUT': parameters['Vuilwaterriolen_en_gemengd_riolen_die_niet_meedoen_in_bergingsberekening']
        }
        outputs['ExtractByExpressionVuilwaterriolen_en_gemengd_riolen_die_niet_meedoen_in_bergingsberekening'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Vuilwaterriolen_en_gemengd_riolen_die_niet_meedoen_in_bergingsberekening'] = outputs['ExtractByExpressionVuilwaterriolen_en_gemengd_riolen_die_niet_meedoen_in_bergingsberekening']['OUTPUT']

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by expression Vuilwaterriool en Gemengd riool
        alg_params = {
            'EXPRESSION': '("type" LIKE \'%erg%\' OR\r\n"type" LIKE \'%emengd%\' OR\r\n"type" LIKE \'%uilwate%\' ) AND "Bemalingsgebied_ID" IS NOT NULL',
            'INPUT': outputs['JoinAttributesByLocationBemalingsgebied_idAanLeidingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionVuilwaterrioolEnGemengdRiool'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Buffer rioolstelsel
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': parameters['buffer_rioolstelsel'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByExpressionVuilwaterrioolEnGemengdRiool']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferRioolstelsel'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts buffer
        alg_params = {
            'INPUT': outputs['BufferRioolstelsel']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSinglepartsBuffer'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Field calculator Polygoon_ID
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Polygoon_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'lpad( $id+1 ,3,0)',
            'INPUT': outputs['MultipartToSinglepartsBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPolygoon_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Retain fields Polygoon_ID
        alg_params = {
            'FIELDS': ['Polygoon_ID'],
            'INPUT': outputs['FieldCalculatorPolygoon_id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFieldsPolygoon_id'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Create spatial index Polygoon_ID
        alg_params = {
            'INPUT': outputs['RetainFieldsPolygoon_id']['OUTPUT']
        }
        outputs['CreateSpatialIndexPolygoon_id'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Bemalingsgebied_ID aan Polygoon_ID
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexPolygoon_id']['OUTPUT'],
            'JOIN': outputs['CreateSpatialIndexBemalingsgebied_id']['OUTPUT'],
            'JOIN_FIELDS': ['Bemalingsgebied_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationBemalingsgebied_idAanPolygoon_id'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Field calculator Stelsel_ID
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Stelsel_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Bemalingsgebied_ID" || \'-\' || "Polygoon_ID"',
            'INPUT': outputs['JoinAttributesByLocationBemalingsgebied_idAanPolygoon_id']['OUTPUT'],
            'OUTPUT': parameters['Stelsel_id']
        }
        outputs['FieldCalculatorStelsel_id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stelsel_id'] = outputs['FieldCalculatorStelsel_id']['OUTPUT']

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Stelsel_ID aan knooppunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['JoinAttributesByLocationBemalingsgebied_idAanKnooppunten']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'JOIN_FIELDS': ['Stelsel_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationStelsel_idAanKnooppunten'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Stelsel_ID aan leidingen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['ExtractByExpressionVuilwaterrioolEnGemengdRiool']['OUTPUT'],
            'JOIN': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'JOIN_FIELDS': ['Stelsel_ID'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [5],  # are within
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationStelsel_idAanLeidingen'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Aggregate eindpunt laagste bob en grootste hoogte leiding
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'eindpunt','length': 0,'name': 'eindpunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'Bemalingsgebied_ID','length': 0,'name': 'Bemalingsgebied_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'BobEindpuntLeiding','length': 0,'name': 'BobEindpuntLeiding_Laagste','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'maximum','delimiter': ',','input': 'HoogteLeiding','length': 0,'name': 'HoogteEindpuntLeiding_Grootste','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'type','length': 0,'name': 'type','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'GROUP_BY': 'eindpunt',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanLeidingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateEindpuntLaagsteBobEnGrootsteHoogteLeiding'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Aggregate beginpunt laagste bob en grootste hoogte leiding
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'beginpunt','length': 0,'name': 'beginpunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'Bemalingsgebied_ID','length': 0,'name': 'Bemalingsgebied_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'BobBeginpuntLeiding','length': 0,'name': 'BobBeginpuntLeiding_Laagste','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'maximum','delimiter': ',','input': 'HoogteLeiding','length': 0,'name': 'HoogteBeginpuntLeiding_Grootste','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'type','length': 0,'name': 'type','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'GROUP_BY': 'beginpunt',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanLeidingen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateBeginpuntLaagsteBobEnGrootsteHoogteLeiding'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value beginpunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Stelsel_ID','BobBeginpuntLeiding_Laagste','HoogteBeginpuntLeiding_Grootste','type'],
            'FIELD_2': 'beginpunt',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanKnooppunten']['OUTPUT'],
            'INPUT_2': outputs['AggregateBeginpuntLaagsteBobEnGrootsteHoogteLeiding']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBeginpunt'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value eindpunt
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Stelsel_ID','BobEindpuntLeiding_Laagste','HoogteEindpuntLeiding_Grootste','type'],
            'FIELD_2': 'eindpunt',
            'INPUT': outputs['JoinAttributesByFieldValueBeginpunt']['OUTPUT'],
            'INPUT_2': outputs['AggregateEindpuntLaagsteBobEnGrootsteHoogteLeiding']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEindpunt'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator Laagst_inkomende_bob_mNAP
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Laagst_inkomende_bob_mNAP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round(min("BobBeginpuntLeiding_Laagste","BobEindpuntLeiding_Laagste"),2)',
            'INPUT': outputs['JoinAttributesByFieldValueEindpunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLaagst_inkomende_bob_mnap'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator Grootste_aangesloten_leiding_mm
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Grootste_aangesloten_leiding_mm',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': 'max( "HoogteBeginpuntLeiding_Grootste" , "HoogteEindpuntLeiding_Grootste" )',
            'INPUT': outputs['FieldCalculatorLaagst_inkomende_bob_mnap']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorGrootste_aangesloten_leiding_mm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Field calculator Steslel_ID voor knopen buiten polygoon
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Stelsel_ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("Stelsel_ID" IS NOT NULL, "Stelsel_ID" ,\r\nif("Stelsel_ID" IS NULL AND "Stelsel_ID_2" IS NOT NULL , "Stelsel_ID_2",\r\nif("Stelsel_ID" IS NULL AND "Stelsel_ID_2" IS NULL AND "Stelsel_ID_3" IS NOT NULL , "Stelsel_ID_3", NULL)))',
            'INPUT': outputs['FieldCalculatorGrootste_aangesloten_leiding_mm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorSteslel_idVoorKnopenBuitenPolygoon'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Field calculator Leidingtype
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Leidingtype',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if(("type_2" LIKE \'%uilwater%\' OR  "type_3" LIKE \'%uilwater%\') AND \r\n("type_2" NOT LIKE \'%emengd%\' OR "type_2" IS NULL) AND ("type_3" NOT LIKE \'%emengd%\' OR "type_3" IS NULL), \'Vuilwaterriool\',\r\nif("type_2" LIKE \'%emengd%\' OR  "type_3" LIKE \'%emengd%\' , \'Gemengdriool\',\r\nif(("type_2" LIKE \'%emel%\' OR  "type_3" LIKE \'%emel%\') AND ("type_2" NOT LIKE \'%erbeterd%\' OR "type_2" IS NULL) AND ("type_3" LIKE \'%erbeterd%\' OR "type_3" IS NULL) , \'Hemelwaterriool\',\r\nif(("type_2" LIKE \'%it%\' OR  "type_3" LIKE \'%it%\') AND ("type_2" NOT LIKE \'%emel%\' OR "type_2" IS NULL) AND ("type_3" LIKE \'%emel%\' OR "type_3" IS NULL), \'DIT-riool\',\r\n\'Anders\'))))',
            'INPUT': outputs['FieldCalculatorSteslel_idVoorKnopenBuitenPolygoon']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLeidingtype'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Drop field(s) overbodige velden knooppunten
        alg_params = {
            'COLUMN': ['Maaiveldschematisering','AantalWoningen','Aantal_ieBedrijven','Aantal_ieRecreatie','AfvoerendOppervlak','LateraalDebietDWA','LateraalDebietHWA','LateraalAfvoerendOppervlak','BobBeginpuntLeiding_Laagste','HoogteBeginpuntLeiding_Grootste','BobEindpuntLeiding_Laagste','HoogteEindpuntLeiding_Grootste','Stelsel_ID_2','Stelsel_ID_3','type_2','type_3'],
            'INPUT': outputs['FieldCalculatorLeidingtype']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsOverbodigeVeldenKnooppunten'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Extract by expression Overstort Stuw Drempel Doorlaat
        alg_params = {
            'EXPRESSION': ' "type"  LIKE \'%overst%\' OR  "type"  LIKE \'%tuw%\'  OR  "type"  LIKE \'%rempe%\'  OR  "type"  LIKE \'%oorlaa%\' ',
            'INPUT': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionOverstortStuwDrempelDoorlaat'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Extract by expression Pompput Pompunit Rioolgemaal
        alg_params = {
            'EXPRESSION': ' "type"  LIKE \'%omp%\' OR  "type"  LIKE \'%emaal%\' ',
            'INPUT': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionPompputPompunitRioolgemaal'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Field calculator type
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'type',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "'Pomp'",
            'INPUT': outputs['ExtractByExpressionPompputPompunitRioolgemaal']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorType'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Extract by expression Kooppunten - "Stelsel_ID" IS NOT NULL 1
        alg_params = {
            'EXPRESSION': '"Stelsel_ID" IS NOT NULL',
            'INPUT': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionKooppuntenStelsel_idIsNotNull1'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Aggregate Knooppunten Maaiveldhoogte_Q1_mNAP
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'q1','delimiter': ',','input': 'Maaiveldhoogte','length': 0,'name': 'Maaiveldhoogte_Q1_mNAP','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'Maaiveldhoogte',
            'INPUT': outputs['ExtractByExpressionKooppuntenStelsel_idIsNotNull1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateKnooppuntenMaaiveldhoogte_q1_mnap'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Maaiveldhoogte_Q1_mNAP aan leidingen koppelen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': ['Maaiveldhoogte_Q1_mNAP'],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['JoinAttributesByLocationStelsel_idAanLeidingen']['OUTPUT'],
            'INPUT_2': outputs['AggregateKnooppuntenMaaiveldhoogte_q1_mnap']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMaaiveldhoogte_q1_mnapAanLeidingenKoppelen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value kunstwerken aan overstorten stuw doorlaat drempel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['type','begin','eind','BreedteOpening','HoogteOpening','VormOpening','Doorlaatniveau','Pompcapaciteit','AanslagniveauBeneden','AfslagniveauBeneden','Drempelbreedte','Drempelniveau'],
            'FIELD_2': 'begin',
            'INPUT': outputs['ExtractByExpressionOverstortStuwDrempelDoorlaat']['OUTPUT'],
            'INPUT_2': parameters['netwerk_kunstwerk'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKunstwerkenAanOverstortenStuwDoorlaatDrempel'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator begin
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'begin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"naam"',
            'INPUT': outputs['FieldCalculatorType']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorBegin'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Maaiveldhoogte_Q1_mNAP aan knooppunten koppelen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': ['Maaiveldhoogte_Q1_mNAP'],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'INPUT_2': outputs['AggregateKnooppuntenMaaiveldhoogte_q1_mnap']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMaaiveldhoogte_q1_mnapAanKnooppuntenKoppelen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Field calculator Controle_Kunstwerken
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Controle_Kunstwerken',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if("type" LIKE  \'%oodover%\' AND "type" NOT LIKE  \'%tuw%\'AND  "Doorlaatniveau" IS NULL AND  "Drempelniveau" IS NULL,\r\n\'Noodoverstortput zonder drempelniveau en/of zonder doorlaatniveau\',\r\nif("type" LIKE \'%tuw%\' AND  "Doorlaatniveau" IS NULL,\r\n\'Stuwput zonder doorlaatniveau\',\r\nif("type" LIKE \'%verstort%\' AND "type" LIKE \'%Extern%\' AND "type" NOT LIKE \'%nood%\'  AND "Drempelniveau" IS NULL,\r\n\'Externe overstortput zonder drempelniveau\',\r\nif("type" LIKE \'%verstort%\' AND "type" LIKE \'%Intern%\' AND "type" NOT LIKE \'%nood%\'  AND "Drempelniveau" IS NULL,\r\n\'Interne overstortput zonder drempelniveau\',\r\n\'NULL\'))))',
            'INPUT': outputs['JoinAttributesByFieldValueKunstwerkenAanOverstortenStuwDoorlaatDrempel']['OUTPUT'],
            'OUTPUT': parameters['Controle_kunstwerken']
        }
        outputs['FieldCalculatorControle_kunstwerken'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Controle_kunstwerken'] = outputs['FieldCalculatorControle_kunstwerken']['OUTPUT']

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Field calculator controle
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'controle',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "'controle'",
            'INPUT': outputs['FieldCalculatorBegin']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorControle'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value kunstwerken aan knooppunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'naam',
            'INPUT': outputs['FieldCalculatorControle']['OUTPUT'],
            'INPUT_2': parameters['netwerk_kunstwerk'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueKunstwerkenAanKnooppunten'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Extract by expression Pompen zonder afvoerrelatie
        alg_params = {
            'EXPRESSION': '"naam_2" IS NULL',
            'INPUT': outputs['JoinAttributesByFieldValueKunstwerkenAanKnooppunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionPompenZonderAfvoerrelatie'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Extract by expression Rioolgemaal rioolstelsels zonder afvoerrelatie
        alg_params = {
            'EXPRESSION': '"Stelsel_ID" IS NOT NULL',
            'INPUT': outputs['ExtractByExpressionPompenZonderAfvoerrelatie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionRioolgemaalRioolstelselsZonderAfvoerrelatie'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Retain fields Rioolgemalen_zonder_afvoerrelatie
        alg_params = {
            'FIELDS': ['naam','type','begin'],
            'INPUT': outputs['ExtractByExpressionRioolgemaalRioolstelselsZonderAfvoerrelatie']['OUTPUT'],
            'OUTPUT': parameters['Rioolgemalen_zonder_afvoerrelatie']
        }
        outputs['RetainFieldsRioolgemalen_zonder_afvoerrelatie'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Rioolgemalen_zonder_afvoerrelatie'] = outputs['RetainFieldsRioolgemalen_zonder_afvoerrelatie']['OUTPUT']

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Merge vector layers Kunstwerk en Rioolgemaal zonder afvoerrelatie
        alg_params = {
            'CRS': None,
            'LAYERS': [parameters['netwerk_kunstwerk'],outputs['RetainFieldsRioolgemalen_zonder_afvoerrelatie']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersKunstwerkEnRioolgemaalZonderAfvoerrelatie'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Drop field(s) layer;path
        alg_params = {
            'COLUMN': ['layer','path'],
            'INPUT': outputs['MergeVectorLayersKunstwerkEnRioolgemaalZonderAfvoerrelatie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsLayerpath'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Field calculator eind
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'eind',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("eind" IS NULL,"begin","eind")',
            'INPUT': outputs['DropFieldsLayerpath']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEind'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value begin Bemalingsgebied_ID aan kunstwerk
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'begin',
            'FIELDS_TO_COPY': ['Bemalingsgebied_ID','Leidingtype'],
            'FIELD_2': 'naam',
            'INPUT': outputs['FieldCalculatorEind']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'begin_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBeginBemalingsgebied_idAanKunstwerk'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest begin Stelsel_ID en Leidingtype aan kunstwerk
        # 2 meter zoek radius
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['Stelsel_ID'],
            'INPUT': outputs['JoinAttributesByFieldValueBeginBemalingsgebied_idAanKunstwerk']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'MAX_DISTANCE': 2,
            'NEIGHBORS': 1,
            'PREFIX': 'begin_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestBeginStelsel_idEnLeidingtypeAanKunstwerk'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Drop field(s) nearest Stelseltype by Pomp
        alg_params = {
            'COLUMN': ['n','distance','feature_x','feature_y','nearest_x','nearest_y'],
            'INPUT': outputs['JoinAttributesByNearestBeginStelsel_idEnLeidingtypeAanKunstwerk']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsNearestStelseltypeByPomp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value eind Bemalingsgebied_ID en Stelsel_ID aan kunstwerk
        # Misschien een tussenresultaat van maken
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'eind',
            'FIELDS_TO_COPY': ['Bemalingsgebied_ID','Stelsel_ID','Leidingtype'],
            'FIELD_2': 'naam',
            'INPUT': outputs['DropFieldsNearestStelseltypeByPomp']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsOverbodigeVeldenKnooppunten']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'eind_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEindBemalingsgebied_idEnStelsel_idAanKunstwerk'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Aggregate kunstwerk kenmerken per Stelsel_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'begin_Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'Doorlaatniveau','length': 0,'name': 'Laagste_Doorlaatniveau_mNAP','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'minimum','delimiter': ',','input': 'Drempelniveau','length': 0,'name': 'Laagste_Drempelniveau_mNAP','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'count','delimiter': ',','input': 'Doorlaatniveau','length': 0,'name': 'Aantal_Doorlaten','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'aggregate': 'count','delimiter': ',','input': 'Drempelniveau','length': 0,'name': 'Aantal_Drempels','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'}],
            'GROUP_BY': 'begin_Stelsel_ID',
            'INPUT': outputs['JoinAttributesByFieldValueEindBemalingsgebied_idEnStelsel_idAanKunstwerk']['OUTPUT'],
            'OUTPUT': parameters['Stelsel_id_kenmerken_kunstwerken']
        }
        outputs['AggregateKunstwerkKenmerkenPerStelsel_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stelsel_id_kenmerken_kunstwerken'] = outputs['AggregateKunstwerkKenmerkenPerStelsel_id']['OUTPUT']

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Laagste_Drempelniveau_mNAP aan knooppunten koppelen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': ['Laagste_Drempelniveau_mNAP'],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['JoinAttributesByFieldValueMaaiveldhoogte_q1_mnapAanKnooppuntenKoppelen']['OUTPUT'],
            'INPUT_2': outputs['AggregateKunstwerkKenmerkenPerStelsel_id']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueLaagste_drempelniveau_mnapAanKnooppuntenKoppelen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Extract by expression Pompen
        alg_params = {
            'EXPRESSION': '"type"=\'Pomp\'',
            'INPUT': outputs['JoinAttributesByFieldValueEindBemalingsgebied_idEnStelsel_idAanKunstwerk']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionPompen'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Aggregate Rioolgemalen
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'naam','length': 0,'name': 'Rioolgemaal','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'begin_Bemalingsgebied_ID','length': 0,'name': 'Bemalingsgebied_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'type','length': 0,'name': 'Type','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'begin','length': 0,'name': 'Beginpunt_Afvoerrelatie','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'eind','length': 0,'name': 'Eindpunt_Afvoerrelatie','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'maximum','delimiter': ',','input': 'Pompcapaciteit','length': 0,'name': 'Afvoercapaciteit_m3h','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'maximum','delimiter': ',','input': 'AanslagniveauBoven','length': 0,'name': 'Inslagpeil_mNAP','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'minimum','delimiter': ',','input': 'AfslagniveauBoven','length': 0,'name': 'Uitslagpeil_mNAP','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'},{'aggregate': 'count','delimiter': ',','input': 'naam','length': 0,'name': 'Aantal_Pompen','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'aggregate': 'first_value','delimiter': ',','input': 'begin_Bemalingsgebied_ID','length': 0,'name': 'Bemalingsgebied_ID_Afvoerpunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'begin_Stelsel_ID','length': 0,'name': 'Stelsel_ID_Afvoerpunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'eind_Bemalingsgebied_ID','length': 0,'name': 'Bemalingsgebied_ID_Lozingspunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'first_value','delimiter': ',','input': 'eind_Stelsel_ID','length': 0,'name': 'Stelsel_ID_lozingspunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'GROUP_BY': 'naam',
            'INPUT': outputs['ExtractByExpressionPompen']['OUTPUT'],
            'OUTPUT': parameters['Rioolgemalen']
        }
        outputs['AggregateRioolgemalen'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Rioolgemalen'] = outputs['AggregateRioolgemalen']['OUTPUT']

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Extract by expression Rioolgemalen zonder afvoerrelatie
        alg_params = {
            'EXPRESSION': '"Beginpunt_Afvoerrelatie" = "Eindpunt_Afvoerrelatie"',
            'INPUT': outputs['AggregateRioolgemalen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionRioolgemalenZonderAfvoerrelatie'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Laagste_Drempelniveau_mNAP aan leidingen koppelen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': ['Laagste_Drempelniveau_mNAP'],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['JoinAttributesByFieldValueMaaiveldhoogte_q1_mnapAanLeidingenKoppelen']['OUTPUT'],
            'INPUT_2': outputs['AggregateKunstwerkKenmerkenPerStelsel_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueLaagste_drempelniveau_mnapAanLeidingenKoppelen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines) Afvoerrelatie_Rioolgemalen
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['AggregateRioolgemalen']['OUTPUT'],
            'HUB_FIELD': 'Eindpunt_Afvoerrelatie',
            'HUB_FIELDS': [''],
            'SPOKES': parameters['netwerk_knooppunt'],
            'SPOKE_FIELD': 'naam',
            'SPOKE_FIELDS': ['geen'],
            'OUTPUT': parameters['Afvoerrelatie_rioolgemalen']
        }
        outputs['JoinByLinesHubLinesAfvoerrelatie_rioolgemalen'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Afvoerrelatie_rioolgemalen'] = outputs['JoinByLinesHubLinesAfvoerrelatie_rioolgemalen']['OUTPUT']

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Stelsel_ID rioolgemaaldata
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'Stelsel_ID_Afvoerpunt',
            'INPUT': outputs['FieldCalculatorStelsel_id']['OUTPUT'],
            'INPUT_2': outputs['AggregateRioolgemalen']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStelsel_idRioolgemaaldata'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Field calculator Afvoerpunt_Lozingspunt
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Afvoerpunt_Lozingspunt',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': '"Bemalingsgebied_ID_Afvoerpunt" || \'-\' || "Bemalingsgebied_ID_Lozingspunt" ',
            'INPUT': outputs['JoinByLinesHubLinesAfvoerrelatie_rioolgemalen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAfvoerpunt_lozingspunt'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(60)
        if feedback.isCanceled():
            return {}

        # Field calculator Leidingberging_m3
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Leidingberging_m3',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if(mean( "BobBeginpuntLeiding" , "BobEindpuntLeiding" ) +  ("HoogteLeiding"/1000) > if( "Laagste_Drempelniveau_mNAP" IS NOT NULL,  "Laagste_Drempelniveau_mNAP" , "Maaiveldhoogte_Q1_mNAP"-0.6 ), 0,\r\nif("VormLeiding" LIKE \'%Ei%\' , round((((0.25 * pi()*((("BreedteLeiding"/1000)^2))/2))+(((("BreedteLeiding"/1000)+(("HoogteLeiding"-"BreedteLeiding")/1000))/2)*(("BreedteLeiding"/1000/2)+(("HoogteLeiding"-"BreedteLeiding")/1000/2)))+((0.25*pi()*(("HoogteLeiding"-"BreedteLeiding")/1000)^2/2))) *  "LengteLeiding" ,2),\r\nif("VormLeiding" = \'Rechthoekig\' , round( ("BreedteLeiding" /1000) * ("HoogteLeiding" /1000) *  "LengteLeiding" ,2),\r\nround( ("BreedteLeiding" /1000 /2) * ("BreedteLeiding" /1000 /2) * pi() *  "LengteLeiding" ,2 ))))',
            'INPUT': outputs['JoinAttributesByFieldValueLaagste_drempelniveau_mnapAanLeidingenKoppelen']['OUTPUT'],
            'OUTPUT': parameters['Leidingberging_m3']
        }
        outputs['FieldCalculatorLeidingberging_m3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Leidingberging_m3'] = outputs['FieldCalculatorLeidingberging_m3']['OUTPUT']

        feedback.setCurrentStep(61)
        if feedback.isCanceled():
            return {}

        # Aggregate Leidingberging_m3 per Stelsel_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'type','length': 0,'name': 'Leidingtypen_In_Stelsel','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'concatenate_unique','delimiter': ',','input': 'Stelsel','length': 0,'name': 'Stelselnamen','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'Leidingberging_m3','length': 0,'name': 'Leidingberging_m3','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'}],
            'GROUP_BY': 'Stelsel_ID',
            'INPUT': outputs['FieldCalculatorLeidingberging_m3']['OUTPUT'],
            'OUTPUT': parameters['Stelsel_id_leidingberging_m3']
        }
        outputs['AggregateLeidingberging_m3PerStelsel_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stelsel_id_leidingberging_m3'] = outputs['AggregateLeidingberging_m3PerStelsel_id']['OUTPUT']

        feedback.setCurrentStep(62)
        if feedback.isCanceled():
            return {}

        # Field calculator Lengte_Afvoerrelatie_m
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Lengte_Afvoerrelatie_m',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'round($length,2)',
            'INPUT': outputs['FieldCalculatorAfvoerpunt_lozingspunt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorLengte_afvoerrelatie_m'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(63)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Beginpunt Leidingberging_m3
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Leidingberging_m3'],
            'FIELD_2': 'beginpunt',
            'INPUT': outputs['JoinAttributesByFieldValueLaagste_drempelniveau_mnapAanKnooppuntenKoppelen']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorLeidingberging_m3']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': 'Beginpunt_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueBeginpuntLeidingberging_m3'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(64)
        if feedback.isCanceled():
            return {}

        # Extract by expression Rioolgemalen die naar een ander rioleringsgebied afvoeren
        alg_params = {
            'EXPRESSION': '"Bemalingsgebied_ID_Afvoerpunt" <> "Bemalingsgebied_ID_Lozingspunt" ',
            'INPUT': outputs['FieldCalculatorLengte_afvoerrelatie_m']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionRioolgemalenDieNaarEenAnderRioleringsgebiedAfvoeren'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(65)
        if feedback.isCanceled():
            return {}

        # Aggregate Afvoerpunt_Lozingspunt minimale lengte
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Afvoerpunt_Lozingspunt','length': 0,'name': 'Afvoerpunt_Lozingspunt','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'minimum','delimiter': ',','input': 'Lengte_Afvoerrelatie_m','length': 0,'name': 'Minimale_Lengte_Afvoerrelatie_m','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'Afvoerpunt_Lozingspunt',
            'INPUT': outputs['ExtractByExpressionRioolgemalenDieNaarEenAnderRioleringsgebiedAfvoeren']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateAfvoerpunt_lozingspuntMinimaleLengte'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(66)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Stelsel_ID leidingdata
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['JoinAttributesByFieldValueStelsel_idRioolgemaaldata']['OUTPUT'],
            'INPUT_2': outputs['AggregateLeidingberging_m3PerStelsel_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStelsel_idLeidingdata'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(67)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Eindpunt Leidingberging_m3
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Leidingberging_m3'],
            'FIELD_2': 'eindpunt',
            'INPUT': outputs['JoinAttributesByFieldValueBeginpuntLeidingberging_m3']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculatorLeidingberging_m3']['OUTPUT'],
            'METHOD': 0,  # Create separate feature for each matching feature (one-to-many)
            'PREFIX': 'Eindpunt_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueEindpuntLeidingberging_m3'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(68)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Minimale lengte afvoerrelatie aan rioolgemalen
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Afvoerpunt_Lozingspunt',
            'FIELDS_TO_COPY': ['Minimale_Lengte_Afvoerrelatie_m'],
            'FIELD_2': 'Afvoerpunt_Lozingspunt',
            'INPUT': outputs['ExtractByExpressionRioolgemalenDieNaarEenAnderRioleringsgebiedAfvoeren']['OUTPUT'],
            'INPUT_2': outputs['AggregateAfvoerpunt_lozingspuntMinimaleLengte']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMinimaleLengteAfvoerrelatieAanRioolgemalen'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(69)
        if feedback.isCanceled():
            return {}

        # Extract by expression selectie Afvoerende rioolgemalen
        alg_params = {
            'EXPRESSION': '"Lengte_Afvoerrelatie_m" ="Minimale_Lengte_Afvoerrelatie_m"',
            'INPUT': outputs['JoinAttributesByFieldValueMinimaleLengteAfvoerrelatieAanRioolgemalen']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionSelectieAfvoerendeRioolgemalen'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(70)
        if feedback.isCanceled():
            return {}

        # Drop field(s) Rioolgemalen overbodige velden
        alg_params = {
            'COLUMN': ['Afvoerpunt_Lozingspunt','Lengte_Afvoerrelatie_m','Minimale_Lengte_Afvoerrelatie_m'],
            'INPUT': outputs['ExtractByExpressionSelectieAfvoerendeRioolgemalen']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap1_afvoerrelatie']
        }
        outputs['DropFieldsRioolgemalenOverbodigeVelden'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_afvoerrelatie'] = outputs['DropFieldsRioolgemalenOverbodigeVelden']['OUTPUT']

        feedback.setCurrentStep(71)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices Lozingspunten van de afvoerpunten
        alg_params = {
            'INPUT': outputs['DropFieldsRioolgemalenOverbodigeVelden']['OUTPUT'],
            'VERTICES': '-1',
            'OUTPUT': parameters['Lozingspunten_rioolgemalen']
        }
        outputs['ExtractSpecificVerticesLozingspuntenVanDeAfvoerpunten'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Lozingspunten_rioolgemalen'] = outputs['ExtractSpecificVerticesLozingspuntenVanDeAfvoerpunten']['OUTPUT']

        feedback.setCurrentStep(72)
        if feedback.isCanceled():
            return {}

        # Extract specific vertices extract Resultaat_Stap1_Afvoerpunten
        alg_params = {
            'INPUT': outputs['DropFieldsRioolgemalenOverbodigeVelden']['OUTPUT'],
            'VERTICES': '0',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractSpecificVerticesExtractResultaat_stap1_afvoerpunten'] = processing.run('native:extractspecificvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(73)
        if feedback.isCanceled():
            return {}

        # Aggregate Max_Leidingberging_m3 aan knooppunten
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'naam','length': 0,'name': 'naam','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'maximum','delimiter': ',','input': 'round("Beginpunt_Leidingberging_m3"+"Eindpunt_Leidingberging_m3",2)','length': 0,'name': 'Max_Leidingberging_m3','precision': 2,'sub_type': 0,'type': 6,'type_name': 'double precision'}],
            'GROUP_BY': 'naam',
            'INPUT': outputs['JoinAttributesByFieldValueEindpuntLeidingberging_m3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AggregateMax_leidingberging_m3AanKnooppunten'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(74)
        if feedback.isCanceled():
            return {}

        # Merge vector layers Afvoerpunten
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['ExtractByExpressionRioolgemalenZonderAfvoerrelatie']['OUTPUT'],outputs['ExtractSpecificVerticesExtractResultaat_stap1_afvoerpunten']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersAfvoerpunten'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(75)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Max_Leidingberging_m3 aan knooppunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'naam',
            'FIELDS_TO_COPY': ['Max_Leidingberging_m3'],
            'FIELD_2': 'naam',
            'INPUT': outputs['JoinAttributesByFieldValueLaagste_drempelniveau_mnapAanKnooppuntenKoppelen']['OUTPUT'],
            'INPUT_2': outputs['AggregateMax_leidingberging_m3AanKnooppunten']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueMax_leidingberging_m3AanKnooppunten'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(76)
        if feedback.isCanceled():
            return {}

        # Field calculator Knooppuntberging_m3
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Knooppuntberging_m3',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': 'if("Max_Leidingberging_m3"<=0 OR "Max_Leidingberging_m3" IS NULL,0,\r\nround(\r\nif( "VormPut" LIKE \'%Rond%\',  (("BreedtePut" /1000/2) * ("BreedtePut" /1000/2) * pi()) * \r\n(if( "Laagste_Drempelniveau_mNAP" IS NULL,  abs(("Maaiveldhoogte_Q1_mNAP"-0.6) - "Laagst_inkomende_bob_mNAP"),  abs("Laagste_Drempelniveau_mNAP" - "Laagst_inkomende_bob_mNAP"))),\r\n("BreedtePut" /1000) * ("Lengteput" /1000) * if( "Laagste_Drempelniveau_mNAP" IS NULL,  abs(("Maaiveldhoogte_Q1_mNAP"-0.6) - "Laagst_inkomende_bob_mNAP"),  abs("Laagste_Drempelniveau_mNAP" - "Laagst_inkomende_bob_mNAP")))\r\n, 2))',
            'INPUT': outputs['JoinAttributesByFieldValueMax_leidingberging_m3AanKnooppunten']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorKnooppuntberging_m3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(77)
        if feedback.isCanceled():
            return {}

        # Extract by expression Kooppunten - "Stelsel_ID" IS NOT NULL 2
        alg_params = {
            'EXPRESSION': '"Stelsel_ID" IS NOT NULL',
            'INPUT': outputs['FieldCalculatorKnooppuntberging_m3']['OUTPUT'],
            'OUTPUT': parameters['Knooppuntberging_m3']
        }
        outputs['ExtractByExpressionKooppuntenStelsel_idIsNotNull2'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Knooppuntberging_m3'] = outputs['ExtractByExpressionKooppuntenStelsel_idIsNotNull2']['OUTPUT']

        feedback.setCurrentStep(78)
        if feedback.isCanceled():
            return {}

        # Aggregate Knooppuntberging_m3 per Stelsel_ID
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'Stelsel_ID','length': 0,'name': 'Stelsel_ID','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'},{'aggregate': 'sum','delimiter': ',','input': 'Knooppuntberging_m3','length': 0,'name': 'Knooppuntberging_m3','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'}],
            'GROUP_BY': 'Stelsel_ID',
            'INPUT': outputs['ExtractByExpressionKooppuntenStelsel_idIsNotNull2']['OUTPUT'],
            'OUTPUT': parameters['Stelsel_idKnooppuntberging_m3']
        }
        outputs['AggregateKnooppuntberging_m3PerStelsel_id'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stelsel_idKnooppuntberging_m3'] = outputs['AggregateKnooppuntberging_m3PerStelsel_id']['OUTPUT']

        feedback.setCurrentStep(79)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Stelsel_ID knooppuntdata
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['JoinAttributesByFieldValueStelsel_idLeidingdata']['OUTPUT'],
            'INPUT_2': outputs['AggregateKnooppuntberging_m3PerStelsel_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStelsel_idKnooppuntdata'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(80)
        if feedback.isCanceled():
            return {}

        # Field calculator Stelselberging_m3
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Stelselberging_m3',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '"Leidingberging_m3"+"Knooppuntberging_m3"',
            'INPUT': outputs['JoinAttributesByFieldValueStelsel_idKnooppuntdata']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorStelselberging_m3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(81)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value Stelsel_ID kunstwerkdata
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Stelsel_ID',
            'FIELDS_TO_COPY': [''],
            'FIELD_2': 'Stelsel_ID',
            'INPUT': outputs['FieldCalculatorStelselberging_m3']['OUTPUT'],
            'INPUT_2': outputs['AggregateKunstwerkKenmerkenPerStelsel_id']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueStelsel_idKunstwerkdata'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(82)
        if feedback.isCanceled():
            return {}

        # Drop field(s) overbodige Stelselkenmerken
        alg_params = {
            'COLUMN': ['Polygoon_ID','Stelsel_ID_2','Stelsel_ID_3','Stelsel_ID_4','Stelsel_ID_5','Bemalingsgebied_ID_2'],
            'INPUT': outputs['JoinAttributesByFieldValueStelsel_idKunstwerkdata']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap1_rioolstelsels']
        }
        outputs['DropFieldsOverbodigeStelselkenmerken'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_rioolstelsels'] = outputs['DropFieldsOverbodigeStelselkenmerken']['OUTPUT']

        feedback.setCurrentStep(83)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest Resultaat_Stap1_Rioolstelsels aan Afvoerpunten
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['Leidingtypen_In_Stelsel','Stelselnamen','Leidingberging_m3','Knooppuntberging_m3','Stelselberging_m3','Laagste_Doorlaatniveau_mNAP','Laagste_Drempelniveau_mNAP','Aantal_Doorlaten','Aantal_Drempels',''],
            'INPUT': outputs['MergeVectorLayersAfvoerpunten']['OUTPUT'],
            'INPUT_2': outputs['DropFieldsOverbodigeStelselkenmerken']['OUTPUT'],
            'MAX_DISTANCE': 3,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestResultaat_stap1_rioolstelselsAanAfvoerpunten'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(84)
        if feedback.isCanceled():
            return {}

        # Drop field(s) Resultaat_Stap1_Afvoerpunten overbodige velden
        alg_params = {
            'COLUMN': ['vertex_pos','vertex_index','vertex_part','vertex_part_index','distance','angle','layer','path','n','distance_2','feature_x','feature_y','nearest_x','nearest_y'],
            'INPUT': outputs['JoinAttributesByNearestResultaat_stap1_rioolstelselsAanAfvoerpunten']['OUTPUT'],
            'OUTPUT': parameters['Resultaat_stap1_afvoerpunten']
        }
        outputs['DropFieldsResultaat_stap1_afvoerpuntenOverbodigeVelden'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_afvoerpunten'] = outputs['DropFieldsResultaat_stap1_afvoerpuntenOverbodigeVelden']['OUTPUT']

        feedback.setCurrentStep(85)
        if feedback.isCanceled():
            return {}

        # Join attributes by location Afvoerpunten aan Rioleringsgebieden
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['CreateSpatialIndexBemalingsgebied_id']['OUTPUT'],
            'JOIN': outputs['DropFieldsResultaat_stap1_afvoerpuntenOverbodigeVelden']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': parameters['Resultaat_stap1_rioleringsgebieden']
        }
        outputs['JoinAttributesByLocationAfvoerpuntenAanRioleringsgebieden'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_rioleringsgebieden'] = outputs['JoinAttributesByLocationAfvoerpuntenAanRioleringsgebieden']['OUTPUT']

        feedback.setCurrentStep(86)
        if feedback.isCanceled():
            return {}

        # Drop field(s) Rioleringsgebieden - Bemalingsgebied_ID_2
        alg_params = {
            'COLUMN': ['Bemalingsgebied_ID_2'],
            'INPUT': outputs['JoinAttributesByLocationAfvoerpuntenAanRioleringsgebieden']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldsRioleringsgebiedenBemalingsgebied_id_2'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(87)
        if feedback.isCanceled():
            return {}

        # Point on surface Rioleringsgebieden_Afvoerpunt
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['DropFieldsRioleringsgebiedenBemalingsgebied_id_2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointOnSurfaceRioleringsgebieden_afvoerpunt'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(88)
        if feedback.isCanceled():
            return {}

        # Point on surface Rioleringsgebieden_Lozingspunt
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['DropFieldsRioleringsgebiedenBemalingsgebied_id_2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointOnSurfaceRioleringsgebieden_lozingspunt'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(89)
        if feedback.isCanceled():
            return {}

        # Join by lines (hub lines) Resultaat_Stap1_Afvoerboom
        alg_params = {
            'ANTIMERIDIAN_SPLIT': False,
            'GEODESIC': False,
            'GEODESIC_DISTANCE': 1000,
            'HUBS': outputs['PointOnSurfaceRioleringsgebieden_afvoerpunt']['OUTPUT'],
            'HUB_FIELD': 'Bemalingsgebied_ID_Lozingspunt',
            'HUB_FIELDS': [''],
            'SPOKES': outputs['PointOnSurfaceRioleringsgebieden_lozingspunt']['OUTPUT'],
            'SPOKE_FIELD': 'Bemalingsgebied_ID',
            'SPOKE_FIELDS': ['geen_velden'],
            'OUTPUT': parameters['Resultaat_stap1_afvoerboom']
        }
        outputs['JoinByLinesHubLinesResultaat_stap1_afvoerboom'] = processing.run('native:hublines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Resultaat_stap1_afvoerboom'] = outputs['JoinByLinesHubLinesResultaat_stap1_afvoerboom']['OUTPUT']

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
