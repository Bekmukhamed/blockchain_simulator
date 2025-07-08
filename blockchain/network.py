import random

def stub_pairing(nodes_list, neighbors):
    stubs = []
    for node in nodes_list:
        for _ in range(neighbors):
            stubs.append(node.node_id)

    random.shuffle(stubs)
    
    while len(stubs) >= 2:
        stub1 = stubs.pop()
        stub2 = stubs.pop()
        if stub1 == stub2 or stub2 in nodes_list[stub1].neighbors:
            stubs.extend([stub1, stub2])
            random.shuffle(stubs)
            continue


        nodes_list[stub1].neighbors.add(stub2)
        nodes_list[stub2].neighbors.add(stub1)

                