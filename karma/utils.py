def get_sound_regex() -> dict[str, str]:
    """
    Build the sound dictionary to select a group of sounds, including vowels,
    consonants, uvulars, or a group consonants excluding at most 3 consonants.
    """
    from itertools import product
    sound_dict: dict[str, str] = {}
    consonants = "tscðpvfkgqrlmnŋjɴ"
    uvulars = "qrɴ"
    vowels = "aiuəV"
    for con in consonants:
        sound_dict["cons"] = f"[{consonants}]"
        sound_dict["vow"] = f"[{vowels}]"
        sound_dict["uv"] = f"[{uvulars}]"
        sound_dict[f"^{con}_cons"] = f"[{''.join(filter(lambda c: c != con, consonants))}]"
    for twocon in ["".join(l) for l in product(consonants, consonants)]:
        sound_dict[f"^{twocon}_cons"] = f"[{''.join(filter(lambda c: c not in twocon, consonants))}]"
    for tricon in ["".join(l) for l in product(consonants, consonants, consonants)]:
        sound_dict[f"^{tricon}_cons"] = f"[{''.join(filter(lambda c: c not in tricon, consonants))}]"
    return sound_dict

sound_dict = get_sound_regex()

def is_vowel(char: str):
    assert len(char) == 1
    return char in "aiuəoe"

def is_ou(char: str):
    return char in "ou"

def is_aie(char: str):
    return char in "aiəe"

def is_cons(char: str):
    return char in "tscðpvfkgqrlmnŋj"
