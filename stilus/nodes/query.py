import copy
import json

from stilus.nodes.node import Node


class Query(Node):

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.type = ''
        self.predicate = ''

    def __str__(self):
        pred = self.predicate + ' ' if self.predicate else ''
        if self.type:
            type = self.type
        else:
            type = ''
        s = ' and '.join([str(e) for e in self.nodes])
        return f'{pred}{type}{s}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.value

    def __eq__(self, other):
        if isinstance(other, Query):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def append(self, feature):
        self.nodes.append(feature)

    def resolved_type(self):
        if self.type:
            if hasattr(self.type, 'node_name'):
                return self.type.string
            else:
                return self.type

    def resolved_predicate(self):
        if self.predicate:
            if hasattr(self.predicate, 'node_name'):
                return self.predicate.string
            else:
                return self.predicate

    def merge(self, other):
        query = Query()
        p1 = self.resolved_predicate()
        p2 = other.resolved_predicate()
        t1 = self.resolved_type()
        t2 = other.resolved_type()

        if t1:
            t1 = t1
        else:
            t1 = t2
        if t2:
            t2 = t2
        else:
            t2 = t1

        if 'not' == p1 ^ 'not' == p2:
            if t1 == t2:
                return
            type = t2 if 'not' == t1 else t1
            pred = p2 if 'not' == p1 else p1
        elif 'not' == p1 and 'not' == p2:
            if t1 != t2:
                return
            type = t1
            pred = 'not'
        elif t1 != t2:
            return
        else:
            type = t1
            if p1:
                pred = p1
            else:
                pred = p2

        query.predicate = pred
        query.type = type
        query.nodes = self.nodes.extend(other.nodes)
        return query

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Query',
                           'predicate': self.predicate,
                           'type': self.type,
                           'nodes': self.nodes,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
