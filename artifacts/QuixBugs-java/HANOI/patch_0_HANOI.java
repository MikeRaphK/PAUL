        // Fix: Correct the logic for moving the disks to the correct helper peg
            PriorityQueue<Integer> crap_set = new PriorityQueue<Integer>();
            crap_set.add(1);
            crap_set.add(2);
            crap_set.add(3);
            crap_set.remove(start);
            crap_set.remove(end);
            int helper = crap_set.peek(); // Use peek instead of poll
            steps.add(new Pair<Integer,Integer>(start, helper));
