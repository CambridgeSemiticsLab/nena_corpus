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

# Node Types

| node type   | description                                                                                                              |   frequency | features                                                                                                                                                                                                                                                                                          |
|:------------|:-------------------------------------------------------------------------------------------------------------------------|------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dialect     | dialect of North Eastern Neo-Aramaic                                                                                     |           3 | [dialect](#dialect)                                                                                                                                                                                                                                                                               |
| text        | transcribed story from a native NENA informant                                                                           |         127 | [speakers](#speakers), [dialect](#dialect), [place](#place), [text_id](#text_id), [title](#title)                                                                                                                                                                                                 |
| paragraph   | paragraph segment based on newlines                                                                                      |         351 |                                                                                                                                                                                                                                                                                                   |
| line        | verse-like section used for reference; corresponds with publications where applicable                                    |        2587 | [line_number](#line_number)                                                                                                                                                                                                                                                                       |
| sentence    | sentence based on one or more of the following punctuators [.!?]                                                         |       16369 |                                                                                                                                                                                                                                                                                                   |
| subsentence | part of sentence based on one of the following punctuators: [;,—:]                                                       |       24617 |                                                                                                                                                                                                                                                                                                   |
| inton       | intonation group of words/letters based on ˈ symbol (superscript |), which marks such boundaries                         |       36594 |                                                                                                                                                                                                                                                                                                   |
| stress      | stress group of words, marked either by hyphenated segments or standalone words; e.g. 'xa-ga' is 2 words, 1 stress group |       94101 |                                                                                                                                                                                                                                                                                                   |
| word        | word in NENA or other language segmented by either whitespace or one of [-=]                                             |      120598 | [fuzzy_end](#fuzzy_end), [full](#full), [text_end](#text_end), [lite_end](#lite_end), [text](#text), [text_nostress](#text_nostress), [full_end](#full_end), [timestamp](#timestamp), [lite](#lite), [lang](#lang), [fuzzy](#fuzzy), [speaker](#speaker), [text_nostress_end](#text_nostress_end) |
| letter      | an individual letter including diacritics recognized by pattern matches against canonical NENA alphabet                  |      541384 | [full](#full), [phonetic_manner](#phonetic_manner), [phonetic_place](#phonetic_place), [phonation](#phonation), [text](#text), [text_nostress](#text_nostress), [lite](#lite), [fuzzy](#fuzzy), [phonetic_class](#phonetic_class)                                                                 |

# Features

## dialect

name of a dialect in North Eastern Neo-Aramaic

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| dialect     |           3 |
| text        |         127 |

**Values**
| dialect   |   frequency |
|:----------|------------:|
| urmi_c    |          75 |
| barwar    |          53 |
| alquosh   |           2 |

[back to node types](#Node-Types)
<hr>

## title

title of a text (story)

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| text        |         127 |

**Values**
| title                                         | dialect   |
|:----------------------------------------------|:----------|
| Bread and cheese                              | alquosh   |
| A Hundred Gold Coins                          | barwar    |
| A Man Called Čuxo                             | barwar    |
| A Tale of Two Kings                           | barwar    |
| A Tale of a Prince and a Princess             | barwar    |
| Baby Leliθa                                   | barwar    |
| Dəmdəma                                       | barwar    |
| Gozali and Nozali                             | barwar    |
| I Am Worth the Same as a Blind Wolf           | barwar    |
| Man Is Treacherous                            | barwar    |
| Measure for Measure                           | barwar    |
| Nanno and Jəndo                               | barwar    |
| Qaṭina Rescues His Nephew From Leliθa         | barwar    |
| Sour Grapes                                   | barwar    |
| Šošət Xere                                    | barwar    |
| Tales From the 1001 Nights                    | barwar    |
| The Battle With Yuwanəs the Armenian          | barwar    |
| The Bear and the Fox                          | barwar    |
| The Brother of Giants                         | barwar    |
| The Cat and the Mice                          | barwar    |
| The Cooking Pot                               | barwar    |
| The Crafty Hireling                           | barwar    |
| The Crow and the Cheese                       | barwar    |
| The Daughter of the King                      | barwar    |
| The Fox and the Lion                          | barwar    |
| The Fox and the Miller                        | barwar    |
| The Fox and the Stork                         | barwar    |
| The Giant’s Cave                              | barwar    |
| The Girl and the Seven Brothers               | barwar    |
| The King With Forty Sons                      | barwar    |
| The Leliθa From č̭āl                           | barwar    |
| The Lion King                                 | barwar    |
| The Lion With a Swollen Leg                   | barwar    |
| The Man Who Cried Wolf                        | barwar    |
| The Man Who Wanted to Work                    | barwar    |
| The Monk Who Wanted to Know When He Would Die | barwar    |
| The Monk and the Angel                        | barwar    |
| The Priest and the Mullah                     | barwar    |
| The Sale of an Ox                             | barwar    |
| The Scorpion and the Snake                    | barwar    |
| The Selfish Neighbour                         | barwar    |
| The Sisisambər Plant                          | barwar    |
| The Story With No End                         | barwar    |
| The Tale of Farxo and Səttiya                 | barwar    |
| The Tale of Mămo and Zine                     | barwar    |
| The Tale of Mərza Pămət                       | barwar    |
| The Tale of Nasimo                            | barwar    |
| The Tale of Parizada, Warda and Nargis        | barwar    |
| The Tale of Rustam (1)                        | barwar    |
| The Tale of Rustam (2)                        | barwar    |
| The Wise Daughter of the King                 | barwar    |
| The Wise Snake                                | barwar    |
| The Wise Young Man                            | barwar    |
| A Close Shave                                 | urmi_c    |
| A Cure for a Husband’s Madness                | urmi_c    |
| A Donkey Knows Best                           | urmi_c    |
| A Dragon in the Well                          | urmi_c    |
| A Dutiful Son                                 | urmi_c    |
| A Frog Wants a Husband                        | urmi_c    |
| A Lost Donkey                                 | urmi_c    |
| A Lost Ring                                   | urmi_c    |
| A Painting of the King of Iran                | urmi_c    |
| A Pound of Flesh                              | urmi_c    |
| A Sweater to Pay Off a Debt                   | urmi_c    |
| A Thousand Dinars                             | urmi_c    |
| A Visit From Harun Ar-Rashid                  | urmi_c    |
| Agriculture and Village Life                  | urmi_c    |
| Am I Dead?                                    | urmi_c    |
| An Orphan Duckling                            | urmi_c    |
| Axiqar                                        | urmi_c    |
| Events in 1946 on the Urmi Plain              | urmi_c    |
| Games                                         | urmi_c    |
| Hunting                                       | urmi_c    |
| I Have Died                                   | urmi_c    |
| Ice for Dinner                                | urmi_c    |
| Is There a Man With No Worries?               | urmi_c    |
| Kindness to a Donkey                          | urmi_c    |
| Lost Money                                    | urmi_c    |
| Mistaken Identity                             | urmi_c    |
| Much Ado About Nothing                        | urmi_c    |
| Nipuxta                                       | urmi_c    |
| No Bread Today                                | urmi_c    |
| Problems Lighting a Fire                      | urmi_c    |
| St. Zayya’s Cake Dough                        | urmi_c    |
| Star-Crossed Lovers                           | urmi_c    |
| Stomach Trouble                               | urmi_c    |
| The Adventures of Ashur                       | urmi_c    |
| The Adventures of Two Brothers                | urmi_c    |
| The Adventures of a Princess                  | urmi_c    |
| The Angel of Death                            | urmi_c    |
| The Assyrians of Armenia                      | urmi_c    |
| The Assyrians of Urmi                         | urmi_c    |
| The Bald Child and the Monsters               | urmi_c    |
| The Bald Man and the King                     | urmi_c    |
| The Bird and the Fox                          | urmi_c    |
| The Cat’s Dinner                              | urmi_c    |
| The Cow and the Poor Girl                     | urmi_c    |
| The Dead Rise and Return                      | urmi_c    |
| The Fisherman and the Princess                | urmi_c    |
| The Giant One-Eyed Demon                      | urmi_c    |
| The Little Prince and the Snake               | urmi_c    |
| The Loan of a Cooking Pot                     | urmi_c    |
| The Man Who Wanted to Complain to God         | urmi_c    |
| The Old Man and the Fish                      | urmi_c    |
| The Purchase of a Donkey                      | urmi_c    |
| The Snake’s Dilemma                           | urmi_c    |
| The Stupid Carpenter                          | urmi_c    |
| The Wife Who Learns How to Work               | urmi_c    |
| The Wife Who Learns How to Work (2)           | urmi_c    |
| The Wife’s Condition                          | urmi_c    |
| The Wise Brother                              | urmi_c    |
| The Wise Young Daughter                       | urmi_c    |
| Trickster                                     | urmi_c    |
| Two Birds Fall in Love                        | urmi_c    |
| Two Wicked Daughters-In-Law                   | urmi_c    |
| Village Life                                  | urmi_c    |
| Village Life (2)                              | urmi_c    |
| Village Life (3)                              | urmi_c    |
| Village Life (4)                              | urmi_c    |
| Village Life (5)                              | urmi_c    |
| Village Life (6)                              | urmi_c    |
| Vineyards                                     | urmi_c    |
| Weddings                                      | urmi_c    |
| Weddings and Festivals                        | urmi_c    |
| When Shall I Die?                             | urmi_c    |
| Women Are Stronger Than Men                   | urmi_c    |
| Women Do Things Best                          | urmi_c    |

[back to node types](#Node-Types)
<hr>

## place

place a text was recorded

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| text        |         127 |

**Values**
| place                  |   frequency |
|:-----------------------|------------:|
| +Hassar +Baba-čanɟa, N |          36 |
| Dure                   |          31 |
| ʾƐn-Nune               |          20 |
| Zumallan, N            |          11 |
| Canda, Georgia         |           7 |
| Guylasar, Armenia      |           7 |
| Arzni, Armenia         |           4 |
| Babari, S              |           3 |
| +Hassar +Baba-canɟa, N |           1 |
| +Spurġān, N            |           1 |
| Gulpashan, S           |           1 |
| Mushava, N             |           1 |
| Mushawa, N             |           1 |
| NW Iraq                |           1 |
| Spurġān, N             |           1 |
| Ɛn Nune                |           1 |

[back to node types](#Node-Types)
<hr>

## text_id

id of a text within its original publication; can overlap between publications

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| text        |         126 |

**Examples**
```
A10
A11
A12
A13
A14
```

[back to node types](#Node-Types)
<hr>

## speakers

names of speakers found in a text

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| text        |         126 |

**Examples**
```
Yulia Davudi
Dawið ʾAdam
Yuwəl Yuḥanna
Maryam Gwirgis
Yuwarəš Xošăba Kena
```

[back to node types](#Node-Types)
<hr>

## line_number

sequential number of a line for reference purposes; corresponds with publications where applicable

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| line        |        2587 |

**Examples**
```
1
2
3
4
5
```

[back to node types](#Node-Types)
<hr>

## text

utf8 text representation of a letter or word

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |
| letter      |      541384 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## text_nostress

utf8 text without stress markers

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |
| letter      |      541384 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## full

full transcription, one-to-one transcription of a letter or word

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |
| letter      |      541384 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## lite

lite transcription of a letter or word, without vowel accents

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |
| letter      |      541384 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## fuzzy

fuzzy transcription that leaves out most diacritics and maps certain characters in certain dialects to common characters

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |
| letter      |      541384 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## text_end

space, punctuation, or other stylistic text at the end a letter or word

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## full_end

full transcription of punctuation or other stylistic text at the end of a letter or word; see also trans_f

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120586 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## lite_end

lite transcription of punctuation or other stylistic text at the end of a letter or word, excluding intonation boundary markers; see also trans_l

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120586 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## fuzzy_end

fuzzy transcription of punctuation or other stylistic text at the end of a letter or word, excluding intonation boundary markers; see also trans_l

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## text_nostress_end

non-stressed transcription of punctuation or other stylistic text at the end of a letter or word, excluding intonation boundary markers; see also trans_l

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120586 |


See the [transcription tables](transcription.md).

[back to node types](#Node-Types)
<hr>

## timestamp

timestamp in original audio after which a given word is spoken

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |         447 |

**Examples**
```
0:00
```

[back to node types](#Node-Types)
<hr>

## speaker

name of person speaking a given word

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |

**Examples**
```
Dawið ʾAdam
Yulia Davudi
Yuwarəš Xošăba Kena
Manya Givoyev
Yuwəl Yuḥanna
```

[back to node types](#Node-Types)
<hr>

## lang

language of a foreign word

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| word        |      120598 |

**Values**
| lang   |   frequency |
|:-------|------------:|
| NENA   |      120598 |

[back to node types](#Node-Types)
<hr>

## phonetic_class

class of a letter (consonant or vowel)

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| letter      |      541366 |

**Values**
| phonetic_class   |   frequency |
|:-----------------|------------:|
| consonant        |      312113 |
| vowel            |      229253 |

[back to node types](#Node-Types)
<hr>

## phonetic_place

place of articulation of a given letter

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| letter      |      312113 |

**Values**
| phonetic_place   |   frequency |
|:-----------------|------------:|
| dental-alveolar  |      150693 |
| labial           |       62302 |
| velar            |       32162 |
| palatal          |       25877 |
| laryngeal        |       23864 |
| palatal-alveolar |       12596 |
| uvular           |        4225 |
| pharyngeal       |         394 |

[back to node types](#Node-Types)
<hr>

## phonetic_manner

manner of the sound of a letter

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| letter      |      312113 |

**Values**
| phonetic_manner   |   frequency |
|:------------------|------------:|
| affricative       |      108725 |
| nasal             |       52723 |
| other             |       49176 |
| fricative         |       40326 |
| lateral           |       39379 |
| sibilant          |       21784 |

[back to node types](#Node-Types)
<hr>

## phonation

phonation of a letter

**Node Counts**
| node type   |   frequency |
|:------------|------------:|
| letter      |      307888 |

**Values**
| phonation            |   frequency |
|:---------------------|------------:|
| plain                |      140560 |
| unvoiced_aspirated   |       56847 |
| voiced               |       51033 |
| unvoiced             |       44250 |
| unvoiced_unaspirated |       10671 |
| emphatic             |        4527 |

[back to node types](#Node-Types)
<hr>

