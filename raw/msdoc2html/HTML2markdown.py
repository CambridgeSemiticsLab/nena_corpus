#!/usr/bin/env python3

# To run pipeline:
# python HTML2markdown.py dialects/

import sys
import re
import collections
from pathlib import Path
from nena_corpus import Text, html_to_text, parse_metadata
# for title capitalzation with apostrophes:
# https://stackoverflow.com/questions/8199966/python-title-with-apostrophes
import string

# first arg should be directory containing dialect subdirectories
# ex:
# html_dir
#     Barwar
#     Urmi_C
dialects = list(Path(sys.argv[1]).glob('*'))

output = '../../markdown/{dialect}' # markdown output to here

# Characters to be replaced
replace = {
    '\u2011': '\u002d',  # U+2011 NON-BREAKING HYPHEN -> U+002D HYPHEN-MINUS
    '\u01dd': '\u0259',  # U+01DD LATIN SMALL LETTER TURNED E -> U+0259 LATIN SMALL LETTER SCHWA
    '\uf1ea': '\u003d',  # U+F1EA Deprecated SIL character -> U+003D '=' EQUALS SIGN
    '\u2026': '...',  # U+2026 '…' HORIZONTAL ELLIPSIS -> three dots
    'J\u0335': '\u0248',  # 'J' + U+0335 COMBINING SHORT STROKE OVERLAY -> U+0248 'Ɉ' LATIN CAPITAL LETTER J WITH STROKE
    'J\u0336': '\u0248',  # 'J' + U+0336 COMBINING LONG STROKE OVERLAY -> U+0248 'Ɉ' LATIN CAPITAL LETTER J WITH STROKE
    '\u002d\u032d': '\u032d\u002d',  # Switch positions of Hyphen and Circumflex accent below
    '\u2011\u032d': '\u032d\u002d',  # Switch positions of Non-breaking hyphen and Circumflex accent below
}

def exportdialect(textdict, dialect='', out_dir='{dialect}'):
    '''
    Writes texts to disk.
    Expects a dict of title:markdown mapping.
    '''
    
    outpath = Path(out_dir.format(dialect=dialect))
    if not outpath.exists():
        outpath.mkdir()
    
    # write each text
    for title, markdown in textdict.items():
        file = f'{title}.nena'
        outfile = Path(outpath, file)
        with open(outfile, 'w') as out:
            out.write(markdown.strip())

def sortpaths(pathlist):
    '''
    Sort pathlib paths in natural order
    https://stackoverflow.com/a/4836734/9230612
    '''
    return sorted(pathlist, key=lambda x: [int(e) if e.isdigit() else e.lower()
                                           for e in re.split('(\d+)', x.name)])

def returnline(s, maxlen=80):
    '''
    Returns a line with maximum length
    '''
    pos = 0
    line = []
    lines = []
    for w in s.split():
        if pos + len(w) > maxlen:
            lines.append(' '.join(line))
            pos = 0
            line = []
        pos += len(w)
        line.append(w)
    lines.append(' '.join(line))
    return '\n'.join(lines)

def convertdialect(dialect):
    '''
    Accesses, converts, and returns source HTML
    texts for a given dialect. Returns a dict w/
    keys of text titles and markdown string values.
    
    dialect_dir - PosixPath containing HTML files
    '''
    
    textpaths = list(dialect.glob('*.html'))
    
    # the following variables keep track of texts and their metadata
    # since files can contain numerous texts in one 
    # this allows texts to be processed in one continuous loop
    metadata = {}
    newtext = True
    
    # title:markdown mapped here where title == text title
    # duplicate title checks operate on this dict as well
    # default dict means that we can simply compile in place
    # based on the title without need to reset the string each new text
    texts = collections.defaultdict(str)
    
    for file in textpaths:
        for p in html_to_text(file, replace=replace):

            # process metadata
            if p.type.startswith('gp-') and str(p).strip():
                
                # get title
                if p.type.startswith('gp-sectionheading'):
                    metadata = {}
                    newtext = True
                    
                # get additional metadata like informant, place, etc.
                elif p.type.startswith('gp-subsubsection'):
                    newtext = True
                    
                # populate metadata
                for k, v in parse_metadata(p):
                    metadata[k] = v
                    
            # store footnotes
            elif p.type.startswith('sdfootnote'):
                line = ''
                for text, text_style in p:
                    if text_style == 'fn_symbol':
                        line += f'[^{text}]'
                    elif text_style == 'italic':
                        line += f'*{text}*'
                    else:
                        line += text
                texts[title] += returnline(line)

            # store normal paragraphs
            elif p.type == 'p':

                # store metadata on start of new text
                if newtext and metadata:
                    
                    newtext = False
                    title = string.capwords(metadata['title'])

                    # make sure title is unique
                    # if not, assign number (num)
                    num = 1
                    while texts.get(title, False):
                        num += 1
                        title = f"{metadata['title']} ({num})"
                        
                    # store text title
                    texts[title] += f'# {title}\n'
                    texts[title] += f'dialect: {dialect.name}\n'
                    texts[title] += f'source_file: {file.name}\n'
                    
                    # add metadata
                    for meta in ('text_id', 'informant', 'place', 'version'):
                        if meta in metadata:
                            texts[title] += f'{meta}: {metadata[meta]}\n'
                            
                    texts[title] += '\n'  # blank line between metadata and text

                # compile lines
                line = ''

                for text, text_style in p:

                    if text_style == 'verse_no':
                        if line:
                            texts[title] += returnline(line) + '\n'
                            line = ''
                        line += f'\n{text.strip()} '

                    elif text_style == 'fn_anchor':
                        line += f'[^{text}]'

                    elif text_style == 'comment':
                        line += text

                    elif text_style == 'marker':
                        line += f'<{text}>'

                    elif text_style == 'foreign':
                        line += f'*{text}*'

                    else:
                        line += text

                texts[title] += returnline(line)
                texts[title] += '\n'  # blank line between paragraphs
                
    # give the texts dict
    return texts

# run the conversion
for dialect in dialects:
    texts = convertdialect(dialect)
    dialect_name = dialect.name
    exportdialect(texts, dialect=dialect_name, out_dir=output)