from core_logic.sentence_object import SentenceObject as SenObj
from core_logic.complement import Complement as Cmp
from core_logic.valency_frame import ValencyFrame as VaFr
from core_logic.dependency_tree import IncorrectTreeError
from core_logic.sentence_object import IncorrectInstantiationError
from core_logic.various_errors import KMeanError
from core_logic.various_errors import ValencyAnalysisError

import logging

logger = logging.getLogger('ValancyRelationshipRecognizer')


class ValencyAnalysis:
    """
    Main class used to analyze dependency trees for verb valencies, creates list of sentences with given data, tries to
    analyze correctly instantiated sentences, resulting dependency analyses are used for evaluation via k-means.
    Note: Functions to correct/specify Kadv/Kprp alter the dependency analyses used to create the valency frame (by
    changing the complement class of some of these analyses), while functions to delete objects from the valency frame
    are only executed on the dictionary used to indicate the current valency frame. Therefore, correction/specification
    of Kadv/Kprp can only be reversed by using function initialize_valency_frame() while deletion of rare signatures,
    deletion of multiple complements or deletion of certain complements from the frame can be undone by using
    function reset_valency_frame()
    """

    def __init__(self, raw_data, verb):
        """
        creates sentence for each data-set in raw_data and creates dependency analysis for each sentence
        :param raw_data: data from database as list [[sentence_id1, word_ids1, words1, tree_data1, sentence1, lemma1],
         [sentence_id2, word_ids2, words2, tree_data2, sentence2, lemma2], ...]
        :type raw_data: List with following data types at positions: [0]: integer; [1]: list of integers; [2]: list of
        strings, [3]: list of edges (each edge is a list of the form [vertex1, vertex2, label] where vertex1 and vertex2
        are integers, label is a string); [4]: string; [5]: list of strings
        :param verb: verb that was used for lookup in database, needed to distinguish between analysis of searched
        verb and others
        :type verb: String
        """
        self.sentences = list()
        for raw_sentence_data in raw_data:
            sentence_id = raw_sentence_data[0]
            word_ids = raw_sentence_data[1]
            words = raw_sentence_data[2]
            tree_data = raw_sentence_data[3]
            sentence = raw_sentence_data[4]
            lemmata = raw_sentence_data[5]
            try:
                new_sentence = SenObj(sentence_id, sentence, word_ids, words, tree_data, lemmata)
                self.sentences.append(new_sentence)
                w_id_to_lemmata = dict()
                for word_id, lemma in zip(word_ids, lemmata):
                    w_id_to_lemmata[word_id] = lemma
                new_sentence.analyze_dependence_tree(w_id_to_lemmata, verb)
                logger.debug(new_sentence)
            except IncorrectTreeError as error1:
                logger.warning("TreeError in: {sid} - {err}".format(sid=str(raw_sentence_data[0]), err=error1))
            except IncorrectInstantiationError as error2:
                logger.warning("InstantiationError in: {sid} - {err}".format(sid=str(raw_sentence_data[0]), err=error2))
        quantity = str(len(self.sentences))
        self.sentences_w_valid_analysis = SenObj.get_sentences_with_valid_analysis(self.sentences)
        valid_quantity = str(len(self.sentences_w_valid_analysis))
        logger.info("\nData extraction complete: {qty} Sentences created - {vldqty} Analyses created".
              format(qty=quantity, vldqty=valid_quantity))
        self.valency_frame = None

    def __str__(self):
        return "\n{vlncyfrm}".format(vlncyfrm=str(self.valency_frame))

    def get_current_valency_frame_as_dict(self):
        """
        used to get dictionary with result of valency analysis
        :raises ValencyAnalysisError if no valency frame is found
        :return: dictionary with complement class signatures of current valency analysis as keys and all sentence ids
        (as a list of integers) where this signature occurs as values for each key
        """
        if self.valency_frame is None:
            raise ValencyAnalysisError(1)
        else:
            return self.valency_frame.get_current_dep_class_pattern_mapping()

    def get_most_recent_k_mean_count(self):
        """
        for output purposes
        :return: integer indicating how many tries were identical to the result for the last successful execution of
        any k-mean-algorithm (or 0 if no clustering via k-mean has been done)
        """
        if self.valency_frame is not None:
            return self.valency_frame.get_k_mean_result_count()
        else:
            return 0

    def initialize_valency_frame(self, main_prime=True):
        """
        used for creation of a valency frame
        :param main_prime: if True, only the analyses of sentences are used, where the main sentence (i.e. the sub tree
        of the dependency tree that contains the root of the complete tree) contains the verb used for the fetching
        sentences from the database, if False all analyses of sub sentences that contain the verb used for the lookup
        are used
        """
        if main_prime:
            main_prime_sentences = SenObj.get_only_sentences_w_main_primary_analysis(self.sentences_w_valid_analysis)
            analysis_mapping_for_frame = SenObj.get_mapping_sid_to_main_sentence_analysis(main_prime_sentences)
            w_id_to_word_mapping_for_frame = SenObj.get_w_id_to_word_mapping_as_mapping_on_sid(main_prime_sentences)
            w_id_to_lemma_mapping_for_frame = SenObj.get_w_id_to_lemma_mapping_as_mapping_on_sid(main_prime_sentences)
            len_used_sentences = len(main_prime_sentences)
        else:
            all_prime_sentences = SenObj.get_only_sentences_w_primary_analysis(self.sentences_w_valid_analysis)
            analysis_mapping_for_frame = SenObj.get_mapping_sen_id_to_primary_analysis_list(all_prime_sentences)
            w_id_to_word_mapping_for_frame = SenObj.get_w_id_to_word_mapping_as_mapping_on_sid(all_prime_sentences)
            w_id_to_lemma_mapping_for_frame = SenObj.get_w_id_to_lemma_mapping_as_mapping_on_sid(all_prime_sentences)
            len_used_sentences = len(all_prime_sentences)
        self.valency_frame = VaFr(analysis_mapping_for_frame, w_id_to_word_mapping_for_frame, w_id_to_lemma_mapping_for_frame)
        logger.info("\nValency Frame initialized\nnumber of total sentences: {ttlqnty} | number of used "
                                 "sentences: {usdqnty}\n".format(ttlqnty=len(self.sentences),
                                                                   usdqnty=str(len_used_sentences)))
        logger.info("~~~~~~~~~~~~~~complete Valency Frame without postprocessing~~~~~~~~~~~\n{vlncyfrm}".format(
            vlncyfrm=str(self.valency_frame)))

    def delete_multiple_complements_from_frame(self, quantity, simply_delete=False):
        """
        used to trim a valency frame so that no complement class occurs more often than determined by param quantity
        :param quantity: maximum number of complements of the same class <= quantity
        :type quantity: integer
        :param simply_delete: if True, all complement signatures that have a complement class occurring more often than
        determined by quantity are simply deleted from the valency frame (therefore, the sentences that have the
        affected signatures are deleted from the frame as well);
        if False, the affected complements are deleted from their respective signatures and the objects of this "new"
        signature are added to any signature in the valency frame that is equal to this "new" signature, if this "new"
        signature does not currently exist in the valency frame, the "new" signature is added to the frame with all its
        sentences
        :type simply_delete: bool
        :return: no return value, alters valency frame
        """
        old_dep_class_pattern = self.valency_frame.get_current_dep_class_pattern_mapping()
        new_dep_class_pattern = dict()
        for old_key in old_dep_class_pattern.keys():
            new_key = tuple()
            current_complement = None
            current_complement_count = None
            for complement in old_key:
                if current_complement != complement:
                    current_complement = complement
                    current_complement_count = 1
                    new_key += (current_complement,)
                else:
                    if current_complement_count < quantity:
                        current_complement_count += 1
                        new_key += (current_complement,)
            if simply_delete:
                if new_key != old_key:
                    continue
                else:
                    new_dep_class_pattern = VaFr.add_sen_id_to_dep_class_pattern_mapping(old_key, new_key,
                                                                                         old_dep_class_pattern,
                                                                                         new_dep_class_pattern)
            else:
                new_dep_class_pattern = VaFr.add_sen_id_to_dep_class_pattern_mapping(old_key, new_key,
                                                                                     old_dep_class_pattern,
                                                                                     new_dep_class_pattern)
        try:
            self.valency_frame.set_current_dep_class_pattern_mapping(new_dep_class_pattern)
        except ValencyAnalysisError as valanerr:
            logger.error(valanerr)

    def delete_complements_from_frame(self, complement_list, keep=True, simply_delete=False):
        """
        used to delete specific complements from a valency frame
        :param complement_list: complements to be deleted or kept
        :type complement_list: list
        :param keep: used to determine if complements given in complement_list should be kept or deleted
        :type keep: bool
        :param simply_delete: if True, all complement signatures that are altered, are simply deleted from the
        valency frame (therefore, the sentences that have the affected signatures are deleted from the frame as well);
        if False, the affected complements are deleted from their respective signatures and the objects of this "new"
        signature are added to any signature in the valency frame that is equal to this "new" signature, if this "new"
        signature does not currently exist in the valency frame, the "new" signature is added to the frame with all its
        sentences
        :type simply_delete: bool
        :return: no return value, alters valency frame
        """
        old_dep_class_pattern = self.valency_frame.get_current_dep_class_pattern_mapping()
        new_dep_class_pattern = dict()
        for old_key in old_dep_class_pattern.keys():
            new_key = tuple()
            for complement in old_key:
                if keep:
                    if complement in complement_list:
                        new_key += (complement,)
                else:
                    if complement not in complement_list:
                        new_key += (complement,)
            if simply_delete:
                if new_key != old_key:
                    continue
                else:
                    new_dep_class_pattern = VaFr.add_sen_id_to_dep_class_pattern_mapping(old_key, new_key,
                                                                                         old_dep_class_pattern,
                                                                                         new_dep_class_pattern)
            else:
                new_dep_class_pattern = VaFr.add_sen_id_to_dep_class_pattern_mapping(old_key, new_key,
                                                                                     old_dep_class_pattern,
                                                                                     new_dep_class_pattern)
        try:
            self.valency_frame.set_current_dep_class_pattern_mapping(new_dep_class_pattern)
        except ValencyAnalysisError as valanerr:
            logger.error(valanerr)

    def delete_rare_signatures_from_frame_by_k_mean(self, cluster_quantity, max_tries, clusters_to_keep=None,
                                                    random_reset=True):
        """
        used to trim a valency frame so that only the "most frequent" signatures remain, uses k-mean algorithm for
        clustering to determine clusters of various frequency ranges, clusters with "most frequent objects" are kept
        :raises KMeanError if no conclusive KMeanResult was found or error during instantiation of object of class
        KMeanHelper occurs
        :param cluster_quantity: number of clusters to create
        :type cluster_quantity: integer
        :param max_tries: number of k-mean tries that should be executed and compared
        :type max_tries: integer
        :param clusters_to_keep: number of clusters that should be kept (clusters are sorted in descending frequency)
        :type clusters_to_keep: integer or None
        :param random_reset: if True, whenever a cluster centroid needs to be reset during k-mean execution, a new
        cluster with a random centroid is created and one object is put in this cluster (the object out of all objects
        to cluster that is currently the farthest distance away from its own cluster centroid);
        if False, whenever a cluster centroid needs to be reset during k-mean execution, a new cluster centroid is
        created by choosing the object value of the object that is put in this cluster (again choosing the one object
        that is furthest away from its current cluster centroid out of all objects to cluster)
        :type random_reset: bool
        :return: no return value, possibly sets valency frame attribute
        """
        if cluster_quantity == 0:
            raise ValencyAnalysisError(4)
        if clusters_to_keep is not None:
            if clusters_to_keep < 1:
                raise ValencyAnalysisError(2)
            elif clusters_to_keep >= cluster_quantity:
                raise ValencyAnalysisError(3)
            else:
                max_cluster = clusters_to_keep - cluster_quantity
        else:
            max_cluster = -1
        try:
            result = self.valency_frame.k_means_for_complement_signature_quantity(cluster_quantity, max_tries, random_reset)
        except KMeanError as kmherr:
            raise kmherr
        else:
            logger.debug("k-mean-result overview:\n{kmrslt}".format(kmrslt=result))
            result_keys = list(x for x in result.get_centroid_to_mapped_objects().keys())
            result_keys = result_keys[:max_cluster]
            old_dep_class_pattern = self.valency_frame.get_current_dep_class_pattern_mapping()
            new_dep_class_pattern = dict()
            for k_mean_key in result_keys:
                classified_object_list = result.get_centroid_to_mapped_objects()[k_mean_key]
                for classified_object in classified_object_list:
                    new_key = classified_object.get_object_key()
                    new_dep_class_pattern[new_key] = old_dep_class_pattern[new_key]
            self.valency_frame.set_current_dep_class_pattern_mapping(new_dep_class_pattern)

    def correct_kadv_kprp(self, cluster_quantity, max_tries, random_reset=True, clusters_to_keep=None):
        """
        changes all complements in all analyses with the most frequent prepositions from complement class 5 (Kadv) to
        complement class 4 (Kprp), uses k-means algorithm to determine clusters of various frequency ranges;
        the most frequent prepositions are always seen as the prepositions indicating a Kprp, no further analysis is
        made to distinguish between complements correctly or incorrectly identified as Kprp's by this clustering
        :raises KMeanError if no conclusive KMeanResult was found or error during instantiation of object of class
        KMeanHelper occurs
        :param cluster_quantity: number of clusters to create
        :type cluster_quantity: integer
        :param max_tries: number of k-mean tries that should be executed and compared
        :type max_tries: integer
        :param clusters_to_keep: number of clusters that should be kept (clusters are sorted in descending frequency)
        :type clusters_to_keep: integer or None
        :param random_reset: if True, whenever a cluster centroid needs to be reset during k-mean execution, a new
        cluster with a random centroid is created and one object is put in this cluster (the object out of all objects
        to cluster that is currently the farthest distance away from its own cluster centroid);
        if False, whenever a cluster centroid needs to be reset during k-mean execution, a new cluster centroid is
        created by choosing the object value of the object that is put in this cluster (again choosing the one object
        that is furthest away from its current cluster centroid out of all objects to cluster)
        :type random_reset: bool
        :return: no return value, possibly sets valency frame attribute
        """
        if clusters_to_keep is not None:
            if clusters_to_keep < 1:
                raise ValencyAnalysisError(2)
            elif clusters_to_keep >= cluster_quantity:
                raise ValencyAnalysisError(3)
            else:
                max_cluster = clusters_to_keep - cluster_quantity
        else:
            max_cluster = -1
        cmp_class = [5]
        preposition_to_sen_id_dict = self.valency_frame.create_interesting_object_to_sen_id_mapping_for_k_means(cmp_class)
        list_for_k_means = VaFr.create_k_mean_list_via_dict(preposition_to_sen_id_dict)
        try:
            k_mean_result = VaFr.execute_k_means(list_for_k_means, cluster_quantity, max_tries, random_reset)
            self.valency_frame.set_k_mean_result_count(k_mean_result[1])
            k_mean_result = k_mean_result[0]
            self.valency_frame.set_k_mean_result(k_mean_result)
        except KMeanError as kmherr:
            raise kmherr
        else:
            logger.debug("k-mean-result overview:\n{kmrslt}".format(kmrslt=k_mean_result))
            k_mean_result_keys = list(x for x in k_mean_result.get_centroid_to_mapped_objects().keys())
            k_mean_result_keys = k_mean_result_keys[:max_cluster]
            preposition_list = list()
            for k_mean_result_key in k_mean_result_keys:
                for classified_object in k_mean_result.get_centroid_to_mapped_objects()[k_mean_result_key]:
                    preposition_list.append(classified_object.get_object_key())
            sen_id_to_analyses_mapping = self.valency_frame.get_sen_id_to_analyses_mapping()
            for sen_id in sen_id_to_analyses_mapping.keys():
                for analysis in sen_id_to_analyses_mapping[sen_id]:
                    potential_complements_to_change = analysis.get_complement_by_class(cmp_class)
                    for complement in potential_complements_to_change:
                        new_preposition = self.valency_frame.get_word_by_w_id_s_id(complement.get_root_w_id(), sen_id)
                        if new_preposition[0].isupper():
                            new_preposition = new_preposition[0].lower() + new_preposition[1:]
                        if new_preposition in preposition_list:
                            complement.set_complement_class(4)
                    analysis.sort_complements()
            self.valency_frame.update_current_dep_class_pattern_mapping()

    def specify_complements_by_preposition(self, complement_list):
        """
        further specifies complement by the root word that occurs as head of the phrase, intended for use with
        complements of class 4 (requiring prior altering of Kadv to Kprp by function correct_kadv_kprp) or 5 so that
        these complement classes are further divided by their preposition (therefore altering a complement of class Kprp
        to class Kprp_preposition or Kadv to Kadv_preposition), function is tested but not evaluated due to missing
        availability of access to correct answers;
        note that the complement class of the affected complements is altered, therefore should not be used consecutive
        times on the same object of class ValencyAnalysis
        :param complement_list: list of complement classes that should be further specified by their root word
        :type complement_list list of integers
        :return: no return value, alters valency frame
        """
        sen_id_to_analyses_mapping = self.valency_frame.get_sen_id_to_analyses_mapping()
        for sen_id in sen_id_to_analyses_mapping.keys():
            for analysis in sen_id_to_analyses_mapping[sen_id]:
                potential_complements_to_change = analysis.get_complement_by_class(complement_list)
                for complement in potential_complements_to_change:
                    new_preposition = self.valency_frame.get_word_by_w_id_s_id(complement.get_root_w_id(), sen_id)
                    if len(new_preposition) > 0:
                        if new_preposition[0].isupper():
                            new_preposition = new_preposition[0].lower() + new_preposition[1:]
                    complement_coding_dict = Cmp.comp_class_coding()
                    for preposition_coding in complement_coding_dict.keys():
                        if new_preposition == complement_coding_dict[preposition_coding]:
                            new_comp_class = preposition_coding + complement.get_complement_class()
                            complement.set_complement_class(new_comp_class)
                            break
                analysis.sort_complements()
        self.valency_frame.update_current_dep_class_pattern_mapping()

    def reset_valency_frame(self):
        """
        resets valency frame by rewriting valency frame to the complement class signatures currently found in all
        analyses, therefore does not recreate "initial" valency frame but resets frame to last time any analysis was
        changed (e.g. due to specification of Kprp and Kadv), for reset of frame to initial status, use function
        initialize_valency_frame
        :return: none, alters valency frame
        """
        self.valency_frame.update_current_dep_class_pattern_mapping()

    @staticmethod
    def standard_cleaning(working_analysis):
        """
        used to delete unwanted complements (currently hardcoded as any class that is only used for internal analysis,
        i.e. all complement classes that are not Ksub, Kgen, Kdat, Kakk, Kadv, Kprp, Kprd or Kvrb) from frame;
        also reduces maximum number of any complements of the same class to a specific count (currently hardcoded as 2),
        i.e. trims maximum number of complements of any class to 2
        :param working_analysis: the analysis to be cleaned
        :type working_analysis: object of class ValencyAnalysis
        :return: none, working_analysis is altered
        """
        list_to_keep = list(x for x in range(8))
        cnt_to_delete = 2
        logger.info("delete obsolete complements (i.e. keep only {keep}) from frame\n"
              "deleted all complements with count > {cnt}\n".format(keep=str(list_to_keep), cnt=cnt_to_delete))
        working_analysis.delete_complements_from_frame(list_to_keep)
        working_analysis.delete_multiple_complements_from_frame(cnt_to_delete)
