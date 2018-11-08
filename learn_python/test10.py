# water container
class Solution(object):
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        the_max = 0
        for i in range(len(height)-1):
            for j in range(i+1, len(height)):
                if height[i] > height[j]:
                    if the_max < height[j] * (j-i):
                        the_max = height[j] * (j-i)
                else:
                    if the_max < height[i]* (j-i):
                        the_max = height[i] * (j-i)
        return the_max

class Solution(object):
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        the_max = 0
        left, right = 0, len(height)-1
        while left < right:
            the_max = max(the_max, min(height[left], height[right])*(right-left))
            if height[left] > height[right]:
                right = right-1
            else:
                left = left+1
        return the_max

