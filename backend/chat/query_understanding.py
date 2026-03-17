import re
from dataclasses import dataclass


INTENT_KEYWORDS = {
    'theft': {
        'theft', 'stolen', 'steal', 'snatching', 'pickpocket', 'robbery', 'missing',
        'mobile theft', 'phone theft', 'wallet stolen',
    },
    'murder': {
        'murder', 'killed', 'homicide', 'dead', 'shooting', 'stabbing',
    },
    'harassment': {
        'harassment', 'misbehave', 'molest', 'eve teasing', 'abuse', 'intimidation',
    },
    'sexual_offence': {
        'rape', 'sexual assault', 'gang rape', 'sexual harassment', 'outrage modesty',
        'bad touch', 'inappropriate touch', 'unwanted touching', 'child sexual abuse',
        'raped', 'forced sex', 'minor raped',
    },
    'cyber_fraud': {
        'scam', 'fraud', 'phishing', 'online fraud', 'upi fraud', 'otp fraud',
        'account hacked', 'sim misuse', 'cyber attack',
    },
    'privacy_violation': {
        'photo misuse', 'image leak', 'morphed photo', 'private photo', 'online defamation',
    },
    'fire_arson': {
        'fire', 'arson', 'burn', 'blaze', 'house on fire',
    },
    'wage_dispute': {
        'salary not paid', 'unpaid salary', 'wages', 'minimum wages', 'underpaid',
        'salary due', 'private company salary due',
    },
    'domestic_violence': {
        'domestic violence', 'husband beating', 'cruelty', 'dowry harassment', 'dowry demand',
    },
    'marriage_divorce': {
        'marriage dispute', 'divorce', 'family court', 'dowry',
    },
    'education_fee': {
        'college fee', 'college fine', 'no facilities in college', 'student grievance',
    },
    'hospital_issue': {
        'hospital denied treatment', 'medical negligence', 'wrong treatment', 'patient grievance',
    },
    'transport_bus': {
        'private bus complaint', 'government bus complaint', 'bus overcharge', 'unsafe bus',
    },
    'rto_transport': {
        'rto issue', 'driving licence', 'driving license', 'license renewal', 'rc transfer',
        'vehicle registration', 'e challan', 'wrong challan', 'permit issue', 'commercial permit',
    },
    'accident_traffic': {
        'accident', 'traffic injury', 'mact', 'compensation claim',
    },
    'traffic_rules': {
        'traffic rules', 'helmet fine', 'drunk driving', 'overspeed', 'dangerous driving',
        'no seat belt', 'red light jump', 'challan',
    },
    'chain_snatching': {
        'chain snatching', 'gold chain snatched', 'neck chain stolen', 'snatched chain',
    },
    'tree_cutting': {
        'tree cutting', 'illegal tree cutting', 'tree felling', 'cutting trees',
    },
    'fake_doctor_medicine': {
        'fake doctor', 'quack doctor', 'unlicensed doctor', 'fake medicine',
        'spurious medicine', 'duplicate medicine', 'adulterated medicine',
    },
    'women_safety': {
        'women safety', 'stalking woman', 'eve teasing', 'molestation', 'outrage modesty',
        'domestic violence against woman', 'dowry harassment',
    },
    'men_safety': {
        'men safety', 'man blackmail', 'false complaint', 'criminal intimidation to man',
        'assault on man', 'extortion from man',
    },
    'child_elder_safety': {
        'child safety', 'child abuse', 'minor assault', 'elder abuse', 'senior citizen abuse',
        'parents maintenance', 'old age harassment',
    },
    'trai_telecom': {
        'no signal', 'network not coming', 'call not coming', 'call not going', 'call drop',
        'voice call issue', 'sim network issue', 'tower issue', 'trai complaint',
    },
    'loan_banking': {
        'home loan rejected', 'loan not approved', 'bank not approved loan', 'loan delay',
        'housing loan issue', 'emi dispute', 'bank grievance', 'loan processing complaint',
    },
    'family_property': {
        'family land dispute', 'family property dispute', 'partition suit', 'ancestral property',
        'brother land dispute', 'family vehicle ownership dispute',
    },
    'landlord_tenant': {
        'house owner forcing', 'landlord harassment', 'eviction threat', 'water supply not gave',
        'water supply denied by owner', 'essential service denied by landlord',
    },
    'pollution': {
        'noise pollution', 'sound pollution', 'air pollution', 'land pollution', 'soil pollution',
        'waste burning smoke', 'factory pollution', 'water pollution',
    },
    'political_issues': {
        'political issue', 'election threat', 'vote buying', 'money for vote',
        'booth intimidation', 'candidate bribery', 'party worker threat',
    },
    'local_governance': {
        'panchayat issue', 'village issue', 'town issue', 'city issue',
        'no water tank', 'ward complaint', 'municipality issue', 'corporation complaint',
        'garbage not collected', 'drainage not cleaned', 'mla not consider complaint', 'mp not consider complaint',
        'water tank not clean', 'dirty water tank',
    },
    'missing_person': {
        'person missing', 'missing person', 'person are missing', 'person is missing',
        'child missing', 'man missing', 'woman missing', 'not returned home',
    },
    'temple_issues': {
        'temple issue', 'temple trust money misuse', 'temple administration complaint',
        'encroachment near temple', 'temple property dispute', 'religious place damage',
    },
    'civic_infra': {
        'no road', 'pothole', 'drainage issue', 'sewage overflow', 'street light', 'water supply issue',
    },
    'land_property': {
        'land encroachment', 'boundary dispute', 'illegal construction', 'property dispute',
    },
    'agriculture': {
        'crop loss', 'farmer compensation', 'agriculture grievance',
    },
    'governance_rti': {
        'rti', 'government complaint', 'district grievance', 'state department complaint',
    },
    'electricity_eb': {
        'eb issue', 'electricity board complaint', 'wrong electricity bill', 'high electricity bill',
        'power cut', 'no current', 'low voltage', 'meter tampering', 'electricity theft',
        'illegal power connection', 'disconnection notice',
    },
    'advertising_grievance': {
        'advertisement complaint', 'misleading advertisement', 'false ad', 'fake ad', 'ad fraud',
        'obscene advertisement', 'indecent advertisement', 'magic remedy advertisement',
    },
}

LOCATION_HINTS = {
    'home', 'house', 'bus', 'office', 'street', 'school', 'college', 'market', 'workplace',
    'village', 'city', 'town', 'district', 'state', 'country',
}
TIME_HINTS = {'today', 'yesterday', 'night', 'morning', 'evening', 'afternoon'}
OBJECT_HINTS = {
    'bike', 'phone', 'car', 'wallet', 'money', 'salary', 'photo', 'cheque', 'land',
    'road', 'drainage', 'water', 'bus', 'hospital', 'mobile',
    'electricity', 'eb', 'meter', 'bill', 'voltage', 'current',
}

TYPO_MAP = {
    'marraige': 'marriage',
    'dowri': 'dowry',
    'driverse': 'divorce',
    'diverse': 'divorce',
    'hosipital': 'hospital',
    'goverment': 'government',
    'accitent': 'accident',
    'telated': 'related',
    'drelated': 'related',
    'tret': 'threat',
    'facilites': 'facilities',
    'facilitis': 'facilities',
    'phne': 'phone',
    'stolan': 'stolen',
    'frad': 'fraud',
    'badtouch': 'bad touch',
    'harrasing': 'harassment',
    'harasing': 'harassment',
    'harresing': 'harassment',
    'harrasment': 'harassment',
    'harasment': 'harassment',
    'rapped': 'rape',
    'rapd': 'rape',
    'rapeed': 'rape',
    'pocho': 'pocso',
    'poxo': 'pocso',
    'advadistment': 'advertisement',
    'advertizement': 'advertisement',
    'medician': 'medicine',
    'medecine': 'medicine',
    'docter': 'doctor',
    'sanaching': 'snatching',
    'snaching': 'snatching',
    'ruls': 'rules',
    'eleter': 'elder',
    'lon': 'loan',
    'lone': 'loan',
    'comming': 'coming',
    'womens': 'women',
    'mens': 'men',
    'vehical': 'vehicle',
    'noice': 'noise',
    'pollutione': 'pollution',
    'gave': 'give',
    'politcal': 'political',
    'panchyat': 'panchayat',
    'municpality': 'municipality',
    'villge': 'village',
    'tample': 'temple',
    'isuess': 'issues',
    'clened': 'cleaned',
    'cleen': 'clean',
    'missng': 'missing',
    'prson': 'person',
    'consder': 'consider',
    'considar': 'consider',
    'currnt': 'current',
    'electrcity': 'electricity',
    'volatge': 'voltage',
}

PHRASE_ALIASES = {
    'no road in my street': 'no road civic infrastructure',
    'drainage damage': 'drainage issue sewage overflow',
    'sewage damage': 'sewage overflow drainage issue',
    'water logging': 'drainage issue sewage overflow',
    'street light not working': 'street light civic issue',
    'water supply issue': 'water supply complaint civic issue',
    'neighbor encroached my land': 'land encroachment boundary dispute',
    'illegal construction': 'land encroachment illegal construction',
    'college amount due fine': 'college fee fine grievance',
    'paid but not getting facilities': 'college no facilities grievance',
    'hospital denied treatment': 'hospital denied treatment patient grievance',
    'private company salary due': 'private company salary due grievance',
    'private bus issue': 'private bus complaint transport grievance',
    'government bus issue': 'government bus complaint transport grievance',
    'publish related': 'online publication defamation',
    'mobile related': 'mobile theft sim misuse cyber grievance',
    'natural related': 'natural disaster grievance',
    'agriculture related': 'agriculture crop loss grievance',
    'village related': 'village panchayat grievance',
    'eb issue': 'electricity board complaint',
    'current issue': 'power cut no current electricity complaint',
    'wrong current bill': 'wrong electricity bill billing grievance',
    'low voltage in my area': 'electricity low voltage complaint',
    'meter issue': 'electricity meter reading complaint',
    'bad touch': 'inappropriate touch sexual harassment',
    'bad touching': 'inappropriate touch sexual harassment',
    'touched me inappropriately': 'inappropriate touch sexual harassment',
    'inappropriately touched': 'inappropriate touch sexual harassment',
    'bad touch in school': 'child sexual abuse pocso',
    'bad touch to child': 'child sexual abuse pocso',
    'minor raped': 'child rape pocso penetrative sexual assault',
    'child raped': 'child rape pocso penetrative sexual assault',
    'misleading ad': 'misleading advertisement consumer grievance',
    'fake advertisement': 'misleading advertisement consumer grievance',
    'advertisement fraud': 'misleading advertisement consumer grievance',
    'advadistment fraud': 'misleading advertisement consumer grievance',
    'obscene ad': 'obscene advertisement indecent representation',
    'chain sanaching': 'chain snatching robbery theft',
    'gold chain sanaching': 'chain snatching robbery theft',
    'tree cutting': 'illegal tree cutting environmental offence',
    'fake doctor': 'quack doctor impersonation cheating medical fraud',
    'fake medician': 'spurious medicine fake medicine drugs and cosmetics offence',
    'traffic rules': 'traffic rule violation helmet seatbelt overspeed drunk driving',
    'women safety': 'women safety harassment molestation stalking legal protection',
    'men safety': 'men safety assault blackmail extortion intimidation legal protection',
    'child safety': 'child safety pocso juvenile justice legal protection',
    'eleter safety': 'elder safety senior citizen protection and maintenance',
    'no signal in my area': 'telecom no signal network issue trai grievance',
    'calls are not coming': 'telecom incoming call issue call drop trai grievance',
    'calls are not going': 'telecom outgoing call issue call drop trai grievance',
    'bank not approved my home loan': 'home loan rejection banking grievance rbi ombudsman',
    'bank was not approved my loan': 'loan rejection banking grievance rbi ombudsman',
    'house owner is forcing': 'landlord harassment illegal eviction tenant grievance',
    'water supply not gave': 'landlord denied essential water supply tenant grievance',
    'noice like sound and air pollution': 'noise pollution sound pollution air pollution grievance',
    'family land issue': 'family land dispute partition ancestral property',
    'family vehical issue': 'family vehicle ownership dispute property sharing',
    'family vehical ownership dispute': 'family vehicle ownership dispute property sharing',
    'family vehical and ownership problem': 'family vehicle ownership dispute property sharing',
    'noice pollution': 'noise pollution sound nuisance complaint',
    'air pollution complaint': 'air pollution environmental complaint',
    'land pollution complaint': 'land pollution soil contamination complaint',
    'political issues': 'election intimidation vote bribery political grievance',
    'panchayat not water tank': 'panchayat village no water tank civic grievance',
    'town issues': 'town municipality civic grievance',
    'village issues': 'village panchayat civic grievance',
    'city issues': 'city municipal corporation civic grievance',
    'temple issues': 'temple administration trust grievance religious institution complaint',
    'garbage was not take': 'garbage not collected municipal solid waste grievance',
    'garbage was not taken': 'garbage not collected municipal solid waste grievance',
    'drainage was not clean': 'drainage not cleaned sewage municipal grievance',
    'water tank was not clean': 'water tank not clean public health grievance',
    'person are missing': 'person missing tracing complaint',
    'person is missing': 'person missing tracing complaint',
    'mla was not consider': 'mla not responding public grievance escalation',
    'mp was not consider': 'mp not responding public grievance escalation',
}


@dataclass
class QueryUnderstanding:
    normalized_query: str
    intents: list[str]
    entities: list[str]
    enriched_query: str


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def _apply_typos_and_aliases(normalized_query: str) -> str:
    tokens = [TYPO_MAP.get(tok, tok) for tok in normalized_query.split()]
    q = ' '.join(tokens)
    for src, dst in PHRASE_ALIASES.items():
        if src in q:
            q = q.replace(src, f'{src} {dst}')
    return q


def _extract_intents(normalized_query: str) -> list[str]:
    found = []

    # include uni/bi/tri-grams for better phrase matching
    toks = normalized_query.split()
    grams = set(toks)
    grams.update(' '.join(toks[i:i + 2]) for i in range(max(0, len(toks) - 1)))
    grams.update(' '.join(toks[i:i + 3]) for i in range(max(0, len(toks) - 2)))

    for intent, words in INTENT_KEYWORDS.items():
        if any(word in normalized_query for word in words) or any(word in grams for word in words):
            found.append(intent)

    return sorted(set(found))


def _extract_entities(tokens: list[str]) -> list[str]:
    entities = []
    for tok in tokens:
        if tok in LOCATION_HINTS or tok in TIME_HINTS or tok in OBJECT_HINTS:
            entities.append(tok)
    return sorted(set(entities))


def build_enriched_query(normalized_query: str, intents: list[str], entities: list[str]) -> str:
    parts = [normalized_query]
    if intents:
        # Intent tags guide downstream scoring/routing
        parts.append(' '.join(intents))
    if entities:
        parts.append(' '.join(entities))
    return ' '.join(parts).strip()


def understand_user_query(user_query: str) -> QueryUnderstanding:
    normalized = _normalize_text(user_query)
    normalized = _apply_typos_and_aliases(normalized)
    tokens = normalized.split()
    intents = _extract_intents(normalized)
    entities = _extract_entities(tokens)
    enriched = build_enriched_query(normalized, intents, entities)
    return QueryUnderstanding(
        normalized_query=normalized,
        intents=intents,
        entities=entities,
        enriched_query=enriched,
    )
