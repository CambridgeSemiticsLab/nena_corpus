import json
import tabulate
import collections
from pathlib import Path
from tf.fabric import Fabric

class DocsBuilder:

    """
    Automatically build corpus documentation using TF files.
    """

    def __init__(self, configdata, outdir):

        self.outdir = Path(outdir)

        # read in the template file for the docs
        template_file = configdata['doc_template']
        with open(template_file, 'r') as doc_template:
            self.doc = doc_template.read()

        # read in the metadata for the corpus
        meta_file = configdata['metadata']
        with open(meta_file, 'r') as infile:
            self.metadata = json.load(infile)

        # read in the metadata for tf
        tf_config = configdata['tf_config']
        with open(tf_config, 'r') as infile:
            self.tf_config = json.load(infile)

    def maketable(self, tabledata, headers=('','')):
        """Build a markdown table."""
        return tabulate.tabulate(tabledata, headers=headers, tablefmt='pipe')

    def load_tf(self):
        """Load the TF corpus for infering nodes and features."""
        tf_dir = self.outdir.joinpath('tf')
        TF = Fabric(locations=str(tf_dir))
        api = TF.loadAll()
        self.F, self.L, self.Fs = api.F, api.L, api.Fs
        self.C = api.C 

    def export_doc(self, string, name):
        """Write the documentation doc to disk."""
        filepath = self.outdir.joinpath(name)
        filepath.write_text(string)

    def compile_doc(self):
        """Iterate through the TF corpus and document features."""

        # load the TF data
        self.load_tf()

        feature_otype_counts = collections.defaultdict(lambda: collections.Counter())
        node_data = []

        # build table for node types
        self.doc += '# Node Types'
        filter_features = {
            f:fd for f, fd in self.metadata['object_features'].items()
                if f not in self.tf_config['ignore_features']
        }

        for otype_data in self.C.levels.data:
            
            otype = otype_data[0]
            otype_meta = self.metadata['corpus_objects'][otype]
            count = len(list(self.F.otype.s(otype)))
            
            attested_features = set()
            
            for feat, fdata in filter_features.items():
                feat_data = self.Fs(feat)
                freqlist = list(feat_data.freqList(nodeTypes=otype))
                feature_values = [fl[0] for fl in freqlist]
                feature_total = sum(fl[-1] for fl in freqlist)

                # skip if otype is never used with a given feature
                if not freqlist:
                    continue
                
                feature_otype_counts[otype][feat] += feature_total
                attested_features.add(feat)
            
            att_features = ', '.join(f'[{f}](#{f})' for f in attested_features)
            node_data.append((otype, otype_meta, count, att_features))

        self.doc += '\n\n'
        self.doc += self.maketable(node_data, ('node type', 'description', 'frequency', 'features'))
            
        # build tables for features
        self.doc += '\n\n'
        self.doc += '# Features\n\n'
        for feat, fdata in filter_features.items():
            
            # add feature section to the document
            self.doc += f'## {feat}'
            self.doc += '\n\n'
            self.doc += fdata['about']
            self.doc += '\n\n'
                
            freqlist = list(self.Fs(feat).freqList())
            feature_values = [fl[0] for fl in freqlist]
            
            otype_freqs = []
            for otype in feature_otype_counts:
                if feat in feature_otype_counts[otype]:
                    otype_freqs.append((otype, feature_otype_counts[otype][feat]))
            
            self.doc += '**Node Counts**\n'
            self.doc += self.maketable(otype_freqs, ('node type', 'frequency'))
            self.doc += '\n\n'
            
            # add data about the feature
            if fdata['value'] == 'categorical':
                self.doc += '**Values**'
                self.doc += '\n'
                self.doc += self.maketable(freqlist, (feat, 'frequency'))
                self.doc += '\n\n'
            elif fdata['value'] == 'text':
                self.doc += '\n'
                self.doc += 'See the [transcription tables](transcription.md).\n\n'
            elif feat == 'title':
                # retrieve dialects for the titles
                titles = []
                for title in feature_values:
                    node = next(
                        text for text in self.F.otype.s('text')
                            if self.F.title.v(text) == title
                    )
                    dialect = self.F.dialect.v(self.L.u(node,'dialect')[0])
                    titles.append((title, dialect))
                titles = sorted(titles, key=lambda k: (k[-1], k[0]))
                self.doc += '**Values**'
                self.doc += '\n'
                self.doc += self.maketable(titles, ('title', 'dialect'))
                self.doc += '\n\n'
            else:
                self.doc += '**Examples**'
                self.doc += '\n'
                self.doc += '```' + '\n' + '\n'.join(str(v) for v in feature_values[:5]) + '\n' + '```'
                self.doc += '\n\n'
                
            self.doc += '[back to node types](#Node-Types)\n'
            
            self.doc += '<hr>\n\n' 

            self.export_doc(self.doc, 'documentation.md')
