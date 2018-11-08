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
get_heses("")
print l 
