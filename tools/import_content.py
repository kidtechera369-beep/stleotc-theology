#!/usr/bin/env python3
"""Import real content from the old GitHub site into the new vibe-coded site.

Parses the 21 lesson HTML pages, the glossary, and the curriculum JSON files,
and regenerates assets/js/data.js and assets/js/curriculum-data.js.
Standard library only (no bs4)."""
import re, json, html, os, glob

OLD = os.path.expanduser("~/Desktop/GitHub/stleotc-theology")
NEW = os.path.expanduser("~/Desktop/stl_theology_class")

def text(s):
    """Strip tags + unescape entities + collapse whitespace."""
    s = re.sub(r"<[^>]+>", "", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def lis(block):
    return [text(m) for m in re.findall(r"<li>(.*?)</li>", block or "", re.S) if text(m)]

# ---- lesson section slicing ------------------------------------------------
def sections(body):
    """Return {label: html_between_this_h3_and_next} for every <h3> in body."""
    heads = list(re.finditer(r"<h3>(.*?)</h3>", body, re.S))
    out = {}
    for i, h in enumerate(heads):
        label = text(h.group(1))
        start = h.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out[label] = body[start:end]
    return out

def parse_lesson(path):
    raw = open(path, encoding="utf-8").read()
    slug = os.path.splitext(os.path.basename(path))[0]
    main = re.search(r"<main class=\"wrap\">(.*)</main>", raw, re.S).group(1)

    accent = (re.search(r"--accent:(#[0-9a-fA-F]+)", main) or [None, "#6b1f2a"])[1]
    head = re.search(r"<div class=\"lesson-head\">(.*?)</div>\s*</div>", main, re.S)
    head = head.group(1) if head else main

    title = text((re.search(r"<h2>(.*?)</h2>", head, re.S) or [None, slug])[1])
    cat = re.search(r"<span class=\"cat-chip\">.*?</svg>([^<]+)</span>", head, re.S)
    category = text(cat.group(1)) if cat else "Lesson"
    tags = [text(t) for t in re.findall(r"<span class=\"tag\">(.*?)</span>", head)]
    week = None
    audience = []
    for t in tags:
        m = re.match(r"week\s*(\d+)", t, re.I)
        if m: week = int(m.group(1))
        else: audience.append(t)
    audience = audience[0] if audience else ""
    byline = text((re.search(r"<p class=\"byline\">(.*?)</p>", head) or [None, ""])[1])
    sm = re.search(r"</p>\s*<p>(.*?)</p>", head, re.S)
    summary = text(sm.group(1)) if sm else ""

    sec = sections(main)

    def find(*names):
        for n in names:
            for k in sec:
                if n.lower() in k.lower():
                    return sec[k]
        return ""

    objectives = lis(find("Lesson Objectives", "Objectives"))
    teaching = lis(find("Main Teaching Points", "Teaching Points"))
    discussion = lis(find("Discussion", "Reflection"))
    sources = lis(find("Sources", "Citations"))

    verses = []
    for v in re.findall(r"<div class=\"verse-block\">(.*?)</div>", find("Key Bible Verses", "Bible Verses"), re.S):
        t = text(v)
        parts = re.split(r"\s+[—–-]\s+", t, maxsplit=1)
        verses.append({"ref": parts[0], "text": parts[1] if len(parts) > 1 else ""})

    guard = find("Doctrinal Guardrails", "Guardrails")
    confess, reject = [], []
    if guard:
        c = re.search(r"confess\">(.*?)</div>", guard, re.S)
        r = re.search(r"reject\">(.*?)</div>", guard, re.S)
        confess = lis(c.group(1)) if c else []
        reject = lis(r.group(1)) if r else []

    terms = []
    for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", find("Key Terms"), re.S):
        terms.append({"term": text(dt), "def": text(dd)})

    quiz = []
    for ans, leg, opts in re.findall(
        r"<fieldset data-answer=\"(\d+)\"><legend>(.*?)<span class=\"result-tag\"></span></legend>(.*?)</fieldset>",
        main, re.S):
        q = re.sub(r"^\d+\.\s*", "", text(leg))
        options = [text(o) for o in re.findall(r"<label><input[^>]*>(.*?)</label>", opts, re.S)]
        quiz.append({"q": q, "options": options, "answer": int(ans)})

    downloads = []
    dbox = re.search(r"<div class=\"download-box\">(.*?)</div>", main, re.S)
    if dbox:
        for href, label in re.findall(r"<a class=\"btn[^\"]*\" href=\"\.\./downloads/([^\"]+)\"[^>]*>(.*?)</a>", dbox.group(1), re.S):
            ext = href.rsplit(".", 1)[-1].lower()
            typ = {"pptx": "ppt", "ppt": "ppt", "pdf": "pdf", "docx": "doc", "doc": "doc"}.get(ext, "doc")
            downloads.append({"type": typ, "label": text(label).replace("⬇", "").strip(), "file": "downloads/" + href})

    related = []
    rel = find("Related Lessons")
    for href, txt in re.findall(r"<a href=\"([^\"]+)\">(.*?)</a>", rel):
        if "lessons.html" in href: continue
        related.append({"id": os.path.splitext(os.path.basename(href))[0], "title": text(txt)})

    return {
        "id": slug, "title": title, "category": category, "audience": audience,
        "week": week, "accent": accent, "byline": byline, "summary": summary,
        "objectives": objectives, "verses": verses, "confess": confess, "reject": reject,
        "teaching": teaching, "terms": terms, "discussion": discussion,
        "quiz": quiz, "downloads": downloads, "sources": sources, "related": related,
    }

# ---- glossary --------------------------------------------------------------
def parse_glossary():
    raw = open(os.path.join(OLD, "glossary.html"), encoding="utf-8").read()
    dl = re.search(r"<dl class=\"glossary\">(.*?)</dl>", raw, re.S).group(1)
    out = []
    for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", dl, re.S):
        term = text(dt)
        src = re.search(r"<span class=\"src\">.*?<a href=\"([^\"]+)\">(.*?)</a>", dd, re.S)
        source = None
        if src:
            source = {"id": os.path.splitext(os.path.basename(src.group(1)))[0], "title": text(src.group(2))}
        definition = text(re.sub(r"<span class=\"src\">.*", "", dd, flags=re.S))
        gid = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        out.append({"id": gid, "term": term, "def": definition, "source": source})
    return out

# ---- write JS --------------------------------------------------------------
def js(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def main():
    files = sorted(glob.glob(os.path.join(OLD, "lessons", "*.html")))
    lessons = [parse_lesson(f) for f in files]
    glossary = parse_glossary()

    lessons.sort(key=lambda l: (l["week"] is None, l["week"] or 0, l["title"]))

    featured = {"holy-trinity", "st-cyril", "orthodox-fasting"}
    for l in lessons:
        l["featured"] = l["id"] in featured

    # Standardize the curriculum author's name everywhere it appears.
    def fix_name(s):
        if not isinstance(s, str):
            return s
        s = s.replace("Kesis Solomon Mulugeta Zewde (PhD)", "Dr. Kesis Solomon Mulugeta Zewde")
        s = s.replace("Kesis Solomon Mulugeta Zewde", "Dr. Kesis Solomon Mulugeta Zewde")
        return s.replace("Dr. Dr. Kesis", "Dr. Kesis")
    for l in lessons:
        l["sources"] = [fix_name(s) for s in l.get("sources", [])]

    site = {
        "name": "STL Ethiopian Orthodox Tewahedo Theology Class",
        "shortName": "STL Theology",
        "parish": "Debre Nazreth St. Mary & St. Gabriel Ethiopian Orthodox Tewahedo Church",
        "author": "Deacon Yonnas",
        "curriculumSource": "Sunday School Curriculum in English — compiled by Dr. Kesis Solomon Mulugeta Zewde",
        "email": "kidtechera369@gmail.com",
    }
    resources = [
        {"title": "We Believe in One God (Parts 1–5)", "desc": "Foundational study on the doctrine of God, from the parish library.", "category": "Doctrine", "file": "downloads/library/We_Believe_In_One_God_Part1.pdf"},
        {"title": "EOTC: Our Beliefs and Values", "desc": "An overview of the faith and values of the Ethiopian Orthodox Tewahedo Church.", "category": "Doctrine", "file": "downloads/library/EOTC_Our_Beliefs_And_Values.pdf"},
        {"title": "The Seven Sacraments & Holy Orders", "desc": "A guide to the Mysteries of the Church.", "category": "Sacraments", "file": "downloads/library/Seven_Sacraments_Holy_Orders.pdf"},
        {"title": "The Divinity of Our Lord Jesus Christ", "desc": "Scriptural and patristic witness to the divinity of Christ.", "category": "Christology", "file": "downloads/library/Divinity_Of_Our_Lord_Jesus_Christ.pdf"},
        {"title": "The Divinity of the Holy Spirit", "desc": "On the person and divinity of the Holy Spirit.", "category": "Doctrine", "file": "downloads/library/Divinity_Of_The_Holy_Spirit.pdf"},
        {"title": "Virgin Mary and Intercession", "desc": "The Church's doctrine on the Theotokos and the intercession of the saints.", "category": "Doctrine", "file": "downloads/library/EOTC_Doctrine_Virgin_Mary_And_Intercession.pdf"},
        {"title": "Dogma (Kesis Solomon)", "desc": "Dogmatic theology reference by Kesis Solomon.", "category": "Doctrine", "file": "downloads/library/Dogma_Kesis_Solomon.pdf"},
    ]

    data_js = (
        "/* AUTO-GENERATED from the parish content by tools/import_content.py.\n"
        "   You can edit by hand, but re-running the importer will overwrite it. */\n\n"
        f"const SITE = {js(site)};\n\n"
        f"const LESSONS = {js(lessons)};\n\n"
        f"const GLOSSARY = {js(glossary)};\n\n"
        f"const RESOURCES = {js(resources)};\n\n"
        "window.SITE = SITE; window.LESSONS = LESSONS; window.GLOSSARY = GLOSSARY; window.RESOURCES = RESOURCES;\n"
    )
    open(os.path.join(NEW, "assets/js/data.js"), "w", encoding="utf-8").write(data_js)

    # ---- curriculum (separate, heavy file) --------------------------------
    levelV = json.load(open(os.path.join(OLD, "curriculum.json"), encoding="utf-8"))
    extra = json.load(open(os.path.join(OLD, "curricula_extra.json"), encoding="utf-8"))

    # Backfill missing titles in any level from the aligned Level V week
    # (the curriculum is one syllabus across levels; some weeks left the title blank).
    v_titles = {w["week"]: w.get("title", "").strip() for w in levelV}
    backfilled = 0
    for lvl in extra:
        for w in lvl["weeks"]:
            if not w.get("title", "").strip() and v_titles.get(w["week"]):
                w["title"] = v_titles[w["week"]]
                backfilled += 1
    print(f"Backfilled blank curriculum titles: {backfilled}")

    # Level IV (Grades 7-9) is intentionally excluded from the published curriculum browser.
    extra = [lvl for lvl in extra if lvl.get("key") != "level-4"]

    # Strip external hyperlinks (Google Drive, etc.) from all curriculum text.
    url_re = re.compile(r"https?://\S+")
    def clean_str(s):
        if not isinstance(s, str):
            return s
        if url_re.search(s):
            s = url_re.sub("", s)
            s = re.sub(r"\s*(?:from|under|at|see also|see|via)\s*$", "", s.strip(), flags=re.I)
            s = s.strip().rstrip(" .,:;-–—")
        return re.sub(r"\s{2,}", " ", s).strip()
    def clean_weeks(weeks):
        for w in weeks:
            for field in ("objectives", "memory_verse", "references", "body"):
                if isinstance(w.get(field), list):
                    w[field] = [c for c in (clean_str(x) for x in w[field]) if c]
        return weeks
    clean_weeks(levelV)
    for lvl in extra:
        clean_weeks(lvl.get("weeks", []))
    curricula = [{
        "key": "level-5",
        "label": "Level V — Youth & Young Adults",
        "weeks": levelV,
    }] + extra
    cur_js = (
        "/* AUTO-GENERATED curriculum data (Levels I–V). Loaded only on curriculum.html. */\n"
        f"window.CURRICULA = {js(curricula)};\n"
    )
    open(os.path.join(NEW, "assets/js/curriculum-data.js"), "w", encoding="utf-8").write(cur_js)

    # ---- report -----------------------------------------------------------
    print(f"Lessons parsed: {len(lessons)}")
    for l in lessons:
        print(f"  [{l['week'] if l['week'] else '--':>2}] {l['title']}  "
              f"(verses:{len(l['verses'])} teach:{len(l['teaching'])} terms:{len(l['terms'])} "
              f"quiz:{len(l['quiz'])} dl:{len(l['downloads'])})")
    print(f"Glossary terms: {len(glossary)}")
    print(f"Curriculum levels: {len(curricula)} ({', '.join(c['key'] for c in curricula)})")
    print(f"data.js: {os.path.getsize(os.path.join(NEW,'assets/js/data.js'))//1024} KB")
    print(f"curriculum-data.js: {os.path.getsize(os.path.join(NEW,'assets/js/curriculum-data.js'))//1024} KB")

if __name__ == "__main__":
    main()
