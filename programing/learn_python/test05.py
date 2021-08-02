#encoding:UTF-8
# https://leetcode.com/problems/next-permutation/description/

def nextPermutation(nums):
    """
    :type nums: List[int]
    :rtype: void Do not return anything, modify nums in-place instead.
    1,2,3 → 1,3,2
    3,2,1 → 1,2,3
    1,1,5 → 1,5,1
    """
    if len(nums) >1:
        # get start place
        temp = len(nums)-1
        for i in range(len(nums)-1, -1, -1):
            if i == 0:
                for m in range(0, len(nums)-1):
                    for n in range(m+1 ,len(nums)):
                        if nums[m] > nums[n]:
                            nums[m], nums[n] = nums[n], nums[m]
                return
            if i != 0 and nums[i] > nums[i-1]:
                temp = i
                break
        print temp
        for i in range(len(nums)-1, temp-1, -1):
            if nums[i] > nums[temp-1]:
                nums[i], nums[temp-1] = nums[temp-1],  nums[i]
                print "-----"
                break
        print temp
        for m in range(temp, len(nums)):
            for n in range(m+1 ,len(nums)):
                if nums[m] > nums[n]:
                    nums[m], nums[n] = nums[n], nums[m]
        print nums

#nextPermutation([4,2,0,2,3,2,0])
nextPermutation([2,3,0,2,4,1])
#nextPermutation([3,2,1])
# nextPermutation([1,2,3])
nextPermutation([1,3,2])
