def minimum_spanning_tree(weight_by_edge):
    group_by_node = {}
    mst_edges = set()
    parent = {}

    def find(node):
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    # Initialize the parent of each node to itself
    for edge in weight_by_edge:
        u, v = edge
        parent[u] = u
        parent[v] = v

    for edge in sorted(weight_by_edge, key=weight_by_edge.__getitem__):
        u, v = edge
        root_u = find(u)
        root_v = find(v)

        if root_u != root_v:
            mst_edges.add(edge)
            parent[root_u] = root_v

    return mst_edges



"""
Minimum Spanning Tree


Kruskal's algorithm implementation.

Input:
    weight_by_edge: A dict of the form {(u, v): weight} for every undirected graph edge {u, v}

Precondition:
    The input graph is connected

Output:
    A set of edges that connects all the vertices of the input graph and has the least possible total weight.

Example:
    >>> minimum_spanning_tree({
    ...     (1, 2): 10,
    ...     (2, 3): 15,
    ...     (3, 4): 10,
    ...     (1, 4): 10
    ... })
    {(1, 2), (3, 4), (1, 4)}
"""