from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re
from functools import cached_property
from enum import Enum
from itertools import product
from .utils import *

class BaseSandhi:
    pass

@dataclass
class Sandhi(BaseSandhi):
    pos: SandhiPOS | None

# TODO: make a left sandi and a right sandhi
@dataclass
class LeftSandhi(Sandhi):
    """
    The generic left sandhi with default expected behavior.

    Note that the data fields `cons_start` and `double_cons` 
    will be calculated upon creation.
    """
    cons_start: bool = False
    # vow_start: bool = False
    double_cons: bool = False # NOTE: only for nontruncative ones
    truncative: bool = False # also left sandhi
    weakening: bool = False  # left sandhi
    # special: = None
    # TODO: make them in postinit, not in passable data fields

    def _get_chunk(self, self_nonstem: NonStem):
        """Get the main body of an epenthetic affix."""
        chunk_ind = self_nonstem.form.find("^") + 1
        return self_nonstem.form[chunk_ind:]

    def left_join(self, self_nonstem: NonStem, left_stem: Stem) -> list[str]: 
        # NOTE: not implemented for left_affix
        """
        Check the sandhi of its left partner (e.g. Stem), and then change form.
        """
        # assert self_nonstem.sandi is self
        if "^" in self_nonstem.form:
            # NOTE: assume that epenthetic affixes/endings start with consonant in their chunk part
            # exception: g^innaq

            # TODO: what made me add the final isinstance about WeakQStem and Gem???
            # if (not left_stem.right.cons_end 
            #     or (isinstance(self_nonstem, NounEnding) and isinstance(left_stem.right, (WeakQStemSandhi, GemSandhi)))): 
            if not left_stem.right.cons_end:
                return [self_nonstem.form.replace("^", "")]
            return [self._get_chunk(self_nonstem=self_nonstem)]
        # note: this includes t^, but excludes SG.ABS, -p and -t
        # NOTE: ð will NOT become T directly after vowels
        if len(self_nonstem.form) > 1 and (self_nonstem.form[0] == 't' 
                                           or (self_nonstem.form[0] == 'ð' 
                                               and left_stem.right.cons_end 
                                               and not self_nonstem.left.truncative)):
            return [self_nonstem.form, 'T' + self_nonstem.form[1:]]
        return [self_nonstem.form]

@dataclass
class RightSandhi(Sandhi):
    """
    The generic right sandhi with default expected behavior.

    This includes the qg=>r rule when the g-initial affix is truncative 
    (i.e., truncative loses its effect).
    """
    cons_end: bool = False
    # vow_end: bool | None

    def right_join(self, self_stem: Stem, right_nonstem: NonStem) -> list[str]:
        """
        Check the sandhi of its right partner (e.g. Affix/Ending), and then change form.
        """
        if self_stem.greenlandic_i:
            if right_nonstem.form == "":
                return [self_stem.form, self_stem.form + "i"]
            return [self_stem.form + "i"]
        if right_nonstem.form == "" and self_stem.form.endswith("ə"):
            return [self_stem.form[:-1] + "i"]
        # TODO: the qg => r rule seems to be quite strong
        if self_stem.form.endswith("q"):
            if (right_nonstem.form.startswith("g") 
                                             and "^" not in right_nonstem.form 
                                             and right_nonstem.left.truncative):
                return [self_stem.form]
            elif isinstance(right_nonstem.left, HTRSandhi):
                if self_stem.form.endswith("əq"):
                    return [self_stem.weakened]
                return [self_stem.dropped]
        if self_stem.right.cons_end and (right_nonstem.left.truncative 
                                         or right_nonstem.left.double_cons):
            return [self_stem.dropped]
        return [self_stem.form]

class JuaqSandhi(LeftSandhi):

    def left_join(self, self_nonstem, left_stem):
        if left_stem.right.cons_end:
            return ["t" + self_nonstem.form[1:]]
        return super().left_join(self_nonstem, left_stem)

class PassPartSandhi(LeftSandhi):
    """
    Left sandhi of the passive participle `-ðaq`. 

    This class prototype does not state the fact that it is truncative,
    but should be included upon instance creation.
    """

    def left_join(self, self_nonstem, left_stem):
        # update: ignore the following comment
        # NOTE: we can directly state its form because it is a *left* sandhi;
        # for right sandhis, because they will be inherited, this will be a wrong approach
        assert self_nonstem.form.startswith("ða")
        if not left_stem.right.cons_end or isinstance(left_stem.right, TeSandhi):
            return ["c" + self_nonstem.form[1:]]
        if left_stem.form.endswith("q"):
            return ["g" + self_nonstem.form[1:]]   # TODO: geminating?!?!?!
        return ["t" + self_nonstem.form[1:]]
        # return super().left_join(self_nonstem, left_stem)

class KStemSandhi(RightSandhi):
    
    def right_join(self, self_stem: Stem, right_nonstem: NonStem):
        if isinstance(right_nonstem.left, (PluralSandhi, SgErgSandhi)):
            # special case for nuup
            if self_stem.form == "nuuk" and isinstance(right_nonstem.left, SgErgSandhi): 
                return ["nu"]
            if self_stem.form.endswith("iik"):
                return [self_stem.form[:-2]]
            return [self_stem.dropped] # delete -k
        if right_nonstem.form.startswith('g') and not right_nonstem.left.truncative:
            return [self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

class MarlukSandhi(KStemSandhi):
    # NOTE: this might be temporary fix only, as marlunnut means "two o'clock" specifically
    def right_join(self, self_stem, right_nonstem):
        if isinstance(right_nonstem, NounEnding) and right_nonstem.form.startswith('n'):
            # NOTE: this may involve wrong cases of possessive endings, but give up treatment for now
            return [self_stem.form, self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

class LimitedGemSandhi(RightSandhi):
    def right_join(self, self_stem, right_nonstem):
        if isinstance(right_nonstem.left, (PluralSandhi, SgErgSandhi)):
            return [self_stem.geminated]
        return super().right_join(self_stem, right_nonstem)

class SsaSandhi(RightSandhi):
    """
    This is just a "flag" to some verbal endings indicating that there's a -ssa
    coming round. Nothing special will happen on -ssa itself.
    """
    pass

class HabDupSandhi(RightSandhi):
    """
    The sandhi of habitual -ðaq. 
    
    The only notable thing is that it duplicates itself when meeting -ðaq 
    (passive participle) **after vowel stems**.
    """

    # TODO: remember vowel stem???

    def right_join(self, self_stem, right_nonstem):
        if isinstance(right_nonstem.left, PassPartSandhi) and self_stem.form.endswith("aioueə"):
            if right_nonstem.left.truncative or right_nonstem.left.double_cons:
                return [self_stem.form + "ða"]
            # NOTE: this is actually useless, but for the sake of someone using
            # PassPartSandhi without being truncative
            return [self_stem.form + "ðaq"]
        return super().right_join(self_stem, right_nonstem)

class VGeDropSandhi(LeftSandhi):
    
    def left_join(self, self_nonstem, left_stem):
        if isinstance(left_stem.right, GeSandhi):
            if self_nonstem.form.startswith(("va", "v^vu", "vi")):
                return [self._get_chunk(self_nonstem)[1:]] + super().left_join(self_nonstem, left_stem) # OPTIONALLY
            elif self_nonstem.form.startswith("l^l"):
                return [self._get_chunk(self_nonstem)] # compulsory
        return super().left_join(self_nonstem, left_stem)

class SsaDropSandhi(LeftSandhi):
    # TODO: this also includes ge, but is not neat

    def left_join(self, self_nonstem, left_stem):
        if isinstance(left_stem.right, SsaSandhi):
            return [self_nonstem.form[1:]]
        if isinstance(left_stem.right, GeSandhi):
            # if self_nonstem.form.startswith(("va", "v^vu")):
            return [self._get_chunk(self_nonstem)[1:]] + super().left_join(self_nonstem, left_stem) # OPTIONALLY
        return super().left_join(self_nonstem, left_stem)

    # form = re.sub(pattern="ssavu([^ ])", repl=r"ssau\1", string=form)

class WeakQStemSandhi(RightSandhi):
    
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
            and right_nonstem.left.cons_start 
            and "^" not in right_nonstem.form
            and right_nonstem.form != "ga"):
            return [self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

class WeakenableSandhi(RightSandhi):
    """
    For strong q-stems and the rare strong k-stems.

    Their q/k endings get weakened (nasalized) upon several weakening endings/affixes.
    """

    def right_join(self, self_stem, right_nonstem):
        # assign this to both -u and other vowel-initial endings at the start, so no more computation
        if right_nonstem.left.weakening:  
            return [self_stem.weakened]
        return super().right_join(self_stem, right_nonstem)

class ReplaceSandhi(LeftSandhi):
    """
    This makes -təl- into -s- (TODO: OPTIONALLY). 
    The most representative affix is `-liuq`.
    """
    
    def left_join(self, self_nonstem: NonStem, left_stem: Stem) -> str: 
        if isinstance(left_stem.right, TeSandhi):
            return ["s" + self_nonstem.form[1:], self_nonstem.form] # OPTIONALLY
        return super().left_join(self_nonstem, left_stem)

class TeSandhi(RightSandhi):
    # TODO: this may be general? or, how to assign this to general verbs?
    # TODO: if something OPTIONALLY happens, how to make sure something happens at the same time.
    """
    Sandhi behavior of -tə verbal and noun stems. This basically includes three:
    - -tə drops its -ə when combining with SG.ABS
    - -tə-l?? becomes -s?? OPTIONALLY [realization: drop both t and ə, l becomes s]
    - when combined with a VERBAL affix, drop ə for NON-truncative affixes, and 
    keep the ə for truncative affixes (AND affixes with double consonants)
    """
    # form = re.sub(pattern=r"tə([mn])([iu])([kt])$", repl=r"\1\1\2\3", string=form)
    def right_join(self, self_stem, right_nonstem):
        if isinstance(right_nonstem.left, ReplaceSandhi): # OPTIONALLY
            return [self_stem.form[:-2], self_stem.form]
        if isinstance(right_nonstem.left, (PassPartSandhi, HTRSandhi)):  # ut(ə)-ðaq => uccaq
            return [self_stem.form[:-2] + "c"]
        if isinstance(right_nonstem.left, GukSandhi):
            return [self_stem.form[:-2]]
        if (right_nonstem.form == ""  # -tə originally gets dropped here
            or (right_nonstem.left.pos is SandhiPOS.VERB 
                and not right_nonstem.left.truncative 
                and not right_nonstem.left.double_cons
                and not isinstance(right_nonstem.left, PassPartSandhi))
            or (isinstance(right_nonstem, NounEnding) 
                and right_nonstem.form.startswith(('mi', 'mu')))):
            if "^" in right_nonstem.form:
                return [self_stem.form[:-2]]
            return [self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

class SchwaElideSandhi(RightSandhi):
    
    # The sandhi of qulə etc.
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
                and right_nonstem.form.startswith(('mi', 'mu'))):
            return [self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

# NOTE: we judge the Sandhi upon collection (and formation by "inheritance"), 
# so that no additional check is needed at runtime
class GemSandhi(RightSandhi):
    """Gemination behavior for weak q-stems and some k-ending stems such as ujarak."""
    
    # TODO: ujarak [temporary fix done]
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
            and "^" not in right_nonstem.form
            and right_nonstem.left.cons_start 
            and right_nonstem.form != "ga"):
            return [self_stem.geminated]
            # return self_stem.form[:-3] + gem_dict[self_stem.form[-3]] * 2 + self_stem.form[-2]
        return super().right_join(self_stem, right_nonstem)

class Type1MetathesisSandhi(RightSandhi):
    
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
            and not right_nonstem.left.cons_start 
            and right_nonstem.form != "") or isinstance(right_nonstem.left, (PluralSandhi)):
            return [self_stem.form[:-3] + "qq"]
        return super().right_join(self_stem, right_nonstem)

class Type2MetathesisSandhi(RightSandhi):
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
            and (isinstance(right_nonstem.left, (SgErgSandhi, PluralSandhi))
                or (not right_nonstem.left.cons_start and right_nonstem.form != ""))):
            # if len(self_stem.form) > 4 and self_stem.form[-3] == self_stem.form[-4]:
            #     return [self_stem.form[:-4] + "q" + self_stem.form[-3], self_stem.form[:-3] + "ɴɴ"]
            return [self_stem.form[:-3] + "q" + self_stem.form[-3], self_stem.form[:-3] + "ɴɴ"]
        return super().right_join(self_stem, right_nonstem)

class FusionalCMPSandhi(RightSandhi):
    # TODO
    
    def right_join(self, self_stem, right_nonstem):
        if right_nonstem.form == "nəq":  # comparative -nəq
            pass
        return super().right_join(self_stem, right_nonstem)

@dataclass
class HyphenSandhi(RightSandhi):
    # need_i_insertion: bool = True

    def right_join(self, self_stem, right_nonstem):
        if right_nonstem.form != "":
            return [self_stem.form + "~", self_stem.form + "~i"] # TODO: continue to use tilde?
        return [self_stem.form]

class GreenlandicISandhi(RightSandhi):
    """
    TODO: NOT YET IN USE.
    
    Sandhi behavior of greenlandized nouns such as `Jensen`.
    There will be an inserted i before subsequent affixes and endings
    if the noun ends in a consonant.
    """
    
    def right_join(self, self_stem, right_nonstem):
        return super().right_join(self_stem, right_nonstem)

class UsiqSandhi(RightSandhi):
    """
    A special group of nouns ending in -usiq, such as atausiq.

    Upon gemination, -s- becomes -tt-.
    """
    def right_join(self, self_stem, right_nonstem):
        if (isinstance(right_nonstem, NounEnding) 
            and right_nonstem.left.cons_start 
            and right_nonstem.form != "ga"):
            return [self_stem.form[:-3] + "tti"]
        return super().right_join(self_stem, right_nonstem)

class KkuqSandhi(RightSandhi):
    # TODO: can be with additional n or not
    
    def right_join(self, self_stem, right_nonstem):
        if right_nonstem.form.startswith("n"):
            return [self_stem.dropped, self_stem.dropped + "n"]
        elif right_nonstem.left.cons_start:
            return [self_stem.dropped]
        return super().right_join(self_stem, right_nonstem)

class GinnaqSandhi(LeftSandhi):

    def left_join(self, self_nonstem, left_stem):
        if bool(re.search(pattern="[aə][aiuə]$", string=left_stem.right.right_join(self_stem=left_stem, right_nonstem=self_nonstem)[0])):
            return [self_nonstem.form.replace("^", "")]
        return [self._get_chunk(self_nonstem=self_nonstem)]
        # return super().left_join(self_nonstem, left_stem)

class ThirdPlPossPlSandhi(LeftSandhi):
    """
    The left sandhi of 3PL.POSS.PL.ABS -i(t).

    It will become -at if its vowel can be assimilated to a, or it will become -i.
    """

    def left_join(self, self_nonstem, left_stem):
        # NOTE: you can use right_join of the other to peek what is really needed!
        left = left_stem.right.right_join(self_stem=left_stem, right_nonstem=self_nonstem)
        if left[0].endswith(tuple("aə")):
            return ["at"]
        return ["i"]
        # return super().left_join(self_nonstem, left_stem)

class PluralSandhi(LeftSandhi):
    """
    Sandhi of the plural absolutive/ergative marker -t (and also the 2nd person 
    possessive absolutive). It becomes -it for the following groups:

    - k-stems.
    - aq-dropping stems.
    - strong q-stems.
    """
    
    def left_join(self, self_nonstem, left_stem):
        if isinstance(left_stem.right, (KStemSandhi, AqDropSandhi, WeakenableSandhi, Type1MetathesisSandhi)):
            return ["it"]
        return super().left_join(self_nonstem, left_stem)

class SgErgSandhi(LeftSandhi):
    """
    Sandhi of the singular ergative marker -p. It becomes -up for the following groups:

    - k-stems.
    - aq-dropping stems.
    - strong q-stems.
    """
    def left_join(self, self_nonstem, left_stem):
        if isinstance(left_stem.right, (KStemSandhi, AqDropSandhi, WeakenableSandhi, Type1MetathesisSandhi, Type2MetathesisSandhi)):
            return ["up"]
        return super().left_join(self_nonstem, left_stem)
      
class GeSandhi(RightSandhi):
    """
    Sandhi of the possessive -gə (have ... as), -qə (very), and their derivational 
    verbal stems.
    """
    
    def right_join(self, self_stem, right_nonstem):
        # TODO: how to force the right to drop its first v?
        if isinstance(right_nonstem.left, VGeDropSandhi):
            if right_nonstem.form.startswith("l^l"): # contemporative, compulsory
                return [self_stem.dropped + "a"]
            # triple vowel, avoid the ə. OPTIONAL.
            elif bool(re.search("^va([aiəu])", right_nonstem.form)): 
                return [self_stem.dropped, self_stem.form]  # either gaa, or givaa
        return super().right_join(self_stem, right_nonstem)

class AqDropSandhi(RightSandhi):
    """
    The sandhi for aq-dropping nouns (e.g. nuliaq).

    This group of nouns (typically) drop their -aq with vowel-initial nonstems 
    (including the copular -u), and also with -it (PL.ABS) or -up (SG.ERG), 
    while at other times behave like a strong q-stem.
    """

    # TODO: irregularity
    def right_join(self, self_stem, right_nonstem):
        if ((not right_nonstem.left.cons_start and right_nonstem.form != "") 
            or isinstance(right_nonstem.left, (PluralSandhi, SgErgSandhi))):
            return [self_stem.form[:-2]] # delete -aq
        return super().right_join(self_stem, right_nonstem)

class GiJaqtuqSandhi(LeftSandhi):
    """
    The sandhi of `-(gi)jaqtuq`.

    It drops its gi before vowel-ending stems, but retains it after consonant-ending stems.
    """

    def left_join(self, self_nonstem, left_stem):
        if not left_stem.right.cons_end:
            return [self._get_chunk(self_nonstem=self_nonstem)]
        return [self_nonstem.form.replace("^", "")]

class TcTriggerSandhi(RightSandhi):
    
    def right_join(self, self_stem: Stem, right_nonstem: NonStem):
        if isinstance(right_nonstem.left, ActPartSandhi):
            if self_stem.form[-2] == "i":
                new_form = self_stem.form[:-2] + "ə" + self_stem.form[:-1]
                return super().right_join(self_stem, right_nonstem) + \
                    super().right_join(Stem(form=new_form, right=self_stem.right), right_nonstem)
        return super().right_join(self_stem, right_nonstem)
    
    # def right_join(self, self_stem, right_nonstem):
    #     # TODO: itself will have nothing to change! so this should be an indicator sandhi
    #     # change i to ə???
    #     if isinstance(right_nonstem.left, ActPartSandhi):
    #         # the -i(c) part should be dealt *before*, so just find loc of i and change it to ə
    #         return [self_stem.form[::-1].replace("i", "ə")[::-1]]
    #         # TODO: how to prevent assimilation? this is strange
    #     return super().right_join(self_stem, right_nonstem)

class ActPartSandhi(LeftSandhi):

    def left_join(self, self_nonstem, left_stem):
        if isinstance(left_stem.right, TcTriggerSandhi):
            return ["c" + self_nonstem.form[1:], self_nonstem.form]  # NONONONONONO
        return super().left_join(self_nonstem, left_stem)

class GukSandhi(LeftSandhi):
    
    def left_join(self, self_nonstem, left_stem):
        # if isinstance(left_stem, Te)
        if not left_stem.right.cons_end:
            return [self_nonstem.form, "j" + self_nonstem.form[1:], self_nonstem.form[1:] ]
        return super().left_join(self_nonstem, left_stem)

class HTRSandhi(LeftSandhi):
    """
    The sandhi of the HTR morpheme -ði/-ci/-i.
    """

    def left_join(self, self_nonstem, left_stem):
        if left_stem.form.endswith(tuple("kt")) or isinstance(left_stem.right, TeSandhi):
            return ["ci"]
        if left_stem.form.endswith("q"):
            return ["i"]
        return super().left_join(self_nonstem, left_stem)

class TTruncSandhi(LeftSandhi):
    """A sign that some affix will delete the final t in SOME stems."""
    pass

class TDeletingSandhi(TcTriggerSandhi):
    """
    Stems with this sandhi removes its final t when meeting `TTruncSandhi`.
    Since it ends in -t, it will also suffer from `TcTriggerSandhi` (for the moment).
    """
    # TODO: better way is to add a property to get real_truncative
    def right_join(self, self_stem, right_nonstem):
        if isinstance(right_nonstem.left, TTruncSandhi):
            return [self_stem.form[:-1]]
        return super().right_join(self_stem, right_nonstem)

class SandhiPOS(Enum):
    VERB = "verb"
    NOUN = "noun"

# @dataclass
# class Rule:
#     pattern: typing.Pattern
#     repl: str

# rule_patterns: dict[str, Rule] = {
#     'ð-cons': Rule(pattern=re.compile(f"({sound_dict['cons']})ð"), repl=r"\1t"), 
#     'ð-vow': Rule(pattern=re.compile(f"({sound_dict['vow']})ð"), repl=r"\1c")
# }

@dataclass
class Form:
    form: str # NOTE: now this becomes the expedited form
    left: LeftSandhi | BaseEncSandhi | None = None
    right: RightSandhi | WordSandhi | None = None
    protected_len: int = 0
    form_is_sound: bool = False
    greenlandic_i: bool = False

    def __post_init__(self):
        pass

    @cached_property
    def sound_surface(self) -> str:
        """
        A preprocessed (sound) representation of the underlying `form`.
        It has not yet reached the stage of spelling, and
        some notational conventions are still waiting to be incorporated.
        """
        protected_form = self.form[:self.protected_len]
        form = self.form[self.protected_len:]
        if len(form) > 0:
            if not self.form_is_sound:
                form = self._get_sound(form=form)
            form = self._adjust_sound(form=form)
        return protected_form + form

    @cached_property
    def surface(self) -> str:
        """
        The *unique* surface spelling representation of the underlying `form`.

        Any differences in spelling should come from different forms.
        """
        protected_form = self.form[:self.protected_len]
        form = self.form[self.protected_len:]
        if len(form) > 0:
            if not self.form_is_sound:
                form = self._get_sound(form=form)
            form = self._adjust_sound(form=form)
            # TODO: we still need to adjust something here
            form = self._sound_to_spelling(form=form)
        return protected_form + form
    
    def _get_sound(self, form: str) -> str:
        form = re.sub(pattern=f"({sound_dict['cons']})ð", repl=r"\1t", string=form)   # ð-rule-1
        form = re.sub(pattern=f"({sound_dict['vow']})ð", repl=r"\1c", string=form)   # ð-rule-2
        form = re.sub(pattern=f"i({sound_dict['cons']}?)t({sound_dict['vow']})", repl=r"i\1s\2", string=form) # t2s-rule
        form = form.replace("T", "t") # release those not to be affected by the t2s rule
        form = re.sub(pattern=f"({sound_dict['cons']})y", repl=r"\1g", string=form)  # y-rule-1
        form = re.sub(pattern=f"({sound_dict['vow']})y", repl=r"\1j", string=form) # y-rule-2
        form = re.sub(pattern=f"ə({sound_dict['cons']})", repl=r"i\1", string=form) # ə-rule-1
        form = re.sub(pattern=f"ə([aiuəj])", repl=r"a\1", string=form) # ə-rule-2
        form = form.replace("aai", "aavi")
        form = form.replace("aau", "aaju")
        return form

    def _adjust_sound(self, form: str) -> str:
        # form = re.sub(pattern=rf"({sound_dict['vow']})V", repl=r"\1\1", string=form)

        # modified a-rule to exclude -ai-ending ones
        form = re.sub(pattern=rf"a(?!i\Z){sound_dict['vow']}", repl=r"aa", string=form) 
        # TODO: t(ts)-rule
        
        # g-rule
        form = form.replace("qg", "r") 
        # consonant-rules
        form = re.sub(pattern=f"{sound_dict['^qr_cons']}([qtslmnŋf])", repl=r"\1\1", string=form) 
        form = re.sub(pattern=f"{sound_dict['^tqr_cons']}c", repl=r"cc", string=form)
        form = re.sub(pattern="[qr]([tcslmn])", repl=r"r\1", string=form)
        form = re.sub(pattern=f"{sound_dict['^qr_cons']}[vp]", repl="pp", string=form)
        form = re.sub(pattern=f"[qr][vp]", repl="rp", string=form)
        form = re.sub(pattern=f"{sound_dict['^gqr_cons']}[gk]", repl="kk", string=form)
        form = re.sub(pattern=f"[qr][gk]", repl="rk", string=form)
        # form = re.sub(pattern="[qr]v", repl="rp", string=form)

        form = re.sub(pattern=f"i({sound_dict["uv"]})", repl=r"e\1", string=form) # uv-rule-1
        form = form.replace("ie", "ee") # uv-rule-1
        form = re.sub(pattern=f"u({sound_dict["uv"]})", repl=r"o\1", string=form) # uv-rule-2
        form = form.replace("uo", "oo") # uv-rule-2

        # form = re.sub(pattern="gg", repl="kk", string=form)
        # form = re.sub(pattern="[qr]g", repl="rk", string=form)
        form = re.sub(pattern="[qr]f", repl="rf", string=form)
        form = re.sub(pattern=f"{sound_dict['^r_cons']}r", repl="qq", string=form)
        # form = re.sub(pattern="[rq]q", repl="qq", string=form)
        # form = re.sub(pattern="jj", repl="ss", string=form)

        form = form.replace("ij", "i")
        form = re.sub("uv([aie])", r"u\1", form)
        form = form.replace("uuu", "uuju")
        form = form.replace("iii", "iivi")
        form = form.replace("aaa", "aava")
        return form
    
    def _sound_to_spelling(self, form:str) -> str:
        # TODO: we might need to add Vq/rC to here, depending on acc
        form = form.replace("ŋŋ", "nng")
        form = form.replace("ŋ", "ng")
        form = form.replace("tti", "tsi")
        form = form.replace("tte", "tse")
        form = form.replace("c", "s")
        form = form.replace("ɴɴ", "rng")
        form = form.replace("ɴ", "rng")
        return form
    
    @property
    def mofo_form(self):
        return "{" + self.form + "}"

@dataclass
class Word(Form):
    # pos: str | None = None

    def __post_init__(self):
        super().__post_init__()
        if self.right is None:
            self.right = WordSandhi()
        self.right.cons_end = bool(re.search(pattern=f"{sound_dict['cons']}$", string=self.form))
    
    def join(self, enc: Enclitic) -> list[Word | Stem]:
        assert isinstance(enc, Enclitic)
        if self.greenlandic_i and not self.form.endswith("i"):
            return []
        left_forms = self.right.right_join(self_word=self, right_enc=enc)
        right_forms = enc.left.left_join(self_enc=enc, left_word=self)
        if min(len(left_forms), len(right_forms)) == 1:
            new_forms = list(l+r for l, r in product(left_forms, right_forms))
        else:
            assert max(len(left_forms), len(right_forms)) == 2
            new_forms = list(l+r for l, r in zip(left_forms, right_forms))
        if "V" in right_forms[0]:
            new_forms = [re.sub(pattern=rf"({sound_dict['vow']})V", 
                                repl=r"\1\1", 
                                string=new_form) for new_form in new_forms]
        if isinstance(enc, CommonEnclitic):
            return [Word(form=new_form, 
                         form_is_sound=True, 
                         protected_len=self.protected_len) for new_form in new_forms]
        # print(Stem(form=self.form+enc.form, protected_len=self.protected_len))
        assert isinstance(enc, DerivEnclitic)
        return [Stem(form=new_form, 
                     protected_len=self.protected_len, 
                     right=enc.right) for new_form in new_forms]

@dataclass
class Morpheme(Form):
    pass

@dataclass
class NonEnding(Morpheme):
    pass
    
@dataclass
class NonStem(Morpheme):
    truncative: bool = False
    weakening: bool = False

gem_dict = {
    "v" : "p", 
    "l": "l", 
    "j": "s", 
    "g": "k", 
    "r": "q", 
    "q": "q",
    "m": "m", 
    "t": "t"
}

# TODO: idea: NonStem uses its left sandhi to check Stem and changes its shape
# Stem uses its right sandhi to check NonStem and changes its shape
# then combine the changed form of both

@dataclass
class Stem(NonEnding):

    @cached_property
    def geminated(self):
        assert self.form[-3] in gem_dict
        return self.form[:-3] + gem_dict[self.form[-3]] * 2 + self.form[-2]

    # @property
    # def metathesized(self):
    #     raise NotImplementedError

    @property
    def dropped(self):
        """The form dropping its last phoneme, no matter whether it is a consonant or vowel."""
        return self.form[:-1]
    
    @property
    def weakened(self):
        if self.form[-1] == "q":
            return self.dropped + "r"
        if self.form[-1] == "k":
            return self.dropped + "ŋ"
        raise NotImplementedError
    
    @property
    def mofo_form(self):
        sandhi_dict = {
            SandhiPOS.VERB: "V", 
            SandhiPOS.NOUN: "N",
            None: "?"
        }
        return "{" + self.form + "}" + sandhi_dict[self.right.pos]

    # TODO: we should be able to yield more than one way of joining
    def join(self, morph: NonStem) -> list[Stem | Word]:
        left_forms = self.right.right_join(self_stem=self, right_nonstem=morph)
        right_forms = morph.left.left_join(self_nonstem=morph, left_stem=self)
        if min(len(left_forms), len(right_forms)) == 1:
            new_forms = list(l+r for l, r in product(left_forms, right_forms))
        else:
            assert max(len(left_forms), len(right_forms)) == 2
            new_forms = list(l+r for l, r in zip(left_forms, right_forms))
        # new_forms = [left_form + right_form]
        new_forms = [re.sub(pattern=rf"({sound_dict['vow']})V", 
                            repl=r"\1\1", 
                            string=new_form) for new_form in new_forms]
        results = []
        # TODO, this will be slow, notice that no judgments are done based on new forms
        for new_form in new_forms: 
            if isinstance(morph, Ending):
                gr_i = self.greenlandic_i if morph.form == "" else False
                results.append(Word(form=new_form, 
                                    greenlandic_i=gr_i, 
                                    protected_len=self.protected_len))
            else:
                if isinstance(morph.left, PassPartSandhi) and right_forms == ["gaq"]:
                    new_right = GemSandhi(pos=SandhiPOS.NOUN, cons_end=True)
                elif ((morph.form == "ðaq" 
                       and not isinstance(morph.left, PassPartSandhi) 
                       and not self.right.cons_end)
                    or (isinstance(self.right, HabDupSandhi) 
                        and morph.form == "ðaq" 
                        and not isinstance(morph.left, PassPartSandhi))):
                    new_right = HabDupSandhi(pos=SandhiPOS.VERB, cons_end=True)
                else:
                    new_right = morph.right
                results.append(Stem(form=new_form, right=new_right, protected_len=self.protected_len))
        return results
 

@dataclass
class Affix(NonStem, NonEnding):
    
    def __post_init__(self):
        super().__post_init__()
        form = self.form
        if bool(re.search(f"^{sound_dict['cons']}", form)):
            self.left.cons_start = True
        if bool(re.search(f"^{sound_dict['cons']}{sound_dict['cons']}", form)) and "^" not in form:
            self.left.double_cons = True
        if bool(re.search(f"{sound_dict['cons']}$", form)):
            self.right.cons_end = True
    
    def __hash__(self):
        return hash((self.form, self.left.truncative, type(self.left), type(self.right)))
    
    @property
    def mofo_form(self):
        sandhi_dict = {
            SandhiPOS.VERB: "V", 
            SandhiPOS.NOUN: "N",
            None: "?"
        }
        trunc = "-" if self.left.truncative else ""
        return sandhi_dict[self.left.pos] + "{" + trunc + self.form + "}" + sandhi_dict[self.right.pos]


@dataclass
class Ending(NonStem):
    _truncative: bool = False  # NOTE: this is only a temporary fix
    
    def __post_init__(self):
        super().__post_init__()
        if self.left is None:
            self.left = LeftSandhi(pos=None, truncative=self._truncative)
        form = self.form
        if bool(re.search(f"^{sound_dict['cons']}", form)):
            self.left.cons_start = True
        if bool(re.search(f"^{sound_dict['cons']}{sound_dict['cons']}", form)) and "^" not in form:
            self.left.double_cons = True
    
    @property
    def mofo_form(self):
        sandhi_dict = {
            SandhiPOS.VERB: "V", 
            SandhiPOS.NOUN: "N",
            None: "?"
        }
        trunc = "-" if self.left.truncative else ""
        return sandhi_dict[self.left.pos] + "{" + trunc + self.form + "}"

@dataclass
class Enclitic(Morpheme):
    
    def __post_init__(self):
        super().__post_init__()
        if self.left is None:
            self.left = BaseEncSandhi()
        self.left.cons_start = bool(re.search(f"^{sound_dict['cons']}", string=self.form))

    @property
    def mofo_form(self):
        sandhi_dict = {
            SandhiPOS.VERB: "V", 
            SandhiPOS.NOUN: "N",
            None: "?"
        }
        trunc = "-" if self.left.truncative else ""
        pos = sandhi_dict[self.right.pos] if self.right is not None and self.right.pos is not None else ""
        return "*{" + trunc + self.form + "}" + pos

class CommonEnclitic(Enclitic):
    pass

@dataclass
class WordSandhi(BaseSandhi): # TODO: this is not stem and nonstem, but word and enc
    cons_end: bool = False

    def right_join(self, self_word: Word, right_enc: Enclitic):
        nasal_dict = {
            "p": "m", 
            "t": "n", 
            "k": "ŋ",
        }
        form = self_word.form if isinstance(right_enc, DerivEnclitic) else self_word.sound_surface
        # the first if says: either it starts with a consonant or both are vowels
        if right_enc.left.truncative and self_word.right.cons_end:
            return [form[:-1]]
        if (right_enc.left.cons_start or 
            (not self_word.right.cons_end and not right_enc.left.cons_start)):
            if not isinstance(right_enc.left, GuuqSandhi):
                return [form]
            if form.endswith(tuple("ptk")):
                return [form[:-1] + "ŋ"] 
            return [form]  # vowel or q-ending
        if form.endswith(tuple("ptk")):
            return [form[:-1] + nasal_dict[form[-1]]]
        # q-ending, presumably
        return [form[:-1] + "r", form[:-1] + "ɴ"]
        # return super().right_join(self_stem, right_nonstem)

@dataclass
class BaseEncSandhi(BaseSandhi):
    cons_start: bool = True
    truncative: bool = False

    def _get_chunk(self, self_enc: Enclitic):
        chunk_ind = self_enc.form.find("^") + 1
        return self_enc.form[chunk_ind:]

    def left_join(self, self_enc: Enclitic, left_word: Word) -> list[str]: 
        # NOTE: not implemented for left_affix
        # check the sandhi of its left partner (e.g. Stem), and then change form
        if "^" in self_enc.form:
            if not left_word.right.cons_end:
                return [self_enc.form.replace("^", "")]
            return [self._get_chunk(self_enc=self_enc)]
        return [self_enc.form]


class GuuqSandhi(BaseEncSandhi):
    
    def left_join(self, self_enc, left_word):
        if left_word.right.cons_end and not left_word.form.endswith("q"):
            return ["ŋ" + self_enc.form[1:]]
        return super().left_join(self_enc, left_word)

@dataclass
class DerivEnclitic(Enclitic, Affix):
    pass #TODO: this may be better called EncliticStem, so it can take affixes and endings

enclitics: list[Enclitic] = [
    CommonEnclitic(form="lu"), 
    CommonEnclitic(form="li"), 
    CommonEnclitic(form="mi"), 
    CommonEnclitic(form="guuq", left=GuuqSandhi()),
    CommonEnclitic(form="luunniit"),
    CommonEnclitic(form='t^tauq'), 
    CommonEnclitic(form="kiaq"),
    CommonEnclitic(form="una"),
    CommonEnclitic(form="uku"),
    DerivEnclitic(form="ət", right=TDeletingSandhi(SandhiPOS.VERB)), 
    DerivEnclitic(form="kaq", 
                  left=BaseEncSandhi(truncative=True), 
                  right=RightSandhi(SandhiPOS.VERB)),
    DerivEnclitic(form="Vq", 
                  left=BaseEncSandhi(truncative=True), 
                  right=RightSandhi(SandhiPOS.VERB)),
]

class NounEnding(Ending):
    
    def __post_init__(self):
        super().__post_init__()
        self.left.pos = SandhiPOS.NOUN
        self.left.weakening = self.form in ("p", "t") or (not self.left.cons_start and self.form != "")

class VerbEnding(Ending):
    def __post_init__(self):
        super().__post_init__()
        self.left.pos = SandhiPOS.VERB

@dataclass
class BaseMorphemeSeq:
    morphemes: list[Morpheme]
    protected_len: int = 0

    
    def __str__(self):
        if len(self.morphemes) == 0:
            return ""
        if isinstance(self.morphemes[-1], Enclitic):
            return self._prior_str() + "=" + self.morphemes[-1].form
        if self.morphemes[-1].form == "": # sg.abs
            return self._prior_str()
        if len(self.morphemes) > 1:
            return self._prior_str() + "-" + self.morphemes[-1].form
        if self.morphemes[-1].form.endswith("~"):
            return self.morphemes[-1].form[:-1]
        return self.morphemes[-1].form
    
    @property
    def mofo_str(self):
        if len(self.morphemes) == 0:
            return ""
        if len(self.morphemes) > 1:
            prior_str = self._prior_mofo_str()
            if isinstance(self.morphemes[-1], Enclitic):
                # assert prior_str[-1] == "?" or prior_str[-1] == self.morphemes[-1].mofo_form[0]
                return prior_str + self.morphemes[-1].mofo_form
            assert prior_str[-1] == "?" or prior_str[-1] == self.morphemes[-1].mofo_form[0]
            if self.morphemes[-1].form == "": # sg.abs
                # assert prior_str[-1] in ("?", "N")
                return prior_str[:-1] + "N{∅}"
            return prior_str[:-1] + self.morphemes[-1].mofo_form
        if self.morphemes[-1].form.endswith("~"):
            return "{" + self.morphemes[-1].form[:-1] + "}?"
        return self.morphemes[-1].mofo_form
    
    def _prior_str(self):
        return str(MorphemeSeq(morphemes=self.morphemes[:-1]))
    
    def _prior_mofo_str(self):
        return MorphemeSeq(morphemes=self.morphemes[:-1]).mofo_str

@dataclass
class MorphemeSeq(BaseMorphemeSeq):
    """
    Morpheme sequence with computational function supported.
    """

    def join(self) -> list[Word | Stem]:
        # TODO: maybe this not needed?
        if len(self.morphemes) == 1:
            return [self.morphemes[0]]
        if len(self.morphemes) == 2:
            morph0 = self.morphemes[0]
            morph1 = self.morphemes[1]
            # we allow MorphemeSeq to be incomplete, so not necessarily ending
            assert ((isinstance(morph0, Stem) and isinstance(morph1, NonStem)) 
                    or (isinstance(morph0, Word) and isinstance(morph1, Enclitic)))
            new_morphs = morph0.join(morph1)
            for new_morph in new_morphs:
                new_morph.protected_len = self.protected_len
            return new_morphs
        last_morpheme, prior_morphemes = self.morphemes[-1], self.morphemes[:-1]
        priors = MorphemeSeq(morphemes=prior_morphemes, 
                             protected_len=self.protected_len).join()
        return [r for prior in priors for r in prior.join(last_morpheme)]
    
    def extend(self, morpheme: Morpheme):
        return MorphemeSeq(morphemes=self.morphemes + [morpheme], 
                           protected_len=self.protected_len)
    
    def to_data(self) -> list[MorphemeSeqData]:
        return [MorphemeSeqData(morphemes=self.morphemes, 
                               protected_len=self.protected_len, 
                               repr=rep) for rep in self.join()]


# NOTE: we give up join here, and only use this as a container, to improve speed.
# TODO: each MorphemeSeqData should still have one Word | Stem, 
# BUT `extend` should produce LISTS of MorphemeSeqData
@dataclass
class MorphemeSeqData(BaseMorphemeSeq):
    """
    A mere data container tracking the sequence of morphemes and 
    their corresponding joined form `repr.`
    
    There is no computational function here; users should use `MorphemeSeq` instead.

    The main usage of this class is to save the time of repeated `MorphemeSeq.join`
    computations by using the `extend` method.
    """
    repr: Stem | Word = field(default_factory=lambda _: Word(form=""))

    def extend(self, morpheme: Morpheme) -> list[MorphemeSeqData]:
        extended_list = self.morphemes + [morpheme]
        return [MorphemeSeqData(morphemes=extended_list, 
                                protected_len=self.protected_len, 
                                repr=rep) for rep in self.repr.join(morpheme)]

# TODO: affixes and endings are more or less closed, but stems are too open and better be extracted
#TODO: prefixes (aa-, tac(c)-)
#TODO: enclitics: nasalization (esp. =guuq) still not done