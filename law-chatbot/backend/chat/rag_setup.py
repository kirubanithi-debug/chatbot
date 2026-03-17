import os
import re
import shutil
from difflib import SequenceMatcher, get_close_matches
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_PATH = DATA_DIR / 'legal_sections.csv'
CHROMA_DIR = BASE_DIR / 'chroma_db'
COLLECTION_NAME = 'indian_law_collection'
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_EMBED_MODEL = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
REQUIRED_COLUMNS = ['law', 'section', 'punishment', 'next_steps', 'keywords']
STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'my', 'our', 'your', 'in', 'on',
    'at', 'of', 'to', 'for', 'with', 'by', 'from', 'and', 'or', 'not',
}
SYNONYM_GROUPS = [
    {'theft', 'stolen', 'steal', 'stealing', 'robbed', 'robbery', 'snatch', 'snatched', 'pickpocket', 'missing', 'lost'},
    {'murder', 'killed', 'kill', 'homicide', 'dead', 'death', 'stabbing', 'shooting'},
    {'salary', 'wage', 'wages', 'pay', 'paid', 'unpaid', 'income'},
    {'scam', 'fraud', 'phishing', 'cheated', 'cheating', 'upi', 'cyber', 'online'},
    {'photo', 'image', 'picture', 'pic', 'selfie', 'morph', 'morphed', 'leak', 'leaked', 'upload', 'uploaded', 'social', 'media', 'instagram', 'facebook'},
    {'misbehave', 'misbehavior', 'misbehaviour', 'harass', 'harassment', 'molest', 'abuse', 'eve', 'teasing'},
    {'bad touch', 'inappropriate touch', 'unwanted touching', 'sexual harassment', 'child abuse', 'minor'},
    {'rape', 'raped', 'forced sex', 'sexual assault', 'minor rape', 'child rape', 'pocso'},
    {'fire', 'arson', 'blaze', 'burn', 'burning', 'flames', 'explosive'},
    {'internet', 'network', 'broadband', 'wifi', '5g', '4g', 'speed', 'slow', 'lag', 'call', 'drop'},
    {'road', 'street', 'pothole', 'drainage', 'sewage', 'municipal', 'civic', 'footpath'},
    {'land', 'property', 'encroachment', 'boundary', 'construction', 'illegal', 'plot', 'survey'},
    {'social', 'community', 'caste', 'discrimination', 'abuse', 'public', 'nuisance'},
    {'marriage', 'dowry', 'divorce', 'threat', 'family', 'husband', 'wife'},
    {'college', 'student', 'fee', 'fine', 'facility', 'education', 'refund'},
    {'hospital', 'medical', 'treatment', 'patient', 'negligence', 'emergency'},
    {'company', 'private', 'employment', 'salary', 'pf', 'termination', 'workplace'},
    {'bus', 'private bus', 'government bus', 'transport', 'rto', 'ticket', 'licence', 'license', 'rc', 'challan', 'permit'},
    {'electricity', 'eb', 'tneb', 'bescom', 'power', 'current', 'meter', 'bill', 'transformer', 'disconnection', 'outage', 'voltage'},
    {'accident', 'traffic', 'injury', 'claim', 'compensation', 'mact'},
    {'chain snatching', 'snatching', 'gold chain', 'neck chain', 'robbery', 'theft'},
    {'tree cutting', 'tree felling', 'illegal cutting', 'forest', 'environment'},
    {'fake doctor', 'quack', 'unlicensed doctor', 'impersonation', 'medical fraud'},
    {'fake medicine', 'spurious drug', 'duplicate medicine', 'drugs and cosmetics'},
    {'traffic rules', 'helmet', 'seat belt', 'overspeed', 'drunk driving', 'dangerous driving'},
    {'women safety', 'stalking', 'molestation', 'eve teasing', 'domestic violence', 'dowry harassment'},
    {'men safety', 'assault', 'blackmail', 'extortion', 'criminal intimidation'},
    {'child safety', 'pocso', 'juvenile justice', 'child abuse', 'minor protection'},
    {'elder safety', 'senior citizen', 'parents maintenance', 'elder abuse'},
    {'trai', 'no signal', 'call drop', 'incoming call issue', 'outgoing call issue', 'network issue'},
    {'home loan', 'loan rejected', 'loan delay', 'housing loan', 'bank grievance', 'rbi ombudsman'},
    {'family property', 'ancestral property', 'partition', 'family land', 'co-owner dispute', 'vehicle ownership'},
    {'landlord', 'tenant', 'house owner', 'eviction', 'rent', 'water supply denied', 'essential service'},
    {'noise pollution', 'sound pollution', 'air pollution', 'land pollution', 'soil pollution', 'public nuisance'},
    {'political', 'election', 'vote', 'candidate', 'booth', 'bribery', 'undue influence', 'party worker'},
    {'panchayat', 'village', 'town', 'city', 'municipality', 'corporation', 'ward', 'water tank', 'civic'},
    {'temple', 'religious institution', 'trust', 'hrce', 'endowment', 'devotee', 'temple property'},
    {'garbage', 'waste', 'collection', 'municipal solid waste', 'door to door collection', 'not lifted'},
    {'mla', 'mp', 'representative', 'not responding', 'grievance', 'public complaint'},
    {'missing person', 'person missing', 'tracing', 'not returned home', 'kidnapping', 'abduction'},
    {'agriculture', 'farmer', 'crop', 'village', 'panchayat', 'rural'},
    {'mobile', 'phone', 'sim', 'imei', 'data', 'misuse'},
    {'cyber', 'online', 'publication', 'defamation', 'post', 'social media'},
    {'advertisement', 'ad', 'ads', 'misleading', 'false claim', 'fake ad', 'obscene ad', 'indecent', 'magic remedy'},
]
PHRASE_NORMALIZATION = {
    'salary not paid': 'unpaid wages salary',
    'incentive not provided': 'bonus withheld unpaid wages salary',
    'incentive not paid': 'bonus withheld unpaid wages salary',
    'insentive not provided': 'bonus withheld unpaid wages salary',
    'insentive not paid': 'bonus withheld unpaid wages salary',
    'company does not provide incentive': 'bonus withheld unpaid wages salary',
    'company does not provide insentive': 'bonus withheld unpaid wages salary',
    'company not providing incentive': 'bonus withheld unpaid wages salary',
    'company not providing insentive': 'bonus withheld unpaid wages salary',
    'bonus not paid': 'bonus withheld unpaid wages salary',
    'money missing': 'cash stolen theft',
    'amount missing': 'cash stolen theft',
    'phone missing': 'phone stolen theft',
    'bike missing': 'bike stolen theft',
    'photo misuse': 'image misuse privacy violation',
    'image misuse': 'photo misuse privacy violation',
    'misbehave on me': 'harassment misbehavior',
    'someone misbehaved with me': 'harassment misbehavior',
    'misbehaved with me': 'harassment misbehavior',
    'bad touch': 'inappropriate touch sexual harassment',
    'bad touching': 'inappropriate touch sexual harassment',
    'unwanted touching': 'inappropriate touch sexual harassment',
    'inappropriate touching': 'inappropriate touch sexual harassment',
    'touched me inappropriately': 'inappropriate touch sexual harassment',
    'inappropriately touched': 'inappropriate touch sexual harassment',
    'rapped': 'rape',
    'raped': 'rape',
    'minor raped': 'child rape pocso penetrative sexual assault',
    'child raped': 'child rape pocso penetrative sexual assault',
    'misleading ad': 'misleading advertisement consumer grievance',
    'fake advertisement': 'misleading advertisement consumer grievance',
    'advertisement fraud': 'misleading advertisement consumer grievance',
    'advadistment fraud': 'misleading advertisement consumer grievance',
    'obscene ad': 'obscene advertisement indecent representation grievance',
    'chain sanaching': 'chain snatching robbery theft grievance',
    'gold chain sanaching': 'chain snatching robbery theft grievance',
    'tree cutting issue': 'illegal tree cutting environmental offence grievance',
    'fake docter': 'fake doctor medical impersonation grievance',
    'fake medician': 'fake medicine spurious drug grievance',
    'traffic rule issue': 'traffic rules violation grievance',
    'women safety issue': 'women safety harassment molestation stalking grievance',
    'men safety issue': 'men safety assault blackmail extortion grievance',
    'child safety issue': 'child safety pocso juvenile justice grievance',
    'eleter safety issue': 'elder safety senior citizen grievance',
    'no signal issue': 'trai telecom no signal call drop grievance',
    'calls not coming': 'trai telecom incoming call issue grievance',
    'calls not going': 'trai telecom outgoing call issue grievance',
    'home loan not approved': 'home loan rejection banking grievance',
    'loan not approved': 'home loan rejection banking grievance',
    'bank was not approved my loan': 'home loan rejection banking grievance',
    'house owner is forcing': 'landlord harassment illegal eviction tenant grievance',
    'water supply not gave': 'landlord denied essential water supply tenant grievance',
    'noice like sound and air pollution': 'noise pollution sound pollution air pollution grievance',
    'family land issue': 'family land dispute partition ancestral property grievance',
    'family vehical issue': 'family vehicle ownership dispute grievance',
    'family vehical and ownership problem': 'family vehicle ownership dispute grievance',
    'noice pollution': 'noise pollution public nuisance grievance',
    'air pollution complaint': 'air pollution environmental grievance',
    'land pollution complaint': 'land pollution environmental grievance',
    'political issues': 'political election intimidation vote bribery grievance',
    'panchayat not water tank': 'panchayat village no water tank civic grievance',
    'town issues': 'town municipal civic grievance',
    'village issues': 'village panchayat civic grievance',
    'city issues': 'city municipal corporation civic grievance',
    'temple issues': 'temple administration trust grievance religious institution complaint',
    'garbage was not take': 'garbage not collected municipal solid waste grievance',
    'garbage was not taken': 'garbage not collected municipal solid waste grievance',
    'drainage was not clean': 'drainage not cleaned sewage municipal grievance',
    'water tank was not clean': 'water tank not clean public health grievance',
    'person are missing': 'person missing tracing complaint',
    'person is missing': 'person missing tracing complaint',
    'prson is missng': 'person missing tracing complaint',
    'prson missing': 'person missing tracing complaint',
    'person is missng': 'person missing tracing complaint',
    'mla was not consider': 'mla not responding public grievance escalation',
    'mp was not consider': 'mp not responding public grievance escalation',
    'following and harassing': 'stalking harassment',
    'keeps following me': 'stalking',
    'fire in my house': 'house fire arson',
    'house on fire': 'house fire arson',
    'someone set fire': 'arson fire',
    'internet speed is low': 'telecom internet slow speed network issue',
    'my internet speed is low': 'telecom internet slow speed network issue',
    'network speed low': 'telecom internet slow speed network issue',
    'pay for 5g': 'telecom 5g service deficiency',
    'no road in my street': 'civic road infrastructure street grievance',
    'there is no road in my street': 'civic road infrastructure street grievance',
    'bad road in my area': 'civic road pothole infrastructure grievance',
    'pothole problem': 'civic road pothole infrastructure grievance',
    'drainage damage': 'civic drainage sewage municipal grievance',
    'drainage problem': 'civic drainage sewage municipal grievance',
    'sewage overflow': 'civic drainage sewage municipal grievance',
    'water logging': 'civic drainage sewage municipal grievance',
    'land encroachment': 'land property encroachment boundary dispute',
    'neighbor encroached my land': 'land property encroachment boundary dispute',
    'illegal construction': 'land property illegal construction municipal complaint',
    'property boundary dispute': 'land property boundary dispute',
    'street light not working': 'civic municipal street light grievance',
    'water supply issue': 'civic municipal water supply grievance',
    'marraige problem': 'marriage family dispute grievance',
    'dowri harassment': 'dowry demand harassment grievance',
    'driverse problem': 'divorce family dispute grievance',
    'diverse problem': 'divorce family dispute grievance',
    'marraige problem': 'marriage family dispute grievance',
    'dowri problem': 'dowry demand harassment grievance',
    'treat by someone': 'criminal intimidation threat grievance',
    'someone treat me': 'criminal intimidation threat grievance',
    'college amount due': 'college fee dues grievance',
    'paid but no facilities': 'college service deficiency grievance',
    'hosipital issue': 'hospital treatment negligence grievance',
    'private company problem': 'private company employment grievance',
    'private bus issue': 'private bus passenger grievance',
    'goverment bus issue': 'government bus service grievance',
    'rto issue': 'rto transport grievance',
    'driving licence issue': 'rto driving licence grievance',
    'driving license issue': 'rto driving licence grievance',
    'rc transfer issue': 'rto registration certificate transfer grievance',
    'vehicle registration issue': 'rto registration certificate transfer grievance',
    'wrong challan': 'rto challan dispute grievance',
    'challan issue': 'rto challan dispute grievance',
    'permit issue': 'rto permit grievance',
    'school bus safety issue': 'school bus safety transport grievance',
    'natural related issue': 'natural disaster relief grievance',
    'agriculture related issue': 'agriculture crop loss grievance',
    'village telated issue': 'village panchayat civic grievance',
    'city related issue': 'city town municipal grievance',
    'accitent issue': 'accident compensation traffic grievance',
    'mobile related issue': 'mobile theft data misuse grievance',
    'publish related issue': 'online publication defamation grievance',
    'eb issue': 'electricity board service grievance',
    'current bill issue': 'electricity billing grievance',
    'power cut issue': 'electricity outage complaint',
    'low voltage issue': 'electricity voltage fluctuation complaint',
    'meter issue': 'electricity meter tampering billing complaint',
    'illegal electricity connection': 'electricity theft unauthorized connection complaint',
}
COMMON_TYPOS = {
    'sallary': 'salary',
    'salery': 'salary',
    'insentive': 'incentive',
    'incetive': 'incentive',
    'incenitve': 'incentive',
    'paied': 'paid',
    'payed': 'paid',
    'cheatd': 'cheated',
    'som1': 'someone',
    'plz': 'please',
    'hlp': 'help',
    'phne': 'phone',
    'bas': 'bus',
    'murdr': 'murder',
    'muder': 'murder',
    'stolan': 'stolen',
    'frad': 'fraud',
    'thieft': 'theft',
    'morping': 'morphing',
    'insta': 'instagram',
    'misbehaviour': 'misbehavior',
    'misbehaved': 'misbehave',
    'fiar': 'fire',
    'fier': 'fire',
    'marraige': 'marriage',
    'dowri': 'dowry',
    'driverse': 'divorce',
    'diverse': 'divorce',
    'hosipital': 'hospital',
    'goverment': 'government',
    'accitent': 'accident',
    'telated': 'related',
    'drelated': 'related',
    'neighbour': 'neighbor',
    'neighbours': 'neighbors',
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
    'consder': 'consider',
    'considar': 'consider',
    'missng': 'missing',
    'prson': 'person',
}
_LAST_DATA_MTIME = None
FUZZY_TOKEN_MIN_LEN = 4
FUZZY_TOKEN_CUTOFF = 0.86
MAX_CANDIDATE_EVAL = 160
KEYWORD_ENRICHMENT_RULES = {
    'theft': ['stolen', 'steal', 'snatching', 'pickpocket', 'robbery', 'missing', 'property'],
    'robbery': ['snatching', 'weapon', 'threat', 'loot'],
    'murder': ['killed', 'homicide', 'death', 'attack'],
    'harassment': ['misbehave', 'abuse', 'molest', 'eve', 'teasing'],
    'sexual': ['bad touch', 'inappropriate touch', 'child abuse', 'unwanted touching', 'sexual harassment'],
    'stalking': ['follow', 'tracking', 'repeated calls', 'messages'],
    'rape': ['sexual assault', 'forced sex', 'consent'],
    'advertisement': ['misleading ad', 'false claim', 'fake ad', 'consumer complaint', 'obscene ad', 'indecent ad', 'magic remedy ad'],
    'fire': ['arson', 'burn', 'blaze', 'explosive'],
    'fraud': ['cheating', 'scam', 'phishing', 'otp', 'upi', 'online'],
    'privacy': ['photo misuse', 'image leak', 'morphed', 'without consent'],
    'wages': ['salary', 'unpaid', 'underpaid', 'employer'],
    'domestic': ['husband', 'family abuse', 'dowry', 'cruelty'],
    'kidnapping': ['abduct', 'missing child', 'ransom'],
    'forgery': ['fake document', 'signature', 'certificate'],
    'defamation': ['reputation', 'false statement', 'social media'],
    'intimidation': ['threat', 'fear', 'criminal intimidation'],
    'fir': ['police refused complaint', 'register complaint', 'cognizable'],
    'cheque': ['bounce', 'dishonour', 'bank memo'],
    'consumer': ['defective product', 'service deficiency', 'refund'],
    'drugs': ['narcotics', 'ganja', 'charas', 'heroin'],
    'rera': ['builder delay', 'flat possession', 'real estate'],
    'gst': ['fake invoice', 'itc', 'tax'],
    'tax': ['income tax', 'evasion', 'prosecution'],
    'telecom': ['internet speed', '5g', '4g', 'network issue', 'call drop', 'service deficiency', 'billing grievance'],
    'internet': ['telecom', 'network', 'slow speed', 'broadband', 'mobile data'],
    'road': ['street', 'pothole', 'drainage', 'municipal', 'civic', 'public works'],
    'drainage': ['sewage', 'water logging', 'municipal', 'sanitation', 'overflow'],
    'land': ['encroachment', 'boundary', 'survey', 'patta', 'title', 'property'],
    'construction': ['illegal construction', 'building rules', 'municipal approval'],
    'social': ['caste abuse', 'discrimination', 'public nuisance', 'community harassment'],
    'marriage': ['dowry', 'divorce', 'family court', 'maintenance'],
    'college': ['fee refund', 'student grievance', 'facility not provided', 'fine'],
    'hospital': ['medical negligence', 'denial of treatment', 'patient rights'],
    'company': ['salary due', 'pf issue', 'termination', 'labour complaint'],
    'bus': ['private bus', 'government bus', 'passenger grievance', 'ticket complaint'],
    'accident': ['mact claim', 'traffic injury', 'compensation'],
    'agriculture': ['crop loss', 'farmer compensation', 'village grievance'],
    'mobile': ['sim misuse', 'imei block', 'phone theft'],
    'rto': ['driving licence', 'license renewal', 'rc transfer', 'registration certificate', 'e challan dispute', 'permit issue'],
    'electricity': ['eb complaint', 'power cut', 'low voltage', 'wrong electricity bill', 'meter fault', 'unauthorized connection', 'disconnection notice'],
    'chain': ['chain snatching', 'gold chain snatched', 'neck chain theft', 'robbery'],
    'tree': ['tree cutting', 'tree felling', 'illegal tree removal', 'forest offence'],
    'doctor': ['fake doctor', 'quack', 'impersonation', 'medical fraud'],
    'medicine': ['fake medicine', 'spurious drug', 'counterfeit medicine', 'adulterated drug'],
    'traffic': ['traffic rules', 'helmet fine', 'seat belt', 'overspeed', 'drunk driving', 'dangerous driving'],
    'women': ['women safety', 'molestation', 'stalking', 'eve teasing', 'domestic violence', 'dowry harassment'],
    'men': ['men safety', 'assault', 'blackmail', 'extortion', 'intimidation'],
    'child': ['child safety', 'pocso', 'juvenile justice', 'child abuse', 'minor protection'],
    'elder': ['elder safety', 'senior citizen', 'parents maintenance', 'elder abuse'],
    'trai': ['no signal', 'call drop', 'incoming call issue', 'outgoing call issue', 'network issue'],
    'loan': ['home loan rejected', 'loan not approved', 'housing loan delay', 'bank grievance', 'rbi ombudsman'],
    'family': ['family property dispute', 'ancestral property', 'partition suit', 'co-owner dispute', 'family vehicle dispute'],
    'landlord': ['house owner forcing', 'landlord harassment', 'water supply denied', 'essential service denied', 'eviction threat'],
    'pollution': ['noise pollution', 'sound pollution', 'air pollution', 'land pollution', 'soil contamination', 'public nuisance'],
    'political': ['election threat', 'vote buying', 'money for vote', 'booth intimidation', 'candidate bribery'],
    'panchayat': ['panchayat issue', 'village civic issue', 'water tank missing', 'ward complaint'],
    'municipal': ['town issue', 'city issue', 'municipality complaint', 'corporation grievance'],
    'temple': ['temple issue', 'temple trust misuse', 'religious institution complaint', 'temple property dispute'],
    'garbage': ['garbage not collected', 'waste not lifted', 'solid waste complaint', 'door to door collection issue'],
    'drainage_cleaning': ['drainage not cleaned', 'sewer not cleaned', 'desilting not done', 'blocked drain complaint'],
    'mla_mp': ['mla not consider complaint', 'mp not consider complaint', 'representative not responding', 'public grievance escalation'],
    'missing_person': ['person missing', 'missing person report', 'tracing complaint', 'not returned home', 'missing diary'],
}

SEED_ROWS = [
    {
        'law': 'IPC 378',
        'section': 'Theft',
        'punishment': 'Up to 3 years imprisonment, or fine, or both',
        'next_steps': '1. File FIR at nearest police station. 2. Preserve ownership proof and CCTV. 3. Track FIR follow-up.',
        'keywords': 'bike stolen motorcycle theft cycle stolen vehicle theft phone stolen cash stolen money missing amount missing pickpocket bus theft wallet stolen',
    },
    {
        'law': 'IPC 302',
        'section': 'Murder',
        'punishment': 'Death penalty or life imprisonment, and fine',
        'next_steps': '1. Call police emergency immediately. 2. File FIR and provide witness details. 3. Cooperate with investigation and preserve evidence.',
        'keywords': 'murder killed homicide death attack stabbing shooting',
    },
    {
        'law': 'IPC 435',
        'section': 'Mischief by fire or explosive substance with intent to cause damage',
        'punishment': 'Imprisonment up to 7 years and fine',
        'next_steps': '1. Call fire service and police immediately. 2. Preserve fire-scene photos/CCTV and witness details. 3. File FIR for suspected arson and damage valuation.',
        'keywords': 'fire arson burn burning blaze set fire property damage explosive',
    },
    {
        'law': 'IPC 436',
        'section': 'Mischief by fire or explosive substance with intent to destroy house',
        'punishment': 'Imprisonment for life, or up to 10 years, and fine',
        'next_steps': '1. Inform fire brigade and police immediately. 2. Secure occupants and medical help. 3. File FIR with ownership proof, witness details, and loss assessment.',
        'keywords': 'house fire home burned arson house set on fire dwelling fire',
    },
    {
        'law': 'Payment of Wages Act, 1936',
        'section': 'Delayed or non-payment of wages',
        'punishment': 'Employer may face penalties and prosecution under labour law',
        'next_steps': '1. Send written demand notice. 2. Approach Labour Commissioner. 3. File claim under wages law.',
        'keywords': 'salary not paid unpaid wages employer not paying salary',
    },
    {
        'law': 'IT Act 2000 - Section 66D',
        'section': 'Cheating by personation using computer resources',
        'punishment': 'Up to 3 years imprisonment and fine up to 1 lakh rupees',
        'next_steps': '1. File cyber complaint at cybercrime.gov.in. 2. Report to bank and freeze transactions. 3. File FIR with evidence.',
        'keywords': 'online scam cyber fraud upi fraud phishing whatsapp scam',
    },
    {
        'law': 'IT Act 2000 - Section 66E',
        'section': 'Violation of privacy (capturing/publishing private images without consent)',
        'punishment': 'Up to 3 years imprisonment or fine up to 2 lakh rupees, or both',
        'next_steps': '1. Preserve screenshots/URLs/profile links. 2. File complaint at cybercrime.gov.in. 3. File FIR and request takedown from platform.',
        'keywords': 'photo misuse image misuse social media private photo leaked morphed photo fake profile instagram facebook whatsapp photo uploaded without consent',
    },
]

DOWNLOAD_URLS = [
    'https://raw.githubusercontent.com/vidhyasagarsriram/indian-law-datasets/main/ipc_sections.csv',
]


def _ollama_available(timeout: float = 1.2) -> bool:
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=timeout)
        return response.ok
    except requests.RequestException:
        return False


def _build_default_dataset() -> pd.DataFrame:
    return pd.DataFrame(SEED_ROWS, columns=REQUIRED_COLUMNS)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        lc = str(col).strip().lower()
        if lc in REQUIRED_COLUMNS:
            renamed[col] = lc
    if renamed:
        df = df.rename(columns=renamed)

    if any(col not in df.columns for col in REQUIRED_COLUMNS):
        return _build_default_dataset()

    out = df[REQUIRED_COLUMNS].copy().fillna('')
    for col in REQUIRED_COLUMNS:
        out[col] = out[col].astype(str).str.strip()
    return out


def _row_to_document(row: pd.Series) -> str:
    return (
        f"LAW: {str(row.get('law', '')).strip()}\n"
        f"SECTION: {str(row.get('section', '')).strip()}\n"
        f"PUNISHMENT: {str(row.get('punishment', '')).strip()}\n"
        f"NEXT STEPS: {str(row.get('next_steps', '')).strip()}\n"
        f"KEYWORDS: {str(row.get('keywords', '')).strip()}"
    )


def _token_parts(text: str) -> set[str]:
    parts = re.findall(r'[a-z0-9]+', str(text).lower())
    return {COMMON_TYPOS.get(p, p) for p in parts if p and p not in STOPWORDS}


def _enrich_keywords(law: str, section: str, keywords: str) -> str:
    section_lc = section.lower()
    law_lc = law.lower()
    enriched = set()
    enriched.update(_token_parts(keywords))
    enriched.update(_token_parts(section))
    enriched.update(_token_parts(law))

    combined = f'{law_lc} {section_lc} {keywords.lower()}'
    for trigger, extra_words in KEYWORD_ENRICHMENT_RULES.items():
        if trigger in combined:
            for word in extra_words:
                enriched.update(_token_parts(word))

    # Keep only useful search terms.
    enriched = {w for w in enriched if len(w) > 2}
    return ' '.join(sorted(enriched))


def _augment_keywords_column(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out['keywords'] = out.apply(
        lambda r: _enrich_keywords(
            law=str(r.get('law', '')),
            section=str(r.get('section', '')),
            keywords=str(r.get('keywords', '')),
        ),
        axis=1,
    )
    return out


def ensure_dataset() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists():
        return DATA_PATH

    for url in DOWNLOAD_URLS:
        try:
            response = requests.get(url, timeout=8)
            if response.ok and 'text' in response.headers.get('Content-Type', ''):
                DATA_PATH.write_text(response.text, encoding='utf-8')
                return DATA_PATH
        except requests.RequestException:
            continue

    _build_default_dataset().to_csv(DATA_PATH, index=False)
    return DATA_PATH


def _to_documents(df: pd.DataFrame):
    texts, metadatas = [], []
    for _, row in df.iterrows():
        law = str(row.get('law', '')).strip()
        section = str(row.get('section', '')).strip()
        texts.append(_row_to_document(row))
        metadatas.append({'law': law, 'section': section})
    return texts, metadatas


@lru_cache(maxsize=1)
def _load_df() -> pd.DataFrame:
    dataset_path = ensure_dataset()
    try:
        external_df = _normalize_df(pd.read_csv(dataset_path))
    except Exception:
        external_df = _build_default_dataset()

    seed_df = _build_default_dataset()
    merged = pd.concat([external_df, seed_df], ignore_index=True)
    merged = merged.drop_duplicates(subset=['law', 'section'], keep='first').fillna('')
    return _augment_keywords_column(merged)


def build_vector_store(reset: bool = True) -> None:
    df = _load_df()
    texts, metadatas = _to_documents(df)

    if reset and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    embedding = OllamaEmbeddings(base_url=OLLAMA_HOST, model=OLLAMA_EMBED_MODEL)
    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding,
        metadatas=metadatas,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )
    db.persist()


def clear_runtime_caches() -> None:
    _load_df.cache_clear()
    get_vector_store.cache_clear()
    _build_keyword_vocabulary.cache_clear()
    _build_search_records.cache_clear()


def rebuild_knowledge_base() -> None:
    clear_runtime_caches()
    build_vector_store(reset=True)


def _refresh_caches_if_data_changed() -> None:
    global _LAST_DATA_MTIME
    current_mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else None
    if _LAST_DATA_MTIME is None:
        _LAST_DATA_MTIME = current_mtime
        return
    if current_mtime != _LAST_DATA_MTIME:
        clear_runtime_caches()
        _LAST_DATA_MTIME = current_mtime


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        build_vector_store()

    embedding = OllamaEmbeddings(base_url=OLLAMA_HOST, model=OLLAMA_EMBED_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding,
        persist_directory=str(CHROMA_DIR),
    )


def similarity_search(query: str, k: int = 3):
    if not _ollama_available():
        raise RuntimeError('Ollama unavailable')
    db = get_vector_store()
    return db.similarity_search(query, k=k)


def _keyword_fallback(query: str, k: int = 3) -> str:
    query_tokens = _expand_with_synonyms(_tokenize(_normalize_query(query)))
    if not query_tokens:
        return ''

    ranked_rows = []
    for record in _build_search_records():
        score = len(query_tokens.intersection(record['haystack_tokens']))
        if score > 0:
            ranked_rows.append((score, record['row']))

    if not ranked_rows:
        return ''

    ranked_rows.sort(key=lambda item: item[0], reverse=True)
    docs = []
    for _, row in ranked_rows[:k]:
        docs.append(_row_to_document(row))
    return '\n\n'.join(docs)


@lru_cache(maxsize=1)
def _build_keyword_vocabulary() -> set[str]:
    vocab: set[str] = set()
    df = _load_df()

    for col in ['law', 'section', 'keywords']:
        for value in df[col].astype(str).str.lower():
            for token in re.findall(r'[a-z0-9]+', value):
                vocab.add(COMMON_TYPOS.get(token, token))

    for group in SYNONYM_GROUPS:
        vocab.update(group)

    return vocab


@lru_cache(maxsize=1)
def _build_search_records() -> list[dict]:
    records: list[dict] = []
    for row in _load_df().to_dict(orient='records'):
        law = str(row.get('law', ''))
        section = str(row.get('section', ''))
        keywords = str(row.get('keywords', ''))
        haystack_text = f'{keywords} {section} {law}'
        records.append(
            {
                'row': row,
                'law_lc': law.lower(),
                'section_lc': section.lower(),
                'haystack_text': haystack_text,
                'haystack_tokens': _token_parts(haystack_text),
            }
        )
    return records


def _normalize_token(token: str) -> str:
    normalized = COMMON_TYPOS.get(token, token)
    if len(normalized) < FUZZY_TOKEN_MIN_LEN:
        return normalized

    vocab = _build_keyword_vocabulary()
    if normalized in vocab:
        return normalized

    closest = get_close_matches(normalized, vocab, n=1, cutoff=FUZZY_TOKEN_CUTOFF)
    return closest[0] if closest else normalized


def _tokenize(text: str) -> set[str]:
    raw = re.findall(r'[a-z0-9]+', text.lower())
    normalized = [_normalize_token(token) for token in raw]
    return {token for token in normalized if token not in STOPWORDS}


def _normalize_query(query: str) -> str:
    normalized = query.lower().strip()
    for source, target in PHRASE_NORMALIZATION.items():
        normalized = normalized.replace(source, target)
    return normalized


def _expand_with_synonyms(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for group in SYNONYM_GROUPS:
        if expanded.intersection(group):
            expanded.update(group)
    return expanded


def _fuzzy_similarity(query: str, haystack: str) -> float:
    return SequenceMatcher(a=query.lower().strip(), b=haystack.lower().strip()).ratio()


def _entry_score(query: str, row: pd.Series) -> tuple[float, set[str]]:
    normalized_query = _normalize_query(query)
    base_query_tokens = _tokenize(normalized_query)
    query_tokens = _expand_with_synonyms(base_query_tokens)
    haystack_text = f"{row.get('keywords', '')} {row.get('section', '')} {row.get('law', '')}"
    haystack_tokens = _tokenize(haystack_text)

    overlap = query_tokens.intersection(haystack_tokens)
    if not base_query_tokens:
        return 0.0, set()

    token_score = min(1.0, len(overlap) / max(1, len(base_query_tokens)))
    fuzzy_score = _fuzzy_similarity(normalized_query, haystack_text)
    exact_bonus = 0.15 if str(row.get('section', '')).lower() in normalized_query else 0.0
    score = (0.7 * token_score) + (0.3 * fuzzy_score) + exact_bonus

    section_lc = str(row.get('section', '')).lower()
    if any(term in normalized_query for term in ['misbehave', 'misbehavior', 'harassment']):
        if ('sexual harassment' in section_lc) or ('insult modesty' in section_lc):
            score += 0.2
        if 'stalking' in section_lc and not any(t in normalized_query for t in ['follow', 'stalk', 'call', 'message']):
            score -= 0.2
        if 'suicide' in section_lc and not any(t in normalized_query for t in ['suicide', 'self harm', 'self-harm']):
            score -= 0.3

    if any(term in normalized_query for term in ['house', 'home', 'dwelling']) and any(
        term in normalized_query for term in ['fire', 'arson', 'burn', 'blaze']
    ):
        if 'destroy house' in section_lc:
            score += 0.2
        if 'cause damage' in section_lc:
            score -= 0.1

    if any(term in normalized_query for term in ['cheat', 'cheated', 'cheating', 'fraud', 'scam']):
        if 'cheating' in section_lc:
            score += 0.2
        if 'forgery' in section_lc and not any(t in normalized_query for t in ['document', 'certificate', 'signature', 'forged', 'fake']):
            score -= 0.2
        if any(t in normalized_query for t in ['upi', 'otp', 'online', 'bank']) and 'cheating by personation' in section_lc:
            score += 0.3

    law_lc = str(row.get('law', '')).lower()

    if any(term in normalized_query for term in ['hacked', 'hack', 'cyber attack', 'malware', 'ransomware', 'unauthorized access']):
        if ('computer related offences' in section_lc) or ('damage to computer systems' in section_lc):
            score += 0.25
        if 'it act' in law_lc and (('section 66' in law_lc) or ('section 43' in law_lc)):
            score += 0.35
        if 'cheating' in section_lc and not any(t in normalized_query for t in ['otp', 'upi', 'payment', 'bank']):
            score -= 0.35
        if 'personation' in section_lc and not any(t in normalized_query for t in ['otp', 'upi', 'payment', 'bank', 'scam', 'fraud']):
            score -= 0.25

    if ('itr' in normalized_query or 'return' in normalized_query) and any(
        t in normalized_query for t in ['late', 'penalty', 'fee']
    ):
        if 'default in furnishing return' in section_lc:
            score += 0.25
        if 'return of income filing obligations' in section_lc:
            score -= 0.1

    if any(t in normalized_query for t in ['internet', 'network', 'broadband', 'wifi', '5g', '4g', 'speed', 'call drop']):
        if any(t in section_lc for t in ['telecom', 'service quality', 'service deficiency', 'consumer']):
            score += 0.35
        if any(t in law_lc for t in ['income tax', 'gst', 'fema']):
            score -= 0.35

    if any(t in normalized_query for t in ['road', 'street', 'pothole', 'drainage', 'sewage', 'municipal', 'civic']):
        if any(t in section_lc for t in ['road', 'street', 'infrastructure', 'municipal', 'nuisance', 'public works']):
            score += 0.35
        if any(t in law_lc for t in ['income tax', 'gst']):
            score -= 0.3
        if any(t in normalized_query for t in ['drainage', 'sewage', 'water logging', 'sanitation']):
            if any(t in section_lc for t in ['drainage', 'sewage', 'sanitation']):
                score += 0.4
            if 'road and civic infrastructure' in section_lc:
                score -= 0.2
        if any(t in normalized_query for t in ['illegal construction', 'construction', 'building']):
            if any(t in section_lc for t in ['construction', 'building']):
                score += 0.4
        if any(t in normalized_query for t in ['street light', 'light not working']):
            if 'street light' in section_lc:
                score += 0.4
        if any(t in normalized_query for t in ['water supply', 'no water', 'dirty water']):
            if 'water supply' in section_lc:
                score += 0.4

    if any(t in normalized_query for t in ['land', 'property', 'encroachment', 'boundary', 'construction', 'plot']):
        if any(t in section_lc for t in ['encroachment', 'boundary', 'property', 'injunction', 'construction', 'land']):
            score += 0.35
        if any(t in law_lc for t in ['income tax', 'gst', 'fema']):
            score -= 0.3

    if any(t in normalized_query for t in ['caste', 'discrimination', 'social', 'community', 'public nuisance']):
        if any(t in section_lc for t in ['atrocities', 'nuisance', 'discrimination', 'community', 'public']):
            score += 0.3

    # Constitution is large; avoid accidental matches unless user asks constitutional questions.
    if ('constitution of india' in law_lc) and not any(
        t in normalized_query for t in ['constitution', 'article', 'fundamental right', 'writ', 'supreme court', 'high court']
    ):
        score -= 0.45

    if not overlap:
        score *= 0.35
    return min(score, 1.0), overlap


def _row_to_entry(row: pd.Series, confidence: float = 1.0) -> dict:
    return {
        'law': str(row.get('law', '')).strip(),
        'section': str(row.get('section', '')).strip(),
        'punishment': str(row.get('punishment', '')).strip(),
        'next_steps': str(row.get('next_steps', '')).strip(),
        'keywords': str(row.get('keywords', '')).strip(),
        'confidence': round(confidence, 3),
        'matched_terms': [],
    }


def _find_curated_complaint_entry(normalized_query: str) -> dict | None:
    df = _load_df()
    law_lc = df['law'].astype(str).str.lower()
    section_lc = df['section'].astype(str).str.lower()

    def _is_placeholder_punishment(value: str) -> bool:
        text = str(value or '').strip().lower()
        return any(
            token in text
            for token in [
                'not explicitly available',
                'not available',
                'not applicable',
                'consult lawyer',
            ]
        )

    def pick(law_contains: str, section_contains: str) -> dict | None:
        mask = (
            law_lc.str.contains(law_contains, na=False, regex=False)
            & section_lc.str.contains(section_contains, na=False, regex=False)
        )
        rows = df[mask]
        if rows.empty:
            return None
        best = None
        best_score = -1
        for _, row in rows.iterrows():
            punishment = str(row.get('punishment', ''))
            law_value = str(row.get('law', '')).lower()
            section_value = str(row.get('section', '')).lower()
            score = 0
            if not _is_placeholder_punishment(punishment):
                score += 3
            if any(token in law_value for token in ['section', 'ipc', 'act']):
                score += 2
            if any(token in section_value for token in ['section', 'punishment', 'offence', 'offense']):
                score += 1
            if score > best_score:
                best_score = score
                best = row

        if best is None:
            return None
        return _row_to_entry(best, confidence=1.0)

    q = normalized_query
    q_tokens = set(q.split())
    if any(t in q for t in ['political issue', 'election threat', 'booth intimidation', 'vote buying', 'money for vote', 'candidate bribery']):
        if any(t in q for t in ['vote buying', 'money for vote', 'candidate bribery']):
            return pick('ipc 171b/171e', 'bribery in elections')
        return pick('representation of the people act, 1951', 'corrupt practices and undue influence in elections')
    if any(t in q for t in ['panchayat not water tank', 'no water tank in village', 'village water tank issue']) or (
        'panchayat' in q and 'water tank' in q
    ):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['person missing', 'missing person', 'person are missing', 'person is missing', 'not returned home']):
        return pick('bnss/crpc missing person procedure', 'immediate registration and tracing of missing person')
    if any(t in q for t in ['water tank not clean', 'water tank was not clean', 'dirty water tank', 'public water tank dirty']):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['mla not consider complaint', 'mp not consider complaint', 'mla was not consider', 'mp was not consider']) or (
        any(t in q_tokens for t in ['mla', 'mp']) and any(t in q for t in ['not consider', 'not responding', 'no response'])
    ):
        return pick('public grievance redressal mechanisms (state grievance portal/cpgrams)', 'escalation for non-response to civic grievances by authorities/elected representatives')
    if any(t in q for t in ['garbage not collected', 'garbage was not take', 'garbage was not taken', 'waste not lifted', 'door to door waste not collected']):
        return pick('solid waste management rules, 2016', 'door-to-door garbage collection and scientific disposal obligations')
    if any(t in q for t in ['drainage not cleaned', 'drainage was not clean', 'sewer not cleaned', 'blocked drain not cleaned', 'desilting not done']):
        return pick('state municipal acts / local body rules', 'drainage cleaning and sewage maintenance duty')
    if any(t in q for t in ['city issue', 'city issues', 'city corporation issue', 'municipal corporation complaint', 'city municipal corporation', 'urban civic grievance']) and any(
        t in q for t in ['water', 'drainage', 'road', 'garbage', 'street light', 'civic']
    ):
        return pick('municipal corporation acts', 'city civic services and urban local body obligations')
    if any(t in q for t in ['town issue', 'town issues', 'municipality issue', 'town municipal complaint', 'town municipal civic grievance', 'town municipal']) and any(
        t in q for t in ['water', 'drainage', 'road', 'garbage', 'street light', 'civic']
    ):
        return pick('state municipalities acts', 'town municipal civic services and grievance redress')
    if any(t in q for t in ['village', 'panchayat', 'rural']) and any(
        t in q for t in ['drainage', 'sewage', 'water', 'road', 'sanitation']
    ):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['drainage', 'sewage', 'water logging', 'sanitation']):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['illegal construction', 'construction', 'building']):
        return pick('state municipal acts / building bye-laws', 'illegal construction')
    if any(t in q for t in ['street light', 'light not working']):
        return pick('essential services / local utility grievance', 'street light')
    if any(t in q for t in ['water supply denied by owner', 'water supply not give', 'water supply not gave', 'essential service denied by landlord']) or (
        any(t in q for t in ['house owner', 'landlord', 'tenant']) and any(t in q for t in ['water supply', 'no water', 'not give'])
    ):
        return pick('state rent control / tenancy laws', 'denial of essential services (water/electricity) to tenant')
    if any(t in q for t in ['water supply', 'no water', 'dirty water']):
        return pick('water supply / public utility rules', 'water supply')
    if any(t in q for t in ['cgrf', 'ombudsman', 'consumer grievance forum', 'electricity grievance forum']):
        return pick('electricity act, 2003', 'section 42(5)-(6)')
    if any(t in q for t in ['wrong electricity bill', 'high electricity bill', 'eb bill', 'meter reading issue', 'billing error', 'overbilling']):
        return pick('electricity act', 'billing')
    if any(t in q for t in ['meter tampering', 'electricity theft', 'illegal power connection', 'hooking current', 'unauthorized connection']):
        return pick('electricity act, 2003', 'section 135')
    if any(t in q for t in ['disconnection notice', 'power disconnected', 'service disconnected', 'wrongful disconnection', 'disconnected without notice']) or (
        'disconnect' in q and 'notice' in q
    ):
        return pick('electricity act, 2003', 'section 56')
    if any(t in q for t in ['eb', 'electricity board', 'power cut', 'no current', 'current problem', 'frequent outage', 'low voltage']):
        if any(t in q for t in ['low voltage', 'high voltage', 'fluctuation', 'voltage', 'power cut', 'outage']):
            return pick('electricity act, 2003', 'section 57')
        return pick('electricity act, 2003', 'section 43')
    if any(t in q for t in ['land encroachment', 'encroached', 'property boundary', 'boundary dispute']):
        return pick('land revenue / property laws', 'land encroachment')
    if any(t in q for t in ['marriage', 'marraige', 'divorce', 'driverse', 'diverse', 'dowry', 'dowri', 'family court']):
        if any(t in q for t in ['dowry', 'dowri']):
            return pick('dowry prohibition act 1961 section 4', 'penalty for demanding dowry')
        if any(t in q for t in ['divorce', 'driverse', 'diverse']):
            return pick('hindu marriage act 1955 section 13', 'divorce grounds')
        if any(t in q for t in ['marriage', 'marraige']):
            return pick('hindu marriage act 1955 section 13', 'divorce grounds')
    if any(t in q for t in ['women safety', 'woman safety', 'eve teasing', 'molestation', 'outrage modesty', 'woman stalking', 'women harassment', 'woman harassment']):
        return pick('ipc 354', 'assault or criminal force to woman')
    if any(t in q for t in ['child safety', 'child abuse', 'minor safety', 'pocso']):
        return pick('pocso act 2012', 'section 3')
    if any(t in q for t in ['elder safety', 'senior citizen abuse', 'parents maintenance', 'old age harassment', 'senior citizen']):
        return pick('maintenance and welfare of parents and senior citizens act, 2007', 'section 4')
    if any(t in q for t in ['men safety', 'blackmail me', 'extortion from me', 'assault on me', 'man safety', 'blackmail and extortion', 'blackmail', 'extortion']):
        if any(t in q for t in ['blackmail', 'extortion']):
            return pick('ipc 384', 'extortion')
        return pick('ipc 323', 'voluntarily causing hurt')
    if any(t in q for t in ['threat', 'intimidation', 'threatened']) and not any(t in q for t in ['election', 'political', 'vote', 'candidate']):
        return pick('ipc 506', 'criminal intimidation')
    if any(t in q for t in ['theft', 'stolen', 'steal', 'stealing', 'missing']) and any(t in q for t in ['house', 'home', 'dwelling']):
        return pick('ipc 380', 'theft in dwelling house')
    if any(t in q for t in ['theft', 'stolen', 'steal', 'stealing', 'missing']) and not any(t in q for t in ['robbery', 'snatching', 'chain snatching']):
        return pick('ipc 379', 'punishment for theft')
    if any(t in q for t in ['no signal', 'signal not coming', 'network not coming', 'call not coming', 'call not going', 'call drop', 'voice call issue', 'trai complaint']):
        return pick('telecom consumer protection regulations (trai)', 'deficiency in telecom service quality')
    if any(t in q for t in ['home loan rejected', 'loan not approved', 'bank not approved loan', 'bank was not approved my loan', 'housing loan issue', 'loan processing delay']) or (
        'bank' in q and 'loan' in q and ('not approved' in q or 'rejected' in q)
    ):
        return pick('rbi integrated ombudsman scheme, 2021', 'banking service deficiency in loan processing/grievance handling')
    if any(t in q for t in ['village issues', 'panchayat issue', 'village civic issue']):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['town issues', 'municipality issue', 'town municipal complaint']):
        return pick('state municipalities acts', 'town municipal civic services and grievance redress')
    if any(t in q for t in ['city issues', 'city corporation issue', 'municipal corporation complaint']):
        return pick('municipal corporation acts', 'city civic services and urban local body obligations')
    if any(t in q for t in ['temple damage', 'insult temple', 'religious place insult']):
        return pick('ipc 295a', 'outrage religious feelings')
    if any(t in q for t in ['temple trust money misuse', 'temple administration complaint', 'temple issue trust', 'hrce complaint', 'temple trust', 'temple corruption']):
        return pick('ipc 405/406', 'criminal breach of trust')
    if any(t in q for t in ['temple property dispute', 'encroachment near temple']) or (
        'temple' in q and 'property dispute' in q
    ):
        return pick('ipc 405/406', 'criminal breach of trust')
    if any(t in q for t in ['family land dispute', 'family property dispute', 'ancestral property dispute', 'partition suit', 'brother land dispute']):
        return pick('hindu succession act, 1956', 'partition and succession rights in ancestral/family property')
    if any(t in q for t in ['family vehicle dispute', 'family vehical dispute', 'vehicle ownership dispute in family', 'car ownership family dispute', 'family vehical ownership dispute']) or (
        'family' in q and ('vehicle' in q or 'vehical' in q) and 'ownership' in q
    ):
        return pick('motor vehicles act, 1988', 'ownership transfer and registration disputes')
    if any(t in q for t in ['house owner forcing', 'landlord harassment', 'owner forcing vacate', 'eviction threat without notice']):
        return pick('state rent control / tenancy laws', 'illegal eviction and tenant protection')
    if any(t in q for t in ['water supply denied by owner', 'water supply not give', 'water supply not gave', 'essential service denied by landlord']):
        return pick('state rent control / tenancy laws', 'denial of essential services (water/electricity) to tenant')
    if any(t in q for t in ['noise pollution', 'sound pollution', 'loudspeaker nuisance', 'construction noise']):
        return pick('noise pollution (regulation and control) rules, 2000', 'permissible noise limits and complaint mechanism')
    if any(t in q for t in ['air pollution', 'smoke pollution', 'factory smoke', 'waste burning smoke']):
        return pick('air (prevention and control of pollution) act 1981', 'emission standards')
    if any(t in q for t in ['land pollution', 'soil pollution', 'solid waste dumping', 'garbage dumping on land']):
        return pick('environment (protection) act, 1986', 'environmental pollution and waste dumping control')
    if any(t in q for t in ['chain snatching', 'gold chain snatched', 'neck chain snatched', 'snatched chain']):
        return pick('ipc 356 read with ipc 379', 'chain snatching')
    if any(t in q for t in ['rape', 'raped', 'forced sex', 'sexual intercourse without consent', 'child rape', 'minor rape']):
        if any(t in q for t in ['child', 'minor', 'kid', 'under 18', 'school girl', 'school boy', 'pocso']):
            return pick('pocso act 2012', 'section 3')
        return pick('ipc 376', 'rape')
    if any(t in q for t in ['bad touch', 'inappropriate touch', 'unwanted touching', 'sexual touch', 'child sexual abuse']) or (
        'inappropriately' in q and ('touch' in q or 'touched' in q)
    ):
        if any(t in q for t in ['child', 'minor', 'kid', 'school child', 'student minor', 'under 18']):
            return pick('pocso act 2012', 'section 7/8')
        return pick('ipc 354a', 'sexual harassment')
    if any(t in q for t in ['misleading advertisement', 'false advertisement', 'fake advertisement', 'ad fraud', 'advertisement fraud', 'ad claim false', 'consumer ad complaint']):
        return pick('consumer protection act, 2019', 'misleading advertisements')
    if any(t in q for t in ['obscene advertisement', 'indecent advertisement', 'vulgar ad', 'women objectified ad']):
        return pick('indecent representation of women (prohibition) act, 1986', 'section 3')
    if any(t in q for t in ['magic remedy advertisement', 'sex power medicine ad', 'miracle cure ad', 'drug cure advertisement']):
        return pick('drugs and magic remedies (objectionable advertisements) act, 1954', 'section 3')
    if any(t in q for t in ['illegal tree cutting', 'tree cutting', 'tree felling', 'cutting trees without permission']):
        return pick('indian forest act, 1927', 'section 26')
    if any(t in q for t in ['fake doctor', 'quack doctor', 'unlicensed doctor', 'doctor without degree']):
        return pick('ipc 419/420', 'cheating by personation as doctor')
    if any(t in q for t in ['fake medicine', 'spurious medicine', 'duplicate medicine', 'counterfeit medicine', 'adulterated medicine']):
        return pick('drugs and cosmetics act, 1940', 'section 18(a)(i) and section 27')
    if any(t in q for t in ['traffic rules', 'helmet fine', 'no helmet', 'no seat belt', 'seatbelt', 'drunk driving', 'overspeed', 'dangerous driving']):
        if any(t in q for t in ['drunk driving', 'alcohol driving']):
            return pick('motor vehicles act, 1988', 'section 185')
        if any(t in q for t in ['overspeed', 'speed limit']):
            return pick('motor vehicles act, 1988', 'section 183')
        if any(t in q for t in ['dangerous driving', 'rash driving']):
            return pick('motor vehicles act, 1988', 'section 184')
        if any(t in q for t in ['helmet', 'no helmet', 'seat belt', 'seatbelt']):
            return pick('motor vehicles act, 1988', 'section 129 read with section 194d')
    college_context = any(t in q for t in ['college', 'student', 'university', 'campus', 'education', 'hostel'])
    if college_context and any(t in q for t in ['fee', 'fine', 'facilities', 'facility', 'refund', 'due']):
        return pick('consumer protection act 2019', 'deficiency in service')
    if any(t in q for t in ['hospital', 'hosipital', 'medical', 'treatment denied', 'patient']):
        if any(t in q for t in ['negligence', 'wrong treatment']):
            return pick('ipc 304a', 'causing death by negligence')
        return pick('consumer protection act 2019', 'deficiency in service')
    if any(t in q for t in ['private company', 'private sector', 'salary due', 'workplace', 'salary not paid', 'salary delayed', 'unpaid wages', 'unpaid salary', 'wage_dispute', 'salary pending', 'wages not paid', 'incentive not provided', 'incentive not paid', 'bonus not paid', 'bonus withheld', 'hike', 'salary hike', 'not hike', 'raise']) or (
        'salary' in q and any(t in q for t in ['not paid', 'delay', 'pending', 'due', 'unpaid', 'denied', 'withheld', 'not giving', 'not give', 'not gave', 'not received'])
    ) or (
        'company' in q and any(t in q for t in ['incentive', 'insentive', 'bonus', 'hike', 'raise']) and any(t in q for t in ['not paid', 'not provide', 'not provided', 'not giving', 'withheld', 'denied', 'not hike', 'not raise'])
    ):
        return pick('payment of wages act, 1936', 'timely payment of wages')
    if any(t in q for t in ['pf', 'epf']):
        return pick('epf act 1952', 'penalties for default')
    if any(t in q for t in ['permit issue', 'commercial permit', 'transport permit', 'route permit', 'goods permit', 'rto permit grievance']):
        return pick('motor vehicles act (transport permit)', 'permit issuance/renewal')
    if any(t in q for t in ['challan', 'e challan', 'wrong challan', 'traffic fine dispute', 'fine dispute']):
        return pick('motor vehicles act 1988 section 200', 'composition of offences')
    if any(t in q for t in ['driving licence', 'driving license', 'license renewal', 'licence renewal', 'learner license', 'dl renewal']):
        return pick('motor vehicles act 1988 section 3', 'necessity for driving licence')
    if any(t in q for t in ['rc transfer', 'registration certificate', 'vehicle registration', 'ownership transfer', 'rc book']):
        return pick('motor vehicles act 1988 section 39', 'necessity for registration')
    if 'rto' in q_tokens or 'rto' in q:
        if any(t in q_tokens for t in ['license', 'licence', 'dl']) or any(t in q for t in ['driving license', 'driving licence']):
            return pick('motor vehicles act 1988 section 3', 'necessity for driving licence')
        if 'registration' in q_tokens or any(t in q for t in ['registration certificate', 'rc transfer']):
            return pick('motor vehicles act 1988 section 39', 'necessity for registration')
        if 'permit' in q_tokens or 'permit grievance' in q:
            return pick('motor vehicles act, 1988', 'section 88a')
        if any(t in q_tokens for t in ['challan', 'fine']) or 'e challan' in q:
            return pick('motor vehicles act 1988 section 200', 'composition of offences')
    if any(t in q for t in ['overloading', 'overspeed', 'dangerous driving', 'unsafe school bus', 'school bus']):
        return pick('motor vehicles act (road safety compliance)', 'overloading/unsafe driving and school bus safety')
    if any(t in q for t in ['government bus', 'goverment bus', 'public bus']):
        return pick('government bus service grievance', 'public bus service deficiency')
    if any(t in q for t in ['private bus', 'bus overcharge']) or (
        'bus complaint' in q and 'government bus' not in q and 'goverment bus' not in q and 'public bus' not in q
    ):
        return pick('motor vehicles act, 1988', 'section 194a')
    if any(t in q for t in ['accident', 'accitent', 'traffic injury', 'mact']):
        return pick('ipc 279', 'rash driving')
    if any(t in q for t in ['natural disaster', 'flood', 'cyclone', 'earthquake']):
        return pick('disaster management act 2005', 'relief and response')
    if any(t in q for t in ['agriculture', 'farmer', 'crop loss']):
        return pick('pmfby', 'crop insurance')
    if any(t in q for t in ['village', 'panchayat', 'rural']):
        return pick('state panchayati raj acts', 'powers, authority and responsibilities')
    if any(t in q for t in ['city', 'town', 'district municipal']):
        return pick('municipal corporation act / ipc 283', 'danger or obstruction')
    if any(t in q for t in ['rti', 'information']):
        return pick('rti act 2005', 'right to information')
    if any(t in q for t in ['mobile', 'sim misuse', 'imei', 'phone stolen']):
        return pick('ipc 379', 'punishment for theft')
    if any(t in q for t in ['publish', 'publication', 'online defamation', 'social media post', 'cyber bullying', 'cyberbullying', 'online abuse']):
        return pick('it act 2000 section 66a', 'offensive message') or pick('it act 2000 section 66', 'computer related offences')
    if any(t in q for t in ['no road', 'road damage', 'pothole']) or (
        'road' in q_tokens and any(t in q for t in ['damage', 'broken', 'repair', 'pothole', 'no road'])
    ):
        return pick('municipal corporation act / ipc 283', 'danger or obstruction')
    return None


def find_best_legal_entry(query: str, min_confidence: float = 0.32) -> dict | None:
    _refresh_caches_if_data_changed()
    normalized_query = _normalize_query(query)
    query_tokens = _tokenize(normalized_query)
    if not query_tokens:
        return None
    expanded_query_tokens = _expand_with_synonyms(query_tokens)

    curated = _find_curated_complaint_entry(normalized_query)
    if curated:
        return curated

    candidate_records = []
    for record in _build_search_records():
        overlap_size = len(expanded_query_tokens.intersection(record['haystack_tokens']))
        if overlap_size > 0:
            candidate_records.append((overlap_size, record))

    if not candidate_records:
        return None

    # Evaluate only the most relevant candidates to keep latency low on large CSVs.
    candidate_records.sort(key=lambda item: item[0], reverse=True)
    top_records = [record for _, record in candidate_records[:MAX_CANDIDATE_EVAL]]

    best_score = 0.0
    best_row = None
    best_overlap = set()
    best_priority = -1
    for record in top_records:
        row = record['row']
        score, overlap = _entry_score(query=normalized_query, row=row)
        priority = len(overlap)
        law_lc = record['law_lc']
        section_lc = record['section_lc']
        if any(t in normalized_query for t in ['house', 'home', 'dwelling']) and 'destroy house' in section_lc:
            priority += 2
        if any(t in normalized_query for t in ['theft', 'stolen', 'missing', 'robbery']):
            if any(t in normalized_query for t in ['house', 'home', 'dwelling']) and (
                'theft in dwelling house' in section_lc or 'ipc 380' in law_lc
            ):
                priority += 6
            if 'punishment for theft' in section_lc or 'ipc 379' in law_lc:
                priority += 4
            if 'theft' == section_lc.strip() and ('ipc 378' in law_lc):
                priority -= 2
        if any(t in normalized_query for t in ['cyber', 'hack', 'hacked', 'malware', 'ransomware']) and 'it act' in law_lc:
            priority += 3
        if any(t in normalized_query for t in ['upi', 'otp', 'online', 'bank']) and 'it act' in law_lc:
            priority += 3
        if any(t in normalized_query for t in ['tax', 'itr', 'income']) and 'income tax' in law_lc:
            priority += 3
        if 'gst' in normalized_query and 'gst' in law_lc:
            priority += 3
        if 'fir' in normalized_query and ('crpc' in law_lc or 'bnss' in law_lc):
            priority += 2
        if any(t in normalized_query for t in ['internet', 'network', 'broadband', 'wifi', '5g', '4g', 'speed']) and (
            'telecom' in law_lc or 'consumer' in law_lc
        ):
            priority += 4
        if any(t in normalized_query for t in ['road', 'street', 'pothole', 'drainage', 'sewage', 'municipal', 'civic']) and (
            'municipal' in law_lc or 'public nuisance' in section_lc or 'infrastructure' in section_lc
        ):
            priority += 4
        if any(t in normalized_query for t in ['drainage', 'sewage', 'water logging']) and any(
            t in section_lc for t in ['drainage', 'sewage', 'sanitation']
        ):
            priority += 5
        if any(t in normalized_query for t in ['illegal construction', 'construction', 'building']) and any(
            t in section_lc for t in ['construction', 'building']
        ):
            priority += 5
        if any(t in normalized_query for t in ['street light', 'light not working']) and 'street light' in section_lc:
            priority += 5
        if any(t in normalized_query for t in ['water supply', 'no water', 'dirty water']) and 'water supply' in section_lc:
            priority += 5
        if any(t in normalized_query for t in ['land', 'property', 'encroachment', 'boundary', 'construction']) and (
            'property' in section_lc or 'land' in section_lc or 'injunction' in section_lc or 'encroachment' in section_lc
        ):
            priority += 4
        if any(t in normalized_query for t in ['caste', 'discrimination', 'social', 'community', 'nuisance']) and (
            'sc/st' in law_lc or 'atrocities' in section_lc or 'public nuisance' in section_lc
        ):
            priority += 3

        if (score > best_score) or (score == best_score and priority > best_priority):
            best_score = score
            best_row = row
            best_overlap = overlap
            best_priority = priority

    if best_row is None or best_score < min_confidence or not best_overlap:
        return None

    return {
        'law': str(best_row.get('law', '')).strip(),
        'section': str(best_row.get('section', '')).strip(),
        'punishment': str(best_row.get('punishment', '')).strip(),
        'next_steps': str(best_row.get('next_steps', '')).strip(),
        'keywords': str(best_row.get('keywords', '')).strip(),
        'confidence': round(best_score, 3),
        'matched_terms': sorted(best_overlap),
    }


def get_context(query: str, k: int = 3) -> str:
    _refresh_caches_if_data_changed()
    try:
        docs = similarity_search(query=query, k=k)
    except Exception:
        return _keyword_fallback(query=query, k=k)

    if not docs:
        return _keyword_fallback(query=query, k=k)

    return '\n\n'.join(doc.page_content for doc in docs)


def get_legal_catalog(search: str = '') -> list[dict]:
    df = _load_df().copy()
    if search.strip():
        s = search.strip().lower()
        mask = (
            df['law'].str.lower().str.contains(s, na=False)
            | df['section'].str.lower().str.contains(s, na=False)
            | df['keywords'].str.lower().str.contains(s, na=False)
        )
        df = df[mask]

    records = (
        df[['law', 'section', 'punishment', 'next_steps', 'keywords']]
        .fillna('')
        .to_dict(orient='records')
    )
    return records


if __name__ == '__main__':
    build_vector_store()
    print(f'RAG store ready at: {CHROMA_DIR}')
