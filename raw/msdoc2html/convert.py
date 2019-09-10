# Run instructions:
# to convert dialects/ to nena markdown:
# `python convert.py dialects/`

# principal code is thanks to Hannes Vlaardingerbroek

import sys
import re
from pathlib import Path
from html_to_nena import html_todict
# for title capitalzation with apostrophes:
# https://stackoverflow.com/questions/8199966/python-title-with-apostrophes
import string

# first arg should be directory containing dialect subdirectories
# ex:
# dialects
#     Barwar
#     Urmi_C
dialects = list(Path(sys.argv[1]).glob('*'))
output = '../../markdown/{dialect}' # markdown files to go here

# configure dialect metadata regex patterns
# key itself is regex pattern that should match a file name
# file-based keys are more desireable than dialect keys
# since regex patterns could theoretically differ from file to file
patterns = {
    
    'bar text .*\.html':
        {
            'gp-sectionheading-western': (
                (('text_id', 'title'),
                 '^\s*([A-Z]\s*[0-9]+)\s+(.*?)\s*$'),
            ),
            'gp-subsectionheading-western': (
                (('informant', 'place'),
                 '^\s*Informant:\s+(.*)\s+\((.*)\)\s*$'),
            ),
        },
    
    'cu vol 4 texts.html':
        {
            'gp-sectionheading-western': (
                (('text_id',),
                 '^\s*([A-Z]\s*[0-9]+)\s*'),
            ),
            'gp-subsectionheading-western': (
                (('title', 'informant', 'place'),
                 '^\s*(.*?)\s*\(([^,]*),\s+(.*)\)\s*$'),
                (('title',),
                 '^\s*(.*?)\s*$'),
            ),
            'gp-subsubsectionheading-western': (
                (('version', 'informant', 'place'),
                 '^\s*(Version\s+[0-9]+):\s+(.*?)\s+\((.*)\)\s?$')
            ),
    }    
}

# configure character replacements
replace = {
    # standardizing substutions
    '\u2011': '\u002d',  # non-breaking hyphen to normal hyphen-minus
    '\u01dd': '\u0259',  # 'ǝ' "turned e" to 'ə' schwa
    '\uf1ea': '\u003d',  # SIL deprecated double hyphen to '=' equals sign
    '\u2026': '...',  # '…' horizontal ellipsis to three dots
    'J\u0335': '\u0248',  # 'J' + short combining stroke to 'Ɉ' J with stroke
    'J\u0336': '\u0248',  # J' + long combining stroke to 'Ɉ' J with stroke
    '<y>': '\u02b8',  # superscript small letter y
    # corrections of errors
    '\u002d\u032d': '\u032d\u002d',  # Switch positions of Hyphen and Circumflex accent below
    'ʾ>': '>ʾ',  # misplaced alaph in superscript <sup>Pʾ</sup>afšɑ̄rī̀<sup>P</sup> (Urmi_C, somewhere?)
    
    # There may be some other stray alaph's and other anomalies out there.
    # Will have to think of some tests to find them. -HV
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
            
def is_heading(e):
    '''
    Tests whether a tag is a heading tag.
    '''
    return e.tag == 'h2'

# run the conversion
for dialect in dialects:
    for file in dialect.glob('*.html'):
        
        print(file.name)
        
        file_patts = next(patts for filepatt, patts in patterns.items() 
                            if re.match(filepatt, str(file.name)))
        
        texts = html_todict(
            file,
            heading_patterns = file_patts,
            is_heading = is_heading,
            text_start = is_heading,
            replace = replace,
        )
        dialect_name = dialect.name
        exportdialect(texts, dialect=dialect_name, out_dir=output)