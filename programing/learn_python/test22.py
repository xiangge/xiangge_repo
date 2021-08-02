# Array: [[7], [3, 8], [8, 1, 0], [2, 7, 4, 4], [4, 5, 2, 6, 5]]
# Sample Input
# 5
#     7
#    3 8
#   8 1 0 
#  2 7 4 4
# 4 5 2 6 5
# Sample Output
# 30

def get_large_output(deep, tree_list):
    output = [0]
    if deep ==0:
    	return 0
    if deep == 1:
    	return tree_list[0][0]
    def get_number(layer, layer_index, temp_value):
    	# global output
    	if layer == deep:
    	    if output[0] < temp_value:
    	    	output[0] = temp_value
    	    return
        node_list = tree_list[layer]
    	for i in range(len(node_list)):
    		if i == layer_index or i == layer_index+1:
    			get_number(layer+1, i, temp_value + node_list[i])

    get_number(0, 0, 0)
    return output[0]


def get_output(deep_layer, tree_list):
    if deep_layer ==0:
        return 0
    if deep_layer == 1:
        return tree_list[0][0]
    layer = 0
    max_layer = deep_layer-1
    while layer < max_layer:
        node_list = tree_list[layer]
        next_layer = tree_list[layer+1]
        for i in range(len(node_list)):
            if i == 0:
                next_layer[i] = node_list[i] + next_layer[i]
            if i < len(node_list) - 1:
                if node_list[i] >= node_list[i+1]:
                    next_layer[i+1] = node_list[i] + next_layer[i+1]
                else:
                    next_layer[i+1] = node_list[i+1] + next_layer[i+1]
            else:
                next_layer[i+1] = node_list[i] + next_layer[i+1]        	
        layer = layer + 1
        if max_layer == layer:
        	return max(next_layer)



print(get_output(5, [[7], [3, 8], [8, 1, 0], [2, 7, 4, 4], [4, 5, 2, 6, 5]]))
