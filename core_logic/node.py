from core_logic.various_errors import IncorrectTreeError


class Node:
    """
    Class for recursive creation, traversing and altering of a tree (assumed: dependency tree)
    """

    def __str__(self):
        new_string = "Node: {node} - Label: {lbl}".format(node=str(self.node), lbl=str(self.label))
        return new_string

    def __init__(self, node, label):
        """
        :param node: used as (unique) key identifying this specific node in the tree
        :type node: Integer
        :param label: string with non unique label of this specific node
        :type label: String
        """
        self.node = node
        self.label = label
        self.children = list()

    def get_children(self):
        """
        :return: copy of the list() of objects of type Node given by self.children
        """
        new_children = self.children.copy()
        return new_children

    def get_label(self):
        """
        :return: string that is label for this node (i.e. label of edge ending in this node or root)
        """
        return self.label

    def get_node(self):
        """
        :return: integer that is word_id of this node
        """
        return self.node

    def set_label(self, new_label):
        """
        :raises IncorrectTreeError if no string is entered
        :param new_label:
        :type new_label: string
        :return: no return value
        """
        if new_label.__class__() != '':
            raise IncorrectTreeError(101)
        else:
            self.label = new_label

    def set_new_single_child(self, new_child):
        """
        expects single object as input
        :param new_child: object of class Node
        :type new_child: Node
        :return: sets self.children to a list containing only new_child
        """
        self.children = [new_child]

    def set_new_children_list(self, children_list):
        """
        uses append_children_by_list to set all children in children_list as the only children in self.children
        :param children_list: new children
        :type children_list: List
        :return: none, alters self.children
        """
        self.children = list()
        self.append_children_by_list(children_list)

    def append_children_by_list(self, children_list):
        """
        :param children_list: a list() of objects of class Node
        :type children_list: List
        :return: none, alters self.children
        """
        self.children.extend(children_list)
        self.sort_children()

    def sort_children(self):
        """
        sort self.children by values of "node"
        :return: None, alters self.children
        """
        if len(self.children) > 1:
            self.children.sort(key=lambda x: x.get_node())

    def delete_all_children(self):
        """
        :return: none, sets empty list as self.children
        """
        self.set_new_children_list(list())

    def delete_child_from_children(self, given_child):
        """
        requires exact object of class Node in self.children
        :param given_child: object of class Node
        :return: none, alters self.children by deleting given_child
        """
        for child in self.children:
            if child is given_child:
                self.children.remove(child)

    def delete_child_from_children_by_value(self, child_value):
        """
        :param child_value: identifies node to be deleted
        :type child_value: Integer
        :return: none, alters self.children by deleting node with child_value as node
        """
        for child in self.children:
            if child.get_node() == child_value:
                self.children.remove(child)

    def cut_tree(self):
        """
        alters self.children to empty list()
        :return: deep copy (i.e. new object of class Node) of self including deep copy of all children and children of
        children
        """
        new_root = Node(self.get_node(), self.get_label())
        old_children = self.get_children()
        new_children = list()
        for child in old_children:
            new_child = Node.recursive_deep_copy_tree(child)
            new_children.append(new_child)
        new_root.set_new_children_list(new_children)
        self.children = list()
        return new_root

    def recursive_child_look_up_by_label(self, labels):
        """
        searches children and all children of children via recursion until first occurrence of label given by labels
        :param labels: a list() of strings
        :type labels: List
        :return: complete list of all children (and children of children) that have a label given by labels
        """
        children_with_label = list()
        children_without_label = list()
        for child in self.children:
            if child.get_label() in labels:
                children_with_label.append(child)
            else:
                children_without_label.append(child)
        for child in children_without_label:
            new_children = child.recursive_child_look_up_by_label(labels)
            if len(new_children) > 0:
                children_with_label.extend(new_children)
        return children_with_label

    @staticmethod
    def recursive_deep_copy_tree(given_node):
        """
        creates new object of class Node with new objects of class Node for all its children via recursion
        :param given_node: a tree to copy
        :type given_node: Node
        :return: a new object of class Node
        """
        new_node = Node(given_node.get_node(), given_node.get_label())
        old_children = given_node.get_children()
        if len(old_children) == 0:
            return new_node
        else:
            new_children = list()
            for old_child in old_children:
                new_child = Node.recursive_deep_copy_tree(old_child)
                new_children.append(new_child)
            new_node.append_children_by_list(new_children)
            return new_node

    @staticmethod
    def recursive_search_and_cut(given_node, labels):
        """
        searches tree via recursion for all first occurrences of any label given by labels, cuts of all found nodes and
        returns list of all of their children, intended for cutting a tree into sub sentences given by labels like
        "rel", "neb", ...,
        possibly alters given_node and children of given_node
        :param given_node: node functioning as root of a tree which is to be analyzed
        :type given_node: Node
        :param labels: labels to cut at
        :type labels: List
        :return: list(), of deep copied objects of class Node with all their children or empty list() if no cuts were
        made
        """
        children_to_cut = given_node.recursive_child_look_up_by_label(labels)
        new_children = list()
        for child in children_to_cut:
            new_child = child.cut_tree()
            new_children.append(new_child)
        return new_children

    @staticmethod
    def recursive_tree_look_up_by_node_value(given_node, node_value):
        """
        :param given_node: object of class Node (including root of a tree) whose children are to be searched for a node
               with given value
        :type given_node: Node
        :param node_value: a value to be searched for
        :type node_value: Integer expected
        :return: the first object of class Node whose object.value equals the given node_value, searched via depth first
        search
        """
        if given_node.get_node() == node_value:
            return given_node
        if len(given_node.get_children()) == 0:
            return None
        else:
            for child in given_node.get_children():
                recursive_look_up_result = Node.recursive_tree_look_up_by_node_value(child, node_value)
                if recursive_look_up_result is not None:
                    return recursive_look_up_result
            return None

    @staticmethod
    def recursive_tree_to_list_conversion(given_node):
        """
        searches given_node via recursion
        :param given_node: object of class Node
        :type given_node: Node
        :return: list() of objects of class Node with given_node and all its children (and children of children)
        """
        list_addition = list()
        list_addition.append(given_node)
        if len(given_node.get_children()) == 0:
            return list_addition
        else:
            for child in given_node.get_children():
                list_addition.extend(Node.recursive_tree_to_list_conversion(child))
            return list_addition


class WorkingTreeRootNode(Node):
    """
    Used by SentenceAnalysisConnector during analysis of dependency tree
    """

    def __str__(self):
        return super().__str__() + " original label: {lbl}".format(lbl=self.get_original_label())

    def __init__(self, node, label):
        """
        used for evaluation of original label of tree root of a working_tree that was cut off at an earlier point,
        original label of tree root of complete dependency tree is 'root', each other label is label from within the
        dependency tree (usually "kon", "cj", "rel", "neb", ...)
        :param node:
        :type node: Integer
        :param label:
        :type label String
        """
        super().__init__(node, label)
        self.original_label = self.get_label()
        self.set_label('root')
        self.sub_tree_roots = list()

    def get_original_label(self):
        """
        :return: string that was original label of this node in dependency tree (before this node became root of a
        dependency sub tree)
        """
        return self.original_label

