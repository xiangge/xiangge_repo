# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.next = None

# Write a program to find the node at which the intersection of two singly linked lists begins.
# For example, the following two linked lists:

# A:          a1 → a2
#                   ↘
#                     c1 → c2 → c3
#                   ↗
#B:     b1 → b2 → b3



class Solution(object):
    def getIntersectionNode(self, headA, headB):
        """
        :type head1, head1: ListNode
        :rtype: ListNode
        """
        node1 = headA
        node2 = headB
        if not node1 or not node2:
            return None
        
        while node1 != node2:
            node1 = node1.next
            node2 = node2.next
            if not node1 and not node2:
                return None
            if not node1:
                node1 = headB
            if not node2:
                node2 = headA
        return node1
