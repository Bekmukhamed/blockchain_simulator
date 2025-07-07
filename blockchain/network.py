def connect_nodes(node1, node2):
    node1.neighbors.add(node2)
    node2.neighbors.add(node1)
    print(f"Node {node1.node_id} connected to Node {node2.node_id}.")