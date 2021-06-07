import json
from tf.fabric import Fabric
from tf.convert.walker import CV

class NenaTfBuilder:
    """Construct Text-Fabric graph resource from parsed NENA files."""
    
    def __init__(self, dialect2data, configfile, **TF_kwargs):
        """Load json data from input dir to prepare for TF conversion.
        
        Args:
            input_dir: pathlib Path which is a directory that contains
                subdirectories named after the respective dialects in the
                text corpus. Each subdirectory should contain parsed JSON
                texts ready for analysis.
            output_dir: directory to save the .tf files
            metadata: dictionary containing metadata on the corpus needed
                to construct the TF graph
            Fabric: Text-Fabric module for saving/outputing data
            CV: Text-Fabric CV module for constructing text graphs
            **TF_kwargs: optional kwargs to pass to Text-Fabric loader
        """


        # load JSON data and initialize TF objects
        self.dialect2data = dialect2data
        self.configs = self.load_configs(configfile)
        self.metadata = self.configs['metadata']
        self.Fabric = Fabric(
            locations=self.configs['tf_outdir'],
            **TF_kwargs
        )
        self.cv = CV(self.Fabric)
        self.message = self.Fabric.tmObj # timestamped messages

        # prepare dictionary with all character data
        self.chardata = self.configs['alphabet']
        self.chardata.update(self.configs['punct_begin'])
        self.chardata.update(self.configs['punct_end'])

    def load_configs(self, configfile):
        """Load (sub)configs into dict."""

        # load config data
        with open(configfile, 'r') as infile:
            configs = json.load(infile)

        # load sub-configs
        sconfigs = {}
        for k,v in configs.items():
            if v.endswith('.json'):
                with open(v, 'r') as infile:
                    sconfigs[k] = json.load(infile) 
        configs.update(sconfigs)

        return configs

    def get_char_data(self, char_string, dialect):
        """Retrieve data for a letter/punct from the configs."""
        cdata = self.chardata.get(char_string, {})
        cdata.update(
            self.get_transcriptions(char_string, dialect)
        )
        return cdata
    
    def get_transcriptions(self, char_string, dialect):
        """Retrieve letter/punct transcriptions."""
        trans_data = {}
        for tname, tdata in self.configs['transcriptions'].items():
            try:
                dialect_set = tdata['dialect2set'][dialect]
            except KeyError:
                raise Exception(
                    f'Dialect {dialect} is not '
                    'configured in transcriptions.json!'
                )
            # NB the default string below, to handle non-mapped characters
            trans_data[tname] = tdata[dialect_set].get(char_string, char_string)
        return trans_data
        
    # NB: deprecated now that data is fed in as an arg
    def load_parsed_jsons(self, dialect_dir):
        """Map directory of dialect subdirectories to parsed json data.
        
        Args:
            dialect_dir: a pathlib Path that contains subdirectories
                named after respective dialects; each subdirectory 
                contains parsed JSON files which are each a text
        
        Returns:
            dict with structure of dict[dialect] = list(text_parsings)
        """
        dialect2parsings = collections.defaultdict(list)
        for dialect_dir in sorted(INPUT_DIR.glob('*')):
            for text_file in sorted(dialect_dir.glob('*.json')):
                dialect = dialect_dir.name
                text_data = json.loads(text_file.read_text())
                dialect2parsings[dialect].append(text_data)
        return dialect2parsings
    
    def build(self, **walk_kwargs):
        """Executes the TF conversion on the supplied data.
        
        Args:
            walk_kwargs: optional keyword arguments to feed 
                to TF's cv.walk function.
        """
        self.good = self.cv.walk(
            self.director,
            self.metadata['slot_type'],
            otext=self.metadata['otext'],
            generic=self.metadata['NENA_corpus'],
            intFeatures=self.metadata['intFeatures'],
            featureMeta=self.metadata['object_features'],
            **walk_kwargs,
        )
    
    def dict_intersect(self, dict1, dict2):
        """Set intersection from one dict to another"""
        return {k:v for k,v in dict1.items() if k in dict2}
    
    def director(self, cv):
        """Call Text-Fabric CV methods to index the text graph.
        
        This function does the bulk of the work of building the TF resource.
        It operates in one large loop that walks over all parsed data. 
        The supplied cv Text-Fabric class possesses methods that create node 
        IDs and associate features with those IDs. These methods are called 
        throughout the loop. The CV class also handles embedding relationships
        between the nodes based on the overlap of slots (i.e. atomic units
        for the text graph).
        
        cv methods used here:
            cv.slot: make a new slot, the atomic element of the graph. All 
                nodes active during an active slot will contain that slot.
            cv.node: make a new node in the graph with supplied object name
            cv.feature: add a string/integer feature to a supplied cv.node
            cv.terminate: deactivate a given node; this ends any further
                slot embeddings, which are calculated automatically from 
                whichever slots are activated while the node is also active.
                
        Further info about cv functionality can be referenced in the 
        Text-Fabric documentation.
        
        Args:
            cv: Text-Fabric CV class loaded with Fabric
        """
        
        features = self.metadata['object_features']
        text_features = {f for f,fd in features.items() if fd['value'] == 'text'}
        general_features = {f for f in features if f not in text_features}
        nodes = {} # gets updated throughout
    
        def swap_node(node_type):
            """Replace any active nodes with new node or just add new node."""
            try:
                cv.terminate(nodes[node_type])
                nodes[node_type] = cv.node(node_type)
            except KeyError:
                nodes[node_type] = cv.node(node_type)
        
        # parse all data for every dialect
        for dialect, texts in self.dialect2data.items():
            
            # make dialect node / features
            nodes['dialect'] = cv.node('dialect')
            cv.feature(nodes['dialect'], dialect=dialect)
            
            # make text node / features
            for text in texts:
        
                nodes['text'] = cv.node('text')
                text_attributes, paragraphs = text
                
                for feature, value in text_attributes.items():
                    if feature == 'speakers':
                        speakers = ', '.join(value.values())
                        cv.feature(nodes['text'], speakers=speakers)
                    elif feature in features:
                        cv.feature(nodes['text'], **{feature:value})
                        
                for ith_paragraph, paragraph in enumerate(paragraphs):
                    
                    nodes['stress'] = cv.node('stress')
                    nodes['inton'] = cv.node('inton')
                    nodes['subsentence'] = cv.node('subsentence')
                    nodes['sentence'] = cv.node('sentence')
                    nodes['paragraph'] = cv.node('paragraph')
                
                    # -- Process Paragraph elements --
                    # which are comprised of word and span tags
                    
                    # track span features and add them to words as words are made
                    # span feature values can be altered when triggered by new span tags
                    span_feats = {
                        'speaker': list(text_attributes['speakers'].values())[0],
                        'lang': 'NENA',
                        'timestamp': None,
                    }
                    
                    for ith_element, element in enumerate(paragraph):
                        
                        # -- process span elements --
                        if element['class'] == 'span':
                            
                            # build line nodes
                            if 'line_number' in element:
                                swap_node('line')
                                line_num = element['line_number']
                                cv.feature(
                                    nodes['line'], 
                                    line_number=line_num
                                )
                            
                            # update other span fields
                            span_feats.update(
                                self.dict_intersect(element, span_feats)
                            )
                            
                        # -- Process words, their letters, and their beginnings/ends --
                        elif element['class'] == 'word':
                            
                            nodes['word'] = cv.node('word')
                            word_features = {}
                            word_features.update(span_feats) # inherit span features
                            word_features.update(
                                self.dict_intersect(element, general_features) # + other features
                            )
                            
                            # 1. ** process word's letters and their features **
                            # also get text from the letters
                            for letter in element['letters']:
                                letter_node = cv.slot()
                                letter = self.get_char_data(letter, dialect)
                                letter_features = self.dict_intersect(letter, features)
                                
                                # process features for letter
                                # pass on text features to word 
                                for feature, value in letter_features.items():
                                    cv.feature(letter_node, **{feature:value})
                                    if feature in text_features:
                                        word_features[feature] = (
                                            word_features.get(feature,'') + value
                                        )
                                
                                # we're done with letter node; terminate to deactivate it
                                cv.terminate(letter_node)
    
                            # 2. ** process word's parsing features **
                            # current process allows multiple parsings to co-exist
                            # thus we construct a composite parse-string for each feature
                            parse_values = collections.defaultdict(list)
                            word_features['n_parses'] = len(element['parsings'])
                            for parse in element['parsings']:
                                # gather feature / val strings to be joined on '|' (see next codeblock)
                                keep_parse = self.dict_intersect(parse, features)
                                for feat, val in keep_parse.items():
                                    parse_values[feat].append(val)
                            
                            # join multiple parse strings on '|'
                            # add the new strings to word features
                            for feat, vals in parse_values.items():
                                word_features[feat] = '|'.join(vals)
                            
                            # 3. ** Process beginnings on a word **
                            for begin in element['beginnings']:
                                
                                # build begin strings
                                begin = self.get_char_data(begin, dialect)
                                begin_features = self.dict_intersect(begin, text_features)
                                text_feat_prfx = {k+'_begin':v for k,v in begin_features.items()}
                                for feat_val in text_feat_prfx.items():
                                    word_features[feat] = word_features.get(feat,'') + val
                            
                            # 4. ** Process endings on a word ** 
                            # mark sentence/subsentence/inton/stress bounds on endings of word
                            # also add endings as their own text features of a word, with _end suffix
                            detected_boundaries = set()
                            for end in element['endings']:
                                
                                # build end strings
                                end = self.get_char_data(end, dialect)
                                end_features = self.dict_intersect(end, text_features)
                                text_feat_sffx = {k+'_end':v for k,v in end_features.items()}
                                
                                for feat, val in text_feat_sffx.items():
                                    word_features[feat] = word_features.get(feat,'') + val
                                
                                # skip non-separating punctuation
                                if end['class'] != 'separator':
                                    continue
                                
                                # detect stress bounds; end at any of the following:
                                if end['modifies'] in {'word', 'intonation group',  'subsentence', 'sentence'}:
                                    detected_boundaries.add('stress')
                                
                                # detect inton bounds
                                if end['modifies'] in {'intonation group', 'subsentence', 'sentence'}:
                                    detected_boundaries.add('inton')
                                
                                # detect subsentence bounds
                                if end['modifies'] in {'subsentence', 'sentence'}:
                                    detected_boundaries.add('subsentence')
                                
                                # detect sentence bounds
                                if end['modifies'] in {'sentence'}:
                                    detected_boundaries.add('sentence')
                                
                            # end the word and execute boundary divisions
                            cv.feature(nodes['word'], **word_features)
                            cv.terminate(nodes['word'])
                            for bound in detected_boundaries:
                                if ith_element+1 != len(paragraph):
                                    swap_node(bound)
                                else:
                                    cv.terminate(nodes[bound])

                    # we've come to the end of the paragraph
                    # we do some house-cleaning before finishing with the paragraph
                    
                    # do a sanity check for un-closed intons, subsentences, sentences
                    # possibly due to lack of proper punctuation in the source text (to be fixed later)
                    title = text_attributes['title']
                    for obj in {'stress', 'inton', 'sentence', 'subsentence'} & cv.activeTypes():
                        sys.stderr.write(f'force-closing {obj} in {title}, §{ith_paragraph}.{ith_element}\n')
                        cv.terminate(nodes[obj])
                    
                    # check for active line on last paragraph of a text
                    # though a line can straddle paragraphs it should not straddle texts!
                    if (ith_paragraph+1 == len(paragraphs)) and nodes.get('line', None):
                        cv.terminate(nodes['line'])
                    
                    # close shop on the §
                    cv.terminate(nodes['paragraph'])
                        
                # -- trigger section node endings --
                cv.terminate(nodes['text'])
            cv.terminate(nodes['dialect'])
