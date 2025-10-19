package java_programs;
import java.util.*;
import java.util.ArrayDeque;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class BREADTH_FIRST_SEARCH {

    public static Set<Node> nodesvisited = new HashSet<>();

    public static boolean breadth_first_search(Node startnode, Node goalnode) {
        Deque<Node> queue = new ArrayDeque<>();
        queue.addLast(startnode);

        nodesvisited.add(startnode);

        while (!queue.isEmpty()) { // changed from while(true) to while(!queue.isEmpty())
            Node node = queue.removeFirst();

            if (node == goalnode) {
                return true;
            } else {
                for (Node successor_node : node.getSuccessors()) {
                    if (!nodesvisited.contains(successor_node)) {
                        queue.addLast(successor_node); // changed from addFirst to addLast to maintain BFS order
                        nodesvisited.add(successor_node);
                    }
                }
            }
        }
        return false; // Added return false to exit function when queue is empty.
    }

}