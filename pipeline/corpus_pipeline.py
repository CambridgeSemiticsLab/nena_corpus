import json
import collections
from pathlib import Path
from nena_parser import NenaLexerParser
from build_tf import NenaTfBuilder
#from build_docs import DocsBuilder
import unicodedata as ucd

class CorpusPipeline:

    def __init__(self, configs):
    
        """Initialize pipeline configs / error handling.

        Args:
            configs: string or dict. If string, should be a 
                filepath to a json file of configs. If dict,
                should contain all of the necessary config
                keys for the parser processes.
        """

        # load and set up configs
        if type(configs) == str:
            with open(configs, 'r') as infile:
                self.configs = json.load(infile)
        elif type(configs) == dict:
            self.configs = configs
        else:
            raise Exception(
                '"configs" should be either string (filepath) '
                 f'or dict, not {type(configs)}'
            )
    
        # a place to store error messages;
        # the messages are keyed by process,
        # the value is a list of error strings
        self.errors = {}

    def build_corpus(self):
        """Parse and index (TF) the nena corpus."""
        
        # parse the .nena files 
        dialect2data = self.parse_nena()
        
        # index the data with Text-Fabric;
        # produces .tf files
        self.build_tf(dialect2data)

        # build docs
        self.build_docs()

        # build search tool
        self.build_layered_search()

    def parse_nena(self):
        """Parse .nena markup files."""

        # set up NENA markup lexer and parser
        lexer, parser = NenaLexerParser(self.configs)

        # instantiate error list
        errlog = self.errors['nena_parser'] = []

        # load .nena files
        textdir = Path(
            self.configs['nena_indir']
                .format(version=self.configs['version'])
        )
        _dialect2data_ = collections.defaultdict(list)

        # -- Attempt to parse each text --

        print('Beginning parsing of NENA formatted texts...')
        for textfile in sorted(textdir.glob('*.nena')):
            text = ucd.normalize('NFD', textfile.read_text()) # normalize to decomposed
            name = textfile.stem # <- to be replaced with corpus ID

            # attempt to parse the text
            # if parse fails, save message to the error log
            try:
                print(f'\tparsing {textfile}...')
                parsed = parser.parse(lexer.tokenize(text)) # magic here
            except Exception as e:
                print(f'\t\tfail')
                errlog.append(f'{name}: {e}')
                continue

            metadata, text = parsed
            dialect = metadata['dialect']
            _dialect2data_[dialect].append(parsed) # parse mapped to dialect
        print('DONE parsing all .nena texts!')

        # -------

        # ensure that dialects are sorted alphabetically, because
        # the index made by TF will model whatever order it is fed
        dialect2data = collections.OrderedDict()
        for dialect in sorted(_dialect2data_):
            dialect2data[dialect] = _dialect2data_[dialect]

        return dialect2data

    def get_metadata(self, nenastring):
        """Retrieve metadata from a .nena markdown string.
    
        Though metadata is parsed in the parser,
        we need a "dumb" way to get metadata from a file 
        before it is parsed so that parse errors can be tied to 
        a corpus ID rather than just a filename.
        """
        pass

    def build_tf(self, dialect2data):
        """Index the parsed .nena data into a Text-Fabric resource."""
        # instance an error list
        errlog = self.errors['tf_builder'] = []
        try:
            tfbuilder = NenaTfBuilder(
                dialect2data, 
                self.configs, 
            )
            tfbuilder.build()
        except Exception as e:
            errlog.append(f'TEXT FABRIC INDEXING FAILED; REASON: {e}')

    def build_docs(self):
        """Automatically build documentation on the corpus."""
        pass

    def build_layered_search(self):
        """Build layered search tool from TF files."""
        pass
