# fei bo na qie
a, b = 1, 1
l = [1,1]
while b < 30:
    temp = b
    b = a+b
    a = temp
    l.append(b)
print l

# 递归方式实现 生成前20项
lis =[]
for i in range(20):
    if i ==0 or i ==1:#第1,2项 都为1
        lis.append(1)
    else:
        lis.append(lis[i-2]+lis[i-1])#从第3项开始每项值为前两项值之和
print(lis)
