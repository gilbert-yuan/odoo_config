# -*- coding:utf-8 -*-
class Node:
    def __init__(self, item):
        self.item = item
        self.childOne = None
        self.childTwo = None

class Tree:
    def __init__(self):
        self.root = None
    
    def add(self, item):
        node = Node(item)
        if self.root is None:
            self.root = node
        else:
            q = [self.root]
            while True: 
                pop_node = q.pop(0)
                if pop_node.childOne is None:
                    pop_node.childOne = node
                    break 
                elif pop_node.childTwo is None:
                    pop_node.childTwo = node
                    break
                else:
                    q.append(pop_node.childOne)
                    q.append(pop_node.childTwo)
        return 


    def traverse(self):
        if self.root is None:
            return None
        q = [self.root]
        res = [self.root.item]
        while q != [] :
            pop_node = q.pop(0) 
            if pop_node.childOne is not None:
                q.append(pop_node.childOne)
                res.append(pop_node.childOne.item)
            if pop_node.childTwo is not None:
                q.append(pop_node.childTwo)
                res.append(pop_node.childTwo.item)
        return res

    def preorder(self,root):  # 先序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.preorder(root.childOne)
        right_item = self.preorder(root.childTwo)
        return result + left_item + right_item

    def inorder(self,root):  # 中序序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.inorder(root.childOne)
        right_item = self.inorder(root.childTwo)
        return left_item + result + right_item

    def postorder(self,root):  # 后序遍历
        if root is None:
            return []
        result = [root.item]
        left_item = self.postorder(root.childOne)
        right_item = self.postorder(root.childTwo)
        return left_item + right_item + result

t = Tree()
for i in range(10):
    t.add(i)
#print('层序遍历:',t.traverse())
print('先序遍历:',t.preorder(t.root))
print('中序遍历:',t.inorder(t.root))
print('后序遍历:',t.postorder(t.root))

