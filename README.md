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


Requirements and Installation
-----------------------------
This software was created for and tested with Python 3.7. No further modules are required. However, the input for this program needs to be preprocessed with the ParZu dependency tree parser. 


Example Use
-----------
The directory example_sentences includes 27 sample files with one sentence each. The files also include the preprocessed data required for each sentence, i.e. the tokens and lemmata for each sentence as well as the dependency tree. You can execute the file example_analysis.py to get a simple console output for these examples:

First, a list of all sentences used for this analysis is given. Then, the Initial analysis without postprocessing is shown. Lastly, the final result of the analysis is written to the console. This final result includes three different pruning steps: 1. Removal of all complement classes for internal use. 2. Removal of all complement classes with a count greater than two. 3. Removal of all rare complement class patterns.   

You can also get detailed information on the analysis by using the option --verbose. This option gives more specific information regarding the sentences used for the analysis as well as the state of the analysis at various points. This option also includes an overview of the results of the K-Means algorithm.

If you want to use your own example sentences, you can use the option --verb to specify the verb that you want to use for the valency analysis. The default verb for the given example sentences is "kämpfen". All sentences will still be taken from the directory example_sentences and need the same format as the example sentences given in this repository.

Note that the actual program allows for the specification of various parameters, especially for the K-Means algorithm (e.g. the number of clusters that should be created or the number of clusters that should be deleted). The parameters used in this example were the best parameters according to the evaluation of the group project that the original program was created for. For various verbs, these parameters might need adjustment. For further information, see the documentation.     

Theoretical background
----------------------
Each verb in the German language requires complementary phrases providing necessary information for a sentence to make sense and to be grammatically correct. The number and type of these complements depend on the specific verb and the meaning of this verb in a given sentence. Complements belong to one of several categories (nominative, genitive, dative, accusative, adverbial, prepositional, predicative and verbativ). Phrases in a sentence can be a complement for the verb of this sentence or additional information not necessarily needed for the sentence to make sense. The number and type of complements determine the valency frame of a verb.

Dependency trees show the dependencies of each word in a sentence. A determiner, for example, is dependent on a noun as it cannot occur in a sentence without a noun it belongs to. Similarly, phrases in a sentence depend on other phrases or on single words. Ultimately, every phrase depends on the verb in the sentence.

Not every phrase in a dependency tree is an actual complement in the valency frame. Furthermore, dependency trees only contain limited information regarding the type of some complements. Therefore, this program uses the frequency of specific words and the frequency of all complement patterns in the given sentences to try and determine the actual valency frame of a verb. These frequencies are determined via an implementation of the algorithm K-Means. 

Contact
-------
For questions or feedback, please write to friese.t@yahoo.com.