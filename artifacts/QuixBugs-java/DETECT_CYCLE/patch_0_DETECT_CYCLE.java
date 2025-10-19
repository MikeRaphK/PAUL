package java_programs;
import java.util.*;
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class DETECT_CYCLE {
    public static boolean detect_cycle(Node node) {
        Node hare = node;
        Node tortoise = node;

        while (true) {
            if (hare.getSuccessor() == null) // Check if hare has a successor
                return false;

            tortoise = tortoise.getSuccessor();
            // Added null check for hare's successor
            if (hare.getSuccessor().getSuccessor() == null)
                return false;
            hare = hare.getSuccessor().getSuccessor();

            if (hare == tortoise)
                return true;
        }
    }
}