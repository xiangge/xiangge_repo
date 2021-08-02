#Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.
#For example, given n = 3, a solution set is:
#[
#  "((()))",
#  "(()())",
#  "(())()",
#  "()(())",
#  "()()()"
#]


l = []
n = 3
def get_heses(s):
    if len(s) == n*2:
        if s.count(")") == n:
            l.append(s)
        return
                
    for sub_s in '()':
        if sub_s == ')' and s=="":
            continue
        if s.count("(") >= s.count(")"):
            s = s+sub_s
            get_heses(s)
            s = s[:-1]
# get_heses("")
# print l 


# Insert a value into a sorted list
def insert_value(sl, value):
    l_e = [value]
    l_s = []
    for v in sl:
        if v <= value:
            l_e.append(v)
        else:
            l_s.append(v)
    return l_s + l_e

# print insert_value([9, 8, 7, 5], 6)
# print insert_value([9, 8, 7, 5], 4)

def sort_value(d):
    l = d.keys
    for i in range(len(l)):
        for j in range(i, len(l)):
            if l[i] <= l[j]:
                l[i], l[j] = l[j], l[i]
    return l

def inset_sorts(sorts, sort_keys, d):
    for s in sort_keys:
        if sorts[s]:
            sorts
    

def get_top_fifteen(ll):
    sorts = {}
    for l in ll:
        d = {}
        for i in range(len(l)):
            d[i] = l[i]
        sort_keys = sort_value(d)[:15]
        inset_sorts(sorts, sort_keys, d)

    return sorts


#quick sort
def quickSort(array):
    if len(array) == 1:  # 基线条件（停止递归的条件）
        return array
    else:  # 递归条件
        baseValue = array[0]  # 选择基准值
        # 由所有小于基准值的元素组成的子数组
        less = [m for m in array[1:] if m < baseValue]
        # 包括基准在内的同时和基准相等的元素，在上一个版本的百科当中，并没有考虑相等元素
        equal = [w for w in array if w == baseValue]
        # 由所有大于基准值的元素组成的子数组
        greater = [n for n in array[1:] if n > baseValue]
    return quickSort(less) + equal + quickSort(greater)
# 示例：
array = [2,3,5,7,1,4,6,15,5,2,7,9,10,15,9,17,12]
print(quickSort(array))
# 输出为[1, 2, 2, 3, 4, 5, 5, 6, 7, 7, 9, 9, 10, 12, 15, 15, 17]
