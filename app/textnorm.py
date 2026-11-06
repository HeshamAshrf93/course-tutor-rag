"""Tokenising, Arabic normalisation and Arabic-to-English term mapping."""
import re

_TASHKEEL = re.compile(r"[ؐ-ًؚ-ٰٟـ]")
_TOKEN = re.compile(r"[a-z0-9]+|[ء-ي]+")

STOP_EN = set("""a an and are as at be between by can do does for from has have how i in is it its me of on or
please should tell that the their them there this to use used using what when where which who why will with work
works you your explain define describe mean means difference compare""".split())

STOP_AR_RAW = """ايه اية ما ماذا هو هي هم يعني معني معنى ازاي إزاي كيف ليه لماذا امتى متى فين اين هل في من الى على
عن و او أو ده دي دا دى اللي الذي التي بين الفرق اشرح اشرحلي عرف شرح لي ليا عايز عاوز اعرف ممكن بتشتغل تشتغل
يشتغل يعمل بيعمل بتعمل تعمل نستخدم بنستخدم استخدم استخدام بيستخدم المستخدم مع كل لما لو بقي بقى قد ايش وقت
الوقت مرة بس طيب بيشتغل بتشتغل يشتغل تشتغل بيتستخدم تستخدم بيستخدم الـ ال كده كدا طريقة طريقه بيه به بها عشان علشان ليها ليه له"""


def normalize(text: str) -> str:
    text = _TASHKEEL.sub("", text.lower())
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي"), ("ؤ", "و"), ("ئ", "ي")):
        text = text.replace(a, b)
    return text


STOP_AR = {normalize(w) for w in STOP_AR_RAW.split()}

# Arabic and Arabizi course terms -> the English terms used in the course material.
GLOSSARY_RAW = {
    "قائمة مترابطة": "linked list", "لينكد ليست": "linked list", "القوائم المترابطة": "linked list",
    "مصفوفة": "array", "المصفوفة": "array", "ارراي": "array", "اراي": "array", "الاراي": "array",
    "مصفوفة ديناميكية": "dynamic array", "مكدس": "stack", "المكدس": "stack", "ستاك": "stack", "الستاك": "stack",
    "طابور": "queue", "الطابور": "queue", "كيو": "queue", "الكيو": "queue", "طابور دائري": "circular queue",
    "طابور اولوية": "priority queue", "شجرة بحث ثنائية": "binary search tree", "شجرة ثنائية": "binary tree",
    "شجرة": "tree", "الشجرة": "tree", "جذر": "root", "الجذر": "root", "ورقة": "leaf", "ارتفاع": "height",
    "جدول تجزئة": "hash table", "جدول الهاش": "hash table", "هاش تيبل": "hash table", "دالة هاش": "hash function",
    "دالة التجزئة": "hash function", "تصادم": "collision", "التصادم": "collision", "تصادمات": "collision",
    "معامل التحميل": "load factor", "لود فاكتور": "load factor", "بحث ثنائي": "binary search", "البحث الثنائي": "binary search",
    "بحث خطي": "linear search", "البحث الخطي": "linear search", "ترتيب الفقاعات": "bubble sort", "بابل سورت": "bubble sort",
    "ترتيب بالدمج": "merge sort", "ميرج سورت": "merge sort", "الترتيب بالدمج": "merge sort", "تعقيد": "complexity",
    "التعقيد": "complexity", "تعقيد مكاني": "space complexity", "التعقيد المكاني": "space complexity",
    "بيج او": "big o notation", "اسوا حالة": "worst case", "اسوأ حالة": "worst case", "مؤشر": "pointer", "المؤشر": "pointer",
    "فيفو": "fifo first in first out", "ليفو": "lifo last in first out", "مستقر": "stable", "ثابت": "constant",
    "تجاوز المكدس": "stack overflow", "ستاك اوفرفلو": "stack overflow", "اضافة": "insertion insert", "حذف": "deletion delete",
    "بحث": "search", "البحث": "search", "ترتيب": "sort sorting", "الترتيب": "sort sorting", "ذاكرة": "memory", "الذاكرة": "memory",
    "استدعاء الدوال": "function calls", "الدوال": "functions", "تعارض": "collision", "وصول": "access reading",
    "اوردر ترافيرسال": "inorder traversal", "ان اوردر": "inorder traversal", "زمن": "time", "الزمن": "time",
}
GLOSSARY = {normalize(k): v for k, v in GLOSSARY_RAW.items()}
_KEYS = sorted(GLOSSARY, key=len, reverse=True)


def stem(tok: str) -> str:
    if tok.isascii():
        if tok.endswith("ies") and len(tok) > 4:
            return tok[:-3] + "y"
        if tok.endswith("s") and not tok.endswith("ss") and len(tok) > 3:
            tok = tok[:-1]
        for suffix in ("ing", "ion", "ed"):
            if tok.endswith(suffix) and len(tok) > len(suffix) + 3:
                tok = tok[: -len(suffix)]
                break
        if tok.endswith("e") and len(tok) > 4:
            tok = tok[:-1]
    return tok


def tokens(text: str) -> list[str]:
    stop = STOP_EN | STOP_AR
    return [stem(t) for t in _TOKEN.findall(normalize(text)) if t not in stop and (len(t) > 1 or t.isdigit() or t in "no")]


def raw_tokens(text: str) -> list[str]:
    """Baseline tokeniser used only for evaluation comparison."""
    return re.findall(r"\w+", text.lower())


def _bare(word: str) -> str:
    """Light Arabic stem for term matching: drops attached particles, "al-", and a final ta marbuta."""
    if not re.fullmatch(r"[\u0621-\u064a]+", word):
        return word
    word = re.sub(r"^(?:[وفبكل]?ال|لل)(?=[\u0621-\u064a]{2})", "", word)
    return re.sub(r"(?<=[\u0621-\u064a]{3})ه$", "", word)


def _bare_phrase(text: str) -> str:
    return " ".join(_bare(w) for w in text.split())


STOP_AR |= {_bare(w) for w in STOP_AR}
_BARE_GLOSSARY = {_bare_phrase(k): v for k, v in GLOSSARY.items()}
_BARE_KEYS = sorted(_BARE_GLOSSARY, key=len, reverse=True)


def expand_query(query: str) -> str:
    """Replace known Arabic course terms with their English equivalents, longest match first."""
    text = _bare_phrase(re.sub(r"[؟?!.,:;،]", " ", normalize(query)))
    for key in _BARE_KEYS:
        text = re.sub(rf"(?<![\u0621-\u064a]){re.escape(key)}(?![\u0621-\u064a])", " " + _BARE_GLOSSARY[key] + " ", text)
    return " ".join(text.split())


COURSE_TERMS = sorted({w for v in GLOSSARY.values() for w in v.split() if len(w) >= 4} | {
    "pointer", "node", "index", "memory", "heap", "chaining", "recursion", "merge", "peek", "dequeue", "enqueue", "subtree"})


def has_arabic(text: str) -> bool:
    return bool(re.search(r"[؀-ۿ]", text))
