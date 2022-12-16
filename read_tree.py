"""
ATTENTION!!!
for tree_moreinformation and tree_video I mianly build them in class and function, so for json file, it's just minimal sample information to show the data structure
"""

def loadTree(treefile):
    idc = treefile.readline()
    content = treefile.readline()
    idc = idc.strip()
    content = content.strip()
    if idc == "Internal node":
        node1 = content
        return (node1,loadTree(treefile),loadTree(treefile))
    elif idc == "Leaf":
        return (content,None,None)
def printTree(tree, prefix = '', bend = '', answer = ''):
    text, left, right = tree
    if left is None  and  right is None:
        print(f'{prefix}{bend}{answer}{text}')
    else:
        print(f'{prefix}{bend}{answer}{text}')
        if bend == '+-':
            prefix = prefix + '| '
        elif bend == '`-':
            prefix = prefix + '  '
        printTree(left, prefix, '+-', "Yes: ")
        printTree(right, prefix, '`-', "No:  ")


file_name = "C:/Users/liuxj/Desktop/tree_moreinformation.json"
file_input = open(file_name, 'r')
tree = loadTree(file_input)
file_input.close()
printTree(tree)