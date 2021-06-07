import json
import collections
from pathlib import Path
from nena_parser import NenaLexerParser
from build_tf import NenaTfBuilder

# Load config file to get the input directory
configfile = 'config.json'
with open(configfile, 'r') as infile:
    configs = json.load(infile)

# set up NENA markup lexer and parser
lexer, parser = NenaLexerParser(configfile)

# parse NENA markup texts and map their data
# to their respective dialects
textdir = Path(configs['nena_indir'].format(version=configs['version'])) # input here
_dialect2data_ = collections.defaultdict(list)
print('Beginning parsing of NENA formatted texts...')
for textfile in sorted(textdir.glob('*.nena')):
    print(f'\tparsing {textfile}...')
    text = textfile.read_text()
    parsed = parser.parse(lexer.tokenize(text)) # magic here
    metadata, text = parsed
    dialect = metadata['dialect']
    _dialect2data_[dialect].append(parsed) # parse mapped to dialect
print('DONE parsing all .nena texts!')

# ensure that dialects are sorted alphabetically, because
# the index made by TF will model whatever order it is fed
dialect2data = collections.OrderedDict()
for dialect in sorted(_dialect2data_):
    dialect2data[dialect] = _dialect2data_[dialect]

# hand off the data to the TF builder to construct
# a text-fabric graph
tfbuilder = NenaTfBuilder(dialect2data, configfile)
tfbuilder.build()
