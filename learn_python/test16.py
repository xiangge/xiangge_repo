# 求x开平方
class Solution:
    def mySqrt(self, x):
        """
        利用牛顿法进行x0的更新，比直接从1开始遍历所作的循环要少
        :type x: int
        :rtype: int
        """
        x0 = 1
        while True:
            x1 = x0 - (x0 ** 2 - x)/(2*x0)
            if int(x1) == int(x0):
                break
            else:
                x0 = x1
        return int(x0)
