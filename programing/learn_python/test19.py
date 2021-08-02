
def mergeSort(alist):
    if len(alist)>1:
        mid=len(alist)//2
        lefthalf=alist[:mid]
        righthalf=alist[mid:]
        mergeSort(lefthalf)
        mergeSort(righthalf)
        i=j=k=0
        while i <len(lefthalf) and j<len(righthalf):
            if lefthalf[i]<righthalf[j]:
                alist[k]=lefthalf[i]
                i+=1
            else:
                alist[k]=righthalf[j]
                j+=1
            k=k+1
        while i<len(lefthalf):
            alist[k]=lefthalf[i]
            i+=1
            k+=1
        while j<len(righthalf):
            alist[k]=righthalf[j]
            j+=1
            k+=1
        
        
alist=[52,312,54,7,3,2,56,34,65,82,91,65]
mergeSort(alist)
print alist

