# [1,2,3] backtrack

# nums is the [1,2,3], should be 3
# temp_list is the tree's dfs sub result
import copy
def recursive_func(final_list, temp_list, nums):
    if len(temp_list) == len(nums):
        final_list.append(copy.deepcopy(temp_list))
    else:
        for i in nums:
            if i in temp_list:
                continue
            temp_list.append(i)
            print "before execute recuirsive"
            print temp_list
            recursive_func(final_list, temp_list, nums)
            print "finish previous"
            print temp_list
            temp_list.pop()
            print "pop"
            print temp_list
            print "finish pop"

final_list = []
recursive_func(final_list, [], [1,2,3])
print final_list
