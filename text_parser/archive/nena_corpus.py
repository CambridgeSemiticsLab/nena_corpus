import re
import unicodedata
import lxml.html


class Text:
    """Text with style annotations."""
    
    def __init__(self, dialect=None, filename=None,
                 p_type=None, default_style=''):
        self.dialect = dialect
        self.filename = filename
        self.type = p_type
        self._text = []
        self._default_style = default_style
        self.last_style = self._default_style
    
    def __getitem__(self, index):
        return self._text[index]
    
    def __iter__(self):
        return iter(self._text)
    
    def __bool__(self):
        return bool(self._text)
    
    def __len__(self):
        return len(self._text)
    
    def __str__(self):
        return ''.join(s for s, t in self._text)
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {repr(self.type)} {repr(self.__str__())}>'
    
    def append(self, text, text_style=None):
        """Append tuples of (text, text_style) to list.
        
        Concatenates consecutive strings with the same
        text_style.
        """
        if text_style is None:
            text_style = self._default_style
            
        if self._text and self._text[-1][1] == text_style:
            text = self._text[-1][0] + text
            self._text[-1] = (text, text_style)
        else:
            self._text.append((text, text_style))

        self.last_style = text_style


#
def get_child_text(e, tags=None):
    """Yield text from child nodes recursively."""
    
    style = get_style(e)
    
    if e.text:
        yield (e.text, style)
        
    for c in e.getchildren():
        # recursive call
        for text, text_style in get_child_text(c, tags):
            yield (text, text_style)
        
        # The puzzling part here (for me) was the
        # 'tail', being text inside an element
        # following a child element, e.g.:
        # <b>bold <i>bold italic</i> bold</b>
        # the ' bold' following the </i> tag.
        # Thanks go to:
        # https://stackoverflow.com/a/41359368/9230612
        if c.tail:
            yield (c.tail, style)

def get_style(e):
    """Return style of inner html elements."""
    
    # Footnote anchors in the text are in <a> tags with attributes:
    # class="sdfootnoteanc" name="sdfootnote{n}anc" href="#sdfootnote{n}sym"
    # Footnote symbols before the actual footnote are in <a> tags with:
    # class="sdfootnoteanc" name="sdfootnote{n}sym" href="#sdfootnote{n}anc"
    # Actual footnotes are wrapped in <div> with "id=sdfootnote{n}"
    def fn_class(e, a_class):
        return ([a.attrib['name'][:-3]
                 for a in e.xpath('ancestor-or-self::a')
                 if a.attrib.get('class', '') == a_class]+[''])[0]
    
    def has_tag(e, tag):
        return e.tag == tag or bool(e.xpath(f'ancestor::{tag}'))

    if fn_class(e, 'sdfootnoteanc'):
        style = 'fn_anchor'
    elif fn_class(e, 'sdfootnotesym'):
        style = 'fn_symbol'
    elif has_tag(e, 'sup'):
        style = 'super'
    elif has_tag(e, 'i'):
        style = 'italic'
    else:
        style = ''
    
    return style

def get_paragraph_type(e):
    """Return paragraph type for outer elements <h> <p> and <div>."""
    
    if e.tag == 'p':
        p_type = 'p'
    elif e.tag in ('h1', 'h2'):
        p_type = e.attrib.get('class', '')
    elif e.tag == 'div':
        p_type = e.attrib.get('id', '') or e.attrib.get('title', '')
    else:
        p_type = ''
    
    return p_type

def clean_text(paragraph, replace=None, ignore=None):
    """Normalize unicode and replace or ignore certain characters."""
    
    p_whitespace = re.compile(r'\s+')
    
    oldtext = paragraph._text
    paragraph._text = []
    paragraph.last_style = paragraph._default_style
    
    for text, text_style in oldtext:
        
        text = unicodedata.normalize('NFD', text)
        
        text = p_whitespace.sub(' ', text)

        if replace is not None:
            for c in replace:
                text = text.replace(c, replace[c])

        if ignore is not None:
            for c in ignore:
                text = text.replace(c, '')

        paragraph.append(text, text_style)
        
def clean_styles(paragraph):
    """Remove unnecessary styles from Text paragraph.

    There are only two meaningful style decorations in the
    Word document: superscript, for text markers; and roman
    style, for 'foreign' words and text comments.
    All styles applied to anything that is not text, is
    redundant, since the non-text characters themselves are
    unambiguous.
    After extraction from the HTML, the 'text_style'
    attribute contains the HTML styles 'italic', 'super',
    or '' (unmarked). Normal Aramaic text is set in 'italic'
    type, and foreign words are set apart by being unmarked.
    To simplify things, we will set an 'unmarked' text_style
    on all non-letter characters and all 'italic' characters;
    a 'marker' text_style on all letter characters with
    text_style 'super', and a 'foreign' text_style on all
    'unmarked' letter characters.

    Exceptions: in some cases a letter is set in superscript
    without being a marker. This happens to alaph, as a typo,
    since superscript alaph does not look much different from
    regular alaph; and to y, which is apparently a distinct
    character, appearing several times, always after 'g' or 'k'.
    """

    def is_letter(c):
        """Return True if c is Letter or Marker, False otherwise"""
        return unicodedata.category(c)[0] in ('L', 'M')

    oldtext = paragraph._text
    paragraph._text = []
    paragraph.last_style = paragraph._default_style

    for text, text_style in oldtext:

        # first look for combining characters at beginning of text,
        # which should always be added to the end of the previous
        # text (unless it does not follow a character)
        while text and unicodedata.category(text[0]) == 'Mn':
            paragraph.append(text[0], paragraph.last_style)
            text = text[1:]

        if text_style == 'italic':
            paragraph.append(text, '')
        elif text_style in ('', 'super'):
            letter_style = 'marker' if text_style else 'foreign'
            for c in text:
                # EXCEPTION for superscript alaph,
                # it is always a mistake
                if c == '\u02be' and text_style == 'super':
                    paragraph.append(c, '')
                # EXCEPTION y in superscript is a distinct
                # character. Replace for now by superscript 'y'
                elif c == 'y' and text_style == 'super':
                    paragraph.append('\u02b8', '')
                elif is_letter(c):
                    # connect lonely alaphs to next word
                    # EXCEPTION
                    if paragraph._text[-1][0] == '\u02be':
                        paragraph._text.pop()
                        c = '\u02be' + c
                    paragraph.append(c, letter_style)
                else:
                    paragraph.append(c, '')
        elif text_style in ('fn_anchor', ):
            paragraph.append(text, text_style)
        else:
            raise ValueError('Unexpected `text_style`:', text_style)

def mark_verse_numbers(paragraph):
    """Mark verse numbers.

    Give verse numbers of the form ' (12) ' the text_style 'verse_no'.
    """

    # regex pattern for verse numbers
    p_verse_no = re.compile('(\s*\([0-9]+\)\s*)')

    oldtext = paragraph._text
    paragraph._text = []
    paragraph.last_style = paragraph._default_style

    for text, text_style in oldtext:
        if text_style == '':
            for i, t in enumerate(p_verse_no.split(text)):
                if t and i % 2:
                    paragraph.append(t, 'verse_no')
                elif t:
                    paragraph.append(t, text_style)
                else:
                    pass
        else:
            paragraph.append(text, text_style)

def mark_comments(paragraph):
    """Mark comments (foreign words surrounded by brackets)"""

    # regex pattern for brackets
    p_brackets = re.compile('([\[\]()])')

    oldtext = paragraph._text
    paragraph._text = []
    paragraph.last_style = paragraph._default_style

    for text, text_style in oldtext:
        # brackets are only found in unmarked text
        if text_style == '':
            for i, t in enumerate(p_brackets.split(text)):
                if t and i % 2:
                    paragraph.append(t, 'comment')
                elif t:
                    if (paragraph.last_style == 'comment'
                            and t.startswith(': ')):
                        prev_text, prev_style = paragraph._text.pop()
                        paragraph.append(prev_text + ': ', prev_style)
                        t = t[1:]
                    paragraph.append(t, text_style)
                else:
                    pass
        elif text_style == 'foreign' and paragraph.last_style == 'comment':
            paragraph.append(text, 'comment')
        else:
            paragraph.append(text, text_style)

# nested tuple with regexes for parse_metadata()
# Examples of different patterns to match:
# Barwar:
# <Text 'gp-sectionheading-western' 'A14 TALES FROM THE 1001 NIGHTS'>
# <Text 'gp-subsectionheading-western' 'Informant: Yuwarəš Xošăba Kena (Dure)'>
# Urmi C:
# <Text 'gp-sectionheading-western' ' A34'>
# <Text 'gp-subsectionheading-western' ' The Fisherman and the Princess (Nancy George, Babari, S)'>
# Urmi C with category heading:
# <Text 'gp-sectionheading-western' 'FOLKTALES'>
# <Text 'gp-sectionheading-western' ' '>
# <Text 'gp-sectionheading-western' ' A 1'>
# <Text 'gp-subsectionheading-western' ' The Bald Man and the King (Yulia Davudi, +Hassar +Baba-čanɟa, N)'>
# and:
# <Text 'gp-sectionheading-western' ' '>
# <Text 'gp-sectionheading-western' 'HISTORY AND CULTURE'>
# <Text 'gp-sectionheading-western' 'B1'>
# <Text 'gp-subsectionheading-western' ' The Assyrians of Urmi (Yosəp bet Yosəp, Zumallan, N)'>
# Urmi C with two versions:
# <Text 'gp-sectionheading-western' ' A35'>
# <Text 'gp-subsectionheading-western' ' The Wife who Learns How to Work'>
# <Text 'gp-subsubsectionheading-western' 'Version 1: Nancy George (Babari, S)'>
# <Text 'gp-subsubsectionheading-western' 'Version 2: Yulia Davudi (+Hassar +Baba-canɟa, N)'>

heading_regexes = (
    ('gp-sectionheading',
     # Barwar: text id and title
     ((('text_id', 'title'),
       re.compile('^\s*([A-Z]\s*[0-9]+)\s+(.*?)\s*$')),
      # Urmi_c: text id
      (('text_id',),
       re.compile('^\s*([A-Z]\s*[0-9]+)\s*')),
     )),
    ('gp-subsectionheading',
     # Barwar: informant and place
     ((('informant', 'place'),
       re.compile('^\s*Informant:\s+(.*)\s+\((.*)\)\s*$')),
      # Urmi_C: title, informant, place
      (('title', 'informant', 'place'),
       re.compile('^\s*(.*?)\s*\(([^,]*),\s+(.*)\)\s*$')),
      # Urmi_c: title only
      (('title',),
       re.compile('^\s*(.*?)\s*$')),
     )),
    ('gp-subsubsectionheading',
     # Urmi-C: version, informant, place
     ((('version', 'informant', 'place'),
       re.compile('^\s*(Version\s+[0-9]+):\s+(.*?)\s+\((.*)\)\s?$')),
     )),
)

def parse_metadata(heading, heading_regexes=heading_regexes):
    """Extract metadata from headings

    Arguments:
        heading (Text): Text object of heading
        heading_regexes: nested tuple with regexes:
            ((str:headingtype, tuple:regexes), ...)
            regexes:
                ((tuple:keys, compiled_regex), ...)
                keys:
                    (str:key, ...)
    Returns:
        list of metadata tuples: [(key, value), ...]
    """

    result = []
    for heading_type, regexes in heading_regexes:
        if heading.type.startswith(heading_type):
            for keys, regex in regexes:
                try:
                    matched_groups = regex.match(str(heading)).groups()
                    result = list(zip(keys, matched_groups))
                    break
                except AttributeError:
                    continue
            break
    return result

def html_to_text(html_file, dialect=None, filename=None,
                 markers=None, replace=None, skip_front_matter=True):
    """Yield Text objects generated from the HTML in html_file"""
    
    with open(html_file) as f:
        html = f.read()
    tree = lxml.html.fromstring(html)
    
    def is_sectionheading(e):
        """Return true if e is a non-empty sectionheading."""
        return (e.tag == 'h2'
                and e.text.strip()
                and e.attrib.get('class', '') == 'gp-sectionheading-western')

    start = False
    for e in tree.xpath('/html/body/*'):
        
        # skip all elements before the first non-empty sectionheading
        # (relevant especially for Urmi texts, this skips front matter)
        if start is False and skip_front_matter:
            if is_sectionheading(e):
                start = True
            else:
                continue

        p_type = get_paragraph_type(e)
        p = Text(dialect=dialect, filename=filename,
                 p_type=p_type, default_style='italic')

        for text, text_style in get_child_text(e):
            p.append(text, text_style)
            
        clean_text(p, replace=replace)

        if p.type == 'p':
            clean_styles(p)
            mark_verse_numbers(p)
            mark_comments(p)

        
        yield p
