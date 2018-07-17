# phone dict to words, recursive
phone_dict={'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs',
            '8':'tuv','9':'wxyz'}

def get_list(one_str):
    res_list=[]
    def deep(one_str, tmp_str):
        if not one_str:
            res_list.append(tmp_str)
            return
        for c in phone_dict[one_str[0]]:
            deep(one_str[1:], tmp_str + c)
    deep(one_str, "")
    return res_list
 
if __name__ == '__main__':
    print get_list("23")
