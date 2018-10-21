# print the binary tree by the layers
# 1. use stack

class TreeNode(object):
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def invert_tree(root):
    if not root:
        return None
    invert_tree(root.left)
    invert_tree(root.right)
    root.left, root.right = root.right, root.left
    return root

def print_tree(root):
    node_stack = [root]
    while node_stack:
        head = node_stack[0]
        if head.left:
            node_stack.append(head.left)
        if head.right:
            node_stack.append(head.right)
        print head.value
        del node_stack[0]


# second way is using a hash/dict


# third way is to use two lists
class Solution:
    # 返回二维列表[[1,2],[4,5]]
    def Print(self, pRoot):
        # write code here
        if pRoot is None:
            return []
        p = [pRoot]
        res = []
        while p:
            node = []
            li = []
            for x in p:
                if x.left:
                    node.append(x.left)
                if x.right:
                    node.append(x.right)
                li.append(x.val)
            p = node
            res.append(li)

        return res

