"""
version 0.04 beta

This module contains standard regex patterns and functions for 
handling strings in the NENA text corpus.
"""

import unicodedata

def normalize_string(string):
    """Normalize string for tokenization and matching.
    
    Characters can come in composed or decomposed varieties.
    We normalize to decomposed characters in order to allow
    fine-grained control of accent patterns. The string is 
    converted to lowercase.
    
    Argument:
        string: str to be normalized
    
    Returns:
        str decomposed with NFD and lowercased
    
    NB: normalized text should not replace any display/stored
    texts because capitalization is stripped and also decomposed
    strings are unsightly."""
    
    return unicodedata.normalize('NFD', string).lower()

def tokenize_string(string):
    """Split a string up into analyzable characters.
    
    Returns a list of individual characters that can
    then be matched with the regex patterns.
    
    Note that all accent characters can be found with
    the range: \u0300-\u036F. Thus, strings are split
    by [any_character][any_accent]*.
    """
    norm_string = normalize_string(string)
    return re.findall('.[\u0300-\u036F]*', norm_string)

"""
The following regex patterns only work with normalized characters.
Use `tokenize_string` to split the string into analyzable characters
that can be identified with the regex below.
"""
    
# Regex for foreign letters wrapped with a language tag
#   e.g. <P>Some foreign letters<P>
foreign_letters = '[a-zðɟəɛʾʿθ][\u0300-\u033d]*'

# Regex for NENA letters
base_chars = '[a-zðɟəɛʾʿθ]'
unaccented = base_chars + '(?![\u0300-\u033d])'
cons_accented = '[dhlmprstzð]\u0323|[ckpt]\u032d|[csz]\u030c|c[\u0323\u032d]\u030c|g\u0307'
vowel_accented = '[aeiouəɛ][\u0300\u0301]|[aeiouɛ]\u0304|[aeiou]\u0304[\u0300\u0301]|[au]\u0306[\u0300\u0301]?'
nena_letters = '|'.join([unaccented, cons_accented, vowel_accented]) # i.e. "One Regex to Rule Them All"