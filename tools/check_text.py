"""Originality and style check for the manuscript.

1. Lists every run of N+ words shared with the sample manuscript (plagiarism risk).
2. Flags AI-style tells from the humanizer guide (blader/humanizer): vocabulary,
   em/en dashes, stock phrases.
Usage: python check_text.py SAMPLE.tex OURS.tex [OURS2.tex ...]
"""
import re, sys

def words(tex):
    tex = re.sub(r"%.*", "", tex)
    tex = re.sub(r"\\(cite|ref|cref|Cref|label|bibliography\w*|includegraphics|input)\*?(\[[^]]*\])?\{[^}]*\}", " ", tex)
    tex = re.sub(r"\$[^$]*\$", " ", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?", " ", tex)
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", tex.lower())

N = 6
sample = words(open(sys.argv[1]).read())
grams = {tuple(sample[i:i + N]) for i in range(len(sample) - N + 1)}
STOP = {("the", "of", "the")}
AI = ["delve", "crucial", "pivotal", "landscape", "tapestry", "testament", "underscore", "showcase",
      "intricate", "vibrant", "foster", "garner", "enhance", "additionally", "furthermore", "moreover",
      "notably", "seamless", "robust", "leverage", "paramount", "realm", "holistic", "comprehensive",
      "key role", "plays a", "serves as", "stands as", "not only", "it is important", "in order to",
      "valuable", "novel approach", "state-of-the-art", "cutting-edge", "groundbreaking", "remarkable"]
for path in sys.argv[2:]:
    raw = open(path).read()
    w = words(raw)
    hits, i = [], 0
    while i <= len(w) - N:
        if tuple(w[i:i + N]) in grams:
            j = i + N
            while j < len(w) and tuple(w[j - N + 1:j + 1]) in grams:
                j += 1
            hits.append(" ".join(w[i:j])); i = j
        else:
            i += 1
    print(f"== {path}: {len(hits)} shared runs of >= {N} words with the sample")
    for h in hits: print("   *", h)
    low = re.sub(r"%.*", "", raw).lower()
    for a in AI:
        n = len(re.findall(r"\b" + re.escape(a) + r"\b", low))
        if n: print(f"   AI-word '{a}': {n}")
    for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash"), ("---", "TeX em dash")):
        if ch in raw: print(f"   {name}: {raw.count(ch)}")
