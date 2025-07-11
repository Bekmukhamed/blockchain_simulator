import random
from dataclasses import dataclass
    
@dataclass
class Node:
    node_id: int
    blocks_id: set
    neighbors: set


def stub_pairing(nodes_list, neighbors):
    stubs = []
    for node in nodes_list:
        for _ in range(neighbors):
            stubs.append(node.node_id)

    random.shuffle(stubs)
    print(f"Initial stubs: {stubs}\n")
    
    # Keep track of failed attempts to avoid infinite loops
    max_attempts = len(stubs) * 2
    failed_attempts = 0
    
    while len(stubs) >= 2:
        print(f"Current stubs: {stubs}")

        stub1 = stubs.pop()
        stub2 = stubs.pop()
        print(f"Popped stubs: {stub1} and {stub2}\n")
        print(f"neighbors number for {stub1}: {len(nodes_list[stub1].neighbors)}")
        print(f"neighbors number for {stub2}: {len(nodes_list[stub2].neighbors)}\n")
        
        # Check if both nodes already have enough neighbors
        if (len(nodes_list[stub1].neighbors) >= neighbors or len(nodes_list[stub2].neighbors) >= neighbors):
            print(f"Skipping pairing of {stub1} and {stub2} (one or both have enough neighbors)")
            stubs.extend([stub1, stub2])
            random.shuffle(stubs)
            failed_attempts += 1
            
            # If we've tried too many times, remove stubs from nodes that are full
            if failed_attempts > max_attempts:
                print("Too many failed attempts, cleaning up stubs from full nodes...")
                stubs = [s for s in stubs if len(nodes_list[s].neighbors) < neighbors]
                failed_attempts = 0
            continue

        elif stub1 == stub2 or stub2 in nodes_list[stub1].neighbors:
            print(f"Skipping pairing of {stub1} and {stub2} (same node or already neighbors)")
            # Only add back stubs that haven't reached their neighbor limit
            remaining_stubs = [s for s in [stub1, stub2] if len(nodes_list[s].neighbors) < neighbors]
            stubs.extend(remaining_stubs)
            random.shuffle(stubs)
            failed_attempts += 1
            
            # If we've tried too many times, remove stubs from nodes that are full
            if failed_attempts > max_attempts:
                print("Too many failed attempts, cleaning up stubs from full nodes...")
                stubs = [s for s in stubs if len(nodes_list[s].neighbors) < neighbors]
                failed_attempts = 0
            continue
        
        print(f"Pairing {stub1} with {stub2}")
        nodes_list[stub1].neighbors.add(stub2)
        nodes_list[stub2].neighbors.add(stub1)
        failed_attempts = 0  # Reset failed attempts on successful pairing
    
    # Handle remaining stubs
    if len(stubs) > 0:
        print(f"\nWarning: {len(stubs)} stub(s) could not be paired: {stubs}")
        print("This typically happens when:")
        print("1. Total number of stubs is odd")
        print("2. Some nodes reached their neighbor limit")
        print("3. Remaining stubs belong to nodes that are already neighbors or the same node")
        
        # Clean up remaining stubs from nodes that already have enough neighbors
        remaining_stubs = [s for s in stubs if len(nodes_list[s].neighbors) < neighbors]
        if len(remaining_stubs) < len(stubs):
            print(f"Removed {len(stubs) - len(remaining_stubs)} stubs from nodes that already have enough neighbors")
        
        if len(remaining_stubs) > 0:
            print(f"Final unpaired stubs: {remaining_stubs}")
    
    print("Stub pairing completed!")


# Test with the problematic case
nodes = []
num_of_nodes = 5
neighbors = 3

for id in range(num_of_nodes):
    node = Node(node_id=id, blocks_id=set(), neighbors=set())
    nodes.append(node)
print(f"Created {len(nodes)} nodes.")

print("Nodes before pairing:")
for node in nodes:
    print(f"Node {node.node_id}: neighbors = {node.neighbors}")

print("\nPerforming stub pairing...")
stub_pairing(nodes, neighbors)

print("\nNodes after pairing:")
for node in nodes:
    print(f"Node {node.node_id}: neighbors = {node.neighbors}")
