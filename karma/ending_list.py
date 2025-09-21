from .structures import Ending, VerbEnding, NounEnding, VGeDropSandhi, \
    Sandhi, SandhiPOS, SsaDropSandhi, PluralSandhi, SgErgSandhi, ActPartSandhi, \
    GukSandhi, ThirdPlPossPlSandhi, sound_dict

endings: list[Ending] = [
    # verb endings
    VerbEnding("vamgət"),
    VerbEnding("vagət"), # variant of -vamgət
    VerbEnding("lakkit", _truncative=True),
    VerbEnding("lakka", _truncative=True),
    VerbEnding("laqvut", _truncative=True),
    VerbEnding("ligət", _truncative=True), # TODO: trunc?
    VerbEnding("lijuk", _truncative=True), # TODO: trunc?
    VerbEnding("gakku"),
    VerbEnding("gakkət"),
    VerbEnding("gavət"),
    VerbEnding("gaaŋat"),
    VerbEnding("git"),   # TODO: add back truncative
    VerbEnding("kkit"),
    VerbEnding("gitci"),
    VerbEnding("gisi"),
    VerbEnding("gijuk"),
    VerbEnding("vigət"),
    VerbEnding("visi"), 
    VerbEnding("visijuk"), 
    VerbEnding("vijuk"),
    VerbEnding("vit"), 
    VerbEnding("visigut"),
    VerbEnding("v^vat"), 
    VerbEnding("va"), 
    VerbEnding("la", _truncative=True), 
    VerbEnding("m^mat"), 
    VerbEnding("m^mata"), 
    VerbEnding("m^maŋa"), 
    VerbEnding("m^massuk"),
    VerbEnding("m^magit"),
    VerbEnding("m^magu"),
    VerbEnding("n^nata"), 
    VerbEnding("nakku"),   # CAUSM.NEG.1SG>3SG
    VerbEnding("navət"),
    VerbEnding("namijuk"), # CAUSM.NEG.4SG>3SG
    VerbEnding("gassi"), 
    VerbEnding("gami"), 
    VerbEnding("gamik"), 
    VerbEnding("gamikku"), 
    VerbEnding("gama"), 
    VerbEnding("gamta"), 
    VerbEnding("l^lusi"), 
    VerbEnding("l^lugit"), 
    VerbEnding("l^lutik"), 
    VerbEnding("l^lutət"), 
    VerbEnding("nagu"), 
    VerbEnding("nasi"), 
    VerbEnding("nani"), 
    VerbEnding("natik"),
    VerbEnding("naŋa"),
    VerbEnding("l^lugu"), 
    VerbEnding("l^luŋa"), 
    VerbEnding("l^luni"), 
    VerbEnding("l^luta"),
    VerbEnding("laq", _truncative=True), 
    VerbEnding("lara", _truncative=True), 
    VerbEnding("latət", _truncative=True), 
    VerbEnding("laqsi", _truncative=True), 
    VerbEnding("l^lat"), 
    VerbEnding("lat", _truncative=True),
    VerbEnding("laŋa", _truncative=True), 
    VerbEnding("lagut", _truncative=True), 
    VerbEnding("vuq"),  # IND.3SG
    VerbEnding("vusi"),
    VerbEnding("v^vut"), # IND.3PL
    VerbEnding("vutət"), 
    VerbEnding("vuŋa"),  # IND.1SG
    VerbEnding("vaqma"), 
    VerbEnding("vatət"), 
    VerbEnding("vavut"),
    VerbEnding("vaqvut"),
    VerbEnding("vaatigut"), # IND.3SG>1PL
    VerbEnding("vaa"),  # IND.3SG>3SG
    VerbEnding("vaasi"), 
    VerbEnding("vamsi"), 
    VerbEnding("vat"), 
    VerbEnding("vai"),  # IND.3SG>3PL
    VerbEnding("vara"), # IND.1SG>3PL
    VerbEnding("vaaŋa"), 
    VerbEnding("vakka"), 
    VerbEnding("vaat"), 
    VerbEnding("vugut"), 
    VerbEnding("vaattət"),
    VerbEnding("vaatət"),
    VerbEnding("vasi"),
    VerbEnding("viŋa"),
    VerbEnding("na"), # IMP.2SG
    VerbEnding("ta"), # IMP.1PL
    VerbEnding("guni"),
    VerbEnding("guniuk"),
    VerbEnding("gukku"),
    VerbEnding("gukkit"),
    VerbEnding("gussi"),
    VerbEnding("guit"),
    VerbEnding("ganni"),
    VerbEnding("gaanni"),
    VerbEnding("gaat"),
    VerbEnding("gamigit"),
    VerbEnding("li"),# OPT.3SG
    VerbEnding("guk", left=GukSandhi(pos=SandhiPOS.VERB)),
    VerbEnding("ðuŋa"), # PART.1SG
    VerbEnding("ðuq"),  # PART.3SG
    VerbEnding("ðut"),  # PART.3PL
    VerbEnding("ðutət"),
    VerbEnding("ðugut"),
    VerbEnding("ðusi"),
    VerbEnding("gəa"),
    VerbEnding("gai"),
    VerbEnding("gaaŋata"),  # ITR.3PL
    VerbEnding("gaaŋatta"), # ITR.1PL
    VerbEnding("gaaŋamik"),
    VerbEnding("gamiŋa"),
    VerbEnding("guma"),
    VerbEnding("gutta"),
    VerbEnding("gamijuk"),
    VerbEnding("gamtəgu"),
    VerbEnding("tigut"),
    VerbEnding("p^pat"), # COND.3SG

    # noun endings
    NounEnding("t", left=PluralSandhi(pos=SandhiPOS.NOUN)), 
    NounEnding("p", left=SgErgSandhi(pos=SandhiPOS.NOUN)),
    NounEnding("ata", _truncative=True), 
    NounEnding("isa", _truncative=True), 
    NounEnding("ga"), 
    NounEnding("tta"), # 1PL.POSS.SG.ABS
    NounEnding("tta", _truncative=True), # 1PL.POSS.PL.ABS
    NounEnding("kka", _truncative=True), 
    NounEnding("a", _truncative=True),
    NounEnding("i", _truncative=True),
    NounEnding("ni"),
    NounEnding("ni", _truncative=True), 
    NounEnding("q^vut"), 
    NounEnding("vut", _truncative=True),
    NounEnding("q^si"), 
    NounEnding("si", _truncative=True),
    NounEnding("at", _truncative=True),
    NounEnding("q^tək"), 
    NounEnding("tək", _truncative=True),
    NounEnding("ma"),
    NounEnding("ma", _truncative=True), 
    NounEnding("mi"),
    NounEnding("mi", _truncative=True), 
    NounEnding("vsi"),
    NounEnding("vsi", _truncative=True), 
    NounEnding("ssinnit"),
    NounEnding("ssinnit", _truncative=True), 
    NounEnding("mik"),
    NounEnding("mik", _truncative=True), 
    NounEnding("nik"),
    NounEnding(""),
    NounEnding("mit"),
    NounEnding("nit"),
    NounEnding("miit"),
    NounEnding("niit"),
    NounEnding("mut"),
    NounEnding("nut"),
    NounEnding("mini"),
    NounEnding("mini", _truncative=True),
    NounEnding("minni"),
    NounEnding("minni", _truncative=True),
    NounEnding("minik"),
    NounEnding("minik", _truncative=True),
    NounEnding("minnik"),
    NounEnding("minnik", _truncative=True),
    NounEnding("minut"),
    NounEnding("minut", _truncative=True),
    NounEnding("minnut"), 
    NounEnding("minnut", _truncative=True),
    NounEnding("mikkut"),
    NounEnding("mikkut", _truncative=True),
    NounEnding("ani", _truncative=True),
    NounEnding("anik", _truncative=True),
    NounEnding("annik", _truncative=True),
    NounEnding("anni", _truncative=True),
    NounEnding("anit", _truncative=True),
    NounEnding("annit", _truncative=True),
    NounEnding("anut", _truncative=True),
    NounEnding("annut", _truncative=True),
    NounEnding("inut", _truncative=True),  # 3SG.POSS.PL.ALL
    NounEnding("kkut"),
    # NounEnding("na"),  # remove this, since it will never appear there again
    NounEnding("tut"), 
    NounEnding("nni"),
    NounEnding("nni", _truncative=True), 
    NounEnding("ttənnut"),
    NounEnding("ttənni"),
    NounEnding("ttənnit"),
    NounEnding("təgut"), # PL.VIA
    NounEnding("agut", _truncative=True), # 3SG.POSS.SG.VIA
    NounEnding("atut", _truncative=True), 
    NounEnding("atigut", _truncative=True), # 3PL.POSS.SG.VIA or sometimes 3SG.POSS.SG.VIA due to misuse
    NounEnding("it", left=ThirdPlPossPlSandhi(pos=SandhiPOS.NOUN, truncative=True)),
    NounEnding("itni", _truncative=True),
    NounEnding("tət", _truncative=True),
]

for ending in endings:
    if isinstance(ending, VerbEnding):
        if ending.form.startswith(("l^l", "va", "v^vu", "vi")):
            ending.left = VGeDropSandhi(pos=SandhiPOS.VERB, truncative=ending.left.truncative, cons_start=True)
        elif ending.form.startswith("vu"):
            ending.left = SsaDropSandhi(pos=SandhiPOS.VERB, truncative=ending.left.truncative, cons_start=True)
        elif ending.form.startswith("ðu"): # Participial
            ending.left = ActPartSandhi(pos=SandhiPOS.VERB, truncative=ending.left.truncative, cons_start=True)

ending_vn_dict: dict[SandhiPOS, list[Ending]] = {
    SandhiPOS.NOUN: [],
    SandhiPOS.VERB:[],
    None: endings
}

for ending in endings:
    ending_vn_dict[ending.left.pos].append(ending)
