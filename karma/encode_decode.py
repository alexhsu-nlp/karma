from .affix_list import affix_vn_dict
from .ending_list import ending_vn_dict
from .structures import is_ou, is_aie, is_cons, enclitics, Word, Stem, \
    MorphemeSeq, MorphemeSeqData, DerivEnclitic, NounEnding, VerbEnding, \
    NonEnding, NonStem, Affix, Ending, RightSandhi, SandhiPOS, \
    Type1MetathesisSandhi, Type2MetathesisSandhi, HyphenSandhi, ReplaceSandhi, \
    HTRSandhi, PassPartSandhi
from .word_base import abbrs, get_protected_len, get_words_and_bases
from dataclasses import dataclass
from itertools import product
from pathlib import Path

abbr_with_tilde = tuple(s + "~" for s in abbrs)

current_file = Path(__file__).resolve()
data_file = current_file.parent / "morphemes.txt"

words, bases = get_words_and_bases(files=[data_file])

dep0cnt = [0]
dep1cnt = [0]
allcnt = [0]

guess_dict = {
    "p": "vp",
    "v": "v",
    "l": "l",
    "f": "f",
    "m": "m",
    "j": "jgy",
    "t": "tðj",
    "s": "tðcs",
    "k": "gky",
    "g": "gky",
    "n": "n",
    "ng": "ŋ",
    "a": "aiəuvV",
    "i": "iəjVy",
    "e": "iəeV", 
    "u": "ugV",  # TODO: what is this g?
    "o": "uoV",
    "q": "qr",
    "r": "qrgy"
}

from collections import defaultdict
affix_vn_init_dict: dict[SandhiPOS | None, dict[str, list[Affix]]] = {
    SandhiPOS.VERB: defaultdict(list), 
    SandhiPOS.NOUN: defaultdict(list), 
    None: defaultdict(list)
}
for pos, affix_list in affix_vn_dict.items():
    for affix in affix_list:
        a_form = affix.form
        if "^" in a_form:
            if a_form == "t^": # special
                special, spos = affix, pos
            else:
                affix_vn_init_dict[pos][a_form.split("^")[0][0]].append(affix)
                affix_vn_init_dict[pos][a_form.split("^")[1][0]].append(affix)
        else:
            if len(a_form) > 1 and is_cons(a_form[0]) and is_cons(a_form[1]):
                init = 1
            else:
                init = 0
            affix_vn_init_dict[pos][a_form[init]].append(affix)
            # TODO: temporary fix: təli => si, but s will not be detected
            # currently -liq, -liuq and -lijaq are the only three, and the second of them are both i
            # i may get changed to e (note we are attempting at the *surface* level, not form level)
            if isinstance(affix.left, ReplaceSandhi): 
                if affix.form == "liq": # fix minimally
                    affix_vn_init_dict[pos]['e'].append(affix)
                affix_vn_init_dict[pos]['i'].append(affix)
            if isinstance(affix.left, HTRSandhi): 
                affix_vn_init_dict[pos]['i'].append(affix)
            if isinstance(affix.left, PassPartSandhi): 
                affix_vn_init_dict[pos]['g'].append(affix)
                
for letter in affix_vn_init_dict[spos]:  # this is BAD
    affix_vn_init_dict[spos][letter].append(special)

def decode(word: str, words: dict[str, list[Word]], bases: dict[str, list[Stem]]):
    result = []
    init = word[0]
    if is_ou(init):
        loc_word = words["o|u"]
    elif is_aie(init):
        loc_word = words["a|i|e"]
    else:
        loc_word = words[init.lower()]
    for dict_word in loc_word:
        check_len = max(0, len(dict_word.surface) - 3)
        if word[:check_len] == dict_word.surface[:check_len]:
            if word == dict_word.surface:
                result.append(MorphemeSeq(morphemes=[dict_word]).to_data()[0]) # originally dict_word.form
            result += cliticdecode(word=word, seq=MorphemeSeq(morphemes=[dict_word]).to_data()[0])
    init = word[0]
    if word.startswith(tuple("0123456789")):
        assert "~" in word
        num, *rest = word.rsplit("~", maxsplit=1)  # TODO: this may be problematic if there can be two hyphens in a real word?
        assert all([r.isalpha() for r in rest])
        result = subdecode(word=word, 
                           seq=MorphemeSeq(morphemes=[Stem(form=num, 
                                                           right=HyphenSandhi(pos=SandhiPOS.NOUN))], 
                                                           protected_len=len(num)+1).to_data()[0])
    elif word in abbrs or word.startswith(abbr_with_tilde):
        for abbr in abbrs:
            if word.startswith(abbr):
                result += subdecode(word=word, 
                                    seq=MorphemeSeq(morphemes=[Stem(form=abbr, 
                                                                    right=HyphenSandhi(pos=SandhiPOS.NOUN), 
                                                                    protected_len=len(abbr)+1)], 
                                                    protected_len=len(abbr)+1).to_data()[0])
    else:
        if is_ou(init):
            loc_base = bases["o|u"].copy()
        elif is_aie(init):
            loc_base = bases["a|i|e"].copy()
        else:
            loc_base = bases[init.lower() + "|"].copy()
        for init, l in bases.items():
            if word.lower().startswith(init):
                loc_base += l
        # Frequent code for checking
        # print("loc size:", len(loc_base), flush=True)
        # print([b.form for b in loc_base], flush=True)
        for base in loc_base:
            result.extend(subdecode(word=word, 
                                    seq=MorphemeSeq(morphemes=[base], 
                                                    protected_len=base.protected_len).to_data()[0]))
    return result

def cliticdecode(word: str, seq: MorphemeSeqData, depth=0):
    assert len(word) > 0
    new_words: list[MorphemeSeqData] = []
    last = seq.morphemes[-1]
    assert isinstance(last, (Ending, Word))
    for enclitic in enclitics:
        if not isinstance(enclitic, DerivEnclitic):
            if enclitic.form[-1] == word[-1]:  # TODO: may need to relax this
                new_word_enc = seq.extend(morpheme=enclitic)
                for joined in new_word_enc:
                    if joined.repr.surface == word:
                        new_words.append(joined)
        #TODO: but what about qanorippit, and *=q*
        elif not isinstance(last, VerbEnding): 
            for new_stemseq in seq.extend(morpheme=enclitic):
                new_words += subdecode(word=word, seq=new_stemseq, depth=depth)
    return new_words

def subdecode(word: str, seq: MorphemeSeqData, depth=0) -> list[MorphemeSeqData]:
    stem = seq.repr
    if depth == 0:
        dep0cnt[0] += 1
    if depth == 1:
        dep1cnt[0] += 1
    allcnt[0] += 1
    # length = get_protected_len(stem)
    if isinstance(stem.right, (Type1MetathesisSandhi, Type2MetathesisSandhi)):
        length = len(stem.surface[:-4])
    else:
        length = len(stem.surface[:-3])
    if len(word) <= length + 1 or word[:length] != stem.surface[:length]: # impossible branch
        return []
    next_affix_inits = word[length+2:length+6]
    new_words: list[MorphemeSeqData] = []
    last = seq.morphemes[-1]
    assert isinstance(last, NonEnding)
    for ending in ending_vn_dict[last.right.pos]:
        if len(ending.form) + len(stem.form) <= len(word) + 5:
            new_word = seq.extend(ending)
            for joined in new_word:
                add_len = max(2, len(ending.form) - 3) if "^" in ending.form else max(2, len(ending.form) - 1)
                if joined.repr.surface == word:
                    new_words.append(joined)
                # NOTE: no enclitic does nothing to the word, so if surface matches, no need to check enclitics
                elif len(ending.form) <= 2 or joined.repr.surface[:length+add_len] == word[:length+add_len]: 
                    # TODO: temporarily assert the number of enclitics to be at most 1
                    # for nw in new_word:
                    new_words += cliticdecode(word=word, seq=joined, depth=depth+1)
    real_keys = [k for k in guess_dict if k in next_affix_inits]
    i_s = [ i for k in real_keys for i in guess_dict[k]]
    real_affixes: set[Affix] = set()
    for i in i_s:
        for affix in affix_vn_init_dict[last.right.pos][i]:
            real_affixes.add(affix)
    # frequently used code for checking
    # if stem.form == "":
    #     print("test:", next_affix_inits, real_keys, i_s, [a.form for a in real_affixes])
    for affix in real_affixes:
        if len(affix.form) + len(stem.form) <= len(word) + 5:
            for new_stemseq in seq.extend(affix):
                new_words += subdecode(word=word, seq=new_stemseq, depth=depth+1)
    return new_words

@dataclass
class ParseResult:
    result: list[list[MorphemeSeqData]]

    def product(self) -> list:
        return ["  ".join(map(str, p)) for p in product(*self.result)]

    def match(self, morph_seg: str) -> bool:
        morphs = morph_seg.split()
        return all (morph in map(str, words) for morph, words in zip(morphs, self.result))

    @property
    def list_str(self) -> list[list[str]]:
        return [list(map(str, lst)) for lst in self.result]

    @property
    def list_mofo_str(self):
        return [list(map(lambda m: m.mofo_str, lst)) for lst in self.result]

def parse_sentence(sent: str, words: list[Word] = words, bases: list[Stem] = bases) -> ParseResult:
    # TODO: retain the dots after the numbers (and also in m2w_test.py)
    import re
    from itertools import product
    sent_words = sent.strip().split()
    decoded: list[list[MorphemeSeqData]] = []
    for word in sent_words:
        if word in (":", "-", "--", "»", "«"): # ignore punctuations
            continue
        else:
            word = word.replace("-", "~")
            while word.endswith(tuple(".,!?»«:);")):
                word = word[:-1]
            while word.startswith(tuple(".,!?»«(")):
                word = word[1:]
            if word == "":
                continue
            if bool(re.match(pattern=r"^[0-9]+[a-z\.]?$", string=word)):
                result = MorphemeSeq(morphemes=[Word(form=word)]).to_data()
            else:
                result = decode(word, words=words, bases=bases)
                if result == []:
                    print("Warning:", word, flush=True)
        decoded.append(result)
    return ParseResult(result=decoded)
