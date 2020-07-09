# NENA Text-Parser 1.0

import sys
import re
import json
from sly import Lexer, Parser
import unicodedata

# get file to convert
try:
    file_to_parse = sys.argv[1]
except:
    raise Exception('No file provided to parse!')

# prepare alphabet and punctuation standards for processing
alphabet_std = '../../standards/alphabet.json'
punctuation_std = '../../standards/punctuation.json' 
lang_std = '../../standards/foreign_languages.json'

with open(alphabet_std, 'r') as infile:
    alphabet_data = {
        re.compile(data['decomposed_regex']):data 
            for data in json.load(infile)
    }
with open(punctuation_std, 'r') as infile:
    punct_data = {
        re.compile(data['regex']):data 
            for data in json.load(infile)
    }
with open(lang_std, 'r') as infile:
    foreign_data = set(lang['code'] for lang in json.load(infile))
    
# compile regexes for matching
alphabet_re = '|'.join(data['decomposed_regex'] for letter,data in alphabet_data.items())

punct_begin_re = '|'.join(
    data['regex'] for punct, data in punct_data.items()
        if data['position'] == 'begin'
)
punct_end_re = '|'.join(
    data['regex'] for punct, data in punct_data.items()
        if data['position'] == 'end'
)

foreign_codes = '|'.join(foreign_data)

class NenaLexer(Lexer):
    
    def error(self, t):
        """Give warning for bad characters"""
        raise Exception(f"Illegal character {repr(t.value[0])} @ index {self.index}")
    
    # set of token names as required by
    # the Lexer class
    tokens = {
        LETTER, PUNCT_BEGIN, PUNCT_END, NEWLINES,
        NEWLINE, NEWLINES, ATTRIBUTE, 
        FOREIGN_LETTER,
        LINESTAMP, SPAN_START, SPAN_END        
    }

    # Attribute starts key and colon. Returns 2-tuple (key, value).
    @_(r'[a-z0-9_]+ = .*')
    def ATTRIBUTE(self, t):
        field, value = tuple(t.value.split('='))
        t.value = {field.strip(): value.strip()}
        return t
    
    @_(r'\(\d+\@\d:\d+\)\s*', 
       r'\(\d+\)\s*')
    def LINESTAMP(self, t):
        number = re.findall('^\((\d+)', t.value)[0]
        timestamp = re.findall('@(\d+:\d+)', t.value)
        if timestamp:
            timestamp = timestamp[0]
        t.value = {'number': number, 'timestamp': timestamp}
        return t

    NEWLINES = r'\n\s*\n\s*' # i.e. marks text-blocks
    LETTER = alphabet_re    
    PUNCT_BEGIN = punct_begin_re
    PUNCT_END = punct_end_re
    NEWLINE = '\n\s*'
        
    # treat the language and speaker tag simultaneously as a "span"
    # this optimizes the code quite a bit since both tags
    # behave identically when they are parsed
    @_(r'[<«][A-Za-z?]+:\s*')
    def SPAN_START(self, t):
        if t.value[0] == '<':
            kind = 'language'
            punct_type = 'exclusive'
        else:
            kind = 'speaker'
            punct_type = 'inclusive'
        value = re.match(r'[<«]([A-Za-z?]+):', t.value).group(1)
        tag = t.value.strip() + ' ' # ensure spacing
        t.value = (tag, kind, value, punct_type) # tag, key, value, punct_type
        return t
        
    SPAN_END = r'[>»]'
    
    # NB: tokens evaluated in order of appearance here
    # thus foreign string matched lastly
    FOREIGN_LETTER = r'[a-zA-ZðÐɟəƏɛƐʾʿθΘ][\u0300-\u033d]*'

def make_word(letters, beginnings=[], endings=[]):
    """Return word dictionary"""
    return {
        'word': ''.join(letters),
        'letters': letters,
        'beginnings': beginnings,
        'endings': endings,
    }

def modify_attribute(words, key, value):
    """Modify dict attribute for a list of words"""
    for word in words:
        word[key] = value
    return words

def format_tag_endings(tag, punct_value, endings=[]):
    """Format punctuation around a tag.
    
    Normalizes in case of irregularity. For instance, in the
    cases of both
        words.</> 
        words</>.
    the tags will be normalized to either an in/exclusive order.
    """
    if punct_value == 'inclusive':
        return endings + [tag]
    elif punct_value == 'exclusive':
        return [tag] + endings
    else:
        raise Exception(f'INVALID punct_value supplied: {punct_value}')
    
class NenaParser(Parser):
    
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
    
    @_('paragraph line')
    def paragraph(self, p):
        return p.paragraph + [p.line]
    
    @_('line')
    def paragraph(self, p):
        return [p.line]
    
    @_('LINESTAMP span words',
      'LINESTAMP span span words',
      'LINESTAMP span word span words')
    def line(self, p):
        words = []
        for wordtype in list(p)[1:]:
            if type(wordtype) == list: 
                words += wordtype
            else:
                words.append(wordtype)
        p.LINESTAMP['words'] = words
        return p.LINESTAMP
    
    @_('LINESTAMP word span words')
    def line(self, p):
        p.LINESTAMP['words'] = [p.word] + p.span + p.words
        return p.LINESTAMP
    
    @_('LINESTAMP words')
    def line(self, p):
        p.LINESTAMP['words'] = p.words
        return p.LINESTAMP
    
    @_('words span')
    def words(self, p):
        return p.words + p.span
    
    @_('SPAN_START letters SPAN_END',
       'SPAN_START letters SPAN_END endings',
       'SPAN_START letters SPAN_END NEWLINE',
       'SPAN_START beginnings letters SPAN_END endings',
       'SPAN_START beginnings letters SPAN_END NEWLINE',
      )
    def span(self, p):
        begin_tag, kind, value, punct_type = p.SPAN_START
        beginnings = [begin_tag] + getattr(p, 'beginnings', [])
        
        # build ends
        trailing_ends = getattr(p, 'endings', [])
        if getattr(p, 'NEWLINE', '') and not ''.join(trailing_ends).endswith(' '):
            trailing_ends.append(' ')
        endings = format_tag_endings(p.SPAN_END, punct_type, trailing_ends)
        
        word = make_word(p.letters, beginnings=beginnings, endings=endings)
        word[kind] = value
        return [word]
    
    @_('SPAN_START word letters SPAN_END',
       'SPAN_START word letters SPAN_END endings',
       'SPAN_START word letters SPAN_END NEWLINE',
       'SPAN_START word beginnings letters SPAN_END endings',
       'SPAN_START word beginnings letters SPAN_END NEWLINE',
       'SPAN_START words letters SPAN_END endings',
       'SPAN_START words letters SPAN_END NEWLINE',
       'SPAN_START words beginnings letters SPAN_END endings',
      )
    def span(self, p):
        begin_tag, kind, value, punct_type = p[0]
        
        # compile words
        words = []
        if getattr(p, 'word', None):
            p.word['beginnings'].insert(0, begin_tag)
            words.append(p.word)
        elif getattr(p, 'words', None):
            words.extend(p.words)
            
        # build new word from dangling letters and ends
        trailing_ends = getattr(p, 'endings', [])
        if getattr(p, 'NEWLINE', '') and not ''.join(trailing_ends).endswith(' '):
            trailing_ends.append(' ')
        endings = format_tag_endings(p.SPAN_END, punct_type, trailing_ends)
        beginnings = getattr(p, 'beginnings', [])
        words.append(make_word(p.letters, beginnings=beginnings, endings=endings))
        
        return modify_attribute(words, kind, value)
    
    @_('SPAN_START words SPAN_END',
       'SPAN_START words SPAN_END endings',
       'SPAN_START words SPAN_END NEWLINE',
       'SPAN_START word SPAN_END',
       'SPAN_START word SPAN_END endings',
       'SPAN_START word SPAN_END NEWLINE',)
    def span(self, p):
        words = getattr(p, 'words', [p[1]])
        begin_tag, kind, value, punct_type = p[0]
        first_word, last_word = words[0], words[-1]
        first_word['beginnings'].insert(0, begin_tag)
        
        # build ends
        trailing_ends = last_word['endings'] + getattr(p, 'endings', [])
        if getattr(p, 'NEWLINE', '') and not ''.join(trailing_ends).endswith(' '):
            trailing_ends.append(' ')        
        last_word['endings'] = format_tag_endings(p[2], punct_type, trailing_ends)
        
        return modify_attribute(words, kind, value)
    
    @_('words word')
    def words(self, p):
        return p.words + [p.word]
    
    @_('word word')
    def words(self, p):
        return [p[0]] + [p[1]]
    
    @_('beginnings letters endings', 
       'letters endings',
       'letters NEWLINE',
       'letters NEWLINE endings',
       'beginnings letters NEWLINE',
       'beginnings letters NEWLINE endings',
      )
    def word(self, p):
        beginnings = getattr(p, 'beginnings', [])
        endings =  getattr(p, 'endings', [' '])
        return make_word(p.letters, beginnings, endings)

    @_('PUNCT_BEGIN beginnings')
    def beginnings(self, p):
        return [p.PUNCT_BEGIN] + p.beginnings
    
    @_('PUNCT_BEGIN')
    def beginnings(self, p):
        return [p.PUNCT_BEGIN]
    
    @_('endings NEWLINE')
    def endings(self, p):
        if p.endings[-1] != ' ':
            p.endings.append(' ')
        return p.endings
    
    @_('endings PUNCT_END')
    def endings(self, p):
        return p.endings + [p.PUNCT_END]
    
    @_('PUNCT_END')
    def endings(self, p):
        return [p.PUNCT_END]
        
    @_('LETTER letters', 
       'FOREIGN_LETTER letters')
    def letters(self, p):
        return [p[0]] + p[1]
    
    @_('LETTER', 
       'FOREIGN_LETTER')
    def letters(self, p):
        return [p[0]]

# run the parses on the supplied file
lexer = NenaLexer()
parser = NenaParser()

with open(file_to_parse, 'r') as infile:
    file_raw_text = infile.read()
    parsed_text = parser.parse(lexer.tokenize(file_raw_text))

print(json.dumps(parsed_text, indent=2, ensure_ascii=False))
