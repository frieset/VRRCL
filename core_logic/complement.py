from core_logic.node import Node

import logging

logger = logging.getLogger('VRRCL')


class Complement:
    """
    Complement (phrase) of a verb in a sentence;
    note that results obtained with complement specification via preposition (see split_complement_coding) is not
    evaluated due to lack of available signature equivalents from EValbu
    """
    def __init__(self, complement_root, comp_class):
        """
        note that complement_class should always be an integer either
        - in range of 0-7, 10-16 and 100 for simple dependency analysis or
        - be a six digit integer consisting of a coding for a specific preposition as the first three digits and the
        regular coding in range of 000-007, 010-016 or 100 as the last three digits;
        static methods used for accessing a complement class (i.e. for interpreting the coding as a readable string)
        and checking its validity
        :param complement_root: used to analyze given complement in original tree structure if necessary
        :type complement_root: Node
        :param comp_class: coding for complement class, see static method comp_class_coding
        :type comp_class: Integer
        """
        self.complement_as_tree = complement_root
        self.root_word_id = self.complement_as_tree.get_node()
        self.root_label = self.complement_as_tree.get_label()
        self.complement_class = comp_class

    def __str__(self):
        string = "complement class: {cmpcls}    ".format(cmpcls=Complement.comp_class_def(self.complement_class))
        id_and_label_list = self.get_word_ids_and_labels_in_order()
        for pair in id_and_label_list:
            string += "word-id: {wid} - label: {lbl} | ".format(wid=str(pair[0]), lbl=str(pair[1]))
        if len(id_and_label_list) > 0:
            string = string[:-2]
        string += "\n"
        return string

    def get_root_label(self):
        """
        :return: string that is label for root of this complement
        """
        return self.root_label

    def get_complement_class(self):
        """
        :return: returns integer that represents class of this complement (may be complement classes only used for
        internal analysis, not for output)
        """
        return self.complement_class

    def get_root_w_id(self):
        """
        :return: word id (as int) of root of this complement
        """
        return self.root_word_id

    def get_word_ids_in_order(self):
        """
        :return: list of all word ids in this complement, sorted in ascending order
        """
        node_list = Node.recursive_tree_to_list_conversion(self.complement_as_tree)
        new_node_list = list()
        for node in node_list:
            new_node_list.append([node.get_node()])
        new_node_list.sort()
        return new_node_list

    def get_word_ids_and_labels_in_order(self):
        """
        :return: list() of lists(), each element in outer list contains word ids at position [0] and labels at position [1]
        for each word in this complement, list is sorted in ascending order by word ids
        """
        node_list = Node.recursive_tree_to_list_conversion(self.complement_as_tree)
        new_node_list = list()
        for node in node_list:
            new_node_list.append([node.get_node(), node.get_label()])
        new_node_list.sort(key=lambda x: x[0])
        return new_node_list

    def set_complement_class(self, new_class):
        """
        :raises ValueError if given complement class is not a valid complement class
        :param new_class: new complement class as int
        :type new_class: String
        :return: none, alters self.complement_class
        """
        if not Complement.is_valid_comp_class(new_class):
            raise ValueError
        else:
            self.complement_class = new_class

    @staticmethod
    def specify_initial_complement_classes(label):
        """
        used during initialisation of dependency analysis
        :param label: a label to convert to a complement-class-coding
        :type label: String
        :return: integer in range 0-7 for complement classes intended for output, 10-16 intended for internal with sub
        sentences and 100 intended for indicating a complement that cannot be further specified
        """
        if label in ('subj', 'subjc'):
            return 0
        elif label == 'objg':
            return 1
        elif label == 'objd':
            return 2
        elif label in ('obja', 'obja2'):
            return 3
        elif label == 'objp':
            return 4
        elif label == 'pp':
            return 5
        elif label == 'pred':
            return 6
        elif label == 'obji':
            return 7
        elif label in ('kon', 'cj'):
            return 10
        elif label == 'konj':
            return 11
        elif label == 'neb':
            return 12
        elif label == 'objc':
            return 13
        elif label == 'rel':
            return 14
        elif label == 's':
            return 15
        elif label == 'subjc':
            return 16
        return 100

    @staticmethod
    def sort_complement_list(complement_list):
        """
        sorts list of given complements by coding of complement class, returns copy of list() (not of objects of
        class Complements, Node or the like)
        :param complement_list: list of complements to sort
        :type complement_list: List
        :return: copy of list(), sorted by complement class coding
        """
        new_complement_list = complement_list.copy()
        new_complement_list.sort(key=lambda x: x.complement_class)
        return new_complement_list

    @staticmethod
    def comp_class_def(comp_class):
        """
        used to convert a given complement class to a string (e.g. complement class 0 to Ksubj);
        checks validity of given complement class
        :param comp_class: coding for a complement class
        :type comp_class: integer
        :return: a string, possibly an empty string if no valid complement class was given
        """
        comp_class_def = Complement.comp_class_coding()
        if comp_class.__class__ is not int:
            logger.debug("Error in class Complement: param comp_class is not int")
            return ""
        elif not Complement.is_valid_comp_class(comp_class):
            logger.debug("Error in class Complement: no valid complement class coding given")
            return ""
        split_complement = Complement.split_complement_coding(comp_class)
        comp_class = split_complement[0]
        preposition = split_complement[1]
        if preposition == -1:
            return comp_class_def[comp_class]
        else:
            new_string = comp_class_def[comp_class] + "|" + comp_class_def[preposition]
            return new_string

    @staticmethod
    def split_complement_coding(comp_class):
        """
        used to test a complement class coding for its lengths and split it in separate codings for preposition and
        actual complement class;
        :param comp_class: complement class to be splitted
        :type comp_class: integer
        :return: a list with an integer as coding for actual complement class at position [0] and a coding for the
        specified preposition (or -1 if no preposition was given) at position [1]
        """
        comp_class_as_str = str(comp_class)
        if len(comp_class_as_str) > 3:
            preposition = int(comp_class_as_str[:3]) * 1000
            comp_class = int(comp_class_as_str[3:])
        else:
            preposition = -1
        return [comp_class, preposition]

    @staticmethod
    def is_valid_comp_class(comp_class):
        """
        used to check if given integer is a valid coding for a complement class
        :param comp_class: integer to be checked
        :type comp_class: integer
        :return: True if this integer is a valid coding for a complement class used for output or during analysis of
        valency frame, False otherwise
        """
        comp_class_def = Complement.comp_class_coding()
        split_complement = Complement.split_complement_coding(comp_class)
        comp_class = split_complement[0]
        preposition = split_complement[1]
        if comp_class not in comp_class_def.keys():
            return False
        elif (preposition != -1) & (preposition not in comp_class_def.keys()):
            return False
        else:
            return True

    @staticmethod
    def comp_class_coding():
        """
        used to decode an integer to a string either indicating a complement class, an internal representation of
        a specific type of phrase or a more complex coding of a complement class combined with a coding of a preposition
        (combination only intended for use with complements of class 4 or 5)
        :return: returns a dictionary with integers (in range 0-7, 10-16, 100, and specific six digit values) as keys
        and strings as values for each key
        """
        comp_class_def = {
            0: 'Ksubj',
            1: 'Kgen',
            2: 'Kdat',
            3: 'Kakk',
            4: 'Kprp',
            5: 'Kadv',
            6: 'Kprd',
            7: 'Kvrb',
            10: 'SKkon/cj',
            11: 'SKkonj',
            12: 'SKneb',
            13: 'SKobjc',
            14: 'SKrel',
            15: 'SKs',
            16: 'SKsubjc',
            100: 'NA',
            110000: 'à',
            111000: 'ab',
            112000: 'abseits',
            113000: 'abzüglich',
            114000: 'an',
            115000: 'angesichts',
            116000: 'anhand',
            117000: 'anlässlich',
            118000: 'anstatt',
            119000: 'anstelle',
            120000: 'auf',
            121000: 'aufgrund',
            122000: 'aus',
            123000: 'ausgenommen',
            124000: 'ausschließlich',
            125000: 'außer',
            126000: 'außerhalb',
            127000: 'bar',
            128000: 'bei',
            129000: 'betreffend',
            130000: 'betreffs',
            131000: 'bezüglich',
            132000: 'binnen',
            133000: 'bis',
            134000: 'dank',
            135000: 'diesseits',
            136000: 'durch',
            137000: 'einbegriffen',
            138000: 'eingedenk',
            139000: 'einschließlich',
            140000: 'entgegen',
            141000: 'entlang',
            142000: 'entsprechend',
            143000: 'exklusive',
            144000: 'fern',
            145000: 'fernab',
            146000: 'für',
            147000: 'gegen',
            148000: 'gegenüber',
            149000: 'gemäß',
            150000: 'gleich',
            151000: 'halber',
            152000: 'hinsichtlich',
            153000: 'hinsichts',
            154000: 'hinter',
            155000: 'in',
            156000: 'inbegriffen',
            157000: 'infolge',
            158000: 'inklusive',
            159000: 'inmitten',
            160000: 'innerhalb',
            161000: 'je',
            162000: 'jenseits',
            163000: 'kontra',
            164000: 'kraft',
            165000: 'längs',
            166000: 'längsseits',
            167000: 'laut',
            168000: 'links',
            169000: 'mangels',
            170000: 'mit',
            171000: 'mitsamt',
            172000: 'mittels',
            173000: 'nach',
            174000: 'nächst',
            175000: 'nahe',
            176000: 'neben',
            177000: 'nebst',
            178000: 'ob',
            179000: 'oberhalb',
            180000: 'ohne',
            181000: 'per',
            182000: 'pro',
            183000: 'qua',
            184000: 'rechts',
            185000: 'samt',
            186000: 'seit',
            187000: 'seitens',
            188000: 'seitwärts',
            189000: 'statt',
            190000: 'trotz',
            191000: 'über',
            192000: 'um',
            193000: 'unbeschadet',
            194000: 'unfern',
            195000: 'ungeachtet',
            196000: 'unter',
            197000: 'unterhalb',
            198000: 'unweit',
            199000: 'vermittels',
            200000: 'vermöge',
            201000: 'via',
            202000: 'von',
            203000: 'vor',
            204000: 'vorbehaltlich',
            205000: 'während',
            206000: 'wegen',
            207000: 'wider',
            208000: 'zeit',
            209000: 'zu',
            210000: 'zufolge',
            211000: 'zugunsten',
            212000: 'zuliebe',
            213000: 'zuwider',
            214000: 'zuzüglich',
            215000: 'zwecks',
            216000: 'zwischen'}
        return comp_class_def
