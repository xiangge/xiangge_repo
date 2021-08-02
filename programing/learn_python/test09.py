#

def quick_sort(myL, left, right):
    if left < right:
        low = left
        high = right
        base = myL[low]
        while left < right:
            while left < right and myL[right] >= base:
                right = right - 1
            myL[left] = myL[right]
            while left < right and myL[left] <= base:
                left = left + 1
            myL[right] = myL[left]
    
        myL[left] = base
        quick_sort(myL, low, left-1)
        quick_sort(myL, left+1, high)
    return myL


def quick_sort(array, l, r):
    if l < r:
        q = partition(array, l, r)
        quick_sort(array, l, q - 1)
        quick_sort(array, q + 1, r)

def partition(array, l, r):
    x = array[r]
    i = l - 1
    for j in range(l, r):
        if array[j] <= x:
            i += 1
            array[i], array[j] = array[j], array[i]
    array[i + 1], array[r] = array[r], array[i+1]
    return i + 1
import time
def test_time(func):
    def ex_fu(*args, **kws):
        s = time.time()
        func(*args, **kws)
        print time.time() -s
    return ex_fu

@test_time
def q_sort(ml, left, right):
    if left < right:
        origin_left = left
        origin_right = right
        base = ml[left]
        while left < right:
            while left < right and ml[right] >= base:
                right = right-1
            ml[left] = ml[right]
            while left < right and ml[left] <= base:
                left = left + 1
            ml[right] = ml[left]
        ml[left] = base
        q_sort(ml, origin_left, left-1)
        q_sort(ml, left+1, origin_right)
    return ml





print q_sort([3, 5, 4, 7, 6, 9, 8, 1, 2], 0, 9-1)

