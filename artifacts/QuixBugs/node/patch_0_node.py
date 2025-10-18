class Node:
    def __init__(self, value=None, successor=None, successors=[], predecessors=[], incoming_nodes=[], outgoing_nodes=[]):
        self.value = value
        self.successor = successor
        self.successors = successors
        self.predecessors = predecessors
        self.incoming_nodes = incoming_nodes
        self.outgoing_nodes = outgoing_nodes

    # Renamed method to avoid conflict with property
    def _get_successor(self):
        return self.successor

    # Renamed method to avoid conflict with property
    def _get_successors(self):
        return self.successors

    # Renamed method to avoid conflict with property
    def _get_predecessors(self):
        return self.predecessors
