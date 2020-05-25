#!/usr/bin/env python3

import sys
import re
from pathlib import Path

from nena_corpus import Text, html_to_text, parse_metadata


# Sort paths in natural order, see:
# https://stackoverflow.com/a/4836734/9230612
def sortpaths(pathlist):
    """Sort pathlib paths in natural order"""
    return sorted(pathlist, key=lambda x: [int(e) if e.isdigit() else e.lower()
                                           for e in re.split('(\d+)', x.name)])

# print line with maximum length
def printline(s, maxlen=80):
    pos = 0
    line = []
    for w in s.split():
        if pos + len(w) > maxlen:
            print(' '.join(line))
            pos = 0
            line = []
        pos += len(w)
        line.append(w)
    print(' '.join(line))


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


dialect = sys.argv[1]
# this should work both if os expands wildcard patterns, and if not
paths = sortpaths([p for f in sys.argv[2:] for p in Path.cwd().glob(f)])

newtext = True

# dict to store text metadata
metadata = {}

# store titles in order to check for uniqueness
# TODO This only checks titles in the same run!
titles = set()

for file in paths:
    for p in html_to_text(file, replace=replace):
        
        if p.type.startswith('gp-') and str(p).strip():
            
            if p.type.startswith('gp-sectionheading'):
                metadata = {}
                newtext = True
            elif p.type.startswith('gp-subsubsection'):
                newtext = True
                
            for k, v in parse_metadata(p):
                metadata[k] = v
        
        elif p.type.startswith('sdfootnote'):
            
            line = ''
            
            for text, text_style in p:
                if text_style == 'fn_symbol':
                    line += f'[^{text}]'
                    
                elif text_style == 'italic':
                    line += f'*{text}*'
                
                else:
                    line += text
                
            printline(line)
                
        elif p.type == 'p':
            
            # print metadata on start of new text
            if newtext and metadata:
                newtext = False
                
                title = metadata['title']
                
                # make sure title is unique
                num = 1
                while title in titles:
                    num += 1
                    title = f"{metadata['title']} ({num})"
                titles.add(title)
                    
                print(f'\n# {title}')
                
                print('dialect:', dialect)
                # print('publication:', ??)
                print('source_file:', file.name)
                
                for key in ('text_id', 'informant', 'place', 'version'):
                    if key in metadata:
                        print(f'{key}:', metadata[key])
                print()  # blank line between metadata and text
            
            line = ''

            for text, text_style in p:
                
                if text_style == 'verse_no':
                    if line:
                        printline(line)
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

            printline(line)
            print()  # blank line between paragraphs

