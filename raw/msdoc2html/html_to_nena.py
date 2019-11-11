import re
from pathlib import Path
import collections
import unicodedata
import lxml.html
# for title capitalzation with apostrophes:
# https://stackoverflow.com/questions/8199966/python-title-with-apostrophes
import string


class Text:
    """Text with style annotations."""

    # TODO subclass UserList instead?    
    def __init__(self, elements=None, default_style=None):
        self._text = []
        self._default_style = default_style
        self.last_style = self._default_style

        if elements is not None:
            for text, text_style in elements:
                self.append(text, text_style)
    
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
        return f'<{self.__class__.__name__} {repr(self.__str__())}>'

    def pop(self, *args):
        return self._text.pop(*args)
    
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

        
def html_todict(html_file, xpath=None, ignore_empty=True,
                  heading_patterns=None, replace=None,
                  text_start=None, text_end=None,
                  e_filter=None, is_heading=None,
                  style_map={}, style_char_map={}):
    """Convert HTML file to standard NENA text format.
    Store texts in title:markdown dictionary.

    Arguments:
        html_file (str or pathlib.Path): path to HTML file.

        xpath (str): XPath expression for elements to be processed.
            See `html_elements()` for default and details.

        ignore_empty (boolean): if True, elements which are
            empty (i.e. apart from whitespace characters)
            are ignored.

        heading_patterns (dict): Dictionary with keys and regex
            patterns to extract metadata from headings. See
            `parse_metadata` for details.

        replace (dict): Dictionary with substrings to be replaced
            and the strings to replace them. See `str_replace`.

        text_start (function): A function accepting an HtmlElement,
            and returning a boolean value, deciding if the element
            marks the start of the text.
        
        text_end (function): Function accepting an HtmlElement,
            and returning a boolean value, deciding if the element
            marks the end of the text.

        e_filter (function): Function accepting an HtmlELement,
            returning a boolean value, deciding whether to skip
            the element or not.

        is_heading (function): Function accepting an HtmlELement,
            returning True if it is a heading, or False if not.

    Returns:
        dict: title:string with text in standard NENA text format.
    """

    metadata = {'source': Path(html_file).name}
    meta_updated = False
    started = True if text_start is None else False
    
    # title:markdown mapped here where title == text title
    # duplicate title checks operate on this dict as well
    # default dict means that we can simply compile in place
    # based on the title without need to reset the string each new text
    title2nena = collections.defaultdict(str)
    title2para = collections.defaultdict(list)

    for e in html_elements(html_file):

        # First some checks to see whether to process the element
        if not started and text_start(e):
            started = True
        if text_end is not None and text_end(e):
            break
        elif (
            not started
            or (ignore_empty and not e.text_content().strip())
            or (e_filter is not None and e_filter(e))
        ): continue

        # Process element
        if is_heading is not None and is_heading(e):

            # before updating, delete 'version' key if exists, as
            # most text don't have it so it will not be updated
            if 'version' in metadata:
                del metadata['version']
            fields = parse_metadata(e, patterns=heading_patterns)

            # set text's title to map converted markdown to
            if 'title' in fields:
                
                title = fields['title']
                title = make_unique_title(title, title2nena) 

                # fix capitalization
                title = string.capwords(title)
                fields['title'] = title                

                print(f'\tmaking [{title}]')

            # update the text fields
            if fields:
                metadata.update(fields)
                meta_updated = True
        else:
            # concat text header if metadata is updated
            if meta_updated:
                
                # assign title to last title with version number
                if 'title' not in metadata:
                    metadata['continued_from'] = title 
                    title = make_unique_title(title, title2nena) 
                    metadata['title'] = title
                    print(f'\tmaking [{title}]')
               
                title2nena[title] += meta_tostring(metadata)
                title2nena[title] += '\n' # newline after metadata
                meta_updated = False
                metadata = {'source': metadata['source']} # reset metadata

            # save paragraphs for addition of newline elements
            title2para[title].append(parse_element(
                e, 
                replace=replace,
                style_map=style_map,
                style_char_map=style_char_map,
                e_filter=e_filter,
            ))

    # format and add paragraphs to each text
    # all paragraphs for a text must be collected before this 
    # stage can be done, to allow for contextual choices about 
    # newline additions
    for title, paras in title2para.items():
        title2nena[title] += paragraph_newline(paras)

    return title2nena # give dict

def paragraph_newline(paragraphs):
    """Format newlines for paragraphing"""

    # Put new paragraphs here; will be joined on ''
    newlined_ps = ['']

    first_footnote = True
    line = re.compile('\(\d\d*\)')
    poet_line = re.compile('/\n')
    footnote_line = re.compile('\[\^\d\d*\]:')

    for i, para in enumerate(paragraphs):
        prev_p = newlined_ps[-1] 
        next_p = paragraphs[i+1] if i+1 < len(paragraphs) else '' 
        next2_p = paragraphs[i+2] if i+2 < len(paragraphs) else ''

        # handle poetic blocks with line indicators with slash and newline
        if (line.match(para)
            and not line.match(next_p)
            and not footnote_line.match(next_p)
            and next_p):
            newlined_ps.append(para + ' /\n')

        # add poetic line break situation 2 
        elif (not line.match(para) 
              and not footnote_line.match(para)
              and line.match(next_p)
              and not line.search(next2_p) 
              and next2_p):
            newlined_ps.append(para + ' /\n')

        # add poetic line break sit 3
        elif (not line.match(para) 
              and not footnote_line.match(para)
              and not line.match(next_p)
              and next_p):
            newlined_ps.append(para + ' /\n')
            
        # distinguish footnote block with double newlines
        elif footnote_line.match(para) and first_footnote:
            newlined_ps.append(para + '\n')
            first_footnote = False

        # handle all other paragraphs
        elif i+1 != len(paragraphs):
            newlined_ps.append(para + '\n\n')

        # attach last element without newlines
        else:
            newlined_ps.append(para)

    return ''.join(newlined_ps).strip()

def make_unique_title(title, title_dict):
    """Appends number to title for duplicates"""
    num = 1
    base_title = title
    while title_dict.get(title):
        num += 1
        title = f"{base_title} ({num})"
    return title


def html_elements(html_file, xpath=None):
    """Generator yielding HtmlElements from html_file.

    Arguments:
        html_file (str or pathlib.Path): path to HTML file.

        xpath (str): XPath pattern for elements to be yielded.

    Yields:
        lxml.html.HtmlElement: elements matching xpath pattern
    """

    if xpath is None:
        xpath = '/html/body/*'

    with open(html_file) as f:
        html = f.read()
    tree = lxml.html.fromstring(html)

    for e in tree.xpath(xpath):
        yield e

def parse_metadata(e, patterns):
    """Parse heading metadata

    Arguments:
        e (HtmlElement): html element containing header text
        
        patterns (dict): dictionary with as keys the 'class'
            attribute value the patterns apply to, and as values
            tuples, containing a tuple of keys, and a pattern
            string.
    
    Returns:
        A dictionary with the values from the HTML element mapped
        to the keys from the matching pattern. Returns an empty
        dictionary if there are no matches.
    
    Example:
        >>> import lxml.html
        >>> html = '<h2 class="chapter">1. First chapter</h2>'
        >>> e = lxml.html.fragment_fromstring(html)
        >>> patterns = {
        ...     'chapter': (
        ...         (('ch_num', 'ch_title'), '^(\d+)\. (.*)$'),
        ...     ),
        ... }
        >>> parse_metadata(e, patterns)
        {'ch_num': '1', 'ch_title': 'First chapter'}
    """
    
    result = {}
    e_class = e.attrib.get('class', '')
    text = ' '.join(e.text_content().split())
    
    for keys, pattern in patterns[e_class]:
        try:
            matches = re.match(pattern, text).groups()
            result = dict(zip(keys, matches))
            break
        except AttributeError:
            continue
    return result

def meta_tostring(metadata):
    """Convert the metadata dictionary to text header"""

    lines = []
    lines.append('# {}\n'.format(metadata.get('title', '')))
    for k, v in metadata.items():
        if k != 'title':
            lines.append(f'{k}: {v}')

    return '\n'.join(lines) + '\n'

def parse_element(e, replace=None, style_map={},
                  style_char_map={}, e_filter=None):
    """Parse HTML element to text string."""

    # Convert HTML element to Text object
    t = Text(element_totext(e, e_filter))
    
    # Normalize text styles
    if e.tag == 'p':
       t = normalize_styles(
            t,  
            style_map=style_map,
            style_char_map=style_char_map
        )
    else:
        t = normalize_styles(t, style_char_map=style_char_map)

    # Convert Text object to string with markup for styles
    s = text_tostring(t)

    # Replace substrings provided in `replace`
    if replace:
        s = str_replace(s, replace)

    # split string into lines,
    # and lines into strings with a maximum of 80 characters
    #s = '\n'.join(s for line in split_lines(s) for s in split_string(line))
    s = '\n'.join(split_string(s))

    # return text
    return s 

def element_totext(e, e_filter):
    """Yield (text, style) tuples from HTML element.
    
    Recursively traverses HTML element `e` and its child elements,
    yielding tuples with the contained text and a style string,
    which is provided by the function `get_style`.
    """

    e_filter = e_filter or (lambda e: False)
    e_style = get_style(e)

    if e.text and not e_filter(e):
        yield (e.text, e_style)

    for c in e.getchildren():
        # recursive call
        for text, style in element_totext(c, e_filter):
            yield (text, style)
        
        # Text following an embedded tag is the 'tail'
        # of that embedded tag. E.g. in
        #   <p>text <i>italic</i> tail</p>
        # the string ' tail' is in the  tail attribute
        # of the <i> element, and not at all in <p>.
        # https://stackoverflow.com/a/41359368/9230612
        if c.tail:
            yield(c.tail, e_style)

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
        style = 'fn_anc'
    elif fn_class(e, 'sdfootnotesym'):
        style = 'fn_sym'
    elif has_tag(e, 'sup'):
        style = 'sup'
    elif has_tag(e, 'i'):
        style = 'i'
    elif has_tag(e, 'b'):
        style = 'b'
    else:
        style = None

    return style

def is_letter(c):
    """Return True if c is Letter or Marker, False otherwise"""
    letter = re.compile(r'[^\W\d_]|[\u0300-\u036F]|\u207A')
    return bool(letter.match(c))

def normalize_styles(t, 
                     style_map={'i': 'emphasis','b': 'strong'}, 
                     style_char_map={}
                    ):
    """Normalize styles of Text object.

    Remap document styling according to a style map. 
    Styles not specified in the map are kept as-is.
    Use-case: when most font in a file is formatted with 
    italics, that style can be re-mapped to non-emphasis.

    Arguments:
        t (Text): Text object
        style_map (dict): mapping of a source text's style to its
            .nena representation style. The map is used to normalize
            formatting.
        style_char_map (dict): mapping of style to regex pattern where
            pattern matches valid characters for the given style.

    Returns:
        Text: Text object with normalized text styles.
    """

    new_t = Text()
    #new_t = []
    
    for text, style in t:
        
        style = style_map.get(style, style)
        
        def good_c(ch, style):
            # checks for valid style
            # defaults to True if style unspecified 
            ch_pat = re.escape(ch)        
            return bool(
                re.match(style_char_map.get(style, ch_pat), ch)
            )
            
        # check the validity of char styles
        # and update accordingly 
        for i, c in enumerate(text):            
                        
            # apply style if valid char
            if style and good_c(c, style):
                new_t.append(c, style)
           
            # apply no style
            else:
                new_t.append(c, None)
        
    fill_t = fill_gaps(new_t, good_c, fill=('strong', 'emphasis'))

    return fill_t        

def fill_gaps(t, good_c, fill=tuple()):
    """Fill style gaps.

    Styling is removed from invalid style chars.
    but this should not always be the case.
    For example, emphasis will be applied as follows:
        >> *Lós* *Àngeles*
    There is an unemphasized space between "Los" and "Angeles". 
    This is because spaces are not included in the style_char_map.
    This method handles this by looking for such gaps on
    specified styles.

    Arguments:
        t (Text): a Text object 
        good_c (function): Function that validates
            whether a given character belongs to a
            given style.
        fill (tuple): A tuple of styles that should 
            be filled. All others remain as-is.

    Returns:
        Text object.
    """
    fill_t = Text()
    
    for i,txtstyle in enumerate(t):
        
        text,style = txtstyle

        # skip beginning or end
        if (i < 1) or (i+1 == len(t._text)):
            fill_t.append(text, style)
            continue
                
        # check for gaps to fill
        before = fill_t[-1] if fill_t else ('', None)
        after = t[i+1] 
        
        if (
            style is None
            and before[1] in fill 
            and before[1] == after[1] 
            and not any(good_c(c, before[1]) for c in text)
        ):
            fill_t.append(text, before[1])
        else:
            fill_t.append(text, style)

    return fill_t

def text_tostring(t, default=None, emphasis='emphasis', strong='strong', sup='sup',
               fn_anc='fn_anc', fn_sym='fn_sym'):
    """Convert Text object to str.

    Mark all styled text with special characters and return str

    Example:
        >>> t = [('Unmarked text. ', None), ('Text marked "emphasis".', 'emphasis'),
        ...      (' ', None), ('R', 'sup'), ('not marked', None), ('R', 'sup'),
        ...      ('.', None)]
        >>> text_tostring(t)
        'Unmarked text. *Text marked "emphasis".* <R>not marked<R>.'
    """

    markers = {
        default: '{}',
        emphasis: '*{}*',
        strong: '**{}**',
        sup: '<{}>',
        fn_anc: '[^{}]',
        fn_sym: '[^{}]:',
    }
    s = ''.join(markers[style].format(text) for text, style in t)
    return ' '.join(s.split())

def str_replace(s, replace, msg=None):
    """Replace patterns in string `s`.

    Arguments:
        s (str): string in which to replace patterns.

        replace (dict): dictionary with as keys the
            strings to be replaced, and as values
            the replacing strings.

        msg (str): TODO not implemented -- show a message
            when a pattern is replaced (e.g. logging.info)

    Returns:
        str: The updated string.

    Example:
        >>> replace = {'eggs': 'spam', 'beans': 'spam'}
        >>> str_replace('spam, eggs, beans', replace)
        'spam, spam, spam'
    """
    
    for a, b in replace.items():
        s = re.sub(a, b, s)
    return s

def split_lines(s, pattern='\s*(\([0-9]+\)\s*)'):
    """Split string into lines on pattern

    The matched pattern will be included at the start
    of the line, separated by a space. If string `s`
    does not start with pattern, the first line is
    yielded as it is.

    Arguments:
        s (str): string to be split into lines

        pattern (str): regex pattern on which the string
            shall be split

    Example:
        >>> list(split_lines('First line. (2) Numbered line. (3) End.'))
        ['First line.', '(2) Numbered line.', '(3) End.']
    """

    split = re.split(pattern, s)
    if split[0]:
        yield split[0]
    for num, line in pairs(split[1:]):
        yield f'{num} {line}'

def pairs(seq):
    """Return a sequence in pairs.

    Arguments:
        seq (sequence): A sequence with an even number
            of elements. If the number is uneven, the
            last element will be ignored.

    Returns:
        A zip object with tuple pairs of elements.

    Example:
        >>> list(pairs([1,2,3,4]))
        [(1, 2), (3, 4)]
    """

    return zip(*[iter(seq)]*2)

def split_string(s, maxlen=80):
    """Split a string into substrings with a maximum length

    Splits on whitespace.
    """

    pos = 0
    line = []
    for w in s.split():
        w_len = grapheme_len(w)
        if pos + w_len > maxlen:
            yield ' '.join(line)
            pos = 0
            line = []
        pos += w_len + 1
        line.append(w)
    yield ' '.join(line)

def grapheme_len(s):
    """Return the number of spacing characters in a string"""
    return len([c for c in s if unicodedata.category(c) != 'Mn'])

