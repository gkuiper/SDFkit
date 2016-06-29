#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
class for the CLaSH code generation

author: Rinse Wester

"""


from csdfgraph import *


class ClashCodeGen(object):
    """docstring for ClashCodeGen"""

    def __init__(self, arg):
        super(ClashCodeGen, self).__init__()
        self.arg = arg

    def generateCode(graph, targetdir):

        if not graph.isHSDF():
            raise NotImplementedError(
                'CLaSH codegen only supported for HSDF graphs')
        else:
            print(ClashCodeGen._generateNodeFuncDefs(graph))
            print(ClashCodeGen._generateEdgeDefs(graph))
            print(ClashCodeGen._generateEdgeInstances(graph))
            print(ClashCodeGen._generateNodeDefs(graph))

    def _generateEdgeInstances(graph):

        edgeInstances = ''

        for src, dst in graph.edges():
            ename = 'e_' + src + '_' + dst
            edgeInstances += "({0}_dataout, {0}_empty, {0}_full) = unbundle $ {0}L $ bundle ({0}_datain, {0}_rd, {0}_wrt)\n".format(ename)
        return edgeInstances

    def _generateNodeFuncDefs(graph):

        functions = ''

        for n in graph.nodes():
            functions += graph.node[n]['clashcode']
            functions += '\n\n'
        return functions

    def _generateNodeDefs(graph):

        nodedefs = ''

        for n in graph.nodes():

            nname = 'n_' + n

            # create the type def of the node function
            typenames = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z']
            inputcount = len(graph.predecessors(n))
            outputcount = len(graph.successors(n))

            finptypes = typenames[:inputcount]
            foutptypes = typenames[inputcount:inputcount + outputcount]

            # Create the type definition of the node function
            ftypestr = '('
            for t in finptypes:
                ftypestr += t + ' -> '
            ftypestr += 'Cntr -> Cntr -> ('
            ftypestr += ', '.join(foutptypes)
            ftypestr += '))'

            # create the list of input types
            ninptypes = finptypes
            # add bool types for the 'empty' input
            for i in range(inputcount):
                ninptypes.append('Bool')
            # add bool types for the 'full' input
            for i in range(outputcount):
                ninptypes.append('Bool')
            ninptypesstr = '(' + (', '.join(ninptypes)) + ')'

            # Create the list of output types: types for data on edges and bool for fire
            noutptypes = foutptypes + ['Bool']
            noutptypesstr = '(' + (', '.join(noutptypes)) + ')'

            # And now the final string with the type definition of a node
            ntypedef = nname + ' :: ' + ftypestr + ' -> (Cntr, Cntr) -> ' + ninptypesstr + ' -> ((Cntr, Cntr), ' + noutptypesstr + ')'
            print(ntypedef)

# hsdfnode_1_2 :: (a -> Cntr -> Cntr ->(b, c)) -> (Cntr, Cntr) -> (a, Bool, Bool, Bool) -> ((Cntr, Cntr), (b, c, Bool))
# hsdfnode_1_2 f (firecounter, phase) (datain0, empty0, full0, full1) = ((firecounter', phase'), (dataout0, dataout1, fire))
#     where
#         fire = not empty0 && not full0 && not full1
#         firecounter' = if fire then firecounter + 1 else firecounter
#         phase_max = 0
#         phase' = if fire then (if phase < phase_max then phase + 1 else 0) else phase_max
#         (dataout0, dataout1) = f datain0 firecounter phase



    def _generateEdgeDefs(graph):
        edgedefs = ''

        for src, dst in graph.edges():
            tokens = graph[src][dst]['tkns']
            tokensexp = (tokens + [0,0,0,0,0,0,0,0])[:8]
            tokensstr = ''
            for tkn in tokensexp:
                tokensstr += str(tkn)
                tokensstr += ' <: '
            tokensstr += ' Nil'
            edgedefs += 'e_' + src + '_' + dst +'L = mealy hsdfedge8 (' + tokensstr + ' :: Vec8 Cntr, 0 :: RdPtr, ' + str(len(tokens)) + ' :: WrPtr)\n' 

        return edgedefs
