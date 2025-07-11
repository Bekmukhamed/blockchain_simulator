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
    while len(stubs) >= 2:
        print(f"Current stubs: {stubs}")

        stub1 = stubs.pop()
        stub2 = stubs.pop()
        print(f"Popped stubs: {stub1} and {stub2}\n")
        print(f"neighbors number for {stub1}: {len(nodes_list[stub1].neighbors)}")
        print(f"neighbors number for {stub2}: {len(nodes_list[stub2].neighbors)}\n")
        if (len(nodes_list[stub1].neighbors) >= neighbors or len(nodes_list[stub2].neighbors) >= neighbors):
            print(f"Skipping pairing of {stub1} and {stub2} (one or both have enough neighbors)")
            stubs.extend([stub1, stub2])
            random.shuffle(stubs)
            continue

        elif stub1 == stub2 or stub2 in nodes_list[stub1].neighbors or len(nodes_list[stub1].neighbors) >= neighbors or len(nodes_list[stub2].neighbors) >= neighbors:
            print(f"Skipping pairing of {stub1} and {stub2} (same or already neighbors)")
            stubs.extend([stub1, stub2])
            random.shuffle(stubs)
            continue
        
        print(f"Pairing {stub1} with {stub2}")
        nodes_list[stub1].neighbors.add(stub2)
        nodes_list[stub2].neighbors.add(stub1)
    
    if len(stubs) > 0:
        print(f"WARNING: {len(stubs)} stub(s) remaining: {stubs}")

nodes = []
# Test with parameters that will cause the issue
num_of_nodes = 5
neighbors = 3  # This will create 15 stubs total (odd number)

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
