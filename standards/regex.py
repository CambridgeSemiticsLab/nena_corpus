# version 0.02 beta

import unicodedata

def normalize_char(char):
    """Normalize character for regex testing.
    
    Characters normalized by:
        * decomposing/sorting chars with unicodedata.normalize
        * converted to lowercase
    Decomposition allows for one-to-one matching with accents.
    NB: that normalize_char removes capitalization and
    thus should not replace text inputs.
    
    Arguments:
        char: str of single character
    
    Returns:
        str normalized
    """
    return unicodedata.normalize('NFD', char).lower()

# Regex for foreign letters wrapped with a language tag
#   e.g. <P>Some foreign letters<P>
# CAUTION: does not yet exclude puntuators
foreign_chars = '.[\u0300-\u036F]*'

# Regex for NENA letters
base_chars = '[a-zðɟəɛʾʿθ]'
unaccented = base_chars + '(?![\u0300-\u036F])'
cons_accented = '[dhlmprstzð]\u0323|[ckpt]\u032d|[csz]\u030c|c[\u0323\u032d]\u030c|g\u0307'
vowel_accented = '[aeiouəɛ][\u0300\u0301]|[aeiouɛ]\u0304|[aeiou]\u0304[\u0300\u0301]|[au]\u0306[\u0300\u0301]?'
one_regex = '|'.join([unaccented, cons_accented, vowel_accented])