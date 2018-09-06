import clang.cindex, sys
from BitmapProcessing import *

def trimClangNodeName(nodeName):
    ret = str(nodeName)
    ret = ret.split(".")[1]
    return ret


def locateASTNode(BMPArray, node, depth, length):
    BMPArray[depth-1][length][0] = True
    BMPArray[depth-1][length][1] = (trimClangNodeName(node.kind))
    BMPArray[depth-1][length][3] = (trimClangNodeName(node.type.kind))
    BMPArray[depth-1][length][5] = node.displayname

def traverseAST(BMPArray, node, depth):

    def traverse(BMPArray, node, depth):
        if node is not None:
            depth = depth + 1
            if (prevDepth[0] >= depth) and (depth != 1):
                length[0] +=1
            #print('previous depth  ', prevDepth[0])
            #print('current depth ', depth)
            #print('current length ', length[0])
            prevDepth[0] = depth
            locateASTNode(BMPArray, node, depth, length[0])
            # Recurse for children of this node
            for childNode in node.get_children():
                traverse(BMPArray, childNode, depth)
            depth = depth - 1

    #Define 'global' variables
    prevDepth = [0]
    prevDepth[0] = 1
    length = [0]
    length[0] = 0
    traverse(BMPArray, node, depth)

#Initial setup
def setupParser(astfile):
    index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(False, True))
    tu = index.read(astfile)
    assert tu is not None
    return tu






#for token in tu.get_tokens(extent=tu.cursor.extent):
#    print('token = %s (%s)' % (token.spelling or token.displayname, token.kind))

#print(asciitree.draw_tree(tu.cursor,
 #                         tu.cursor.get_children()))

""" #*PARSING C FILES*
def traverse(node):
    for c in node.get_children():
        print('Cursor %s of kind %s at location %s' % (tu.cursor, tu.cursor.kind, tu.cursor.location))

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1], args=['-std=c11'], options=0)
print('Translation unit: ', tu.spelling)
#traverse(tu.cursor)
for t in tu.get_tokens(extent=tu.cursor.extent):
    if (t.kind != 'TokenKind.PUNCTUATION'):
        print("token = %s,  kind = %s" % (t.spelling, t.kind))
"""





