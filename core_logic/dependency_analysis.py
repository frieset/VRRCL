from core_logic.complement import Complement as Cmp
from core_logic.node import Node


class DependencyAnalysis:
    """
    Analysis of given sub-tree of a dependency tree, analyzes complements of a valenceholder (verb), due recursive
    nature of dependency tree, analyses are structured recursively as well
    """

    def __init__(self, tree_root, verb, avz_nodes, aux_nodes, class_i_analysis, class_ii_analysis):
        """
        note that only tree_rote is saves as an object of class Node, verb, avz_nodes and aux_nodes are only saves by
        their node_value, thus access to the entire tree is only possible via self.raw_tree
        :param tree_root: object of class Node functioning as root of (altered) subtree (sub sentence) used for
        dependency analysis
        :type tree_root: Node
        :param verb: object of class Node used to determine word id (and label) of valency holder
        :type verb: Node
        :param avz_nodes: list of nodes labeled avz in this subtree (sub sentence), indicating a cut off verb prefix
        :type avz_nodes: List
        :param aux_nodes: list of nodes labeled aux in this subtree (sub sentence), indicating auxiliary verbs
        :type aux_nodes: List
        :param class_i_analysis: list of analyses of sub sentences of this sub sentence (sub tree) initiated with the
        label "kon" (i.e. a sub sentence started with "und" or a simple "," but no "indicating phrase")
        :type class_i_analysis: List
        :param class_ii_analysis: list of analyses of sub sentences of this sub sentence (sub tree) initiated with the
        labels "rel", "s", "neb", "objc", "konj", "subjc" (i.e. a sub sentence starting with an "indicating phrase")
        :type class_ii_analysis: List
        """
        self.valence_holder = verb.get_node()
        self.valence_holder_lemma = ""
        self.avz_words = list()
        for avz_word in avz_nodes:
            self.avz_words.append(avz_word.get_node())
        self.aux_words = list()
        for aux_word in aux_nodes:
            self.aux_words.append(aux_word.get_node())
        self.class_i_sub_analysis = class_i_analysis.copy()
        self.class_ii_sub_analysis = class_ii_analysis.copy()
        self.complements = list()
        for child in tree_root.get_children():
            complement_class = Cmp.specify_initial_complement_classes(child.get_label())
            complement_tree = child.cut_tree()
            new_complement = Cmp(complement_tree, complement_class)
            self.complements.append(new_complement)
        self.complements = Cmp.sort_complement_list(self.complements)
        self.primary_analysis = False
        self.raw_tree = tree_root
        self.raw_verb = verb
        self.raw_avz_nodes = avz_nodes
        self.raw_aux_nodes = aux_nodes

    def __str__(self):
        avz_string = ""
        for word in self.avz_words:
            avz_string += str(word) + " "
        aux_string = ""
        for word in self.aux_words:
            aux_string += str(word) + " "
        string = "Valenzträger: {vh}    avz-Nodes: {avz}    aux-Nodes: {aux}\nKomplemente:\n".\
            format(vh=self.valence_holder, avz=avz_string, aux=aux_string)
        for complement in self.complements:
            string += str(complement)
        if len(self.class_i_sub_analysis) > 0:
            string += "Analysen für Sub-Sentences Typ 1\n"
            for analysis in self.class_i_sub_analysis:
                string += str(analysis)
        if len(self.class_ii_sub_analysis) > 0:
            string += "Analysen für Sub-Sentences Typ 2\n"
            for analysis in self.class_ii_sub_analysis:
                string += str(analysis)
        return string

    def get_class_one_sub_analysis(self):
        """
        :return: copy of the list containing all dependency analysis (sub type I) of sub sentences emanating from self
        """
        return self.class_i_sub_analysis.copy()

    def get_class_two_sub_analysis(self):
        """
        :return: copy of the list containing all dependency analysis (sub type II) of sub sentences emanating from self
        """
        return self.class_ii_sub_analysis.copy()

    def get_valence_holder(self):
        """
        :return: word id of valence holder of this analysis
        """
        return self.valence_holder

    def get_complements(self):
        """
        :return: list of complements of this analysis
        """
        return self.complements

    def get_valence_holder_lemma(self):
        """
        :return: lemma (string) of valence holder of this analysis
        """
        return self.valence_holder_lemma

    def get_avz_words(self):
        """
        :return: list of nodes (as integers) in tree with label avz indicating cut off verb prefixes
        """
        return self.avz_words

    def set_avz_words(self, new_words):
        """
        sets attribute self.avz_words with new_words
        :param new_words: list of word ids (as integers) that are cut off verb prefixes for the verb of this sub
        sentence
        :type new_words list
        """
        self.avz_words = new_words

    def get_complement_by_class(self, cmp_class):
        """
        :param cmp_class: coding of complement classes
        :type cmp_class: list
        :return: list of complements of this analysis with the given coding of complement class or an empty list
        """
        complement_list = list()
        for complement in self.complements:
            if complement.get_complement_class() in cmp_class:
                complement_list.append(complement)
        return complement_list

    def sort_complements(self):
        """
        sorts complements of self by using static method of class Complement
        """
        new_complement_list = Cmp.sort_complement_list(self.complements)
        self.complements = new_complement_list

    def set_primary_analysis(self, boolean_value):
        """
        primary analysis is used to determine if analysis of this sub sentence is analysis for the verb looked up in
        database (i.e. this sub sentence contains the verb used for database lookup)
        :param boolean_value: expected True or False
        :type boolean_value: Bool
        :return: no return value, alters self.primary_analysis
        """
        self.primary_analysis = boolean_value

    def is_primary_analysis(self):
        """
        :return: True if analysis of this sub sentence (subtree) is analysis for the verb that was looked up in the
        database, False otherwise
        """
        return self.primary_analysis

    def set_valence_holder_lemma(self, new_lemma):
        """
        :param new_lemma: word lemma of valence holder (possibly appended by cut off prefixes found in dependency tree)
        :type new_lemma: String
        :return: none, alters self.valence_holder_lemma
        """
        self.valence_holder_lemma = str(new_lemma)

    def get_complement_class_pattern(self):
        """
        :return: tuple() of codes (i.e. integers) indicating pattern of complement classes for this analysis, sorted by
        value of complement class coding (includes multiple complements of the same class)
        """
        pattern = tuple()
        for complement in self.complements:
            pattern += (complement.get_complement_class(),)
        return pattern

    def simple_deep_copy_analysis(self):
        """
        :return: copy of this analysis (that is deep copy of dependency tree used for creation of this analysis), note
        that a new analysis with values given for instantiation of this analysis is created;
        sets valence holder lemma and primary analysis for new analysis, does NOT include any analyses of subsentences
        (i.e. analysis in lists of own DependencyAanalysisSubTypeI or DependencyAanalysisSubTypeII)
        """
        new_tree_root = Node.recursive_deep_copy_tree(self.raw_tree)
        new_avz_nodes = self.raw_avz_nodes.copy()
        new_aux_nodes = self.raw_aux_nodes.copy()
        new_analysis = None
        if self.__class__ == DependencyAnalysis:
            new_analysis = DependencyAnalysis(new_tree_root, self.raw_verb, new_avz_nodes, new_aux_nodes, list(),
                                              list())
        elif self.__class__ == DependencyAnalysisSubTypeI:
            new_analysis = DependencyAnalysisSubTypeI(new_tree_root, self.raw_verb, new_avz_nodes, new_aux_nodes,
                                                      list(), list())
        elif self.__class__ == DependencyAnalysisSubTypeII:
            new_analysis = DependencyAnalysisSubTypeII(new_tree_root, self.raw_verb, new_avz_nodes, new_aux_nodes,
                                                       list(), list())
        new_analysis.set_valence_holder_lemma(self.valence_holder_lemma)
        new_analysis.set_primary_analysis(self.primary_analysis)
        return new_analysis

    def updated_complement_class_coding(self, given_analysis):
        """
        intended for use during recursive deep copy of self so that complement classes that were changed during analysis
        of valency frame (e.g. from Kadv to Kprp) are copied correctly
        :param given_analysis: analysis whose complement classes should be copied to the complements of self
        :return: no return value, possibly alters complement classes of own complements
        """
        for my_complement in self.complements:
            for given_complement in given_analysis.get_complements():
                if my_complement.get_root_w_id() == given_complement.get_root_w_id():
                    my_complement.set_complement_class(given_complement.get_complement_class())
                    break

    def recursive_deep_copy_analysis(self):
        """
        :return: deep copy (of current state, i.e. sets all complement codings to current codings of complements in
        self) of analysis
        """
        new_tree_root = Node.recursive_deep_copy_tree(self.raw_tree)
        new_verb = Node.recursive_deep_copy_tree(self.raw_verb)
        new_avz_nodes = self.raw_avz_nodes.copy()
        new_aux_nodes = self.raw_aux_nodes.copy()
        class_i_sub_analyses = list()
        for analysis in self.class_i_sub_analysis:
            class_i_sub_analyses.append(analysis.recursive_deep_copy_analysis())
        class_ii_sub_analysis = list()
        for analysis in self.class_ii_sub_analysis:
            class_ii_sub_analysis.append(analysis.recursive_deep_copy_analysis())
        new_analysis = None
        if self.__class__ == DependencyAnalysis:
            new_analysis = DependencyAnalysis(new_tree_root, new_verb, new_avz_nodes, new_aux_nodes,
                                              class_i_sub_analyses, class_ii_sub_analysis)
            new_analysis.updated_complement_class_coding(self)
        elif self.__class__ == DependencyAnalysisSubTypeI:
            new_analysis = DependencyAnalysisSubTypeI(new_tree_root, new_verb, new_avz_nodes, new_aux_nodes,
                                                      class_i_sub_analyses, class_ii_sub_analysis)
            new_analysis.updated_complement_class_coding(self)
        elif self.__class__ == DependencyAnalysisSubTypeII:
            new_analysis = DependencyAnalysisSubTypeII(new_tree_root, new_verb, new_avz_nodes, new_aux_nodes,
                                                       class_i_sub_analyses, class_ii_sub_analysis)
            new_analysis.updated_complement_class_coding(self)
        new_analysis.set_valence_holder_lemma(self.valence_holder_lemma)
        new_analysis.set_primary_analysis(self.primary_analysis)
        return new_analysis


class DependencyAnalysisSubTypeI(DependencyAnalysis):
    """
    Dependency Analysis for sub sentences of a sentence connected via simple "," or "und" in sentence, TypeI is
    indicated by connecting "kon"- (and possibly "cj"-) Nodes
    """

    def __init__(self, tree_root, verb, avz_nodes, aux_nodes, class_i_analysis, class_ii_analysis):
        """
        see super for all parameters; has new parameter connecting_node_value which indicates which node the subtree
        for this analysis was cut off at (is set to value of kon-node if kon-node is followed by cj-node)
        """
        super().__init__(tree_root, verb, avz_nodes, aux_nodes, class_i_analysis, class_ii_analysis)
        self.connecting_node_value = tree_root.get_node()
        self.direct_upper_analysis = None
        self.main_analysis = None

    def __str__(self):
        new_string = "DependencyAnalysisSubTypeI - connecting node: {nde}\n".format(nde=self.connecting_node_value)
        new_string += super().__str__()
        return new_string

    def get_connecting_node(self):
        """
        :return: node value (as int) indicating the last node the "direct upper" dependency tree was cut off at
        """
        return self.connecting_node_value

    def set_connecting_node(self, new_node):
        """
        intended for use during creation of analysis
        :param new_node: the node to be set as connecting node to the direct upper analysis in the dependency tree
        :type new_node: integer
        :return: no return value
        """
        self.connecting_node_value = new_node

    def simple_deep_copy_analysis(self):
        """
        uses super for copy of analysis and sets connecting node of new analysis to own connecting node
        :return: the copy of the new analysis
        """
        new_analysis = super().simple_deep_copy_analysis()
        new_analysis.set_connecting_node(self.get_connecting_node())
        return new_analysis

    def recursive_deep_copy_analysis(self):
        """
        uses super for copy of analysis and sets connecting node of new analysis to own connecting node
        :return: the copy of the new analysis
        """
        new_analysis = super().recursive_deep_copy_analysis()
        new_analysis.set_connecting_node(self.get_connecting_node())
        return new_analysis


class DependencyAnalysisSubTypeII(DependencyAnalysis):
    """
    Dependency Analysis for sub sentences of a sentence indicated via different phrases, e.g. "dass, es...", TypeII is
    indicated by connecting 'konj', 'neb', 'objc', 'rel', 's' and 'subjc' Nodes (currently hard coded in
    SentenceAnalysisConnector during recursive creation of dependency analysis
    """

    def __init__(self, tree_root, verb, avz_nodes, aux_nodes, class_i_analysis, class_ii_analysis):
        """
        see super for all parameters; has new parameter connecting_node_value which indicates which node the subtree
        for this analysis was cut off at
        """
        super().__init__(tree_root, verb, avz_nodes, aux_nodes, class_i_analysis, class_ii_analysis)
        self.connecting_node_value = tree_root.get_node()
        self.direct_upper_analysis = None
        self.main_analysis = None

    def __str__(self):
        new_string = "DependencyAnalysisSubTypeII - connecting node: {nde}\n".format(nde=self.connecting_node_value)
        new_string += super().__str__()
        return new_string

    def get_connecting_node(self):
        """
        :return node value (as int) indicating the last node the "direct upper" dependency tree was cut off at
        """
        return self.connecting_node_value

