import core_logic.valency_analysis as VA
from core_logic.various_errors import KMeanError, ValencyAnalysisError, ValencyFrameError
import os
import argparse

import logging

logger = logging.getLogger('VRRCL')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_data():
    """
    retrieves data from several text files for the purpose of running an example valency analysis
    :return: raw data in specific format needed by class ValencyAnalysis
    """
    raw_data_list = list()
    try:
        for file in os.listdir("example_sentences"):
            file_object = open("example_sentences\\{fl}".format(fl=file), "r")
            sentence = ""
            sentence_id = 0
            word_ids = list()
            words = list()
            lemmata = list()
            tree = list()
            for line in file_object:
                if line.find(":") == -1:
                    continue
                raw_data = line.split(":")
                if raw_data[1].startswith(" "):
                    continue
                else:
                    raw_data[1] = raw_data[1][:-1]
                    if raw_data[0] == "sentence":
                        sentence = raw_data[1]
                    elif raw_data[0] == "sentence_id":
                        sentence_id = int(raw_data[1])
                    elif raw_data[0] == "word_ids":
                        word_ids.extend(list(int(x) for x in raw_data[1].split(";")))
                    elif raw_data[0] == "words":
                        words.extend((raw_data[1].split(";")))
                    elif raw_data[0] == "lemmata":
                        lemmata.extend(raw_data[1].split(";"))
                    elif raw_data[0] == "tree_data":
                        edge_list = raw_data[1].split(";")
                        for edge in edge_list:
                            string_list = list(x for x in edge.split(","))
                            out_vertex = int(string_list[0])
                            in_vertex = int(string_list[1])
                            label = string_list[2]
                            tree.append([out_vertex, in_vertex, label])
            raw_data_list.append([sentence_id, word_ids, words, tree, sentence, lemmata])
            file_object.close()
    except IOError as ioe:
        logger.warning(ioe)
    except IndexError as ie:
        logger.warning(ie)
    except BaseException as be:
        logger.warning(be)
    logger.info("Example sentences:")
    for raw_data_set in raw_data_list:
        logger.info("{sen}".format(sen=raw_data_set[4]))
    return raw_data_list


def analyse_examples(raw_data, args):
    """
    analysis of example sentences:
    1. correction of adverbial complements to prepositional complements
    2. deletion of complement classes for internal use
    3. deletion of any complement with count > 2
    4. deletion of all rare complement signatures
    output after steps 3 and 4
    :param raw_data: raw data for valency analysis in specific format needed by class ValencyAnalysis
    :type raw_data: list
    :return: no return value
    """
    new_analysis = VA.ValencyAnalysis(raw_data, args.verb)
    if args.main:
        new_analysis.initialize_valency_frame(main_prime=True)
    else:
        new_analysis.initialize_valency_frame(main_prime=False)
    if not args.no_kmone:
        try:
            new_analysis.correct_kadv_kprp(args.kmonecq, args.kmonemt, clusters_to_keep=args.kmoneck)
        except KMeanError as kme:
            logger.warning("Fehler beim 1. K-Mean-Aufruf")
            logger.warning(kme)
            return
        except ValencyAnalysisError as vae:
            logger.warning("Fehler beim 1. K-Mean-Aufruf")
            logger.warning(vae)
            return
        except ValencyFrameError as vfe:
            logger.warning("Fehler beim 1. K-Mean-Aufruf")
            logger.warning(vfe)
            return
        logger.debug("Postprocessing - Correction of Kadv to Kprp")
        logger.debug(new_analysis)
    try:
        new_analysis.delete_complements_from_frame([10, 11, 12, 13, 14, 15, 16, 100], keep=False)
    except ValencyAnalysisError as vae:
        logger.warning("Fehler beim löschen von Komplementsignaturen für internern Gebrauch")
        logger.warning(vae)
        return
    except ValencyFrameError as vfe:
        logger.warning("Fehler beim löschen von Komplementsignaturen für internern Gebrauch")
        logger.warning(vfe)
        return
    try:
        new_analysis.delete_multiple_complements_from_frame(2)
    except ValencyAnalysisError as vae:
        logger.warning(vae)
        logger.warning("Fehler beim löschen von Komplementen mit Anzahl >2")
        return
    except ValencyFrameError as vfe:
        logger.warning("Fehler beim löschen von Komplementen mit Anzahl >2")
        logger.warning(vfe)
        return
    logger.debug("Postprocessing - deletion of multiple complements and complements for internal use:")
    logger.debug(new_analysis)
    if not args.no_kmtwo:
        try:
            new_analysis.delete_rare_signatures_from_frame_by_k_mean(args.kmtwocq, args.kmtwomt, clusters_to_keep=args.kmtwock)
        except KMeanError as kme:
            logger.warning("Fehler beim 2. K-Mean-Aufruf")
            logger.warning(kme)
            return
        except ValencyAnalysisError as vae:
            logger.warning("Fehler beim 2. K-Mean-Aufruf")
            logger.warning(vae)
            return
        except ValencyFrameError as vfe:
            logger.warning("Fehler beim 2. K-Mean-Aufruf")
            logger.warning(vfe)
            return
        logger.debug("postprocessing - Deletion of all rare signatures via K-Means:")
    logger.info("~~~~~~~~~~~~~~Result of analysis~~~~~~~~~~~~~~")
    logger.info(new_analysis)


def initialize_argparser():
    """
    initializes argument parser for user input
    :return: args
    """
    argparser = argparse.ArgumentParser(description="Valancy Relationship Recognizer")
    argparser.add_argument("--verbose", help="detailed information on created sentences and all clustering attempts via k-means",
                           action="store_true")
    argparser.add_argument("--verb", help="specify verb for valency analysis", default="kämpfen", action="store",
                           dest="verb", type=str)
    argparser.add_argument("--kmone_cq", help="k-means cluster quantity for correction of kadv to kprp, default = 3",
                           action="store", dest="kmonecq", default="3", type=int)
    argparser.add_argument("--kmone_ck", help="number of clusters that should be kept during correction of kadv to kprp "
                            "via k-means, default = 1", action="store", dest="kmoneck", default="1", type=int)
    argparser.add_argument("--kmone_mt", help="number of maximum tries for correction of kadv to kprp via k-means, default = 10",
                           action="store", dest="kmonemt", default="10", type=int)
    argparser.add_argument("--no_kmone", help="no correction of Kadv to Kprp will be done", action="store_true")
    argparser.add_argument("--kmtwo_cq", help="k-means cluster quantity for deletion of rare complement sginatures, default = 4",
                           action="store", dest="kmtwocq", default="4", type=int)
    argparser.add_argument("--kmtwo_mt", help="number of maximum tries for deletion of rare complemet signatures via k-means, default = 10",
                           action="store", dest="kmtwomt", default="10", type=int)
    argparser.add_argument("--kmtwo_ck", help="number of clusters that should be kept during deletion of rare complement class "
                            "signatures, default = 3", action="store", dest="kmtwock", default="3", type=int)
    argparser.add_argument("--no_kmtwo", help="no further postprocessing will be done after deletion of "
                                "multiple complements", action="store_true")
    argparser.add_argument("--main", help="use only main sentences for valency frame analysis", action="store_true")
    args = argparser.parse_args()
    return args

def main():
    """
    main function, initializes argument parser, retrieves data from directory example_sentences and analyses valency
    frame of these sentences for specified verb (default for given example sentences: "kämpfen")
    :return: no return value
    """
    args = initialize_argparser()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    raw_data = load_data()
    analyse_examples(raw_data, args)


if __name__ == '__main__':
    main()

