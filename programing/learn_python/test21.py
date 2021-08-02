def handler(left, right):
    l_n = r_n = 0
    f = []
    while l_n < len(left) and r_n < len(right):
        if left[l_n] < right[r_n]:
            f.append(left[l_n])
            l_n +=1
        else:
            f.append(right[r_n])
            r_n +=1
    if l_n == len(left):
        for i in right[r_n:]:
            f.append(i)
    else:
        for i in left[l_n:]:
            f.append(i)
    return f

def merge_k(l):
    if len(l)<=1:
        return l
    midd = len(l)/2
    print l[:midd]
    print l[midd:]
    left = merge_k(l[:midd])
    right = merge_k(l[midd:])
    return handler(left, right)

print merge_k([4,3,5,7,6,2,2])
