# Northeastern Neo-Aramaic Corpus Data [![DOI](https://zenodo.org/badge/204971841.svg)](https://zenodo.org/badge/latestdoi/204971841)

<a href="https://www.ames.cam.ac.uk"><img src="https://github.com/CambridgeSemiticsLab/nena_tf/blob/master/docs/images/CambridgeU_color.jpg?raw=true" width="236" height="4    9"></a>

This repository contains raw and corrected source texts written in North Eastern Neo-Aramaic (NENA) dialects. All original source material is converted to a standard mark-up format, regardless of its original format.

The purpose of this repository is to curate source texts that will be used for building a complete text corpus in Text-Fabric. The corpus will in turn be analyzed and annotated for linguistic features.

## Contents

* [raw](raw) - contains raw, uncorrected source data in its diverse formats
* [nena](nena) - contains the plain text with mark-up in .nena format 


# Markup of Standard Texts of the NENA Corpus

The texts of the NENA corpus originate from various sources.
There are texts that have been published, and exist in MS-Word
format in the layout of the publication.
Other texts have been transcribed and directly published on
the NENA website, and the only version is the one stored
in the MariaDB database of the website.

Ideally, the canonical version of the texts should be available
in one format, where they are updated if necessary.
They should be stored in a format that is easy to read and write.

## Features

The format should be able to store the features we have encountered
in the texts that have been processed so far:

- metadata:
  - Dialect
  - Publication
  - Title (enumerated if duplicate within dialect)
  - Text id (optional)
  - Informant
  - Place
- paragraph structure
- newlines (poetry style)
- line/verse numbers
- text markup:
  - 'foreign' marker
  - language marker
  - footnotes

## Specifications

In order to make the text format as easy to read and write as possible,
the chosen format is inspired by
[Markdown](https://daringfireball.net/projects/markdown/syntax).
It means that it is mostly plain text, with a few special and meaningful
syntax rules.

### Metadata

Every text is introduced by its title. The title is put on its own line,
and preceded by a pound (hash) sign:

    # The Monk and the Angel

The title is followed by an empty line and then the other metadata
(as applicable), starting with a keyword followed by a colon, a space
and the data itself:

    dialect: Barwar (C)
    publication: G. Khan, The Neo-Aramaic Dialect of Barwar (Brill, 2008)
    text_id: A1
    informant: Yulia Davudi
    place: +Hassar +Baba-čanɟa, N

### Paragraph structure

Paragraphs and Line Breaks

From the [Markdown specification](https://daringfireball.net/projects/markdown/syntax):

> A paragraph is simply one or more consecutive lines of text,
> separated by one or more blank lines. (A blank line is any line
> that looks like a blank line — a line containing nothing but spaces
> or tabs is considered blank.)
> Normal paragraphs should not be indented with spaces or tabs.

For example:

    This is
    one paragraph.
    
    This is another paragraph.

### Line breaks

For texts that require line breaks that do not start a new paragraph,
such as poetic texts, it is possible to end the line with a verse marker `/`,
and to add an empty line with a double verse marker `//`:

    This is a normal paragraph.
   
    this /
    is not /
    a poem — //
    but /
    it does /
    look like one.

    Normal paragraph following verse.

### Line numbers

Texts are divided into numbered lines (or 'verses') that make it easy
to refer to a specific location in the text.
These verse numbers are indicated simply by a number surrounded by
round brackets (parentheses) and followed by a space.
They may be placed at the beginning of the actual line, or not; as long
as they are separated from other characters by either a newline character
or a space.

Line divisions do not have to correspond with paragraph divisions
(although probably they usually will).

    (1) This is the first 'line'. (2) This is the second 'line'.

    (3) This is the third line, and the second paragraph.

### Sentence structure

Besides paragraphs and lines, the text will be divided into sentences
and subsentences, based on punctuation. Characters `.`, `!` and `?`
mark the end of a sentence, and the comma `,` marks the end of a
subsentence. Sentence and subsentence do not have to correspond with
line divisions, but they will be terminated on paragraph boundaries,
irrespective of punctuation.

### Text markup

- foreign marker:
  
  In the publications, foreign words or names are indicated with
  emphasis (using roman type, as opposed to the italic type used
  for the Aramaic text).
  
  As in Markdown, emphasis is indicated by surrounding (groups of)
  words with asterisks, such as `*this*`. Asterisks with spaces
  (or newlines) on both sides will be interpreted as asterisks,
  not as emphasis markers.

- language marker:

  To indicate the source language of a foreign word, optionally
  a language marker can be added. In the publications language
  is indicated by a letter code in superscript type (E for English,
  P for Persian etc.). For easier typing, we shall surround the
  letter code by angle brackets, e.g. `<E>`. The indicator is
  placed before and after the word(s) in the specified language,
  and should be within the foreign markers.
  
- footnotes:

  To insert a footnote, place an identifier preceded by a
  circumflex symbol `^` within square brackets. The same
  identifier should occur at the beginning of a line followed
  by a colon and the note text.

      This is a paragraph,[^1] containing a footnote.
      
      [^1]: This is the text of the footnote.

  The identifier can be anything and does not have to be unique.

### Comments

Comments can be written in the text, surrounded by brackets.
There is one special kind of comment, which introduces another
speaker than the main informant of the text, typically the
researcher. It takes the form of round brackets (parentheses),
followed by initials (or a name?) and a colon, and the Aramaic
text of the interjection, e.g.: `(GK: text of interjection?)`.

## Example

TODO add a full example containing all features

