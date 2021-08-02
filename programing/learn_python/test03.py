# Find all permutations of a string
def permute_string(str):
    if len(str) == 0:
        return ['']
    prev_list = permute_string(str[1:len(str)])
    next_list = []
    for i in range(0,len(prev_list)):
        for j in range(0,len(str)):
            new_str = prev_list[i][0:j]+str[0]+prev_list[i][j:len(str)-1]
            if new_str not in next_list:
                next_list.append(new_str)
    return next_list

def permutations(string):
    """Create all permutations of a string with non-repeating characters
    """
    permutation_list = []
    if len(string) == 1:
        return [string]
    else:
        for char in string:
            [permutation_list.append(char + a) for a in permutations(string.replace(char, ""))]
    return permutation_list

def get_permutations(word):
    if len(word) == 1:
        yield word

    for i, letter in enumerate(word):
        for perm in get_permutations(word[:i] + word[i+1:]):
            yield letter + perm

print(permute_string('ABCD'));
print(permutations('ABCD'))
print([l for l in get_permutations('ABCD')])
