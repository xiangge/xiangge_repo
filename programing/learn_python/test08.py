#Combinations:Given two integers n and k,return all possible combinations of k numbers
#out of 1...n.For example, If n = 4 and k =2, a solution is:
#[
#[2,4],
#[3,4],
#[2,3],
#[1,2],
#[1,3],
#[1,4],
#]
f_l = []
def track_sub_list(k, n, start, l=[]):
    if len(l) == k:
    	f_l.append(l[:])
    if len(l) < k:
    	for i in range(start, n+1):
    		l.append(i)
    		track_sub_list(k, n, i+1, l)
    		del l[-1]

# track_sub_list(2, 4, 1, [])
# print f_l


#Input: candidates = [2,3,6,7], target = 7,
#A solution set is:
#[
#  [7],
#  [2,2,3]
#]
#Input: candidates = [2,3,5], target = 8,
#A solution set is:
#[
#  [2,2,2,2],
#  [2,3,3],
#  [3,5]
#]

f_l_sum = []
def track_sum_list(k, n, start, l=[]):
    if sum(l) == k:
    	f_l_sum.append(l[:])
    if sum(l) < k:
    	for i in range(start, len(n)):
    		l.append(n[i])
    		print l
    		track_sum_list(k, n, i, l)
    		del l[-1]

"""
The function is ran as:
[2]
[2, 2]
[2, 2, 2]
[2, 2, 2, 2]
[2, 2, 2, 3]
[2, 2, 2, 5]
[2, 2, 3]
[2, 2, 3, 3]
[2, 2, 3, 5]
[2, 2, 5]
[2, 3]
[2, 3, 3]
[2, 3, 5]
[2, 5]
[2, 5, 5]
[3]
[3, 3]
[3, 3, 3]
[3, 3, 5]
[3, 5]
[5]
[5, 5]
"""
track_sum_list(8, [2, 3, 5], 0, [])
print f_l_sum



parentheses_l = []
def ge_parentheses(p_l, ,l):






