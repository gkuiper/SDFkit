#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main class to that represents an SDF graphf.

author: Rinse Wester

"""

import networkx as nx
import json
from copy import deepcopy


class SDFGraph(nx.DiGraph):

    def __init__(self, name=''):

        super().__init__()

        self.name = name

        # state sorage for backtracking in simulations (tokens and counters)
        self.edgestates = {}
        self.nodestates = {}

        # counter to count number of clockcycles: accessable from node
        # functions
        self.clockcount = 0

    def add_edge(self, src, dst, resnr, argnr, prates, crates, tkns=[]):

        super(SDFGraph, self).add_edge(src, dst)
        self.edge[src][dst]['res'] = resnr
        self.edge[src][dst]['arg'] = argnr
        self.edge[src][dst]['prates'] = prates
        self.edge[src][dst]['crates'] = crates
        self.edge[src][dst]['tkns'] = tkns
        self.edge[src][dst]['itkns'] = []
        self.edgestates[(src, dst)] = [tkns]

    def add_self_edge(self, n, resnr, argnr, prates, crates, tkns=[], angle=0.6):

        self.add_edge(n, n, resnr, argnr, prates, crates, tkns)
        self.edge[n][n]['angle'] = angle

    def add_node(self, n, f, pos):

        super(SDFGraph, self).add_node(n)
        self.updateNodeFunction(n, f)
        self.node[n]['firecount'] = 0
        self.nodestates[n] = [0]
        self.node[n]['pos'] = pos

    def add_nodes_from(self, ns):

        for n, f, p in ns:
            self.add_node(n, f, p)

    def add_edges_from(self, es):

        for src, dst, resnr, argnr, prates, crates, tkns in es:
            self.add_edge(src, dst, resnr, argnr, prates, crates, tkns)

    def reset(self):

        for (src, dst), states in self.edgestates.items():
            self[src][dst]['tkns'] = states[0]
            del self.edgestates[(src, dst)][1:]

        # reset clcok and firing counters
        for n in self.nodes():
            self.node[n]['firecount'] = 0
            self.nodestates[n] = [0]
        self.clockcount = 0

    def _storestate(self):

        for (src, dst), states in self.edgestates.items():
            states.append(self[src][dst]['tkns'])

        for n, states in self.nodestates.items():
            states.append(self.node[n]['firecount'])

    def stateCount(self):

        e0 = list(self.edgestates.keys())[0]
        return len(self.edgestates[e0])

    def back(self):

        for (src, dst), states in self.edgestates.items():
            self[src][dst]['tkns'] = states[-2]
            states.pop()

        for n, states in self.nodestates.items():
            self.node[n]['firecount'] = states[-2]
            states.pop()

    def step(self):

        # perform single iteration of DF graph
        for n in self.nodes():
            canfire = True
            source_nodes = []
            for src in self.predecessors(n):
                source_nodes.append(src)
                phase = self.node[n]['firecount'] % len(self[src][n]['crates'])
                canfire &= len(self[src][n]['tkns']) >= self[
                    src][n]['crates'][phase]
            if canfire:
                # collect arguments
                args = []
                arg_inds = []
                for src in source_nodes:
                    arg_inds.append(self[src][n]['arg'])
                    phase = self.node[n]['firecount'] % len(
                        self[src][n]['crates'])
                    crate = self[src][n]['crates'][phase]
                    if crate > 0:
                        args.append(self[src][n]['tkns'][-crate:])
                        self[src][n]['tkns'] = self[src][n]['tkns'][:-crate]
                    else:
                        args.append([])
                # order arguments
                args_sorted = [0] * len(args)
                for i, v in zip(arg_inds, args):
                    args_sorted[i] = v

                # execute node function where clockcount and firecount are
                # variables that can be used inside the function of a node
                res = self.node[n]['func'](
                    *args_sorted, clockcount=self.clockcount,
                    firecount=self.node[n]['firecount'])
                if type(res) is tuple:
                    results = list(res)
                else:
                    results = [res]
                self.node[n]['firecount'] += 1

                # add result to intermediate buffers connected to succeeding
                # nodes
                for dest in self.successors(n):
                    self[n][dest]['itkns'] = results[self[n][dest]['res']]
        # add all the intermediate buffers to buffers
        for src, dst in self.edges():
            itkns = self[src][dst]['itkns']
            self[src][dst]['tkns'] = itkns + self[src][dst]['tkns']
            self[src][dst]['itkns'] = []

        # store the new state for backtracking
        self._storestate()

        # increase clock for the global clock
        self.clockcount += 1

    # This function converts a list of production/consumption
    # rates to the flat variant: [1, "2*4", 3, "3*2"] becomes:
    # [1, 4, 4, 3, 2, 2, 2]
    def _flattenRateList(lst):

        res = []
        for elm in lst:
            if type(elm) is str:
                replfac, rate = elm.split('*')
                replfac = int(replfac)
                rate = int(rate)
                elms = [rate] * replfac
                res.extend(elms)
            else:
                res.append(elm)
        return res

    def loadFromFile(self, filename):

        try:
            with open(filename, 'r') as f:
                jsonstr = f.read()

            jsondata = json.loads(jsonstr)
            self.name = jsondata['name']

            for jsnode in jsondata['nodes']:
                nodeName = jsnode['name']
                nodeFunction = jsnode['function']
                nodePosition = jsnode['pos'][0], jsnode['pos'][1]
                self.add_node(nodeName, nodeFunction, nodePosition)

            for jsedge in jsondata['edges']:
                edgeSource = jsedge['src']
                edgeDestination = jsedge['dst']
                if 'name' in jsedge.keys():
                    edgeName = jsedge['name']
                else:
                    edgeName = edgeSource + ' → ' + edgeDestination
                edgeResNumber = jsedge['resnr']
                edgeArgNumber = jsedge['argnr']
                edgePRates = SDFGraph._flattenRateList(jsedge['prates'])
                edgeCRates = SDFGraph._flattenRateList(jsedge['crates'])
                edgeTokens = jsedge['tkns']
                if edgeSource == edgeDestination:
                    edgeAngle = jsedge['angle']
                    self.add_self_edge(
                        edgeSource, edgeResNumber, edgeArgNumber, edgePRates,
                        edgeCRates, edgeTokens, edgeAngle)
                else:
                    self.add_edge(
                        edgeSource, edgeDestination, edgeResNumber, edgeArgNumber,
                        edgePRates, edgeCRates, edgeTokens)
        except Exception as e:
            print("Error occurred: ", e)

    def updateNodeFunction(self, nodename, funcstr):

        self.node[nodename]['funcstr'] = funcstr
        self.node[nodename]['func'] = eval(funcstr)

    def print_state(self):

        for src, dst in self.edges():
            tkns = self[src][dst]['tkns']
            print(src, ' --- ', tkns, ' --> ', dst)

    def test(self):

        # Check wether the edges state store and restore works properly
        initEdgeState = deepcopy(self.edgestates)
        self.step()
        self.step()
        self.reset()
        print(
            'Reset check of', self.name,
            'correct: ', initEdgeState == self.edgestates)

        # Check wether the node state store and restore works properly
        self.step()
        secondCntrState = deepcopy(self.nodestates)
        self.step()
        self.step()
        self.back()
        self.back()
        print(
            'Firecount check of', self.name,
            'correct: ', secondCntrState == self.nodestates)


# Create a simple SDF graph
G0 = SDFGraph()
G0.loadFromFile('examples/distinct outputs.json')
G0.test()

G1 = SDFGraph()
G1.loadFromFile('examples/producer consumer.json')
G1.test()

G2 = SDFGraph()
G2.loadFromFile('examples/alternating merge.json')
G2.test()

G3 = SDFGraph()
G3.loadFromFile('examples/simple graph.json')
G3.test()


# Functions for nodes
# cpy = 'lambda xs: [xs[0], xs[0]]'
# forw = 'lambda xs: xs'
# addm = 'lambda xs, y: [((xs[0] + xs[1]) * y[0]) % 27]'
# intgr = 'lambda x, y: [x[0]+y[0]]'

# G0.add_nodes_from([
#   ('n0', cpy,  (100, 100)),
#   ('n1', addm, (100, 300)),
#   ('n2', forw,  (300, 300)),
#   ('n3', intgr,  (300, 100))])
# G0.add_edges_from([
#   ('n0','n1', 0, [2], [2], []),
#   ('n1','n2', 0, [1], [1], []),
#   ('n2','n1', 1, [1], [1], [1]),
#   ('n2','n3', 0, [1], [1], []),
#   ('n3','n0', 0, [1], [1], [1])])
# G0.add_self_edge('n3', 1, [1], [1], [0], 7/8*2*math.pi)
