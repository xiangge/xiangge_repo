"""
Definition of TreeNode:
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left, self.right = None, None
"""


class Solution:
    """
    @param root: The root of binary tree.
    @return: Level order in a list of lists of integers
    """
    def levelOrder(self, root):
        # write your code here
        res = []
        # 如果根节点为空，则返回空列表
        if root is None:
            return res
        # 模拟一个队列储存节点
        q = []
        # 首先将根节点入队
        q.append(root)
        # 列表为空时，循环终止
        while len(q) != 0:
            # 使用列表存储同层节点
            tmp = []
            # 记录同层节点的个数
            length = len(q)
            for i in range(length):
                # 将同层节点依次出队
                r = q.pop(0)
                if r.left is not None:
                    # 非空左孩子入队
                    q.append(r.left)
                if r.right is not None:
                    # 非空右孩子入队
                    q.append(r.right)
                tmp.append(r.val)
            res.append(tmp)
        return res

