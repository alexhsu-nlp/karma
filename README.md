![Static Badge](https://img.shields.io/badge/python-3.12|3.13-blue)
![Static Badge](https://img.shields.io/badge/version-0.0.1-green)


## KARMA: An experimental Kalaallisut Rule-based Morphological Analayzer

KARMA is an experimental non-FST morphological analyzer in Python regarding the Kalaallisut language (West Greenlandic, iso 693-3 code: [kal](https://www.ethnologue.com/language/kal/)) that attempts to give permissive morpheme segmentations that allow unusual ordering of morphemes, so that morphosyntax and syntax can both be analyzed in a subsequent syntactic parser of a pipeline.

KARMA currently is built on and tested by the morphemes used in *Kalaallisut Sungiusaatit* by Chr. Berthelsen (1996) [1], which contains reading materials in elementary Kalaallisut. Currently via testing, KARMA is able to capture the correct morpheme segmentation of around 87% sentences in the book.

> [!CAUTION]
> KARMA at the current stage is far from perfect, and might not be a good enough representation of how the morphemes join together in the language, especially with respect to irregular morpheme combinations; there might be mistakes, undergeneration, and overgeneration. The lexicon is also very poor -- currently only from a single book. When using KARMA, if the user finds any discrepancy from expectation or hopes to add some common words/bases to the lexicon, please kindly raise a GitHub issue or contact the developer through the [IYU Language Discord](https://disboard.org/server/328027881009709056).

> [!WARNING]
> KARMA aims for flexibility and readability of codes, and speed optimization is not of priority concern in the project (as long as it is not too slow), at least in the current stage. The user might expect 2-6 seconds for a sentence to get parsed on a single thread. Multi-processing can partially alleviate this issue, but if speed is a real concern, users are recommended to try a more mature word analyzer developed by [Oqaasileriffik](https://oqaasileriffik.gl/), which holds an [online demo](https://oqaasileriffik.gl/en/langtech/lookup/) and the source code is also available on [Github](https://github.com/giellalt/lang-kal). The morpheme standardization there is a bit different.

An Interactive GUI is achieved by the Python Flask server. This UI allows the user to choose the correct analysis of each word and then copy the morpheme-segmented sentence with all the selected analysis. The format of the displayed morphemes is compatible with both a standard linguistic format mainly following the [Leipzig Glossing Rules](https://www.eva.mpg.de/lingua/pdf/Glossing-Rules.pdf) and the format and notations used by [MOFO](https://mofo.oqa.dk/) and [*An Introduction to West Greenlandic*](https://oqa.dk/assets/aitwg2ED.pdf) developed by Stian Lybech [4], which are used by some Greenlandic learners, as far as I know. 

The developer hopes that this GUI can help linguists studying Kalaallisut build IGT corpora faster and with fewer mistakes (e.g. give segmentation predictions or check the validity of a segmentation guess), or help Greenlandic learners check morphemes in an unknown word, or whether they use morphemes in a (relatively) comprehensible manner.


### Setup and Example Usage

Setup requires Python and pip to be installed:
```
cd /path/to/karma/repo
pip install .
```

The base and word lists that the program use are stored in `karma/morpheme.txt`. The user might want to install via `pip install -e .` instead if they want to modify or add out-of-vocabulary words to this file.

If you want to use the GUI (notice that this will not get installed as a part of the karma package, but simply stays in the repository as a separate script), you will need to either use the [released binaries](https://github.com/alexhsu-nlp/karma/releases/tag/0.0.1), where you don't even need Python installed, or install [flask](https://flask.palletsprojects.com/en/stable/) and [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/):

```
pip install flask waitress
cd /path/to/karma/repo
python karma_app.py
```

You can choose your port upon running the app:
```
python karma_app.py --port 5004
```
On the terminal you will be able to see something like `Serving on http://127.0.0.1:XXXX ...`. Copy this address to the browser to use the GUI.


### References
[1] Berthelsen, C.  (1996). Kalaallisut Sungiusaatit. Atuakkiorfik Ilinniusiorfik.

[2] Fortescue, M. D. (1984). West greenlandic. London: Croom Helm.

[3] Fortescue, M. (1994). Comparative Eskimo Dictionary with Aleut Cognates. Alaska Native Language Center, University of Alaska Fairbanks, PO Box 757680, Fairbanks, AK 99775-7680..

[4] Lybech, S. (2022). An Introductive to West Greenlandic (2nd ed.). URL: https://oqa.dk/assets/aitwg2ED.pdf
