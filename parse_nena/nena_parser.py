"""
NENA Parser

credit: Hannes Vlaardingerbroek
updates/refinements added by Cody Kingham

This is a work in progress.
Copied from the NenaParser.ipynb. -CK 2019-11-11 
"""

from sly import Lexer, Parser

class Morpheme:
    
    def __init__(self, value, trailer='',
                 footnotes=None, speaker=None,
                 foreign=False, lang=None):
        self.value = value  # list of (combined) characters
        self.trailer = trailer  # str (TODO: make this a list as well?)
        self.footnotes = footnotes if footnotes is not None else {}  # dict
        self.speaker = speaker  # str
        self.foreign = foreign  # boolean
        self.lang = lang  # str
    
    def __str__(self):
        return ''.join(self.value)
    
    def __repr__(self):
        sp = f' speaker {self.speaker!r}' if self.speaker else ''
        fr = ' foreign' if self.foreign else ''
        ln = f' lang {self.lang!r}' if self.lang else ''
        fn = f' fn_anc {",".join(str(n) for n in self.footnotes)!r}' if self.footnotes else ''
        fn = f' fn_anc {self.footnotes!r}' if self.footnotes else ''
        return f'<Morpheme {str(self)!r} trailer {self.trailer!r}{sp}{fr}{ln}{fn}>'

# regex for punctuation which is used 
# to also exclude punctuation from letters categories
# TODO: Implement char tables instead
punct = '.,?!:;–\u02c8\u2014\u2019\u2018'

class NenaLexer(Lexer):
    
    # set of token names
    tokens = {
        TITLE, ATTRIBUTE, LETTER, NEWLINES, SPACE,
        PUNCTUATION, HYPHEN,
        LPAREN_COMMENT, LBRACKET_COMMENT, DIGITS,
        LANG_MARKER, COMMENT, FOOTNOTE
    }
    
    # NB \u207A == superscript +
    literals = {'*', '(', ')', '{', '}', '[', ']', '/', '^'}

    # The '(?m)' part turns on multiline matching, which makes
    # it possible to use ^ and $ for the start/end of the line.
    # Title starts with pound sign. Returns 2-tuple (key, value).
    @_(r'(?m)^\# .*$')
    def TITLE(self, t):
        t.value = ('title', t.value[2:])
        return t

    # Attribute starts key and colon. Returns 2-tuple (key, value).
    @_(r'(?m)^[a-z][a-z0-9_]+: .*$')
    def ATTRIBUTE(self, t):
        t.value = tuple(t.value.split(': '))
        return t
    
    # Footnote starts with '[^n]: ', where n is a number.
    # Returns a 2-tuple (int: fn_sym, str: footnote_text)
    @_(r'(?m)^\[\^[1-9][0-9]*\]: \D*$')
    def FOOTNOTE(self, t):
        fn_sym, footnote = t.value.split(maxsplit=1)
        t.value = (int(fn_sym[2:-2]), footnote)
        return t

    # Punctuation is any normal punctuation symbol and vertical bar.
    # as well as a long hyphen (—)
    
    PUNCTUATION = f'[{punct}]'
    
    # How to get combined Unicode characters to be recognized?
    # Matching only Unicode points of letters with pre-combined
    # marks can be done with the 'word' class '\w', but it
    # includes digits and underscore. To remove those, negate
    # the inverted word class along with digits and underscore:
    # '[^\W\d_]. But that does not include separate combining
    # marks, or the '+' sign.
    # One solution would be unicodedata.normalize('NFC', data),
    # except that not all combinations have pre-combined Unicode
    # points.
    # Another solution is to use an external regex engine such as
    # `regex` (`pip install regex`), which has better Unicode
    # support. However, I would like to avoid extra dependencies.
    # Another (less elegant) solution is to make the '+' symbol
    # and the combining characters [\u0300-\u036F] each its own
    # token, which the parser will have to parse into morphemes
    # and words.
    # Another (also less elegant) solution is to use a 'negative
    # lookbehind assertion' for the negation of digits and '_':
    # https://stackoverflow.com/a/12349464/9230612
    # (?!\d_)[\w\u0300-\u036F]+
    # Because combining marks can never appear before the first
    # letter, and because some dialects have a '+' sign at the
    # beginning of some words, we prefix an optional '+' symbol
    # and an obligatory '[^\W\d_]' before the negative lookbehind.
    
    # One letter with (or without) combining marks can be matched
    # with: [^\W\d_][\u0300-\u036F]*
    # We also add a superscript plus (U-207A) as part of a letter, 
    # since this char is not a letter on its own, but rather
    # modifies the quality of a consonant
    # PUNCTUATION is also excluded
    LETTER = f'[\u207A]?[^\W\d_{punct}][\u0300-\u036F]*'
    
    # we try to make a LETTERS token:
#     LETTERS = r'[+]?[^\W\d_](?!\d_)[\w\u0300-\u036F+]*'
    # Unfortunately, with python's `re` it seems impossible to repeat
    # a group like this. So we will group the letters in the parser.
    
    # Newlines: boundaries of paragraphs and metadata are marked
    # with two newlines (meaning an empty line). The empty line
    # may contain whitespace.
    NEWLINES = r'\n\s*\n\s*'
    
    # Space is any successive number of whitespace symbols.
    SPACE = r'\s+'
    # One or more digits, not starting with zero
    DIGITS = r'[1-9][0-9]*'
    # Line id is any number of digits surrounded by round brackets
#     LINE_ID = r'\([0-9]+\)'  # TODO convert to int?
    # There are two different hyphens, a single one and a double one.
    # The double one is the 'equals' sign.
    HYPHEN = r'[-=]'
    # Language markers are ASCII letter strings surrounded by
    # angle brackets.
    LANG_MARKER = r'<[A-Za-z]+>'
    # A special comment starts with an opening bracket, capital initials
    # and a colon.
    LPAREN_COMMENT = r'\([A-Za-z]+:'
    LBRACKET_COMMENT = r'\[[A-Za-z]+:'
    # A regular comment is text (at least one character not being a digit)
    # which may not contain a colon (otherwise it becomes a special comment/interruption)

    COMMENT = r'\([^:)]*[^:)\d]+[^:)]*\)'


# dict stack to contain footnote anchors,
# until the corresponding footnote is encountered.
fn_anchors = {}

class NenaParser(Parser):
    
    # Get the token list from the lexer (required)
    tokens = NenaLexer.tokens
    
    def error(self, t):
        #print('ERROR:')
        #print(f'\tunexpected string {repr(t.value[0])} at index {t.index}')
        raise Exception(f'unexpected string {repr(t.value[0])} at index {t.index}')
    
    @_('heading NEWLINES paragraphs')
    def text(self, p):
        return (p.heading, p.paragraphs)
    
    # -- HEADING --
    
    @_('SPACE TITLE NEWLINES attributes',
       'TITLE NEWLINES attributes')
    def heading(self, p):
        key, value = p.TITLE
        heading = {key: value}
        heading.update(p.attributes)
        return heading
    
    @_('attributes space ATTRIBUTE')
    def attributes(self, p):
        key, value = p.ATTRIBUTE
        p.attributes[key] = value
        return p.attributes 
    
    @_('ATTRIBUTE')
    def attributes(self, p):
        key, value = p.ATTRIBUTE
        return {key: value}
    
    # -- PARAGRAPHS --
    
    @_('paragraphs NEWLINES paragraph')
    def paragraphs(self, p):
        # handle cases of null footnotes
        if p.paragraph is not None:
            return p.paragraphs + [p.paragraph]
        else:
            return p.paragraphs
        
    @_('paragraph')
    def paragraphs(self, p):
        return [p.paragraph]
    
    # paragraph
    @_('paragraph line')
    def paragraph(self, p):
        return p.paragraph + [p.line]
    
    # paragraph from orphaned footnotes
    @_('footnotes')
    def paragraph(self, p):
        if p.footnotes:
            # TODO: issue log warning about
            # unreferenced footnotes?
            return ('footnotes', p.footnotes)
    
    # -- FOOTNOTES -- 
    
    @_('footnotes footnote')
    def footnotes(self, p):
        p.footnotes.update(p.footnote)
        return p.footnotes
    
    @_('footnote')
    def footnotes(self, p):
        return p.footnote
    
    @_('FOOTNOTE space NEWLINES',
       'FOOTNOTE NEWLINES',
       'FOOTNOTE space',
       'FOOTNOTE')
    def footnote(self, p):
        fn_sym, fn_str = p.FOOTNOTE
        footnote = {}
        try:
            # lookup the fn_sym key in the fn_anchors dict,
            # and add the footnote to the appropriate morpheme
            fn_morpheme = fn_anchors.pop(fn_sym)
            fn_morpheme.footnotes[fn_sym] = fn_str
        except KeyError:
            # This means there is not footnote anchor
            # referring to this footnote. So we return
            # the footnote to the text
            footnote = {fn_sym: fn_str}
        return footnote

    # -- LINES --
    
    @_('line')
    def paragraph(self, p):
        return [p.line]
    
    @_('line_id line_elements')
    def line(self, p):
        return (p.line_id, p.line_elements)
    
    @_('"(" DIGITS ")" SPACE')
    def line_id(self, p):
        return int(p.DIGITS)

    @_('line_elements line_element',
       'line_element')
    def line_elements(self, p):
        if len(p) == 2:
            return p.line_elements + p.line_element
        else:
            return p.line_element
    
    @_('morphemes',
       'fn_anchor',
       'interruption',
       'morphemes_foreign',
       'morphemes_language',
       'comment')
    def line_element(self, p):
        return p[0]
    
    # -- MORPHEMES -- 

    # morphemes_language
    @_('lang morphemes_foreign morpheme_trailer lang trailer',
       'lang morphemes_foreign lang trailer',
       'lang morphemes_foreign lang',
       'lang morphemes_foreign')
    def morphemes_language(self, p):
        # check if language markers correspond
        if len(p) > 2:
            lang = p.lang0
            if p.lang0 != p.lang1:
                pass  # TODO issue warning: language markers do not correspond
        else:
            lang = p.lang  # TODO issue warning: missing second language marker
        for m in p.morphemes_foreign:
            m.lang = lang
        if len(p) == 4:
            p.morphemes_foreign[-1].trailer += p.trailer
        elif len(p) == 5:
            p.morpheme_trailer.trailer += p.trailer
            p.morphemes_foreign.append(morpheme_trailer)
        return p.morphemes_foreign
    
    # lang
    @_('LANG_MARKER')
    def lang(self, p):
        return p.LANG_MARKER[1:-1]

    # morphemes_foreign
    # last morpheme may not include trailer
    # add trailer after second asterisk to last morpheme
    @_('"*" morphemes letters "*" trailer',
       '"*" morphemes letters "*"',
       '"*" letters "*" trailer',
       '"*" letters "*"',
      )
    def morphemes_foreign(self, p):
        try:
            trailer = p.trailer
        except KeyError:
            trailer = ''
        try:
            morphemes = p.morphemes
        except KeyError:
            morphemes = []
        morphemes.append(Morpheme(p.letters, trailer=trailer))
        for m in morphemes:
            m.foreign = True
        return morphemes
    
    # comment
    @_('COMMENT trailer',
       'COMMENT')
    def comment(self, p):
        return [('comment', p.COMMENT[1:-1])]

    # interruption
    @_('LPAREN_COMMENT space morphemes ")" trailer',
       'LPAREN_COMMENT space morphemes ")"',
       'LBRACKET_COMMENT space morphemes "]" trailer',
       'LBRACKET_COMMENT space morphemes "]"')
    def interruption(self, p):
        speaker = p[0][1:-1]
        for m in p.morphemes:
            m.speaker = speaker
        try:
            trailer = p.trailer
            if (p.morphemes[-1].trailer.endswith(' ')
                and trailer.startswith(' ')):
                trailer = trailer[1:]
            p.morphemes[-1].trailer += trailer
        except KeyError:
            pass
        return p.morphemes
    
    # morphemes
    @_('morphemes morpheme_trailer',
       'morpheme_trailer')
    def morphemes(self, p):
        if len(p) == 2:
            return p.morphemes + [p.morpheme_trailer]
        else:
            return [p.morpheme_trailer]
    
    # -- MORPHEME ATTRIBUTES --
    
    # morpheme_trailer
    @_('letters trailer',
       'letters')
    def morpheme_trailer(self, p):
        if len(p) == 2:
            trailer = p[1]
        else:
            trailer = ''
        return Morpheme(p.letters, trailer=trailer)

    # morpheme_trailer with footnote anchor
    @_('morpheme_trailer fn_anchor trailer',
       'morpheme_trailer fn_anchor')
    def morpheme_trailer(self, p):
        if len(p) == 3:
            if (p.morpheme_trailer.trailer.endswith(' ')
                and p.trailer.startswith(' ')):
                p.trailer = p.trailer[1:]
            p.morpheme_trailer.trailer += p.trailer
        # add dummy value {fn_anc: None} to footnote dict
        p.morpheme_trailer.footnotes[p.fn_anchor] = None
        # add morpheme object to fn_anchors dict,
        # for easy access when footnote text is found
        fn_anchors[p.fn_anchor] = p.morpheme_trailer
        return p.morpheme_trailer
    
    # --VARIOUS--
    
    @_('"[" "^" DIGITS "]"')
    def fn_anchor(self, p):
        return int(p.DIGITS)
        
    @_('letters LETTER')
    def letters(self, p):
        return p.letters + [p.LETTER]
    
    @_('LETTER')
    def letters(self, p):
        return [p[0]]
    
    # trailer
    @_('trailer versebreak',
       'trailer linebreak',
       'trailer PUNCTUATION',
       'trailer space',
       'PUNCTUATION',
       'space',
       'HYPHEN',
      )
    def trailer(self, p):
        return ''.join(p)
    
    # -- LITERALS --
    
    # reduce any number of spaces (\s+)
    # to a single space (' ')
    @_('SPACE')
    def space(self, p):
        return ' '
    
    @_('"/" "/"',
       '"/" "/" space',
       '"/" "/" NEWLINES',
       '"/" "/" space NEWLINES')
    def versebreak(self, p):
        return '//'
    
    @_('"/"',
       '"/" space',
       '"/" NEWLINES',
       '"/" space NEWLINES')
    def linebreak(self, p):
        return '/'
