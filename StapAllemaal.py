"""
Model exported as python.
Name : genereer_afvoerrelaties
Group : 
With QGIS : 32207
"""
import os
import processing
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProject,
                       QgsVectorLayer)
from .custom_tools import rename_layers, default_inp_fields, default_layer, QgsProcessingAlgorithmPost, cmd_folder

        
class GeodynAlleStappen(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('bag_verblijfsobjecten', 'BAG verblijfsobjecten', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden', 'Input bemalingsgebieden', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2)', 'GWSW knooppunten', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2)', 'GWSW kunstwerken', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2)', 'GWSW verbindingen', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2)', 'BGT inlooptabel', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (2) (2) (2)', 'Plancap', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3)', "VE's", types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputbemalingsgebieden (2) (2) (3) (2)', 'Drinkwater', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('result_folder', 'result_folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue='../results'))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_eindpunten', 'Stap1_Eindpunten', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_gebiedsgegevens_punt_tbv_stap2', 'Stap1_Gebiedsgegevens_punt_tbv_stap2', type=QgsProcessing.TypeVectorPoint, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_bemalingsgebieden_tbv_stap2', 'Stap1_bemalingsgebieden_tbv_stap2', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_berging_in_knopen', 'Stap1_berging_in_knopen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_berging_leiding_aggregated', 'Stap1_berging_leiding_aggregated', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_berging_leiding_parts', 'Stap1_berging_leiding_parts', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_gebiedsgegevens_lijn_tbv_stap2', 'Stap1_gebiedsgegevens_lijn_tbv_stap2', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_gebiedsgegevens_stap1_all_att', 'Stap1_gebiedsgegevens_stap1_all_att', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_gemengde_en_vuilwaterstelsels', 'Stap1_gemengde_en_vuilwaterstelsels', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_knp_stats', 'Stap1_knp_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_leidingen_niet_meegenomen', 'Stap1_leidingen_niet_meegenomen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_rioolstelsel_buffer', 'Stap1_rioolstelsel_buffer', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_rioolstelsel_buffer_10m_buffer', 'Stap1_rioolstelsel_buffer_10m_buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_stelselkenmerken', 'Stap1_stelselkenmerken', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap1_total_storage', 'Stap1_total_storage', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_bemalingsgebieden', 'Stap2_afvoerrelaties_bemalingsgebieden', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_afvoerrelaties_rioolgemalen', 'Stap2_afvoerrelaties_rioolgemalen', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_bemalingsgebieden_met_afvoerrelaties_tbv_stap3', 'Stap2_bemalingsgebieden_met_afvoerrelaties_tbv_stap3', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_eindpunten_in_eindgebied_selected', 'Stap2_eindpunten_in_eindgebied_selected', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_rioolgemalen_gekoppeld', 'Stap2_rioolgemalen_gekoppeld', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap2_van_naar', 'Stap2_van_naar', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eindresultaat', 'Eindresultaat', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_exafw_per_bem_id', 'Stap3_ExAFW_per_bem_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_pc_id', 'Stap3_Plancap_pc_id', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_bemalingsgebieden_joined_stats', 'Stap3_bemalingsgebieden_joined_stats', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_bgt_intersect', 'Stap3_bgt_intersect', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_meerdere_plancaps_in_bemalingsgebied', 'Stap3_meerdere_plancaps_in_bemalingsgebied', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_plancap_in_meerdere_bemalingsgebieden', 'Stap3_plancap_in_meerdere_bemalingsgebieden', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_stats_drinkwater', 'Stap3_stats_drinkwater', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_stats_vbo', 'Stap3_stats_vbo', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Stap3_stats_ve', 'Stap3_stats_ve', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Result_all_fields', 'result_all_fields', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # stap 1.) GWSW to Geodyn
        alg_params = {
            'GWSWBemalingsgebieden': parameters['inputbemalingsgebieden'],
            'GWSWnetwerkknooppunt': parameters['inputbemalingsgebieden (2)'],
            'GWSWnetwerkkunstwerk': parameters['inputbemalingsgebieden (2) (2)'],
            'MaxzoekafstandRG': 3,
            'netwerkverbinding': parameters['inputbemalingsgebieden (2) (2) (2)'],
            'result_folder': parameters['result_folder'],
            'Bemalingsgebieden_tbv_stap2': parameters['Stap1_bemalingsgebieden_tbv_stap2'],
            'BergingInKnopen': parameters['Stap1_berging_in_knopen'],
            'Berging_leiding_aggregated': parameters['Stap1_berging_leiding_aggregated'],
            'Berging_leiding_parts': parameters['Stap1_berging_leiding_parts'],
            'Eindpunten': parameters['Stap1_eindpunten'],
            'GebiedsgegevensStap1AllAtt': parameters['Stap1_gebiedsgegevens_stap1_all_att'],
            'Gebiedsgegevens_lijn_tbv_stap2': parameters['Stap1_gebiedsgegevens_lijn_tbv_stap2'],
            'Gebiedsgegevens_punt_tbv_stap2': parameters['Stap1_gebiedsgegevens_punt_tbv_stap2'],
            'GemengdeEnVuilwaterstelsels': parameters['Stap1_gemengde_en_vuilwaterstelsels'],
            'KnpStats': parameters['Stap1_knp_stats'],
            'LeidingenNietMeegenomen': parameters['Stap1_leidingen_niet_meegenomen'],
            'Rioolstelsel_buffer': parameters['Stap1_rioolstelsel_buffer'],
            'Rioolstelsel_buffer_10m': parameters['Stap1_rioolstelsel_buffer_10m_buffer'],
            'Stelselkenmerken': parameters['Stap1_stelselkenmerken'],
            'Total_storage': parameters['Stap1_total_storage']
        }
        outputs['Stap1GwswToGeodyn'] = processing.run('GeoDynTools:stap 1.) GWSW to Geodyn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stap1_eindpunten'] = outputs['Stap1GwswToGeodyn']['Eindpunten']
        results['Stap1_gebiedsgegevens_punt_tbv_stap2'] = outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_punt_tbv_stap2']
        results['Stap1_bemalingsgebieden_tbv_stap2'] = outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2']
        results['Stap1_berging_in_knopen'] = outputs['Stap1GwswToGeodyn']['BergingInKnopen']
        results['Stap1_berging_leiding_aggregated'] = outputs['Stap1GwswToGeodyn']['Berging_leiding_aggregated']
        results['Stap1_berging_leiding_parts'] = outputs['Stap1GwswToGeodyn']['Berging_leiding_parts']
        results['Stap1_gebiedsgegevens_lijn_tbv_stap2'] = outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2']
        #results['Stap1_gebiedsgegevens_stap1_all_att'] = outputs['Stap1GwswToGeodyn']['GebiedsgegevensStap1AllAtt']
        results['Stap1_gemengde_en_vuilwaterstelsels'] = outputs['Stap1GwswToGeodyn']['GemengdeEnVuilwaterstelsels']
        results['Stap1_knp_stats'] = outputs['Stap1GwswToGeodyn']['KnpStats']
        results['Stap1_leidingen_niet_meegenomen'] = outputs['Stap1GwswToGeodyn']['LeidingenNietMeegenomen']
        results['Stap1_rioolstelsel_buffer'] = outputs['Stap1GwswToGeodyn']['Rioolstelsel_buffer']
        results['Stap1_rioolstelsel_buffer_10m_buffer'] = outputs['Stap1GwswToGeodyn']['Rioolstelsel_buffer_10m']
        results['Stap1_stelselkenmerken'] = outputs['Stap1GwswToGeodyn']['Stelselkenmerken']
        results['Stap1_total_storage'] = outputs['Stap1GwswToGeodyn']['Total_storage']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # stap 2.) genereer_afvoerrelaties
        alg_params = {
            'bemalingsgebieden': outputs['Stap1GwswToGeodyn']['Bemalingsgebieden_tbv_stap2'],
            'gebiedsgegevenspunttbvstap2': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_punt_tbv_stap2'],
            'leidingen': outputs['Stap1GwswToGeodyn']['Gebiedsgegevens_lijn_tbv_stap2'],
            'result_folder': parameters['result_folder'],
            'Afvoerboom': parameters['Stap2_afvoerrelaties_bemalingsgebieden'],
            'Bemalingsgebieden_met_afvoerrelaties_tbv_stap3': parameters['Stap2_bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'Eindpunten_in_eindgebied_selected': parameters['Stap2_eindpunten_in_eindgebied_selected'],
            'Gebiedsgegevens_lijn_selectie': parameters['Stap2_afvoerrelaties_rioolgemalen'],
            'Van_naar': parameters['Stap2_van_naar'],
            'Van_naar_sel': parameters['Stap2_rioolgemalen_gekoppeld']
        }
        outputs['Stap2Genereer_afvoerrelaties'] = processing.run('GeoDynTools:stap 2.) genereer_afvoerrelaties', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Stap2_afvoerrelaties_bemalingsgebieden'] = outputs['Stap2Genereer_afvoerrelaties']['Afvoerboom']
        results['Stap2_afvoerrelaties_rioolgemalen'] = outputs['Stap2Genereer_afvoerrelaties']['Gebiedsgegevens_lijn_selectie']
        results['Stap2_bemalingsgebieden_met_afvoerrelaties_tbv_stap3'] = outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3']
        results['Stap2_eindpunten_in_eindgebied_selected'] = outputs['Stap2Genereer_afvoerrelaties']['Eindpunten_in_eindgebied_selected']
        results['Stap2_rioolgemalen_gekoppeld'] = outputs['Stap2Genereer_afvoerrelaties']['Van_naar_sel']
        results['Stap2_van_naar'] = outputs['Stap2Genereer_afvoerrelaties']['Van_naar']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # stap 3.) bereken afvalwaterprognose
        alg_params = {
            'bemalingsgebiedenstats': outputs['Stap2Genereer_afvoerrelaties']['Bemalingsgebieden_met_afvoerrelaties_tbv_stap3'],
            'bgtinlooptabel': parameters['inputbemalingsgebieden (2) (2) (2) (2)'],
            'inputdrinkwater': parameters['inputbemalingsgebieden (2) (2) (3) (2)'],
            'inputdrinkwater (2)': parameters['bag_verblijfsobjecten'],
            'inputplancap': parameters['inputbemalingsgebieden (2) (2) (2) (2) (2)'],
            'inputves': parameters['inputbemalingsgebieden (2) (2) (3)'],
            'inw_per_adres': 2.5,
            'result_folder': parameters['result_folder'],
            'Bemalingsgebieden_joined_stats': parameters['Stap3_bemalingsgebieden_joined_stats'],
            'Bgt_intersect': parameters['Stap3_bgt_intersect'],
            'Eindresultaat': parameters['Eindresultaat'],
            'Exafw_per_bem_id': parameters['Stap3_exafw_per_bem_id'],
            'Meerdere_plancaps_in_bemalingsgebied': parameters['Stap3_meerdere_plancaps_in_bemalingsgebied'],
            'Plancap_in_meerdere_bemalingsgebieden': parameters['Stap3_plancap_in_meerdere_bemalingsgebieden'],
            'Plancap_pc_id': parameters['Stap3_plancap_pc_id'],
            'Result_all_fields': parameters['Result_all_fields'],
            'Stats_drinkwater': parameters['Stap3_stats_drinkwater'],
            'Stats_vbo': parameters['Stap3_stats_vbo'],
            'Stats_ve': parameters['Stap3_stats_ve']
        }
        outputs['Stap3BerekenAfvalwaterprognose'] = processing.run('GeoDynTools:stap 3.) bereken afvalwaterprognose', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eindresultaat'] = outputs['Stap3BerekenAfvalwaterprognose']['Eindresultaat']
        #results['Stap3_exafw_per_bem_id'] = outputs['Stap3BerekenAfvalwaterprognose']['Exafw_per_bem_id']
        results['Stap3_plancap_pc_id'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_pc_id']
        results['Stap3_bemalingsgebieden_joined_stats'] = outputs['Stap3BerekenAfvalwaterprognose']['Bemalingsgebieden_joined_stats']
        results['Stap3_bgt_intersect'] = outputs['Stap3BerekenAfvalwaterprognose']['Bgt_intersect']
        results['Stap3_meerdere_plancaps_in_bemalingsgebied'] = outputs['Stap3BerekenAfvalwaterprognose']['Meerdere_plancaps_in_bemalingsgebied']
        results['Stap3_plancap_in_meerdere_bemalingsgebieden'] = outputs['Stap3BerekenAfvalwaterprognose']['Plancap_in_meerdere_bemalingsgebieden']
        results['Stap3_stats_drinkwater'] = outputs['Stap3BerekenAfvalwaterprognose']['Stats_drinkwater']
        results['Stap3_stats_vbo'] = outputs['Stap3BerekenAfvalwaterprognose']['Stats_vbo']
        results['Stap3_stats_ve'] = outputs['Stap3BerekenAfvalwaterprognose']['Stats_ve']
        results['Result_all_fields'] = outputs['Stap3BerekenAfvalwaterprognose']['Result_all_fields']


        # --- add below each alg_params {} 
        # alg_params['keepName'] = True

        #results, context, feedback = rename_layers(results, context, feedback)

        return results

    def name(self):
        return 'Alle stappen achter elkaar GWSW'

    def displayName(self):
        return 'Alle stappen achter elkaar GWSW'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return GeodynAlleStappen()    

        # ----- copy this code before returning results in algorithm class 
        # this is needed to rename layers. looks funky, but works!
        # for key in results:
        #     feedback.pushInfo("rename layer to {}".format(key))
        #     globals()[key] = Renamer(key) #create unique global renamer instances
        #     context.layerToLoadOnCompletionDetails(results[key]).setPostProcessor(globals()[key])