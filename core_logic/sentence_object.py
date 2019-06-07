from core_logic.various_errors import ConnectorError
from core_logic.various_errors import IncorrectInstantiationError, IncorrectTreeError
from core_logic.sentence_to_analysis_connector import SentenceAnalysisConnector as SenAnCon

import logging

logger = logging.getLogger('VRRCL')


class SentenceObject:
    """
    Representing a single sentence (ideally) with a complete, correct dependency tree, and an analysis of this
    dependency tree
    """
    def __init__(self, s_id, sentence, raw_w_ids, raw_words, dep_tree, lemma_list):
        """
        check data for incorrect or empty entries, set initial data as raw data, set dict{wid: word} for every word in
        sentence
        :raises various IncorrectInstantiationErrors if incorrect data-sets were netered
        :param s_id, sentence, raw_w_ids, raw_words, dep_tree: raw data from database
        """
        if s_id.__class__() != 0:
            raise IncorrectInstantiationError(0)
        elif s_id <= 0:
            raise IncorrectInstantiationError(1)
        elif (raw_w_ids is None) | (len(raw_w_ids) == 0) | (raw_w_ids.__class__() != []):
            raise IncorrectInstantiationError(2)
        elif (dep_tree is None) | (len(dep_tree) == 0) | (dep_tree.__class__() != []):
            raise IncorrectInstantiationError(3)
        else:
            for edge in dep_tree:
                if (edge[0] is None) | (edge[1] is None) | (edge[2] is None):
                    raise IncorrectInstantiationError(4)
                elif (not edge[0].__class__() == 0) | (not edge[1].__class__() == 0) | (not edge[2].isalpha()):
                    raise IncorrectInstantiationError(4)
                elif (edge[0] <= 0) | (edge[1] <= 0) | (len(edge[2]) == 0):
                    raise IncorrectInstantiationError(4)
        for lemma in lemma_list:
            if lemma.__class__ is not str:
                raise IncorrectInstantiationError(6)
        self.sentence_id = s_id
        self.sentence = sentence
        self.w_ids = raw_w_ids
        self.words = raw_words
        self.raw_dep_tree = dep_tree
        self.id_to_word_mapping = self.get_id_to_word_mapping()
        self.lemma_list = lemma_list
        self.sentence_analysis_connector = None

    def __str__(self):
        return "S-ID: {sid} - Sentence: {sen}\nSentence Analysis:{senanl}\n".format(sid=self.sentence_id,
                                            sen=self.sentence, senanl=self.sentence_analysis_connector)

    def analyze_dependence_tree(self, word_id_to_lemmata, verb):
        """
        initiates creation of tree, creates object of class SentenceAnalysisConnector which is ultimately used for
        access to dependency analysis, initializes dependency analysis if no errors are encountered during creation of
        dependency tree
        :raises IncorrectTreeError if dependency tree could not be created correctly
        :param word_id_to_lemmata: word ids of a sentence as keys and lemma of each word (given by table types in
        database) as value, used to append valence holder lemma by prepositions
        :type word_id_to_lemmata: Dictionary
        :param verb: verb used for lookup in the database, needed to determine primary analyses
        :type verb: String
        :return: none, alters self.sentence_analysis_connector or raises exception
        """
        try:
            new_connector = SenAnCon(self.words, self.raw_dep_tree)
            self.sentence_analysis_connector = new_connector
            self.sentence_analysis_connector.initial_dependency_analysis()
            for analysis in self.get_full_sentence_analysis_list():
                valence_holder = analysis.get_valence_holder()
                new_lemma = str(word_id_to_lemmata[valence_holder])
                new_avz_words = list()
                for word in analysis.get_avz_words():
                    new_lemma = str(word_id_to_lemmata[word]) + new_lemma
                    new_avz_words.append(str(word_id_to_lemmata[word]))
                analysis.set_valence_holder_lemma(new_lemma)
                analysis.set_avz_words(new_avz_words)
                if new_lemma == verb:
                    analysis.set_primary_analysis(True)
        except IncorrectTreeError as error:
            self.sentence_analysis_connector = None
            raise error

    def get_sentence_id(self):
        """
        :return: integer that is sentence_id of this sentence in database
        """
        return self.sentence_id

    def get_sentence(self):
        """
        :return: string that is sentence found in database
        """
        return self.sentence

    def get_w_ids(self):
        """
        :return: list of word_ids for this sentence from database
        (in order of words received from database, consistent with order of self.words)
        """
        return self.w_ids

    def get_words(self):
        """
        :return: list of words for this sentence from database
        (in order of words received from database, consistent with order of self.w_ids)
        """
        return self.words

    def get_raw_dep_tree(self):
        """
        :return: raw dependency tree as list of lists (i.e. list of edges of the dependency tree)
        """
        return self.raw_dep_tree

    def get_dep_tree(self):
        """
        :raises IncorrectTreeError if dependency tree could not be created correctly
        :return:
        """
        try:
            dep_tree = self.sentence_analysis_connector.get_complete_dependency_tree()
        except IncorrectTreeError as inctrerr:
            logger.debug("Fehler beim Baumaufruf: {ite}\n".format(ite=inctrerr))
        else:
            return dep_tree

    def has_valid_analysis(self):
        """
        used to check if dependency analysis of sentence could be created correctly
        :return: True, if sentence object has valid dependency analysis, False otherwise
        """
        return self.sentence_analysis_connector.is_valid_analysis()

    def get_id_to_word_mapping(self):
        """
        intended whenever a word_id (usually received from a dependency analysis or dependency tree) needs to be
        converted to the actual word in the sentence
        :return: dict with {w_id: word} for every word_id, word in self.word_ids, self.words
        """
        ids_and_words = zip(self.w_ids, self.words)
        id_to_word_mapping = dict()
        for word_id, word in ids_and_words:
            id_to_word_mapping[word_id] = word
        return id_to_word_mapping

    def create_id_to_lemma_mapping(self):
        """
        :return: dict with {w_id: lemma} for every word_id, lemma in self.word_ids, self.lemma_list
        """
        ids_and_lemmas = zip(self.w_ids, self.lemma_list)
        id_to_lemma_mapping = dict()
        for w_id, lemma in ids_and_lemmas:
            id_to_lemma_mapping[w_id] = lemma
        return id_to_lemma_mapping

    def id_to_word(self, word_id):
        """
        :param word_id: word_id for which to return word in self.sentence
        :type word_id: Integer
        :return: word (as string) with given word_id in self.sentence, returns None if word_id is not in self.sentence
        """
        try:
            return self.id_to_word_mapping[word_id]
        except KeyError as err:
            logger.debug("Key not found: " + str(err))
            return None

    def get_full_sentence_analysis_list(self):
        """
        returns all analyses in given sentence
        :return: list() of objects of class DependencyAnalysis (or subclass) or empty list()
        """
        try:
            return self.sentence_analysis_connector.get_full_analysis_list()
        except ConnectorError:
            return list()

    def get_all_primary_analysis(self):
        """
        raises ConnectorError
        :return: a list() of objects of class DependencyAnalysis (or subclass) that are primary analyses (i.e. analyses that use the
        verb used for lookup in the database), or empty list() if no such analyses were found, or exception
        """
        try:
            analysis_ist = self.get_full_sentence_analysis_list()
        except ConnectorError as conerr:
            raise conerr
        else:
            primary_analysis_list = list()
            for analysis in analysis_ist:
                if analysis.is_primary_analysis():
                    primary_analysis_list.append(analysis)
            return primary_analysis_list

    def get_main_sentence_dependency_analysis(self):
        """
        raises ConnectorError
        :return: main dependency analysis (i.e. dependency analysis of main sentence) as object of class
        DependencyAnalysis, or exception
        """
        try:
            return self.sentence_analysis_connector.get_main_dependency_analysis()
        except ConnectorError as conerr:
            raise conerr

    @staticmethod
    def get_w_id_to_word_mapping_as_mapping_on_sid(sentences):
        """
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: a dict() with sentence ids as keys and dict() as values, new dict() uses word id as key and word as
        value
        """
        new_mapping = dict()
        for sentence in sentences:
            new_mapping[sentence.get_sentence_id()] = sentence.get_id_to_word_mapping().copy()
        return new_mapping

    @staticmethod
    def get_w_id_to_lemma_mapping_as_mapping_on_sid(sentences):
        """
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: a dict() with sentence ids as keys and dict() as values, new dict() uses word id as key and word lemma
        as value
        """
        new_mapping = dict()
        for sentence in sentences:
            new_mapping[sentence.get_sentence_id()] = sentence.create_id_to_lemma_mapping().copy()
        return new_mapping

    @staticmethod
    def get_only_sentences_w_main_primary_analysis(sentences):
        """
        catches ConnectorErrors to get only those sentence analyses that have a valid connector (i.e. analysis)
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: list() of objects of class SentenceObject whose main sentence analysis is a primary analysis (i.e. main
        sentence contains word that was looked up in the database)
        """
        new_sentences = list()
        for sentence in sentences:
            try:
                main_sentence_analysis = sentence.get_main_sentence_dependency_analysis()
            except ConnectorError:
                continue
            else:
                if main_sentence_analysis.is_primary_analysis():
                    new_sentences.append(sentence)
        return new_sentences

    @staticmethod
    def get_mapping_sid_to_main_sentence_analysis(sentences):
        """
        catches ConnectorErrors to map only those sentence analyses that have a valid connector (i.e. analysis)
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: dict() with sentence ids of given sentences (with valid analysis) as keys and list() with main
        dependency analysis as only element (i.e. analysis of main sentence) as value
        """
        new_mapping = dict()
        for sentence in sentences:
            try:
                new_analysis = sentence.get_main_sentence_dependency_analysis()
            except ConnectorError:
                continue
            else:
                new_mapping[sentence.get_sentence_id()] = [new_analysis]
        return new_mapping

    @staticmethod
    def get_only_sentences_w_primary_analysis(sentences):
        """
        catches ConnectorErrors to get only those sentence analyses that have a valid connector (i.e. analysis)
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: list() of those sentences from given sentences that have at least one primary analysis or empty list if
        none were found
        """
        sentence_list = list()
        for sentence in sentences:
            try:
                primary_analyses = sentence.get_all_primary_analysis()
            except ConnectorError:
                continue
            else:
                if len(primary_analyses) > 0:
                    sentence_list.append(sentence)
        return sentence_list

    @staticmethod
    def get_mapping_sen_id_to_primary_analysis_list(sentences):
        """
        catches ConnectorErrors to map only those sentence analyses that have a valid connector (i.e. analysis),
        intended for use with list of sentences that each have at least one primary analysis
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: dict() with sentence ids as key and list of analyses that are primary analyses for this sentence id as
        values or empty dict() if no sentences were given
        """
        new_analysis_mapping = dict()
        for sentence in sentences:
            try:
                primary_analyses = sentence.get_all_primary_analysis()
            except ConnectorError:
                continue
            else:
                new_analysis_list = list()
                for analysis in primary_analyses:
                    new_analysis = analysis.simple_deep_copy_analysis()
                    new_analysis_list.append(new_analysis)
                new_analysis_mapping[sentence.get_sentence_id()] = new_analysis_list
        return new_analysis_mapping

    @staticmethod
    def get_sentences_with_valid_analysis(sentences):
        """
        :param sentences: objects of class SentenceObject
        :type sentences: List
        :return: list() of all sentences of given sentences that have a valid dependency analysis (indicated by validity
        of connector) or empty list if no such sentences were found
        """
        new_sentence_list = list()
        for sentence in sentences:
            if sentence.has_valid_analysis():
                new_sentence_list.append(sentence)
        return new_sentence_list

