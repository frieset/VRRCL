from core_logic.various_errors import IncorrectTreeError
from core_logic.various_errors import ConnectorError
from core_logic.dependency_tree import DependencyTree as DepTr
from core_logic.dependency_analysis import DependencyAnalysis as DepAn
from core_logic.dependency_analysis import DependencyAnalysisSubTypeI as DasSubOne
from core_logic.dependency_analysis import DependencyAnalysisSubTypeII as DasSbTwo

import logging

logger = logging.getLogger('ValancyRelationshipRecognizer')


class SentenceAnalysisConnector:
    """
    For more straight forward access to object of class DependencyAnalysis (which has sub analyses that were created
    recursively due to sentence structure), also called on by class SentenceObject for basic access to dependency
    analysis
    """
    def __init__(self, words, raw_dep_tree):
        """
        tries to created dependency tree, if tree could not be created (due to IncorrectTreeError), dependency analysis
        is None
        :param words: words (as strings) for given sentence
        :type words: List
        :param raw_dep_tree: edges for dependency tree
        :type raw_dep_tree: List
        """
        try:
            self.complete_dependency_tree = DepTr.initialize_dependency_tree(words, raw_dep_tree)
        except IncorrectTreeError as ite:
            logger.debug("Fehler bei der Baumerstellung: {error}".format(error=ite))
            self.complete_dependency_tree = None
            self.valid_analysis = False
            self.dependency_analysis = None
        else:
            self.dependency_analysis = None
            self.valid_analysis = True

    def __str__(self):
        string = ""
        new_string = ""
        if self.valid_analysis:
            complete_analysis_list = self.get_full_analysis_list()
            main_analysis = complete_analysis_list[0]
            for complement in main_analysis.get_complements():
                string += str(complement)
            new_string = "Hauptsatzanalyse\nValenzträger: {vh} - lemma: {lm}\n{cmpl}\n".\
                format(vh=main_analysis.get_valence_holder(), lm=main_analysis.get_valence_holder_lemma(), cmpl=string)
            for analysis in complete_analysis_list[1:]:
                string = ""
                for complement in analysis.get_complements():
                    string += str(complement)
                new_string += "analysis type: {analysetype}\nValenzträger: {vh} - lemma: {lm}\n{cmpl}\n".\
                    format(analysetype=str(analysis.__class__), vh=analysis.get_valence_holder(),
                           lm=analysis.get_valence_holder_lemma(), cmpl=string)
        if len(new_string) > 0:
            return new_string
        else:
            return "Keine gültige Analyse"

    def is_valid_analysis(self):
        """
        :return: True if dependency analysis could be created correctly, False otherwise
        """
        return self.valid_analysis

    def get_complete_dependency_tree(self):
        """
        :raises IncorrectTreeError if tree could not be created correctly
        :return: object of class DependencyTree or exception
        """
        if self.complete_dependency_tree is not None:
            return self.complete_dependency_tree
        else:
            raise IncorrectTreeError(1)

    def get_main_dependency_analysis(self):
        """
        :raises ConnectorError if dependency analysis is not valid (i.e. dependency tree could not created correctly)
        :return: object of class DependencyAnalysis, the analysis of the main sentence
        """
        if self.valid_analysis:
            return self.dependency_analysis
        else:
            raise ConnectorError(2)

    def get_primary_analysis_list(self):
        """
        :raises ConnectorError if dependency analysis is not valid (i.e. dependency tree could not created correctly)
        :return: list of objects of type DependencyAnalysis (or subclass) that are primary analyses (i.e. analyses of the verb that
        was used for the lookup in the database)
        """
        if self.valid_analysis:
            full_analysis_list = self.get_full_analysis_list()
            primary_analysis_list = list()
            for analysis in full_analysis_list:
                if analysis.is_primary_analysis():
                    primary_analysis_list.append(analysis)
            return primary_analysis_list
        else:
            raise ConnectorError(2)

    def get_analysis_by_connecting_node(self, given_node):
        """
        searches all analyses of self for first analysis with given_node as value of the root of the subtree for this
        analysis
        :raises ConnectorError if dependency analysis is not valid (i.e. dependency tree could not created correctly)
        :param given_node: indicating object of class Node in complete dependency tree that is used as a connecting
        node for any analysis
        :type given_node: Integer
        :return: the analysis (object of class DependencyAnalysisSubTypeI or DependencyAnalysisSubTypeII) that has the
        given node as connecting node
        """
        if self.valid_analysis:
            analysis_list = self.get_full_analysis_list()
            if len(analysis_list) > 1:
                analysis_list = analysis_list[1:]
                for analysis in analysis_list:
                    if analysis.get_connecting_node_value() == given_node:
                        return analysis
        else:
            raise ConnectorError(2)

    def get_full_analysis_list(self):
        """
        :raises ConnectorError if dependency analysis is not valid (i.e. dependency tree could not created correctly)
        :return: list of objects() of class DependencyAnalysis containing all analyses of this sentence (including all
        sub sentence analyses)
        """
        if self.valid_analysis:
            analysis_list = list()
            analysis_list.insert(0, self.dependency_analysis)
            queue = self.dependency_analysis.get_class_one_sub_analysis()
            queue.extend(self.dependency_analysis.get_class_two_sub_analysis())
            for analysis in queue:
                analysis_list.append(analysis)
                new_queue = analysis.get_class_one_sub_analysis()
                new_queue.extend(analysis.get_class_two_sub_analysis())
                queue.pop(0)
                queue = new_queue + queue
            return analysis_list
        else:
            raise ConnectorError(2)

    def initial_dependency_analysis(self):
        """
        used to create object of class DependencyAnalysis out of an object of class DependencyTree via recursion
        (therefore also creating DependencyAnalysisSupTypeI and DependencyAnalysisSupTypeII), if not
        successful sets self.valid_analysis to False
        :return: None, upon completion sets self.dependency_analysis to object of class DependencyAnalysis for main
        sentence given by dependency tree
        """
        if self.valid_analysis:
            raw_working_tree = DepTr(DepTr.deep_copy_complete_tree(self.complete_dependency_tree.get_tree_root()))
            self.dependency_analysis = SentenceAnalysisConnector.recursive_dependency_analysis(raw_working_tree, 0)
            if self.dependency_analysis is None:
                self.valid_analysis = False

    @staticmethod
    def recursive_dependency_analysis(current_working_tree, analysis_type):
        """
        main method to analyze a dependency tree via recursion, creates object of class DependencyAnalysis (or subclass)
        and appends list of sub analyses of this new analysis with recursively created dependency analyses for these
        sub sentences,
        checks for nodes labeled with "aux" and "avz" before using subroutines for creation of analysis of sub sentence,
        nodes with labels "aux" and "avz" are saved separately und used for analysis creation, working tree is cut and
        mended when sliced for labels "aux" and "avz"
        :param current_working_tree: tree that is currently cut/altered/analyzed
        :type current_working_tree: DependencyTree
        :param analysis_type: used to distinguish between main sentence DependencyAnalysis (type 0),
        DependencyAnalysisSubTypeI (type 1) and DependencyAnalysisSubTypeII (type 2), type 0 is only used in
        function "initial_dependency_analysis"
        :type analysis_type: Integer
        :return: newly created dependency analysis with all analyses of subtrees emanating from root of current working
        tree created recursively
        """
        current_working_tree.change_root_class_to_workingtreerootnode()
        labels = ['aux']
        aux_nodes = SentenceAnalysisConnector.cut_and_mend_tree_on_root_lvl(current_working_tree, labels)
        if len(aux_nodes) > 0:
            verb = aux_nodes[-1]
            aux_nodes.pop(-1)
            aux_nodes.insert(0, current_working_tree.get_tree_root())
        else:
            verb = current_working_tree.get_tree_root()
        labels = ['avz']
        avz_nodes = SentenceAnalysisConnector.cut_and_mend_tree_on_root_lvl(current_working_tree, labels)
        labels = ['kon']
        class_i_analysis = SentenceAnalysisConnector.recursive_sub_sentence_type_i_analysis(current_working_tree, labels)
        labels = ['konj', 'neb', 'objc', 'rel', 's', 'subjc']
        class_ii_analysis = SentenceAnalysisConnector.recursive_sub_sentence_type_ii_analysis(current_working_tree, labels)
        new_dependency_analysis = None
        if analysis_type == 0:
            new_dependency_analysis = DepAn(current_working_tree.get_tree_root(), verb, avz_nodes, aux_nodes,
                                            class_i_analysis, class_ii_analysis)
        elif analysis_type == 1:
            new_dependency_analysis = DasSubOne(current_working_tree.get_tree_root(), verb, avz_nodes, aux_nodes,
                                                class_i_analysis, class_ii_analysis)
        elif analysis_type == 2:
            new_dependency_analysis = DasSbTwo(current_working_tree.get_tree_root(), verb, avz_nodes, aux_nodes,
                                               class_i_analysis, class_ii_analysis)
        return new_dependency_analysis

    @staticmethod
    def recursive_sub_sentence_type_i_analysis(current_working_tree, labels):
        """
        subroutine, used during recursive analysis of dependency tree in order to create object of class
        DependencyAnalysisSubTypeI and append this analysis with all analyses further down the dependency tree, checks
        if root of current_working_tree is node with label "kon" and has only one child with label "cj", if so, alters
        current working tree to new tree with root at node with label "cj", sets connecting nodes in
        DependencyAnalysisSubTypeI accordingly,
        alters working_tree by cutting without doing any mending
        :param current_working_tree: tree that is currently cut/altered/analyzed
        :type current_working_tree: DependencyTree
        :param labels: strings, intended for use with any string from [kon]
        :type labels: List
        :return: list() of objects of class DependencyAnalysisSubTypeI
        """
        new_kon_trees = SentenceAnalysisConnector.cut_tree_on_root_lvl(current_working_tree, labels)
        new_class_i_sub_trees = list()
        connecting_kon_nodes = list()
        for tree in new_kon_trees:
            new_dependency_tree = DepTr(tree)
            connecting_kon_nodes.append(new_dependency_tree.get_tree_root().get_node())
            labels = ['cj']
            if len(new_dependency_tree.get_tree_root().get_children()) == 1:
                if new_dependency_tree.get_tree_root().get_children()[0].get_label() in labels:
                    new_root = SentenceAnalysisConnector.cut_tree_on_root_lvl(new_dependency_tree, labels)
                    new_dependency_tree = DepTr(new_root[0])
            new_class_i_sub_trees.append(new_dependency_tree)
        class_i_analysis_list = list()
        for class_i_sub_tree, connecting_kon_node in zip(new_class_i_sub_trees, connecting_kon_nodes):
            new_analysis = SentenceAnalysisConnector.recursive_dependency_analysis(class_i_sub_tree, 1)
            new_analysis.set_connecting_node(connecting_kon_node)
            class_i_analysis_list.append(new_analysis)
        return class_i_analysis_list

    @staticmethod
    def recursive_sub_sentence_type_ii_analysis(current_working_tree, labels):
        """
        subroutine, used during recursive analysis of dependency tree in order to create object of class
        DependencyAnalysisSubTypeII and append this analysis with all analyses further down the dependency tree
        alters working_tree by cutting without doing any mending
        :param current_working_tree: tree that is currently cut/altered/analyzed
        :type current_working_tree: DependencyTree
        :param labels: strings, intended for use with any string from ['konj', 'neb', 'objc', 'rel', 's', 'subjc']
        :type labels: List
        :return: list() of objects of class DependencyAnalysisSubTypeII
        """
        new_class_ii_sub_trees = list()
        new_sub_sentence_trees = SentenceAnalysisConnector.cut_tree_by_labels(current_working_tree, labels)
        for tree in new_sub_sentence_trees:
            new_dependency_tree = DepTr(tree)
            new_class_ii_sub_trees.append(new_dependency_tree)
        class_ii_analysis = list()
        for class_ii_sub_tree in new_class_ii_sub_trees:
            new_analysis = SentenceAnalysisConnector.recursive_dependency_analysis(class_ii_sub_tree, 2)
            class_ii_analysis.append(new_analysis)
        return class_ii_analysis

    @staticmethod
    def cut_tree_by_labels(working_tree, labels):
        """
        makes cuts (at first occurrence of any label given by labels) in the complete tree, intended use: with labels
        "neb", "rel", ... (possibly simultaneously) as these are indicators of certain kinds of sub sentences,
        used to access object of class DependencyTree,
        alters working tree
        :param working_tree: tree that is currently cut/altered/analyzed
        :type working_tree: DependencyTree
        :param labels: strings to search for
        :type labels: List
        :return: list of objects of class Node cut out of the tree (with all their children attached)
        """
        sub_trees = working_tree.slice_tree_by_label(labels)
        return sub_trees

    @staticmethod
    def cut_tree_on_root_lvl(working_tree, labels):
        """
        make cut (with no mending or further altering of initial working tee) at any children of root of
        tree with label given by labels, intended use: with labels "kon" and "cj" (not simultaneously) as these are
        indicators of certain kinds of sub sentences,
        used to access object of class DependencyTree,
        alters working tree
        :param working_tree: tree that is currently cut/altered/analyzed
        :type working_tree: DependencyTree
        :param labels: strings to search for
        :type labels: List
        :return: list() of objects of class Node cut out of the tree (with all their children attached)
        """
        sub_trees = working_tree.slice_tree_on_first_lvl(labels)
        return sub_trees

    @staticmethod
    def cut_and_mend_tree_on_root_lvl(working_tree, labels):
        """
        intended use: recursively slice tree on first lvl at 'avz' and 'aux' nodes, delete node with given label from
        working tree and add all its children to root of working tree, continue until no 'avz' and 'aux' nodes found on
        first lvl and return all nodes that were cut off this way as list() of objects of class nodes, each with no
        children;
        used to access object of class DependencyTree;
        alters working_tree
        :param working_tree: tree that is currently cut/altered/analyzed
        :type working_tree: DependencyTree
        :param labels: strings to search for
        :type labels: List
        :return: list() of nodes cut out of the tree by given labels, each node has no children
        """
        sub_trees_with_label = working_tree.slice_tree_on_first_lvl(labels)
        nodes_with_label = list()
        while len(sub_trees_with_label) > 0:
            for sub_tree_root in sub_trees_with_label:
                working_tree.delete_node_from_root_by_value(sub_tree_root.get_node())
                new_children = list()
                for child in sub_tree_root.get_children():
                    new_children.append(child)
                working_tree.append_tree_root_by_children_list(new_children)
                sub_tree_root.delete_all_children()
            new_nodes_with_label = sub_trees_with_label.copy()
            nodes_with_label.extend(new_nodes_with_label)
            sub_trees_with_label = working_tree.slice_tree_on_first_lvl(labels)
        return nodes_with_label

