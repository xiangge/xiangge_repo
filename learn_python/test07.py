class Solution(object):
    def permuteUnique(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """
        f_list = []
        def add_column(temp_list, nums):
            if len(temp_list) == len(nums):
                f_list.append(temp_list[:])
            for i in nums:
                temp_i = 0
                temp_j = 0
                for n in nums:
                    if n == i:
                        temp_i += 1
                for m in temp_list:
                    if m ==i:
                        temp_j += 1
                if temp_i != temp_j:
                    temp_list.append(i)
                    add_column(temp_list, nums)
                    temp_list.pop()
        add_column([], nums)
        new_list = []
        for l in f_list:
            if l not in new_list:
                new_list.append(l)
        return new_list

class Solution(object):
    def permuteUnique(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """
        f_list = []
        temp_dic = {}
        for i in nums:
            if i in temp_dic.keys():
                temp_dic[i] = temp_dic[i]+1
            else:
                temp_dic[i] = 1
        def add_column(temp_list, nums):
            if len(temp_list) == len(nums):
                if temp_list not in f_list:
                    f_list.append(temp_list[:])
            for i in nums:
                temp_j = 0
                for m in temp_list:
                    if m ==i:
                        temp_j += 1
                if temp_dic[i] != temp_j:
                    temp_list.append(i)
                    add_column(temp_list, nums)
                    temp_list.pop()

        add_column([], nums)
        return f_list

s = Solution1()
#print s.permuteUnique([-1,2,-1,2,1,-1,2,1])
print s.permuteUnique([1,2,3])
