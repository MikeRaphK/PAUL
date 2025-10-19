            if (length == longest || (length + 1 <= longest && val < arr[ends.get(length + 1)])) {
                ends.put(length + 1, i);
                longest = length + 1;
            }  
            
