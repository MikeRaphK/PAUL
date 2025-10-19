package java_programs;
import java.util.*;
/**
 * Minimum spanning tree
 */
public class MINIMUM_SPANNING_TREE {
    public static Set<WeightedEdge> minimum_spanning_tree(List<WeightedEdge> weightedEdges) {
        Map<Node, Set<Node>> groupByNode = new HashMap<>();
        Set<WeightedEdge> minSpanningTree = new HashSet<>();

        Collections.sort(weightedEdges);

        for (WeightedEdge edge : weightedEdges) {
            Node vertex_u = edge.node1;
            Node vertex_v = edge.node2;

            if (!groupByNode.containsKey(vertex_u)) {
                groupByNode.put(vertex_u, new HashSet<>(Arrays.asList(vertex_u)));
            }
            if (!groupByNode.containsKey(vertex_v)) {
                groupByNode.put(vertex_v, new HashSet<>(Arrays.asList(vertex_v)));
            }

            // Only add edge if it connects two different components
            if (!groupByNode.get(vertex_u).equals(groupByNode.get(vertex_v))) {
                minSpanningTree.add(edge);
                groupByNode = union(groupByNode, vertex_u, vertex_v);
            }
        }
        return minSpanningTree;
    }

    private static Map<Node, Set<Node>> union(Map<Node, Set<Node>> groupByNode, Node vertex_u, Node vertex_v) {
        Set<Node> nodes_u = groupByNode.get(vertex_u);
        Set<Node> nodes_v = groupByNode.get(vertex_v);

        // Merge the groups
        nodes_u.addAll(nodes_v);
        for (Node node : nodes_v) {
            groupByNode.put(node, nodes_u);
        }

        return groupByNode;
    }
}