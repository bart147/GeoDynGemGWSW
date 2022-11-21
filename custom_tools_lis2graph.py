# -*- coding: utf-8 -*-
 
"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing

##from .Dijkstra import Graph, dijkstra
from builtins import object
from collections import defaultdict, deque

class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
    def add_node(self, value):
        self.nodes.add(value)
    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
		
def dijkstra(graph, initial):
    visited = {initial: 0}
    path = {}
    nodes = set(graph.nodes)
    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node
        if min_node is None:
            break
        nodes.remove(min_node)
        current_weight = visited[min_node]
        for edge in graph.edges[min_node]:
            try:
                weight = current_weight + graph.distances[(min_node, edge)]
            except:
                continue
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node
    return visited, path
	
def shortest_path(graph, origin, destination):
    visited, paths = dijkstra(graph, origin)
    full_path = deque()
    _destination = paths[destination]
    while _destination != origin:
        full_path.appendleft(_destination)
        _destination = paths[_destination]
    full_path.appendleft(origin)
    full_path.append(destination)
    return visited[destination], list(full_path)

class CustomToolsLis2GraphAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CustomToolsLis2GraphAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lis2graph'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('lis2graph')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('geodyn tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'geodyn_tools'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Maakt Graph met LIS-netwerk en bepaalt onderbemalingen")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def lis2graph(self, feedback, layer):
        """
        Maakt Graph met LIS-netwerk en bepaalt onderbemalingen.
        Vult [ONTV_VAN] en [X_OBEMAL].
        Gebruikt [LOOST_OP] en [VAN_KNOOPN] als edge (relation) en VAN_KNOOPN als node
        """
        # graph aanmaken
        graph = Graph()
        graph_rev = Graph()
        d_K_ONTV_VAN = {}    # alle onderliggende gemalen
        d_K_ONTV_VAN_n1 = {} # alle onderliggende gemalen op 1 niveau diep ivm optellen overcapaciteit
        feedback.pushInfo ("netwerk opslaan als graph...")
        VAN_FLD = "BEM_ID"
        NAAR_FLD = "NAAR_BEM_ID"

        for feature in layer.getFeatures():  # .getFeatures()
            VAN_KNOOPN = feature[VAN_FLD]
            LOOST_OP = feature[NAAR_FLD]
            graph.add_node(VAN_KNOOPN)
            graph_rev.add_node(VAN_KNOOPN)
            if LOOST_OP != None:
                graph.add_edge(VAN_KNOOPN, LOOST_OP, 1)  # richting behouden voor bovenliggende gebied
                graph_rev.add_edge(LOOST_OP, VAN_KNOOPN, 1)  # richting omdraaien voor onderliggende gebied
        edges_as_tuple = list(graph.distances)  # lijst met tuples: [('A', 'B'), ('C', 'B')]
        feedback.pushInfo("onderbemaling bepalen voor rioolgemalen en zuiveringen...")
        where_clause = "Join_Count > 0"
        layer.startEditing()
        for i, feature in enumerate(layer.getFeatures()):  # .getFeatures()
            ##if not feature["count"] >= 1: continue
            VAN_KNOOPN = feature[VAN_FLD]
            ##if not feature[NAAR_FLD]: continue 
            nodes = dijkstra(graph, VAN_KNOOPN)[0]
            ##print_log("nodes for {}: {}".format(VAN_KNOOPN,nodes), 'd')
            K_KNP_EIND, X_OPPOMP = [(key, value) for key, value in sorted(iter(nodes.items()), key=lambda k_v: (k_v[1], k_v[0]))][-1]
            ##print_log("endnode for {}: {},{}".format(VAN_KNOOPN,K_KNP_EIND, X_OPPOMP),'d')
            d_edges = dijkstra(graph_rev, VAN_KNOOPN)[1]  # {'B': 'A', 'C': 'B', 'D': 'C'}
            l_onderliggende_gemalen = str(list(d_edges))  # [u'ZRE-123',u'ZRE-234']
            l_onderliggende_gemalen = l_onderliggende_gemalen.replace("u'", "'").replace("[", "").replace("]", "")
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_ONTV_VAN"), l_onderliggende_gemalen) # K_ONTV_VAN = 'ZRE-1','ZRE-2'
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("X_OBEMAL"), len(list(d_edges)))        # X_OBEMAL = 2 (aantal onderbemalingen)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("X_OPPOMP"),  X_OPPOMP + 1)             # X_OPPOMP = 1 (aantal keer oppompen tot rwzi) met shortestPath ('RWZI','ZRE-4')
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("K_KNP_EIND"), K_KNP_EIND)              # eindbemalingsgebied / overnamepunt. bepaald uit netwerk.
            d_K_ONTV_VAN[VAN_KNOOPN] = l_onderliggende_gemalen
            # onderbemalingen 1 niveau diep
            l_onderliggende_gemalen_n1 = [start for start, end in edges_as_tuple if end == VAN_KNOOPN]  # dus start['A', 'C'] uit tuples[('A', 'B'),('C', 'B')] als end == 'B'
            d_K_ONTV_VAN_n1[VAN_KNOOPN] =  str(l_onderliggende_gemalen_n1).replace("u'", "'").replace("[", "").replace("]", "") # naar str() en verwijder u'tjes en haken
        layer.commitChanges()
        return [d_K_ONTV_VAN, d_K_ONTV_VAN_n1]

    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        input_layer = self.parameterAsVectorLayer(
            parameters, 
            self.INPUT, 
            context
        )


        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))
        feedback.pushInfo('test test')

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        
        self.lis2graph(feedback, input_layer)
        
        if False:
            buffered_layer = processing.run("native:buffer", {
                'INPUT': dest_id,
                'DISTANCE': 1.5,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
