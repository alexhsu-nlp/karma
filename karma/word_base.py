from collections import defaultdict
from .structures import Stem, Word, is_ou, is_aie, RightSandhi, AqDropSandhi, \
    TeSandhi, WeakenableSandhi, GemSandhi, UsiqSandhi, SandhiPOS, sound_dict, \
    GeSandhi, WeakQStemSandhi, KStemSandhi, Type1MetathesisSandhi, Type2MetathesisSandhi, TcTriggerSandhi, enclitics, \
    MorphemeSeq, is_vowel, SchwaElideSandhi, MarlukSandhi
from pathlib import Path
import re

# TODO: automatic identification? 
# A stem must be a loanword when any of the following takes place
# Rule 1: Any o, e, ø, å, æ, b, d, h detected
# Rule 2: An r preceded by any non-r consonant (tscðpvfkgqlmnŋ). This is because such r would be written as q in native stems in the Stianic style.
# Rule 3: Three consonants in a row.
def check_and_add_loanword_simple(word: str, mapping: dict[str, tuple[str, bool]]):
    rare_pattern = re.compile(r"[oeøåæbdhx]|[tscpvfkgqlmn]r|[tscpvfkgqlmnry]{3}")
    if bool(rare_pattern.search(string=word)) and not word.endswith("q"):
        length = len(word) - 1 if word.endswith(tuple("aeiou")) else len(word)
        mapping[word] = (word[:length], length == len(word))
    else: 
        # print(f"maybe not a loanword, please add manually: {word}")
        pass

word_mappings = {
                    "filmiq": ("film", False),
                    "filmi": ("film", False),
                    "filmigaq": ("film", False),
                    "piitaq": ("piitaq", False),
                    "klassi": ("klass", False),
                    "augusti": ("august", False),
                    "augustusi": ("augustus", False),
                    "rask": ("rask", True),
                    # "ittuqquqtuuqmii": ("ittuqquqtuuqmii", False),
                    "minutsi": ("minutsi", False),
                    "svenskeq": ("svenskeq", False),
                    "fanta": ("fanta", False),
                    "kursusi": ("kursus", False),
                    "alaska": ("alaska", False), 
                    "sagn": ("sagn", True), 
                    "lang": ("lang", True),
                    "lasti": ("last", False),
                    "kavaajaq": ("kavaaja", False),
                    "svenskiq": ("svensk", False),
                    # "chr": ("chr", True)
                    # "kg": ("kg", False), # TODO: we need a hyphen, 
                    # "nr": ("nr", False),
                }

# stem_pos_mappings = {
#     SandhiPOS.NOUN: ["inə"],
#     SandhiPOS.VERB: ["ət"],
# }

# def get_word_protected_len(word: Word):
#     idx = len(word.surface) - 1
#     vowel_flag = False
#     while idx >= 0:

def get_protected_len(base: Stem):
    if base.protected_len > 0:
        return base.protected_len
    idx = len(base.surface) - 1
    vowel_flag = False
    while idx >= 0:
        if is_vowel(base.surface[idx]):
            vowel_flag = True
        if vowel_flag and not is_vowel(base.surface[idx]):
            if isinstance(base.right, GemSandhi):
                return max(0, idx - 1)
            if isinstance(base.right, (Type1MetathesisSandhi, Type2MetathesisSandhi)):
                return max(0, idx - 3)
            return idx
        idx -= 1
    return 0

abbrs = ('kg', 'nr', 'kni', 'kr', 'km', 'chr')

def get_sandhi(base_str: str, word_mappings: dict[str]) -> RightSandhi:
    if base_str in word_mappings:
        if base_str.endswith('q'):  # for kavaajaq
            return WeakQStemSandhi(pos=None)
        return RightSandhi(pos=None) # TODO: in fact I can make pos
    if base_str in ("qulə", 'timə'): # directional nouns
        return SchwaElideSandhi(pos=SandhiPOS.NOUN)
    if base_str in ("kaŋirlussuaq", "umiarcuaq", "nuliaq", "quiqcuaq", "ilinniarfissuaq", "siurarsuaq", "ivəgarsuaq", "qasigiaŋŋuaq", "qiqəqtarsuaq", "nuussuaq"):
        return AqDropSandhi(pos=SandhiPOS.NOUN)
    if base_str in ("apirə", "pisiarə", "uqarfigə", "aglaffigə", "qutcavigə", "nuannarə", "telefonirfigə", "uqaluttuarə", "ilisarə"):
        return GeSandhi(pos=SandhiPOS.VERB)
    if base_str.endswith("tə"):
        return TeSandhi(pos=None) # TODO: make this None acceptable
    if base_str in ("ujarak", "pituqaq", "imaq", "nalunaaqutaq"):  # need this test before regular k- and weak q-stems, so have to separate this
        return GemSandhi(pos=None)
    if base_str.endswith(("k", "lliq")) or base_str in ("naliŋinnaq", "taaq"):
        if base_str in ('kiglək'): # strong q-stems
            return WeakenableSandhi(pos=None)
        if base_str.endswith('marluk'):
            return MarlukSandhi(pos=SandhiPOS.NOUN) # currently no exceptions
        return KStemSandhi(pos=None)
    if bool(re.search("[aiu][vljgr][^ə]q$", base_str)):
        return GemSandhi(pos=None)
    if base_str.endswith("usiq") or base_str in ('tasiq'): # TODO: temporarily not sure which -siq should be included
        return UsiqSandhi(pos=None)
    if base_str.endswith("əq"):
        if base_str in ('atəq', 'qitəq', 'tupəq', 'ulluqitəq'):
            return Type1MetathesisSandhi(pos=None)
        if base_str in ('iməq', 'sianəq', 'siunəq', 'aqqanəq'):
            # this None is necessary, since sianəq can be a verbs
            return Type2MetathesisSandhi(pos=None) 
        return WeakenableSandhi(pos=None)
    # elif base_str in ("assigiiŋŋit", "iqqumiit"):
    if base_str.endswith(("ət", "it")):
        return TcTriggerSandhi(pos=SandhiPOS.VERB)
    if bool(re.search("[^ə]q$", base_str)) and base_str != "tamaq":
        return WeakQStemSandhi(pos=None) # TODO
    return RightSandhi(pos=None)

def get_words_and_bases(files: list[Path]):
    bases: dict[str, list[Stem]] = defaultdict(list)
    words: dict[str, list[Word]] = defaultdict(list)

    for (word, (head, _)) in word_mappings.items():
        assert word.startswith(head)
    for file in files:
        base_flag = False
        word_flag = False
        with file.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Others"):
                    word_flag = True
                    base_flag = False
                if word_flag and line != "":
                    word_str = line.split()[0].lower()
                    if word_str not in word_mappings:
                        check_and_add_loanword_simple(word=word_str, mapping=word_mappings)
                    protected_len = len(word_mappings[word_str][0]) if word_str in word_mappings else 0
                    init = word_str[0]
                    if is_ou(init):
                        words['o|u'].append(Word(form=word_str, protected_len=protected_len))
                    elif is_aie(init):
                        words['a|i|e'].append(Word(form=word_str, protected_len=protected_len))
                    else:
                        words[init].append(Word(form=word_str, protected_len=protected_len))
                    
                if base_flag and line != "":
                    base_str = line.split()[0].split("[")[0]
                    base_str = base_str[:-1].lower()
                    if base_str == "kaq": # derivenclitic, not base
                        continue
                    greenlandic_i = False
                    if base_str not in word_mappings:
                        check_and_add_loanword_simple(word=base_str, mapping=word_mappings)
                    if base_str in word_mappings:
                        protected_len = len(word_mappings[base_str][0])
                        greenlandic_i = word_mappings[base_str][1]
                    else:
                        protected_len = 0
                    init = base_str[0]
                    sandhi = get_sandhi(base_str=base_str, word_mappings=word_mappings)
                    # TODO: probably should change this in `get_sandhi`
                    if bool(re.search(f"{sound_dict['cons']}$", base_str)):
                        sandhi.cons_end = True
                    if is_ou(init):
                        bases["o|u"].append(Stem(base_str, protected_len=protected_len, greenlandic_i=greenlandic_i, right=sandhi))
                    elif is_aie(init):
                        bases["a|i|e"].append(Stem(base_str, protected_len=protected_len, greenlandic_i=greenlandic_i, right=sandhi))
                    else:
                        bases[init + '|'].append(Stem(base_str, protected_len=protected_len, greenlandic_i=greenlandic_i, right=sandhi))
                elif line.startswith("Bases"):
                    base_flag = True
    # bases['a|i|e'].append(Stem(form="iqqumiit", right=TcTriggerSandhi(pos=None, cons_end=True))) # be.strange
    # bases['a|i|e'].append(Stem(form="iqquq", right=WeakQStemSandhi(pos=None, cons_end=True)))    # arse

    
    new_bases: dict[str, list[Stem]] = defaultdict(list)
    for letter, l in bases.items():
        for base in l:
            if base.form not in abbrs:
                prot_len = get_protected_len(base)
                if prot_len > 0:
                    new_bases[base.surface[:prot_len]].append(base)
                else:
                    new_bases[letter].append(base)
    # frequently used check, remained
    # print("check number of bases: ", sum(1 for l in bases.values() for base in l), sum(1 for l in new_bases.values() for base in l), flush=True)
    # for k, base_list in new_bases.items():
    #     for b in base_list:
    #         if b.form.startswith("svens"):
    #             print(b, k)
    return words, new_bases
