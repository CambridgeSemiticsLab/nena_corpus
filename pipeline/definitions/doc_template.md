# NENA Text-Fabric Corpus

The NENA Text-Fabric (TF) corpus contains textual transcriptions and linguistic annotations 
from the research group under Geoffrey Khan at the University of Cambridge.

## Contents

* [Data Model](#Data-Model)
* [Node Types](#Node-Types)
* [Features](#Features)

## Data Model

For a full description of the Text-Fabric data model, 
see the [datamodel documentation](https://annotation.github.io/text-fabric/tf/about/datamodel.html).

One can think about the NENA Text-Fabric resource in two ways. 
The first is as a **conceptual** model, and the second is as a literal **implementation**. 
The conceptual model is simply a way of thinking about the text and all its various parts (words, sentences, letters, etc.). 
The literal implementation is the way that conceptual model is actually stored on a computer. 

The **conceptual** model of the TF NENA corpus is a graph. 
A [graph](https://en.wikipedia.org/wiki/Graph_theory) is a method of indicating relationships between entities. 
The entities in a graph are called "nodes", often illustrated visually as circles. 
Their relationships to one another are called "edges", illustrated with lines drawn between two or more circles. 

In the case of a [text graph](https://www.balisage.net/Proceedings/vol19/html/Dekker01/BalisageVol19-Dekker01.html), 
entities like letters, words, sentences are modeled as nodes. These entities also have relationships. 
A key relationship in Text-Fabric is "containment": a sentence contains a word, a word contains a letter. 
Other, optional relationships might be syntactic relations or discourse relations between sentences. 
With the exception of "containment", the graph model of Text-Fabric does not "care" which other relationships are modeled 
(syntax, discourse, etc.). The user(s) are free to choose whatever relationships they are interested in.

In addition to relations between nodes, the TF graph allows for features to be associated with various nodes. 
For example, a word node can have an an associated feature such as "lexeme" or "parsing"; even different
kinds of transcription formats can be defined as features of words.

In this document, the various nodes and their features are described in depth. 

<hr>

