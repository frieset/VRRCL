from core_logic.complement import Complement
from core_logic.k_means_helper import KMeansHelper as KmH
from core_logic.various_errors import ValencyFrameError
from core_logic.various_errors import KMeanError


class ValencyFrame:
    """
    Object used to analyze large quantity of sentences regarding their dependency trees and complements of each sentence
    """
    def __init__(self, sentence_id_to_analyses_mapping, sen_id_to_wo_id_word_mapping, sen_id_to_w_id_lemma_mapping):
        """
        initializes working dictionaries for analysis
        :param sentence_id_to_analyses_mapping: dict() with sentence ids as keys and list of analysis (i.e. list of
        objects of class DependencyAnalysis or subclass) as values
        :type sentence_id_to_analyses_mapping: dictionary
        :param sen_id_to_wo_id_word_mapping: sentence ids as keys and a dict() for each id as value, new dict() has
        word ids as keys and words as values
        :type sen_id_to_wo_id_word_mapping: Dictionary
        """
        self.sen_id_to_full_analyses = sentence_id_to_analyses_mapping
        self.sen_id_to_wid_to_word_mapping = sen_id_to_wo_id_word_mapping
        self.sen_id_to_wid_to_lemma_mapping = sen_id_to_w_id_lemma_mapping
        self.current_dep_class_pattern_to_sen_id = self.create_dep_class_pattern_to_sen_id_dict()
        self.k_mean_result = None
        self.k_mean_result_count = 0

    def __str__(self):
        if len(self.sen_id_to_full_analyses.keys()) > 0:
            new_string = "Valency Analysis:\n"
            new_string += "Count of each class pattern:\n"
            key_list = list(x for x in self.current_dep_class_pattern_to_sen_id.keys())
            for coded_classes in key_list:
                string = ""
                for coded_class in coded_classes:
                    string += "{cmpcls} ".format(cmpcls=Complement.comp_class_def(coded_class))
                new_new_string = "Sentence-ID's with this pattern: "
                for sen_id in self.current_dep_class_pattern_to_sen_id[coded_classes]:
                    new_new_string += "{sid}, ".format(sid=sen_id)
                new_new_string = new_new_string[:-2]
                new_string += "Class pattern: {complement_classes} - Count: {quantity}\n{senid}\n" \
                    .format(complement_classes=string,
                            quantity=len(self.current_dep_class_pattern_to_sen_id[coded_classes]), senid=new_new_string)
        else:
            new_string = "No valency frame for analysis found\n"
        return new_string

    def get_k_mean_result_count(self):
        """
        :return: number of tries (as integer) that were identical to the last result of a successful execution of k-mean algorithm
        or 0 if no clustering via k-mean has been executed yet
        """
        return self.k_mean_result_count

    def create_dep_class_pattern_to_sen_id_dict(self):
        """
        creates a dictionary using all analyses in complete analysis list of self
        :return: dictionary with all complement class patterns (i.e. signatures) in complete analysis list as keys (i.e.
        each key is a tuple of integers indicating a specific complement class pattern) and sentence ids where this
        pattern occurs as values for each key
        """
        dep_class_pattern_to_sen_id = dict()
        for each_key in self.sen_id_to_full_analyses.keys():
            analyses_list = self.sen_id_to_full_analyses[each_key]
            for analysis in analyses_list:
                new_pattern = analysis.get_complement_class_pattern()
                if new_pattern not in dep_class_pattern_to_sen_id.keys():
                    new_sen_id_list = list()
                    new_sen_id_list.append(each_key)
                    dep_class_pattern_to_sen_id[new_pattern] = new_sen_id_list
                else:
                    new_sen_id_list = dep_class_pattern_to_sen_id[new_pattern]
                    new_sen_id_list.append(each_key)
                    dep_class_pattern_to_sen_id[new_pattern] = new_sen_id_list
        return dep_class_pattern_to_sen_id

    def get_word_by_w_id_s_id(self, w_id, s_id, lemma=True):
        """
        gets word by word_id and sentence_id (uses dictionary of sentence ids to dictionary of word ids to words)
        :raises ValencyFrameError if sentence id or word id are not found
        :param w_id: word_id to look for
        :type w_id: Integer
        :param s_id: sen_id to use for lookup of w_id
        :type s_id: Integer
        :param lemma: if True, returns lemma of this word id (e.g. infinitive of verb), else returns word (e.g.
        conjugated verb)
        :type lemma: bool
        :return: word (as string)
        """
        if s_id not in self.sen_id_to_wid_to_word_mapping.keys():
            raise ValencyFrameError(3)
        else:
            if lemma:
                given_mapping = self.sen_id_to_wid_to_lemma_mapping[s_id]
            else:
                given_mapping = self.sen_id_to_wid_to_word_mapping[s_id]
        if w_id not in given_mapping.keys():
            raise ValencyFrameError(4)
        else:
            word = given_mapping[w_id]
            return word

    def create_interesting_object_to_sen_id_mapping_for_k_means(self, cmp_class, label=False):
        """
        creates mapping of "abstract objects" (could be strings indicating prepositions or tuples of integers indicating
        complement signatures) to sentence id's for clustering of these "abstract objects" via k-means;
        searches each complement of each analysis given as value in dict() sen_id_to_full_analyses for given complement
        class, appends word that is head of this complement (i.e. "phrase") to list for k-means;
        :param cmp_class: given complement class
        :type cmp_class: Integer
        :param label: if True algorithm works with label of root of each complement found, otherwise uses
        root word (via conversion of word id (int) to word (string)) as key for dictionary that is returned
        (note that in the latter case the word is used and not the lemma and the first character is always lower case)
        :type label: Bool
        :return dictionary with strings as keys and list of integers (i.e. sentence ids) as values for each key
        """
        sen_id_to_complements = dict()
        for sen_id in self.sen_id_to_full_analyses.keys():
            for analysis in self.sen_id_to_full_analyses[sen_id]:
                new_complement_list = analysis.get_complement_by_class(cmp_class)
                if new_complement_list is not []:
                    sen_id_to_complements[sen_id] = new_complement_list
        sen_id_to_interesting_object_mapping = dict()
        for k_means_key in sen_id_to_complements.keys():
            object_list = list()
            for complement in sen_id_to_complements[k_means_key]:
                if label:
                    object_list.append(complement.get_root_label())
                else:
                    new_string = self.get_word_by_w_id_s_id(complement.get_root_w_id(), k_means_key)
                    if len(new_string) == 1:
                        new_string = new_string[0].lower()
                    else:
                        new_string = new_string[0].lower() + new_string[1:]
                    object_list.append(new_string)
            sen_id_to_interesting_object_mapping[k_means_key] = object_list
        word_to_sen_id_mapping = dict()
        for new_key in sen_id_to_interesting_object_mapping.keys():
            interesting_words = sen_id_to_interesting_object_mapping[new_key]
            for interesting_word in interesting_words:
                if interesting_word not in word_to_sen_id_mapping.keys():
                    word_to_sen_id_mapping[interesting_word] = [new_key]
                else:
                    key_list = list(word_to_sen_id_mapping[interesting_word]).copy()
                    key_list.append(new_key)
                    word_to_sen_id_mapping[interesting_word] = key_list
        return word_to_sen_id_mapping

    @staticmethod
    def create_k_mean_list_via_dict(given_dict):
        """
        intended to create list of given_objects for key-means algorithm, see init of class KMeanHelper for further
        information
        :param given_dict: a dictionary that has strings as keys and a list of integers as value for each keys (intended
        for use with a dictionary returned by function create_interesting_object_to_sen_id_mapping_for_k_means())
        :type given_dict dictionary
        :return: a list where each element is a list with string at position[0] (the keys of the given dictionary) and a
        single integer at position[1] (the length of the list of values for each key of the given dictionary)
        """
        list_for_k_means = list()
        for word in given_dict.keys():
            list_for_k_means.append([word, len(given_dict[word])])
        list_for_k_means = list_for_k_means
        return list_for_k_means

    @staticmethod
    def execute_k_means(list_for_k_means, cluster_quantity, max_tries, random_reset=True):
        """
        used to execute a k-mean clustering
        :raises KMeanError either when result is inconclusive or when an error during instantiation occurred
        :param list_for_k_means: list where each element is a list with a string or tuple of integers at position[0]
        and an integer at position[1]
        :type list_for_k_means: list of lists
        :param cluster_quantity: indicates how many cluster centroids should be created
        :type cluster_quantity: integer
        :param max_tries: indicates how many times the clustering should be made with the given list_for_k_means
        :type max_tries: integer
        :param random_reset: used to determine how lost cluster centroids should be reestablished, see function
        k_means() or function establish_cluster_validity() of class KMeanHelper or function reset_centroid() of class
        ClusteredObject for further information
        :return: a list with a conclusive k-means-analysis at position [0] and an integer indicating how many tries
        were identical to this result at position [1]
        """
        try:
            k_mean_result = KmH.cluster_by_value(list_for_k_means, cluster_quantity, max_tries, random_reset)
        except KMeanError as kmherr:
                raise kmherr
        return k_mean_result

    def k_means_for_complement_signature_quantity(self, cluster_quantity, max_tries, random_reset=True):
        """
        used to cluster the current valency frame (as given in current_dep_class_pattern_to_sen_id) by the frequency
        with which the complement signatures occur in this frame
        :raises KMeanError if result of clustering is inconclusive or an error occurs during instantiation
        :param cluster_quantity: number of proposed clusters
        :type cluster_quantity: integer
        :param max_tries: number of tries that the clustering should be done
        :type max_tries: integer
        :param random_reset: used to determine how lost cluster centroids should be reestablished, see function
        k_means() or function establish_cluster_validity() of class KMeanHelper or function reset_centroid() of class
        ClusteredObject for further information
        :return: a conclusive k-means-analysis
        """
        list_for_k_means = list()
        for signature in self.current_dep_class_pattern_to_sen_id.keys():
            list_for_k_means.append([signature, len(self.current_dep_class_pattern_to_sen_id[signature])])
        try:
            k_mean_result = ValencyFrame.execute_k_means(list_for_k_means, cluster_quantity, max_tries, random_reset)
            self.k_mean_result_count = k_mean_result[1]
            k_mean_result = k_mean_result[0]
            self.k_mean_result = k_mean_result
        except KMeanError as kmherr:
            raise kmherr
        else:
            return k_mean_result

    def set_k_mean_result(self, new_result):
        """
        intended to save result of a k-mean execution (i.e. best result out of all tries) to self
        :param new_result: a k-mean result
        :type new_result: object of class KMeansHelper
        :return: no return value
        """
        self.k_mean_result = new_result

    def set_k_mean_result_count(self, new_count):
        """
        intended to save count of how many tries were identical for most recent successful execution of k-means
        algorithm (only number for final result as indicated by self.K-Mean_result is saved)
        :param new_count: indicating the number of tries that were identical to the result of the last successful
        k-means clustering
        :type new_count: integer
        :return: no return value
        """
        self.k_mean_result_count = new_count

    def get_sen_id_to_analyses_mapping(self):
        """
        :return: dictionary with sentence ids as keys, value for each key is a list of objects of class
        DependencyAnalysis (or subclass) that belong to the sentence with this id
        """
        return self.sen_id_to_full_analyses

    def get_current_dep_class_pattern_mapping(self):
        """
        :return: dictionary with complement class signatures (i.e. tuples of integers) of current valency analysis as
        keys and sentence ids where this signature occurs as values for each key (dictionary affected by altering of
        valency frame, can be used for output of result after analysis)
        """
        return self.current_dep_class_pattern_to_sen_id

    def update_current_dep_class_pattern_mapping(self):
        """
        used to create current_dep_class_pattern_to_sen_id (that is, current dictionary with complement class signatures
        as keys and list of sentence-id's where this signature occurs in as value for each key) from all analyses in
        complete analysis list of self, note that this resets the valency frame to the last time any complement of any
        analysis was changed (e.g. due to correction of Kadv to Kprp) or to the initial valency frame, if no complements
        were changed after creation
        :return: no return value
        """
        self.current_dep_class_pattern_to_sen_id = self.create_dep_class_pattern_to_sen_id_dict()

    def set_current_dep_class_pattern_mapping(self, new_dep_class_pattern_mapping):
        """
        :raises ValencyFrameError if no dictionary is given, or if any key in the dictionary is empty, or if any key in
        the dictionary is not a tuple (no checks for correct use of complement class coding in the tuples is made, see
        class Complement for further information on valid codings for complement classes)
        :param new_dep_class_pattern_mapping: representing the new valency frame, that is a dictionary with
        tuples of integers as keys (indicating complement class signatures) and a list of sentence ids where this
        signature occurs in as value for each key
        :type new_dep_class_pattern_mapping: dictionary
        :return:
        """
        if new_dep_class_pattern_mapping.__class__ is not dict:
            raise ValencyFrameError(5)
        elif len(list(x for x in new_dep_class_pattern_mapping.keys())) == 0:
            raise ValencyFrameError(5)
        else:
            for new_key in new_dep_class_pattern_mapping.keys():
                if new_key.__class__ is not tuple:
                    raise ValencyFrameError(8)
        self.current_dep_class_pattern_to_sen_id = new_dep_class_pattern_mapping

    @staticmethod
    def add_sen_id_to_dep_class_pattern_mapping(old_key, new_key, old_dep_class_pattern, new_dep_class_pattern):
        """
        adds all objects (sentence id's) occurring in the old_dep_class_pattern under old_key to the
        new_dep_class_pattern under new_key, no duplicates of objects (sentence id's) are added; i.e. adds all
        sentence id's of the old valency frame that belonged to the old complement class signature to the new valency
        frame under the new complement class signature
        :param old_key: indicating the old complement class signature
        :type old_key: tuple of integers
        :param new_key: indicating the new complement clas signature
        :type new_key: tuple of integers
        :param old_dep_class_pattern: indicating the old valency frame
        :type old_dep_class_pattern: dictionary with complement class signatures (i.e. tuples of integers) as keys and
        a list of sentence id's (i.e. a list of integers) as value for each key
        :param new_dep_class_pattern: indicating the new valency frame
        :type new_dep_class_pattern: dictionary with complement class signatures (i.e. tuples of integers) as keys and
        a list of sentence id's (i.e. a list of integers) as value for each key
        :return: an altered version of the new_dep_class_pattern that contains all sentence id's previously found in the
        old mapping under old_key and in the new_mapping under new_key, all objects are now found under the new_key in
        the new mapping (no duplicates added)
        """
        if new_key == old_key:
            if new_key not in new_dep_class_pattern.keys():
                new_dep_class_pattern[new_key] = old_dep_class_pattern[old_key]
            else:
                old_sen_id_set = set(x for x in old_dep_class_pattern[old_key])
                new_sen_id_set = set(x for x in new_dep_class_pattern[new_key])
                final_sen_id_set = old_sen_id_set.union(new_sen_id_set)
                new_sen_id_list = list(x for x in final_sen_id_set)
                new_dep_class_pattern[new_key] = new_sen_id_list
        else:
            if new_key in old_dep_class_pattern.keys():
                new_sen_id_list = list()
                new_sen_id_list.extend(old_dep_class_pattern[new_key])
                new_sen_id_list.extend(old_dep_class_pattern[old_key])
                if new_key not in new_dep_class_pattern.keys():
                    new_dep_class_pattern[new_key] = new_sen_id_list
                else:
                    new_sen_id_set = set(x for x in new_sen_id_list)
                    old_sen_id_set = set(x for x in new_dep_class_pattern[new_key])
                    final_sen_id_set = new_sen_id_set.union(old_sen_id_set)
                    final_sen_id_list = list(x for x in final_sen_id_set)
                    new_dep_class_pattern[new_key] = final_sen_id_list
            else:
                if new_key not in new_dep_class_pattern.keys():
                    new_dep_class_pattern[new_key] = old_dep_class_pattern[old_key]
                else:
                    old_sen_id_set = set(x for x in old_dep_class_pattern[old_key])
                    new_sen_id_set = set(x for x in new_dep_class_pattern[new_key])
                    final_sen_id_set = old_sen_id_set.union(new_sen_id_set)
                    final_sen_id_list = list(x for x in final_sen_id_set)
                    new_dep_class_pattern[new_key] = final_sen_id_list
        return new_dep_class_pattern
