# Northeastern Neo-Aramaic Corpus Data [![DOI](https://zenodo.org/badge/204971841.svg)](https://zenodo.org/badge/latestdoi/204971841)

<a href="https://www.ames.cam.ac.uk"><img src="https://github.com/CambridgeSemiticsLab/nena_tf/blob/master/docs/images/CambridgeU_color.jpg" width="236" height="49"></a>

Northeastern Neo-Aramaic consists of a very diverse group of Aramaic dialects that were spoken until modern times in Northern Iraq, North West Iran and South Eastern Turkey by Christian and Jewish communities. These are among the last remaining living vestiges of the Aramaic language, which was one of the major languages of the region in antiquity.

This text corpus consists of transcribed and recorded texts gathered by [Prof. Geoffrey Khan](https://www.ames.cam.ac.uk/people/professor-geoffrey-khan) and his team in their efforts to preserve these increasingly endangered languages. This repository contains raw and corrected source texts written in North Eastern Neo-Aramaic (NENA) dialects. All original source material is converted to a standard mark-up format, regardless of its original format.

The purpose of this repository is to curate source texts that will be used for building a complete text corpus in Text-Fabric. The corpus will in turn be analyzed and annotated for linguistic features.

## Contents

### [nena_format](docs/nena_format.md) - description of the NENA mark-up format
### [standards](standards) - standards for NENA alphabet, linguistic codes, including regex patterns
### [texts](texts) - contains the NENA texts by version and dialect in NENA mark-up
### [parsed_texts](parsed_texts) - contains all NENA texts parsed into JSON hierarchies
### [text_parser](text_parser) - a SLY parser for producing the NENA JSON parsings from NENA mark-up
### [sources](sources) - original source material used for generating NENA texts
