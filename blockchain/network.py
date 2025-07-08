import random


def connect_nodes(node1, node2):
    node1.neighbors.add(node2)
    node2.neighbors.add(node1)
    print(f"Node {node1.node_id} connected to Node {node2.node_id}.")


def stub_pairing(nodes_list, neighbors):
    stubs = []
    for node in nodes_list:
        for _ in range(neighbors):
            stubs.append(node.node_id)

    random.shuffle(stubs)
    neighbor_pairs = [(stubs[i], stubs[i+1]) for i in range (0, len(stubs), 2)]

    # while len(stubs) > 0:
                