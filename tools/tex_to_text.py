"""Plain-text version of the manuscript prose, for pasting into checkers.
Drops figures, tables, equations, citations and LaTeX markup; keeps captions."""
import re, sys
src = open("paper/main.tex").read().replace("\\input{sec_method}", open("paper/sec_method.tex").read())
src = re.sub(r"(?<!\\)%.*", "", src)
body = src[src.index("\\begin{abstract}"):src.index("{\\small")]
caps = re.findall(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", body)
body = re.sub(r"\\begin\{(figure\*?|table)\}.*?\\end\{\1\}", "", body, flags=re.S)
body = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", body, flags=re.S)
def clean(t):
    t = re.sub(r"\s*\\cite\{[^}]*\}", "", t)
    t = re.sub(r"\\[Cc]ref\{fig:teaser\}", "Figure 1", t); t = re.sub(r"\\[Cc]ref\{fig:arch\}", "Figure 2", t)
    t = re.sub(r"\\[Cc]ref\{tab:related\}", "Table 1", t); t = re.sub(r"\\[Cc]ref\{tab:plan\}", "Table 2", t)
    t = re.sub(r"\\[Cc]ref\{sec:plan\}", "Section 4", t); t = re.sub(r"\\[Cc]ref\{eq:score\}", "Equation 1", t)
    t = re.sub(r"\\section\{([^}]*)\}", r"\n\n\1\n", t)
    t = re.sub(r"\\paragraph\{([^}]*)\}", r"\n\n\1 ", t)
    t = t.replace("\\begin{abstract}", "Abstract\n").replace("\\end{abstract}", "\n")
    t = re.sub(r"\\item\s*", "\n- ", t)
    t = re.sub(r"\\(begin|end)\{enumerate\}", "", t)
    t = re.sub(r"\\label\{[^}]*\}", "", t)
    t = re.sub(r"\\(textbf|emph)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\2", t)
    t = t.replace("\\etal", "et al.").replace("\\,", " ").replace("``", '"').replace("''", '"').replace("--", "-")
    t = t.replace("\\%", "%")
    MATH = [(r"\\mathbb\{R\}\^\{(\d+)\\times(\d+)\}", r"R^(\1x\2)"), (r"\\mathbb\{R\}\^\{(\d+)\}", r"R^\1"),
            (r"\\hat z_k", "z'_k"), (r"\\mathcal\{K\}", "K"), (r"\\ell_2", "L2"), (r"\\theta", "theta"),
            (r"\\in", " in "), (r"\\neq", " != "), (r"\\dots", "..."), (r"\\times", " x "),
            (r"s\^\{\\mathrm\{det\}\}_i", "s_det,i"), (r"\\mathrm\{GELU\}", "GELU"), (r"\\,", " "),
            (r"\\text\{([^}]*)\}", r"\1"), (r"\\(arg)?max", lambda m: (m.group(1) or "") + "max"),
            (r"\\(gamma|delta|tau|omega|Delta)", r"\1"), (r"[{}]", "")]
    def m2t(m):
        x = m.group(1)
        for a, b in MATH: x = re.sub(a, b, x)
        return x
    t = re.sub(r"\$([^$]*)\$", m2t, t)
    t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n[ ]+", "\n", t); t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()
out = clean(body) + "\n\nFigure and table captions\n\n" + "\n\n".join(clean(c) for c in caps)
out = out.replace("\\cos", "cos").replace("\\argmax", "argmax").replace("\\1,2,4\\", "{1, 2, 4}")
open("paper_text.txt", "w").write(out + "\n")
print(len(out.split()), "words")
