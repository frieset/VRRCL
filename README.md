ValencyRelationshipRecognizerCoreLogic
======================================

About
-----
This program was created as a practical exercise in the module "Textmining" at the university of Leipzig in the time of October 2018 to March 2019. The goal of this exercise was the automated analysis of valency frames using dependency trees. For a short introduction to the theoretical background, see below.    

The complete program was created as a group project and included the files in the directory core_logic, an ORM to a database for easy sentence acquisition and an evaluation module. The core logic of this program (i.e. all files in the directory core_logic) were created by T. Friese. The ORM and the evaluation module were created by other students.

This repository includes only a part of the complete program, namely the core logic of the ValencyRelationshipRecognizer. To get a first view of what this program does, a small example for the word "kämpfen" is included. For this, 27 example sentences are used for a valency analysis.

The dependency trees for this program, the tokens and the lemmata were created using the ParZu dependency tree parser of the university of Zurich. For further information on ParZu, visit https://github.com/rsennrich/ParZu.

The theoretical information regarding valency frames were aquired from the institue of German language in Mannheim (Institut für deutsche Sprache Mannheim) via their grammis information system. For further information, visit https://grammis.ids-mannheim.de/.


License
-------
This software is licensed under the GNU General Public license. See LICENSE for further information. 


Requirements
------------
This software was created for and tested with Python 3.7. No further modules are required. However, the input for this program needs to be preprocessed with the ParZu dependency tree parser. 


Input Format
------------
Each file in the directory example_sentences requires the following keywords: sentence, sentence_id, word_ids, words, lemmata and tree_data. Each keyword needs to be followed by a ":" and the respective data without a space anywhere in the line (except in the actual sentence, of course). The entries in the lines with the keywords word_id, words, lemmata and tree_data should be separated by a ";". Further lines can be added for your own customisation but should not contain a ":" or if they contain a ":" it should be immediately followed by whitespace.
1. sentence: The actual sentence to be used for the analysis. 
2. sentence_id: A sentence id to keep track of which sentences have which complement class pattern.
3. word_ids: An integer as representation for every word in the sentence. These do not need to be consecutive (as in the given examples) but they need to correspond to the tree_data below and be in the order that the corresponding words have in the sentence.
4. words: Pre-Tokenized words for this sentence in the order they occur in the sentence.
5. lemmata: The lemma for each word in the sentence in the order they occur in the sentence.
6. tree_data: A representation of the dependency tree. Each edge of the tree should be contained in this line in the format "vertex1,vertex2,label". Edges do not need to be in a particular order.


Example Use
-----------
The directory example_sentences includes 27 sample files with one sentence each. The files also include the preprocessed data required for each sentence, i.e. the tokens and lemmata for each sentence as well as the dependency tree. You can execute the file example_analysis.py to get a simple console output for these examples:

First, a list of all sentences used for this analysis is given. Then, the initial analysis without postprocessing is shown. Lastly, you can see the result of the valency analysis.

The analysis can be broken down into 3 main steps:

1. As prepositional complements are in most cases not identified correctly by the dependency tree, the program searches for the most common prepositions and changes their complement class to Kprp (prepositional complement). 
2. Complement classes only used internally are removed and the number of every complement class is reduced to a maximum of 2.
3. The most common complement class signatures of all sentences are selected.

Steps 1 and 3 include a clustering of some objects (prepositions in step 1, complement class signatures in step 3) and the removal of the "worst" clusters, i.e. the clusters with the least common prepositions or signatures. The parameters used for these clustering attempts can be changed via the arguments the program receives. Use the help option for further information. The parameters used in this example were the best parameters according to the evaluation of the group project that the original program was created for. For various verbs, these parameters might need adjustment to yield the best possible results.  

If you want to use your own example sentences, you can use the option --verb to specify the verb that you want to use for the valency analysis. The default verb for the given example sentences is "kämpfen". All sentences will still be taken from the directory example_sentences and need the same format as the example sentences given in this repository.

You can specify that only the main sentences containing the given verb should by analysed via the option "--main".

For more detailed information on the dependency trees or the clustering attempts, use the option "--verbose".


Theoretical background
----------------------
Each verb in the German language requires complementary phrases providing necessary information for a sentence to make sense and to be grammatically correct. The number and type of these complements depend on the specific verb and the meaning of this verb in a given sentence. Complements belong to one of several categories (nominative, genitive, dative, accusative, adverbial, prepositional, predicative and verbativ). Phrases in a sentence can be a complement for the verb of this sentence or additional information not necessarily needed for the sentence to make sense. The number and type of complements determine the valency frame of a verb.

Dependency trees show the dependencies of each word in a sentence. A determiner, for example, is dependent on a noun as it cannot occur in a sentence without a noun it belongs to. Similarly, phrases in a sentence depend on other phrases or on single words. Ultimately, every phrase depends on the verb in the sentence.

Not every phrase in a dependency tree is an actual complement in the valency frame. Furthermore, dependency trees only contain limited information regarding the type of some complements. Therefore, this program uses the frequency of specific words and the frequency of all complement patterns in the given sentences to try and determine the actual valency frame of a verb. These frequencies are determined via an implementation of the algorithm K-Means.

The program gives the following codes for each complement class in the console output:
- Ksub = nominative complement
- Kgen = genetive complement
- Kdat = dative complement
- Kakk = accusative complement
- Kadv = adverbial complement
- Kprp = prepositional complement
- Kprd = predicative complement
- Kvrb = verbativ complement


Contact
-------
For questions or feedback, please write to friese.t@yahoo.com.