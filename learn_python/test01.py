
""" Node is defined as
class node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
"""
# right codes about the binary search tree
# use the LDR to get the list and then check each value and index +1 value
def checkBST(root):
    # global l
    l = []
    def put_tree_to_list(root):
        if not root:
            return None
        put_tree_to_list(root.left)
        l.append(root.data)
        put_tree_to_list(root.right)
    put_tree_to_list(root)
    for i in range(len(l)-1):
        if l[i] >= l[i+1]:
            return False
    return True    

#  1 def preTraverse(root):  
#  2     '''
#  3     前序遍历
#  4     '''
#  5     if root==None:  
#  6         return  
#  7     print(root.value)  
#  8     preTraverse(root.left)  
#  9     preTraverse(root.right)  
# 10 
# 11 def midTraverse(root): 
# 12     '''
# 13     中序遍历
# 14     '''
# 15     if root==None:  
# 16         return  
# 17     midTraverse(root.left)  
# 18     print(root.value)  
# 19     midTraverse(root.right)  
# 20   
# 21 def afterTraverse(root):  
# 22     '''
# 23     后序遍历
# 24     '''
# 25     if root==None:  
# 26         return  
# 27     afterTraverse(root.left)  
# 28     afterTraverse(root.right)  
# 29     print(root.value)  

# WRONG codes about the binary search tree
def checkBST(root):
    def left_check(left):
        if not left:
            return True
        if left.left and (left.left.data >= left.data):
            return False
        if left.right and (left.right.data <= left.data):
            return False
        if not left_check(left.left):
            return False
        if not left_check(left.right):
            return False
        if left.data > root.data:
            return False
        return True
        
    def right_check(right):
        if not right:
            return True
        if right.left and (right.left.data >= right.data):
            return False
        if right.right and (right.right.data <= right.data):
            return False
        if not right_check(right.left):
            return False
        if not right_check(right.right):
            return False
        if right.data < root.data:
            return False
        return True
    
    if not left_check(root.left) or not right_check(root.right):
        return False
    return True