# Run instructions:
# to convert dialects/ to nena markdown:
# `python convert.py dialects/`

# principal code is thanks to Hannes Vlaardingerbroek

import os
import sys
import re
from pathlib import Path
from html_to_nena import html_todict

# first arg should be directory containing dialect subdirectories
# ex:
# dialects
#     Barwar
#     Urmi_C
dialects = list(Path(sys.argv[1]).glob('*'))
version = '0.02'
output = f'../../texts/{version}/{{dialect}}' # markdown files to go here

def is_heading(e):
    return (e.tag == 'h2'
            and e.text_content().strip() if e.text_content() else False
            and e.attrib.get('class', '') == 'gp-sectionheading-western')

# configure character replacements
replace = {
    
    # stylistic substitutions
    '\|': '\u02c8', # pipe to superscript line
    '\+': '\u207A', # plus to superscript plus (esp. Christian Urmi) 

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
    'ʾ\*': '*ʾ',  # misplaced alaph in superscript; should be emphasized -HV+CK 
    '([\w*?])\s(-)': '\g<1>\g<2>', # remove rogue spaces between morphemes
    '\*\*(\u0301)\*\*':'\g<1>', # remove rogue bolding of single accent

    # There may be some other stray alaph's and other anomalies out there.
    # Will have to think of some tests to find them. -HV

    # fix any missing colons in comment
    r'([([]\*[A-Z][A-Z]\*)\s': '\g<1>: ',

    # replace parentheses comments with square brackets
    # NB: \g<1> is capture group
    '\((\*[A-Z][A-Z]\*.*?)\)': '[\g<1>]',

    # remove emphasis from commenter initials 
    '\[\*([A-Z]*)\*:': '[\g<1>:',

    # move punctuation outside of emphasized foreign lang tags
    '(<\w>\*.+?\*)(.)(<\w>)': '\g<1>\g<3>\g<2>',
    
    # move stray terms outside of foreign tags
    '(<\w>\*.+?\*)(\w+?)(<\w>)': '\g<1>\g<3>\g<2>',

}

# Map default styles for documents
style_map = {
    'i': None,
    None: 'emphasis',
    'b': 'strong',
}

# Map acceptable characters to styles
style_char_map = { 
    'emphasis': r'[^\W\d_]|[\u0300-\u036F]|\u207A',
    'strong': r'[^\W\d_]|[\u0300-\u036F]|\u207A',
    'sup': r'[A-Za-z]',
}   

def e_filter(e):
    """Filters out unwanted elements"""
    ignore_tags=('sdfield',)
    if e.tag in ignore_tags:
        return True

# configure data needed to process the given file
# includes regex patterns and args for converter
# the key is a regex pattern that matches the file name

bar_headings = {
'gp-sectionheading-western': (
    (('text_id', 'title'),
     '^\s*([A-Z]\s*[0-9]+)\s+(.*?)\s*$'),),
'gp-subsectionheading-western': (
    (('informant', 'place'),
     '^\s*Informant:\s+(.*)\s+\((.*)\)\s*$'),),
}        

# NB: keys matched on more specific files first
# then more general after
configs = {
    
    'bar text A37-A40.html': {
        'heading_patterns': bar_headings,
        'is_heading': is_heading,
        'text_start': is_heading,
        'replace': replace,
        'style_map': {
            'i': None,
            None: None,
            'b': 'strong',
        },
        'style_char_map': style_char_map,
        'e_filter': e_filter,
    },

    'bar text .*\.html': {
        'heading_patterns': bar_headings,
        'is_heading': is_heading,
        'text_start': is_heading,
        'replace': replace,
        'style_map': style_map,
        'style_char_map': style_char_map,
        'e_filter': e_filter,
    },
    
    'cu vol 4 texts.html': {
        'heading_patterns':
            {
            'gp-sectionheading-western': (
                (('text_id',),
                 '^\s*([A-Z]\s*[0-9]+)\s*'),),
            
            'gp-subsectionheading-western': (
                (('title', 'informant', 'place'),
                 '^\s*(.*?)\s*\(([^,]*),\s+(.*)\)\s*$'),
                (('title',),
                 '^\s*(.*?)\s*$'),),
            
            'gp-subsubsectionheading-western': (
                (('version', 'informant', 'place'),
                 '^\s*(Version\s+[0-9]+):\s+(.*?)\s+\((.*)\)\s?$'),),
        },
        'is_heading': is_heading,
        'text_start': is_heading,
        'replace': replace,
        'style_map': style_map,
        'style_char_map': style_char_map,
        'e_filter': e_filter,
    }
}

def exportdialect(textdict, dialect='', out_dir='{dialect}'):
    '''
    Writes texts to disk.
    Expects a dict of title:markdown mapping.
    '''
    outpath = Path(out_dir.format(dialect=dialect))
    if not outpath.exists():
        outpath.mkdir(parents=True)
    
    # write each text
    for title, markdown in textdict.items():
        file = f'{title}.nena'
        outfile = Path(outpath, file)
        with open(outfile, 'w') as out:
            out.write(markdown)

# run the conversion
for dialect in dialects:
    for file in dialect.glob('*.html'):
        
        print(f'processing {file.name}')
        
        config = next(patts for filepatt, patts in configs.items() 
                            if re.match(filepatt, str(file.name)))
        
        texts = html_todict(
            file,
            **config
        )
        dialect_name = dialect.name
        exportdialect(texts, dialect=dialect_name, out_dir=output)

os.system("cd ../../nena/; sh corrections.sh")
