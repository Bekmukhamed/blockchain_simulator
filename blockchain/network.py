import random

def stub_pairing(nodes_list, neighbors):
    # Initialize stubs list
    stubs = []
    for node in nodes_list:
        for _ in range(neighbors):
            stubs.append(node.node_id)
    
    # print(f"Stubs befor while: {stubs}")
    
    while True:  # Main pairing loop
        # Get nodes that need more neighbors
        nodes_needing_neighbors = [
            node_id for node_id in range(len(nodes_list)) 
            if len(nodes_list[node_id].neighbors) < neighbors
        ]
        
        # print(f"Nodes needing neighbors: {nodes_needing_neighbors}")
        
        if len(nodes_needing_neighbors) < 2:
            break
            
        # Try to find a valid pair
        valid_pair = None
        for i in range(len(nodes_needing_neighbors)):
            for j in range(i + 1, len(nodes_needing_neighbors)):
                node1_id = nodes_needing_neighbors[i]
                node2_id = nodes_needing_neighbors[j]
                
                if (node1_id != node2_id and 
                    node2_id not in nodes_list[node1_id].neighbors and
                    node1_id in stubs and 
                    node2_id in stubs):
                    valid_pair = (node1_id, node2_id)
                    break
            if valid_pair:
                break
                
        if not valid_pair:
            break
            
        # Connect the valid pair
        node1_id, node2_id = valid_pair
        stubs.remove(node1_id)
        stubs.remove(node2_id)
        
        nodes_list[node1_id].neighbors.add(node2_id)
        nodes_list[node2_id].neighbors.add(node1_id)
        
        # print(f"Connected {node1_id} and {node2_id}")
        # print(f"Current neighbors: {[(i, len(nodes_list[i].neighbors)) for i in range(len(nodes_list))]}")
        # print(f"Remaining stubs: {stubs}\n")
    
    # print(f"Remaining stubs: {stubs}")
    # for i, node in enumerate(nodes_list):
    #     # print(f"Node {i} has {len(node.neighbors)} neighbors: {node.neighbors}")
    #     if len(node.neighbors) != neighbors:
    #         # print(f"WARNING: Node {i} should have {neighbors} neighbors!")
    
    return all(len(node.neighbors) == neighbors for node in nodes_list)
    # print("Stub pairing completed!")
    # print("0000--exit while")

