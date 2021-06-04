"""
Yacc-style lexer and parser for NENA-formatted texts with Sly.

Sly is a Python implementation of Yacc ("yet another compiler 
compiler"). Yacc is a unix-based shift-reduce parser. Sly follows
the same basic parsing approach. The Yacc documentation is helpful
for understanding the basic concepts:
https://www.ibm.com/docs/en/zos/2.3.0?topic=tools-tutorial-using-lex-yacc#lytut

With Yacc parsing, there are two classes that are used: a lexer and a parser.
The lexer divides the text into tokens. The parser then combines tokens 
recursively. 

Sly itself has some quirky, non-Pythonic syntax, done with
some under-the-hood workarounds implemented by the developer. 
This is unfortunate. Nevertheless, Sly is a simple and easy 
to use tool that fits the goals here well. For docs see:
    https://sly.readthedocs.io/en/latest/

For the NENA lexer and parser, all of the regular expression definitions
for the tokens are defined in the config file. The parser patterns
are native to the class itself.
"""

import re
from sly import Lexer, Parser

class NenaLexer(Lexer):
    
    def __init__(self):
        super().__init__()
        self.dialect = None
    
    def error(self, t):
        """Give warning for bad characters"""
        print(f"Illegal character {repr(t.value[0])} @ index {self.index}")
        self.index += 1
    
    # set of token names as required by
    # the Lexer class
    tokens = {
        LETTER, PUNCT_BEGIN, PUNCT_END, NEWLINES,
        NEWLINE, NEWLINES, SPAN_TAG, ATTRIBUTE, 
        FOREIGN_LETTER, LANG_START, LANG_END        
    }

    # Attribute starts key and colon. Returns 2-tuple (key, value).
    @_(r'[a-z0-9_]+\s*::\s*.*')
    def ATTRIBUTE(self, t):
        field, value = tuple(t.value.split('::'))
        field, value = field.strip(), value.strip()
        t.value = {field:value}
        for attr, val in t.value.items():
            # arrange loaded speakers into dict
            if attr == 'speakers':
                speakers = {}
                for speakset in val.split(','):
                    initials, speaker = speakset.split('=')
                    speakers[initials.strip()] = speaker.strip()
                t.value[attr] = speakers
                
        # set dialect
        if field == 'dialect':
            self.dialect = value 
            
        return t
    
    @_(r'\(.*?\)\s*')
    def SPAN_TAG(self, t):
        attribs = {'class': 'span'}
        elements = t.value.strip().replace('(', '').replace(')', '')
        elements = elements.split()
        for element in elements:
            if timestamp.match(element):
                attribs['timestamp'] = element
            elif linenum.match(element):
                attribs['line_number'] = element
            elif initials.match(element):
                attribs['speaker'] = element
            else:
                raise Exception(f'invalid element {element} in line indicator {t.value}')
        t.value = attribs
        return t
    
    NEWLINES = r'\n\s*\n\s*' 
    
    @_(alphabet_re)
    def LETTER(self, t):
        t.value = build_char(t.value, 'letter', self.dialect)
        return t
    
    @_(punct_begin_re)
    def PUNCT_BEGIN(self, t):
        t.value = build_char(t.value, 'punctuation', self.dialect)
        return t
    
    @_(punct_end_re)
    def PUNCT_END(self, t):
        t.value = build_char(t.value, 'punctuation', self.dialect)
        return t
    
    NEWLINE = '\n\s*'
    
    @_(r'<[A-Za-z?]+:\s*')
    def LANG_START(self, t):
        lang = re.match(r'<([A-Za-z?]+):', t.value).group(1)
        tag = t.value.strip()
        t.value = {'class': 'LANG_START', 'decomposed_string': tag, 'lang': lang}
        return t
        
    @_(r'>')
    def LANG_END(self, t):
        t.value = {'class': 'LANG_END', 'decomposed_string': t.value}
        return t
    
    # NB: tokens evaluated in order of appearance here
    # thus foreign string matched lastly
    @_(r'[a-zA-ZðÐɟəƏɛƐʾʿθΘ][\u0300-\u033d]*')
    def FOREIGN_LETTER(self, t):
        letter_meta = {'class':'foreign', 'decomposed_string': t.value}
        letter_meta.update(dict(match_transcriptions(t.value, self.dialect)))
        t.value = letter_meta
        return t

class NenaParser(Parser):
    
    def __init__(self, dialect):
        super().__init__()
        self.dialect = dialect
    
    #debugfile = 'nena_parser.out'
    tokens = NenaLexer.tokens
    
    def error(self, t):
        raise Exception(f'unexpected {t.type} ({repr(t.value)}) at index {t.index}')    
    
    @_('attributes NEWLINES text_block')
    def nena(self, p):
        return [p.attributes, p.text_block]
    
    @_('attributes NEWLINE ATTRIBUTE')
    def attributes(self, p):
        p.attributes.update(p.ATTRIBUTE)
        return p.attributes
    
    @_('NEWLINE ATTRIBUTE', 'ATTRIBUTE')
    def attributes(self, p):
        return p.ATTRIBUTE
    
    @_('text_block NEWLINES paragraph')
    def text_block(self, p):
        return p.text_block + [p.paragraph]
    
    @_('paragraph')
    def text_block(self, p):
        return [p.paragraph]
    
    @_('paragraph element')
    def paragraph(self, p):
        return p.paragraph + [p.element]
    
    @_('element')
    def paragraph(self, p):
        return [p.element]
    
    @_('word',
       'SPAN_TAG')
    def element(self, p):
        return p[0]
    
    @_('beginnings letters endings', 
       'letters endings',
       'letters NEWLINE',
       'letters NEWLINE endings',
       'beginnings letters NEWLINE',
       'beginnings letters NEWLINE endings',
      )
    def word(self, p):
        beginnings = getattr(p, 'beginnings', [])
        default_end = build_char(' ', 'punctuation', self.dialect)
        endings =  getattr(p, 'endings', [default_end])
        return make_word(p.letters, self.dialect, beginnings, endings)

    @_('PUNCT_BEGIN beginnings',
       'LANG_START beginnings')
    def beginnings(self, p):
        return [p[0]] + p.beginnings
    
    @_('PUNCT_BEGIN',
       'LANG_START')
    def beginnings(self, p):
        return [p[0]]
    
    @_('endings NEWLINE')
    def endings(self, p):
        if p.endings[-1]['decomposed_string'] != ' ':
            new_end = build_char(' ', 'punctuation', self.dialect)
            p.endings.append(new_end)
        return p.endings
    
    @_('endings PUNCT_END',
       'endings LANG_END',)
    def endings(self, p):
        return p.endings + [p[1]]
    
    @_('PUNCT_END',
       'LANG_END')
    def endings(self, p):
        return [p[0]]
        
    @_('LETTER letters', 
       'FOREIGN_LETTER letters')
    def letters(self, p):
        return [p[0]] + p[1]
    
    @_('LETTER', 
       'FOREIGN_LETTER')
    def letters(self, p):
        return [p[0]]
