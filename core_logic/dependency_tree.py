from core_logic.various_errors import IncorrectTreeError
from core_logic.node import Node
from core_logic.node import WorkingTreeRootNode


class DependencyTree:
    """
    Class used for "connection" of Dependecy Tree created via recursion of simple objects of class Node with more
    straight forward classes for sentences and analyses
    """
    def __init__(self, root):
        """
        :param root: an object of class Node or WorkingTreeRootNode
        :type root: Node or WorkingTreeRootNode
        """
        self.tree_root = root

    def __str__(self):
        pass

    def get_tree_root(self):
        """
        :return: object of class Node or WorkingTreeRootNode that is root of this dependency tree
        """
        return self.tree_root

    def delete_node_from_root_by_value(self, value):
        """
        :param value: node value for child to be deleted from list of children of root of tree
        :type value: Integer
        :return: none, if no child of root of tree has node value given by value, nothing happens
        """
        self.tree_root.delete_child_from_children_by_value(value)

    def append_tree_root_by_children_list(self, new_children):
        """
        uses append_any_node_by_children_list on root of tree
        """
        self.append_any_node_by_children_list(new_children, self.tree_root)

    def append_any_node_by_children_list(self, new_children, given_node):
        """
        uses recursive_tree_look_up_by_node_value() to look for value of given node, appends children of this node via
        append_children_by_list()
        :param new_children: list() of objects of class Node used as new children of given_node
        :type new_children: List
        :param given_node: object of class Node to append new_children to, object to append children is searched for
        in own dependency tree, given_node is only checked regarding is node value
        :type given_node: Node
        :return: none, alters children of a node in own dependency tree (indicated by node value)
        """
        node_to_alter = Node.recursive_tree_look_up_by_node_value(self.tree_root, given_node.get_node())
        if node_to_alter is not None:
            node_to_alter.append_children_by_list(new_children)

    def slice_tree_on_first_lvl(self, labels):
        """
        alters self.children, returns list of Nodes that are roots of new subtrees which were cut off,
        intended for use with labels ('aux' and 'avz') or ('kon') and a freshly instantiated (copied) object,
        intended effect is to alter itself to a new tree, some of whose direct children from root (those nodes that have
        a label as given by labels) are "new" children with no children of themselves (therefore cutting the tree at
        these nodes)
        :param labels: labels to cut at
        :type labels: List
        :return: list() of copies of all direct children of node that was cut off, i.e. list() of deep copied objects
        of class Node with all their children
        """
        new_sub_trees = list()
        for child in self.tree_root.get_children():
            if child.get_label() in labels:
                new_child = child.cut_tree()
                new_sub_trees.append(new_child)
        return new_sub_trees

    def slice_tree_by_label(self, labels):
        """
        slice tree (complete tree given by self.tree_root) on all levels at first occurrence of label
        :param labels: list() of labels to slice at
        :type labels: List
        :return: list() of all children of all nodes (with label given by labels) that were cut off
        """
        new_raw_trees_with_label = Node.recursive_search_and_cut(self.tree_root, labels)
        return new_raw_trees_with_label

    def change_root_class_to_workingtreerootnode(self):
        """
        :return: none, changes class of root of tree given by self.tree_root to WorkingTreeRootNode, sets list() of
        old children as new children
        """
        children = list()
        for child in self.tree_root.get_children():
            children.append(child)
        new_tree_root = WorkingTreeRootNode(self.tree_root.get_node(), self.tree_root.get_label())
        new_tree_root.set_new_children_list(children)
        self.tree_root = new_tree_root

    @staticmethod
    def deep_copy_tree(root, children):
        """
        creates new tree with new object of class Node as root of tree and recursive deep copeies of children as new
        children of new root, does absolutely no checks for tree consistency!
        :param root: single object of class Node
        :type root: Node
        :param children: list() of objects of class Node
        :type children: List
        :return: root (as object of class Node) of the new tree
        """
        new_tree_root = WorkingTreeRootNode(0, 'label')
        if root.__class__ == new_tree_root.__class__:
            new_root = WorkingTreeRootNode(root.get_node(), root.get_label())
        else:
            new_root = Node(root.get_node(), root.get_label())
        new_children = list()
        for child in children:
            new_child = Node.recursive_deep_copy_tree(child)
            new_children.append(new_child)
        new_root.set_new_children_list(new_children)
        return new_root

    @staticmethod
    def deep_copy_complete_tree(given_tree_root):
        """
        returns an object of class Node functioning as a copy of the tree (given by the object given_tree_root as root)
        :param given_tree_root: object of class Node
        :type given_tree_root: Node
        :return: new object of class Node with new objects of class Node as children (and children of children)
        """
        new_root = DependencyTree.deep_copy_tree(given_tree_root, given_tree_root.get_children())
        return new_root

    @staticmethod
    def get_complete_subtree_as_list(root):
        """
        :param root: a tree, given by its root
        :type root: Node
        :return: list() of all nodes (as objects of class Node) that are children (or children of children) of node,
                 ordered by depth-first-search
        """
        sub_tree_as_list = Node.recursive_tree_to_list_conversion(root)
        return sub_tree_as_list

    @staticmethod
    def initialize_dependency_tree(words, raw_dep_tree):
        """
        tries to create dependency tree from raw tree data from database
        :raises various IncorrectTreeErrors
        :param words: words (as strings) for given sentence
        :type words: List
        :param raw_dep_tree: edges for dependency tree
        :type raw_dep_tree: List with format [vertex1, vertex2, label], where vertex1 and vertex2 are integers and label
        is string
        :return: new object of class DependencyTree (with Object of class Node set as tree_root) or exception
        """
        try:
            DependencyTree.check_tree_validity(words, raw_dep_tree)
        except IncorrectTreeError as err:
            raise err
        else:
            new_node_value = DependencyTree.determine_root(raw_dep_tree)
            new_node_value = new_node_value[0]
            new_tree_root = Node(new_node_value, 'root')
            queue = list()
            queue += [new_tree_root]
            while len(queue) > 0:
                current_node = queue[0]
                current_node_value = current_node.get_node()
                new_raw_nodes = DependencyTree.get_outbound_edges(raw_dep_tree, current_node_value)
                new_children = list()
                for node in new_raw_nodes:
                    new_children.append(Node(node[1], node[2]))
                current_node.set_new_children_list(new_children)
                new_queue = current_node.get_children()
                queue.pop(0)
                for old_object in queue:
                    new_queue.append(old_object)
                if len(new_queue) > 0:
                    queue = new_queue
            new_dependency_tree = DependencyTree(new_tree_root)
            return new_dependency_tree

# used for tree initilisation:
    @staticmethod
    def check_tree_validity(words, raw_dep_tree):
        """
        all error-checking should be done here before initialisation
        :raises various IncorrectTreeErrors, depending on specific tree
        :param words: list() of tokens (i.e. words and punctuation) in the sentence
        :type words: List
        :param raw_dep_tree: list of edges for dependency tree
        :type raw_dep_tree: List
        :return:
        """
        diff = 1
        for token in words:
            if len(token) == 1:
                if (not token.isupper()) & (not token.islower()) & (not token.isdigit()):
                    diff = diff + 1
        if len(words) - len(raw_dep_tree) != diff:
            raise IncorrectTreeError(1)
        elif len(DependencyTree.determine_root(raw_dep_tree)) != 1:
            raise IncorrectTreeError(2)
        elif not DependencyTree.circle_free(raw_dep_tree):
            raise IncorrectTreeError(3)
        elif not DependencyTree.valid_root(raw_dep_tree, DependencyTree.determine_root(raw_dep_tree)):
            raise IncorrectTreeError(4)

    @staticmethod
    def determine_root(tree):
        """
        determines all roots of a given forest
        :param tree: edges and labels as [[vertex_11, vertex_12, label_1], ..., [vertex_n1, vertex_n2, label_n]]
        :type tree: List
        :return:  a list of vertices that have no incoming edges
        """
        heads = []
        tails = []
        diff = []
        for edge in tree:
            heads.append(edge[0])
            tails.append(edge[1])
        for head in heads:
            if head not in tails:
                if head not in diff:
                    diff.append(head)
        return diff

    @staticmethod
    def valid_root(tree, root):
        """
        :param tree: edges and labels as [[vertex_11, vertex_12, label_1], ..., [vertex_n1, vertex_n2, label_n]]
        :type tree: List
        :param root: root for which to check in tree
        :type root: List
        returns False if no edge from root in tree has label "subj" or "subjc", True otherwise
        """
        valid = False
        for edge in tree:
            if edge[0] == root[0]:
                if (edge[2] == 'subj') | (edge[2] == 'subjc'):
                    valid = True
                    break
        return valid

    @staticmethod
    def get_children_in_raw_tree(tree, vertex):
        """
        :param tree: edges and labels as [[vertex_11, vertex_12, label_1], ..., [vertex_n1, vertex_n2, label_n]]
        :type tree: List
        :param vertex: vertex to be checked for children
        :type vertex: Integer
        :return: a list of all direct child-vertices from given vertex in given tree
        """
        child_vertices = []
        for edge in tree:
                if edge[0] == vertex:
                    child_vertices.append(edge[1])
        return child_vertices

    @staticmethod
    def circle_free(tree):
        """
        :param tree: edges and labels as [[vertex_11, vertex_12, label_1], ..., [vertex_n1, vertex_n2, label_n]]
        :type tree: List
        :return: True, if forest/tree does not contain circles, loops or edges with two parents, False otherwise
        """
        reachable = DependencyTree.determine_root(tree)
        i = 0
        while i < len(reachable):
            new_vertices = DependencyTree.get_children_in_raw_tree(tree, reachable[i])
            for vertex in reachable:
                for new_vertex in new_vertices:
                        if vertex == new_vertex:
                            return False
            reachable = reachable + new_vertices
            i = i + 1
        return True

    @staticmethod
    def get_outbound_edges(tree, vertex):
        """
        :param tree: edges and labels as [[vertex_11, vertex_12, label_1], ..., [vertex_n1, vertex_n2, label_n]]
        :type tree: List
        :param vertex: a vertex (as int) used as head of edges to determine outgoing edges in given tree
        :type vertex: Integer
        :return: list of all edges going out of given vertex in given tree
        """
        outbound_edges = []
        for edge in tree:
            if vertex == edge[0]:
                outbound_edges.append(edge)
        return outbound_edges
