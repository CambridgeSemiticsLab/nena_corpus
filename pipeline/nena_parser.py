"""
Yacc-style lexer and parser for NENA Markup texts with Sly

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
import json
from sly import Lexer, Parser
import unicodedata as ucd
from pathlib import Path

class Configs:
    """Provide configs for the Lexer/Parser definitions.
    
    Configs for the lexer/parser are stored in various JSON
    files, all linked to by a single config file. These various
    sub-config files contain a lot of regex patterns used by 
    the lexer to recognize the various tokens. 
    These patterns need to be preprocessed in three main ways:

        1. basic patterns simply read in and stored as a definition
            (e.g. the regex for a span tag)
        2. a set of patterns that needs to be pipe-joined for 
            set-based regex matching (e.g. pipe-separated letters in 
            the alphabet)
        3. a set of patterns that are precompiled using re.compile; 
            these are used especially for group matching to extract
            data from the tags (e.g. get the language code out of a
            language tag)

    These three methods are accomplished with self.defitions, 
    self.piped_regex, and self.compiled_regex and stored as
    attributes of the class. The returned data are dictionaries
    keyed by the name of the patterns (e.g. self.piped_regex['alphabet'])
    """

    def __init__(self, configdict):
        # load config file
        self.config = configdict 
        self.definitions = self.load_all_jsons(self.config)
        self.piped_regex = self.pipe_regexs(self.definitions)
        self.compiled_regex = self.compile_regexs(self.definitions)

    def load_json(self, path):
        """Load a JSON file."""
        with open(path, 'r') as infile:
            return json.load(infile)

    def load_all_jsons(self, configdata):
        """Load all JSON files."""
        data = {}
        for key, val in configdata.items():
            if val.endswith('.json'):
                data[key] = self.load_json(val)
        return data

    def compile_regexs(self, data, do_key=['markup_tags']):
        """Compile regular expressions for efficient matching."""
        compregs = {}
        for key in do_key:
            compregs[key] = {
                name:re.compile(pattern)
                    for name, pattern in data[key].items()
            }
        return compregs

    def pipe_regexs(self, data, do_keys=['alphabet', 'punct_begin', 'punct_end']):
        """Wrangle regex data into set of dicts for use."""
        piped_regexs = {}
        for key in do_keys:
            keydata = data[key]
            piped = '|'.join(keydata[c]['regex'] for c in keydata)
            piped_regexs[key] = piped
        return piped_regexs

def NenaLexerParser(configdict):
    """Wrapper for Lexer and Parser instantiations.

    Sly Lexer and Parser objects infer several of their parameters directly
    from the class definition itself rather than from the __init__
    parameters. For example, the tokens are defined as a set of variables,
    whose identity is established when the class is compiled by Python. 
    This is un-Pythonic, and it makes it hard to define parameters
    on the fly from a specified source as we want to do here. For
    instance, it should be easy to feed in a config file and have the 
    tokens identified from patterns in that file. But this is not possible 
    unless the definitions are already in the namespace. This is undesirable
    if we want to load the classes in another module without any run time 
    at import.

    To get around this problem, we provide a function which gives a 
    namespace for the class definitions, so that the varibles can be 
    established dynamically when the function is called, and based on
    the input to the function (in this case the config file).
    An instanced version of the newly-defined class is returned 
    when the function is executed.

    Args:
        configfile: string pointing to a config JSON, itself containing
            paths to definitions (regex patterns, transcription replacements, etc.)
    Returns:
        instanced NenaLexer and NenaParser classes (see below for definition)
    """

    # read in and pre-process all of the necessary configs
    configs = Configs(configdict)
    defs = configs.definitions
    ppr = configs.piped_regex
    cpr = configs.compiled_regex

    # define the lexer by inheriting the Sly Lexer object;
    # token pattern matches defined using decorators (@_) 
    # with definitions established by configs
    class NenaLexer(Lexer):
        
        def __init__(self):
            super().__init__()
            self.dialect = None
       
        def error(self, t):
            """Give warning for bad characters"""
            raise Exception(f"Illegal character {repr(t.value[0])} @ index {self.index}")
        
        # set of token names as required by Sly the Lexer class;
        # NB that these variables have not yet been defined (!)
        # yet this is the method required by the Sly Lexer. A 
        # syntax error does not occur because of under-the-hood
        # work-arounds in the Sly Lexer object (made by the developer)
        tokens = {
            LETTER, PUNCT_BEGIN, PUNCT_END, NEWLINES,
            NEWLINE, SPAN_TAG, ATTRIBUTE, 
            FOREIGN_LETTER, LANG_START, LANG_END        
        }
    
        # ------------------PATTERN MATCHING------------------
        # from this point forward, patterns for matching tokens 
        # are defined using either decorators with function definitions
        # or simple variable definitions; the decorators specify regex
        # patterns as retrieved from the configs, which are in turn used
        # for matching the given item; the functions tell Sly Lexer what to 
        # do with the matched token, fed in as a Token object (t) with 
        # a value attribute that can be modified 

        # Metadata is broken down into specific attributes 
        @_(defs['markup_tags']['text_meta'])
        def ATTRIBUTE(self, t):

            # match field and value with groups
            field, value = (
                cpr['markup_tags']['text_meta'].match(t.value).groups()
            )

            # recognize speakers 
            if field == 'speakers':
                speakers = {}
                for speakset in value.split(','):
                    initials, speaker = speakset.split('=')
                    speakers[initials.strip()] = speaker.strip()
                value = speakers
                    
            # set dialect
            if field == 'dialect':
                self.dialect = value 

            # set the token value
            t.value = {field:value}

            return t
        
        # span tags can contain timestamp, linenumber, or speaker updates;
        # individual fields are space-separated
        @_(defs['markup_tags']['span_tag'])
        def SPAN_TAG(self, t):

            # define dict to hold span data
            attribs = {'class': 'span'}

            # process elements inside the tags
            elements = (
                cpr['markup_tags']['span_tag'].match(t.value).group(1)
            )
            elements = elements.split() # split on spaces
            for element in elements:
                if cpr['markup_tags']['timestamp'].match(element):
                    attribs['timestamp'] = element
                elif cpr['markup_tags']['linenum'].match(element):
                    attribs['line_number'] = element
                elif cpr['markup_tags']['speaker'].match(element):
                    attribs['speaker'] = element
                else:
                    raise Exception(
                        f'invalid element {element} '
                        f'in line indicator {t.value}'
                    )
            t.value = attribs
            return t
        
        # define simple match patterns for newlines
        # NB: that order here matters; first matched first
        # the reason for treating newlines/newline separately is that 
        # 2+ newlines indicate a new paragraph (or alternatively
        # the transition between the attribute block and the text block),
        # whereas a single newline is treated as a space (or a separator
        # between attributes in the attribute block)
        NEWLINES = defs['markup_tags']['newlines']
        NEWLINE = defs['markup_tags']['newline']
        
        # recognize letters in the normal alphabet;
        # separate value into a dict; this is to 
        # accommodate the foreign letter detection 
        # later on (see below), where the letter's 
        # 'class' key will be checked for foreign 
        # status in order to tag the whole word
        @_(ppr['alphabet'])
        def LETTER(self, t):
            t.value = {'text': t.value, 'class': 'letter'}
            return t
        
        # recognize punctuators assigned to beginning of word
        @_(ppr['punct_begin'])
        def PUNCT_BEGIN(self, t):
            return t
        
        # recognize punctuators assigned to end of word
        @_(ppr['punct_end'])
        def PUNCT_END(self, t):
            return t
        
        # foreign language beginning tag
        @_(defs['markup_tags']['lang_start'])
        def LANG_START(self, t):
            lang = cpr['markup_tags']['lang_start'].match(t.value).group(1)
            tag = t.value.strip()
            t.value = {
                'class': 'LANG_START', 
                'text': tag, 'lang': lang
            }
            return t
            
        # foreign language ending tag 
        @_(defs['markup_tags']['lang_end'])
        def LANG_END(self, t):
            t.value = {'class': 'LANG_END', 'text': t.value}
            return t
        
        # recognize letters that are not part of the canonical alphabet;
        # these are often found in foreign words for example
        # NB: tokens evaluated in order of appearance here
        # thus foreign string matched lastly
        @_(defs['markup_tags']['foreign_letter'])
        def FOREIGN_LETTER(self, t):
            t.value = {'class':'foreign', 'text': t.value}
            return t

    # define the parser class; NB that tokens depends on 
    # the NenaLexer definitions a run-time;
    # a shift-reduce debug file is written out to the 
    # parse_debug as configured in config.json
    # For more info on the syntax used for these patterns, 
    # see the Yacc docs linked to at the beginning of this file
    class NenaParser(Parser):
        
        def __init__(self):
            super().__init__()
        
        debugfile = configs.config['parse_debug']
        tokens = NenaLexer.tokens
        
        def error(self, t):
            """Raise error when pattern is unrecognized."""
            raise Exception(
                f'unexpected {t.type} ({repr(t.value)}) '
                f'at index {t.index}'
            ) 

        def make_word(self, letters, beginnings=[], endings=[]):
            """Build word data."""

            word_string = ''.join(l['text'] for l in letters)
            word_data = {
                'class': 'word',
                'string': word_string,
                'letters': [l['text'] for l in letters],
                'beginnings': beginnings,
                'endings': endings,
                'foreign': False,
            }

            # assign word a foreign status if it contains unknown letters
            letter_classes = set(l['class'] for l in letters)
            if 'foreign' in letter_classes:
                word_data['foreign'] = True

            # NB: Here is the place to add any grammatical word parsing
            # in the future. The example below is now defunct, but it is
            # kept here as an example:
            # word_data['parsings'] = parse_word(word_string, self.dialect)

            return word_data
            
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
        
        # words are recognized through a number of begin/end
        # punctuator combinations with a string of letters
        @_('beginnings letters endings', 
           'letters endings',
           'letters NEWLINE',
           'letters NEWLINE endings',
           'beginnings letters NEWLINE',
           'beginnings letters NEWLINE endings',
          )
        def word(self, p):
            beginnings = getattr(p, 'beginnings', [])
            default_end = ' '
            endings =  getattr(p, 'endings', [default_end])
            return self.make_word(p.letters, beginnings, endings)

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
            if p.endings[-1] != ' ':
                new_end = ' '
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

    # give back the newly-defined and instanced Lexer & Parser classes
    return NenaLexer(), NenaParser()
