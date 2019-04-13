#QuickSort by Alvin

def QuickSort(myList,start,end):
    if start < end:
        i,j = start,end
        base = myList[i]

        while i < j:
            while (i < j) and (myList[j] >= base):
                j = j - 1

            myList[i] = myList[j]
            print(myList)

            while (i < j) and (myList[i] <= base):
                i = i + 1
            myList[j] = myList[i]
            print(myList)

        myList[i] = base
        # return
        # Here i is same with j
        QuickSort(myList, start, i - 1)
        QuickSort(myList, j + 1, end)
    return myList

def quickSort(array):
    if len(array) < 2:
        return array
    else:
        baseValue = array[0]
        less = [m for m in array[1:] if m < baseValue]
        equal = [w for w in array if w == baseValue]
        greater = [n for n in array[1:] if n > baseValue]
    return quickSort(less) + equal + quickSort(greater)

def quickSort(l, s, e):
    if s < e:
        i, j = s, e
        base = l[s]
        while 

    quickSort(l[], s, i-1)
    quickSort(l[], i+1, e)

myList = [3, 2, 1, 5, 2, 4, 7]
print("Quick Sort: " + str(myList))
# QuickSort(myList,0,len(myList)-1)
print quickSort(myList)

