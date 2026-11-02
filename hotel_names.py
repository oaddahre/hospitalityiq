"""Hotel name comparison for finding Google IDs (scripts/find_candidates.py).

Order-independent and lenient on wording, unlike scraper.match_hotel:
accents, case, "&"/"and", punctuation, generic words (Hotel, Hôtel,
Resort, Riad, Palace, Spa, ...), labels (Relais & Châteaux, SLH, Adults
Only), city words and word order are ignored. Arabic names are written in
Latin letters first: well-known brand, city and hotel words from a word
list, the rest letter by letter, so a candidate is never rejected only
because Google writes its name in Arabic script.
"""
import re
import unicodedata
from difflib import SequenceMatcher

# Words that say nothing about which hotel it is (after folding to ASCII)
GENERIC = {
    'hotel', 'hotels', 'hostel', 'resort', 'resorts', 'riad', 'riads', 'palace', 'palais', 'spa', 'and', 'the',
    'de', 'du', 'des', 'la', 'le', 'les', 'l', 'd', 'el', 'al', 'by', 'a', 'an', 'at', 'et', 'en', 'in', 'of',
    'morocco', 'maroc', 'suites', 'suite', 'boutique', 'appart', 'apart', 'aparthotel', 'apparthotel',
    'apartments', 'apartment', 'appartements', 'residence', 'relais', 'chateaux', 'slh', 'small', 'luxury',
    'adults', 'only', 'restaurant', 'rooftop', 'bar', 'collection', 'star', 'stars', 'etoiles', 'maison',
    'hotes', 'guest', 'house', 'inn', 'lodge', 'and', 'golf', 'beach', 'sky', 'urban', 'city', 'center',
    'centre', 'sea', 'view', 'club', 'camp', 'desert', 'signature', 'kasbah', 'dar', 'villa',
}
# Generic words that still count when they are nearly all a name has
# ("City Bleu", "White Camp"): they are compared, with half weight
WEAK = {'golf', 'beach', 'sky', 'urban', 'city', 'center', 'centre', 'sea', 'view', 'club', 'camp', 'desert',
        'signature', 'palace', 'palais', 'boutique', 'luxury', 'kasbah', 'dar', 'villa'}

# Other spellings of the same word
SYNONYMS = {'parc': 'park', 'centre': 'center', 'jnane': 'jnan', 'riyad': 'riad', 'hoteles': 'hotel',
            'fez': 'fes', 'marrakesh': 'marrakech', 'tangier': 'tanger', 'tangiers': 'tanger',
            'moevenpick': 'movenpick', 'mohamed': 'mohammed', 'mohammad': 'mohammed', 'v': 'v',
            'chaouen': 'chefchaouen', 'tetuan': 'tetouan', 'ryad': 'riad'}

# Arabic words and phrases -> Latin (brands, cities, hotel words), longest first when applied
ARABIC_WORDS = {
    'موفنبيك': 'movenpick', 'موڤنبيك': 'movenpick', 'موفينبيك': 'movenpick', 'هيلتون': 'hilton',
    'راديسون بلو': 'radisson blu', 'راديسون': 'radisson', 'سوفيتيل': 'sofitel', 'نوفوتيل': 'novotel',
    'إيبيس': 'ibis', 'ايبيس': 'ibis', 'إبيس': 'ibis', 'ماريوت': 'marriott', 'حياة ريجنسي': 'hyatt regency',
    'حياة': 'hyatt', 'هيات': 'hyatt', 'بارسيلو': 'barcelo', 'ريو': 'riu', 'إيبيروستار': 'iberostar',
    'ايبروستار': 'iberostar', 'كنزي': 'kenzi', 'أطلس': 'atlas', 'اطلس': 'atlas', 'شيراتون': 'sheraton',
    'فور بوينتس': 'four points', 'بولمان': 'pullman', 'فيرمونت': 'fairmont', 'ميركيور': 'mercure',
    'ميركور': 'mercure', 'أداجيو': 'adagio', 'اداجيو': 'adagio', 'أونومو': 'onomo', 'اونومو': 'onomo',
    'بيستانا': 'pestana', 'بستانا': 'pestana', 'بانيان تري': 'banyan tree', 'كلوب ميد': 'club med',
    'روبنسون': 'robinson', 'لانكستر': 'lancaster', 'ميا': 'mia', 'رويال': 'royal', 'غولف': 'golf',
    'جولف': 'golf', 'بيتش': 'beach', 'شاطئ': 'beach', 'خليج': 'bay', 'سيتي سنتر': 'city center',
    'قصبة': 'kasbah', 'القصبة': 'kasbah', 'دار': 'dar', 'رياض': 'riad', 'فيلا': 'villa', 'جراند': 'grand',
    'غراند': 'grand', 'بالاس': 'palace', 'قصر': 'palais', 'الصحراء': 'sahara', 'صحراء': 'sahara',
    'محمد': 'mohammed', 'الخامس': 'v', 'أجنحة': 'suites', 'اجنحة': 'suites', 'مخيم': 'camp',
    'فندق': 'hotel', 'أوتيل': 'hotel', 'اوتيل': 'hotel', 'نزل': 'hotel', 'منتجع': 'resort', 'سبا': 'spa',
    'بارك': 'park', 'مارينا': 'marina', 'باي': 'bay', 'سان ماو': 'san mao', 'زلاغ': 'zalagh',
    'منزه': 'menzeh', 'موغادور': 'mogador', 'الموكادور': 'mogador', 'تيرمينوس': 'terminus',
    'الدار البيضاء': 'casablanca', 'مراكش': 'marrakech', 'فاس': 'fes', 'مكناس': 'meknes', 'طنجة': 'tanger',
    'أكادير': 'agadir', 'اكادير': 'agadir', 'الرباط': 'rabat', 'سلا': 'sale', 'وجدة': 'oujda',
    'الناظور': 'nador', 'العيون': 'laayoune', 'الداخلة': 'dakhla', 'ورزازات': 'ouarzazate',
    'الصويرة': 'essaouira', 'الجديدة': 'el jadida', 'الحسيمة': 'al hoceima', 'تطوان': 'tetouan',
    'شفشاون': 'chefchaouen', 'القنيطرة': 'kenitra', 'السعيدية': 'saidia', 'مرزوكة': 'merzouga',
    'مرزوقة': 'merzouga', 'تغازوت': 'taghazout', 'إفران': 'ifrane', 'افران': 'ifrane',
    'الرشيدية': 'errachidia', 'تمارة': 'temara', 'المحمدية': 'mohammedia',
}
ARABIC_LETTERS = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
    'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ڤ': 'v', 'ق': 'q', 'ك': 'k', 'ڭ': 'g', 'گ': 'g', 'ل': 'l', 'م': 'm',
    'ن': 'n', 'ه': 'h', 'ة': 'a', 'و': 'ou', 'ي': 'i', 'ى': 'a', 'ء': '', 'ئ': 'i', 'ؤ': 'o', 'پ': 'p',
}
_ARABIC = re.compile(r'[؀-ۿ]')

# Latin -> Arabic, for Arabic search texts
LATIN_TO_ARABIC = {}
for _ar, _la in ARABIC_WORDS.items():
    LATIN_TO_ARABIC.setdefault(_la, _ar)


# Ordinary words many hotels use: a match on one of them alone is not certain
COMMON = {'palm', 'palms', 'royal', 'grand', 'golden', 'gold', 'blue', 'bleu', 'white', 'blanc', 'sun', 'sunset',
          'ocean', 'star', 'garden', 'gardens', 'jardin', 'jardins', 'green', 'paradise', 'paradis', 'plaza',
          'central', 'park', 'marina', 'bay', 'lagoon', 'sahara', 'atlas', 'oasis', 'rose', 'roses', 'sand', 'sands',
          'dunes', 'dune', 'mer', 'nord', 'sud', 'south', 'north', 'new', 'old', 'top', 'premium', 'prestige', 'nova'}


def has_arabic(s):
    return bool(_ARABIC.search(str(s or '')))


def transliterate(s):
    """Arabic script to Latin letters: listed words first, then letter by letter."""
    s = str(s or '')
    if not has_arabic(s):
        return s
    for ar in sorted(ARABIC_WORDS, key=len, reverse=True):
        s = re.sub(rf'(?<![؀-ۿ]){re.escape(ar)}(?![؀-ۿ])', f' {ARABIC_WORDS[ar]} ', s)
    out = []
    for word in s.split():
        if has_arabic(word):
            if word.startswith('ال') and len(word) > 3:
                word = word[2:]
            word = ''.join(ARABIC_LETTERS.get(ch, ch if not has_arabic(ch) else '') for ch in word)
        out.append(word)
    return ' '.join(out)


def to_arabic(name):
    """An Arabic search text for a Latin name, or '' when its distinctive
    words aren't in the word list."""
    words = fold(name).split()
    out, i = [], 0
    while i < len(words):
        two = ' '.join(words[i:i + 2])
        if len(words) > i + 1 and two in LATIN_TO_ARABIC:
            out.append(LATIN_TO_ARABIC[two]); i += 2; continue
        w = words[i]
        if w in LATIN_TO_ARABIC:
            out.append(LATIN_TO_ARABIC[w])
        elif w not in GENERIC:
            return ''
        i += 1
    return ' '.join(out)


def fold(s):
    """Latin letters, lower case, no accents, '&' as 'and', symbols as spaces, synonyms merged."""
    s = transliterate(s)
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', ' and ').replace("'", ' ')
    words = re.sub(r'[^a-z0-9]+', ' ', s).split()
    return ' '.join(SYNONYMS.get(w, w) for w in words)


def tokens(name, city_words=()):
    """(strong, weak) distinctive words of a name: city phrases and generic words removed."""
    t = f' {fold(name)} '
    for p in sorted({fold(c) for c in city_words if c}, key=len, reverse=True):
        t = t.replace(f' {p} ', ' ')
    words = t.split()
    strong = [w for w in words if w not in GENERIC]
    weak = [w for w in words if w in WEAK]
    return strong, weak


def same_word(a, b):
    if a == b:
        return True
    if min(len(a), len(b)) >= 5 and (a.startswith(b) or b.startswith(a)) and abs(len(a) - len(b)) <= 2:
        return True                                # jnan / jnane, savoy / savoye
    return min(len(a), len(b)) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.8


def score_parts(ours, google, city_words=(), with_weak=False):
    """(score, recall, precision). recall: share of our distinctive words in
    Google's name; precision: share of Google's words that are ours; score
    = 0.7 x recall + 0.3 x precision. When either name has no distinctive
    word left, the generic words it has are compared. with_weak also counts
    the weaker words (City, Center, Sky, Beach, ...), to tell two hotels of
    one family apart."""
    T, Tw = tokens(ours, city_words)
    C, Cw = tokens(google, city_words)
    if with_weak:
        T, C = T + Tw, C + Cw
    same = same_word
    if not T or not C:
        T, C = T or Tw, C or Cw
        if not T or not C:
            a, b = fold(ours), fold(google)
            return (round(SequenceMatcher(None, a, b).ratio() * 0.6, 3) if a and b else 0.0), 0.0, 0.0
        same = str.__eq__                      # generic words only: exact words, no spelling tolerance
    # Two words written as one ("Be Live" / "Belive") count as that word
    Cj = C + [C[i] + C[i + 1] for i in range(len(C) - 1)]
    Tj = T + [T[i] + T[i + 1] for i in range(len(T) - 1)]
    recall = sum(1 for t in T if any(same(t, c) for c in Cj)) / len(T)
    precision = sum(1 for c in C if any(same(c, t) for t in Tj)) / len(C)
    return round(0.7 * recall + 0.3 * precision, 3), recall, precision


def score(ours, google, city_words=()):
    """Name similarity 0-1 (see score_parts)."""
    return score_parts(ours, google, city_words)[0]


def same_full_name(ours, google, city_words=()):
    """The whole names (generic words included, city words out) match."""
    a = ' '.join(w for w in fold(ours).split() if w not in {fold(c) for c in city_words})
    b = ' '.join(w for w in fold(google).split() if w not in {fold(c) for c in city_words})
    return bool(a and b) and SequenceMatcher(None, a, b).ratio() >= 0.9


def shared_words(ours, google, city_words=()):
    T, _ = tokens(ours, city_words)
    C, _ = tokens(google, city_words)
    return [t for t in T if any(same_word(t, c) for c in C)]
