# STL Ethiopian Orthodox Tewahedo Theology Class

The study hub for the theology class of **Debre Nazreth St. Mary & St. Gabriel
Ethiopian Orthodox Tewahedo Church** — lessons, Scripture references, a glossary,
self-tests, and downloadable slides.

Built as a fast, framework-free static site. **No build step. No dependencies.**
It runs directly on GitHub Pages.

---

## 📁 Project structure

```
stl_theology_class/
├── index.html            ← Home
├── start-here.html       ← How to use the site (students / parents / teachers)
├── lessons.html          ← Lesson Library (search + filter)
├── lesson.html           ← Single lesson template (reads ?id=slug)
├── curriculum.html       ← Week-by-week curriculum table
├── glossary.html         ← Searchable glossary of terms
├── resources.html        ← External resources
├── downloads.html        ← Download Center
├── 404.html              ← Friendly not-found page
├── .nojekyll             ← Tells GitHub Pages to serve files as-is
├── assets/
│   ├── css/styles.css    ← All styling (light + dark mode)
│   └── js/
│       ├── data.js       ← ⭐ ALL CONTENT lives here — edit this to add lessons
│       └── site.js       ← Shared behavior + page renderers
└── downloads/            ← Put your real .pptx / .pdf files here
```

---

## 📦 Where the content comes from

The lessons, glossary, and curriculum were imported from the original parish
repo by [`tools/import_content.py`](tools/import_content.py), which writes:

- [`assets/js/data.js`](assets/js/data.js) — 21 lessons, the glossary, site info, resources
- `assets/js/curriculum-data.js` — the full Levels I–V curriculum (loaded only on the Curriculum page)

To re-import after the original repo changes:
```bash
python3 tools/import_content.py
```
> ⚠️ Re-running the importer overwrites `data.js` and `curriculum-data.js`.
> If you edit those files by hand, keep your own copy or update the importer instead.

The lesson slides, study guides, and reference library PDFs live in
[`downloads/`](downloads/) and `downloads/library/`.

## ✍️ How to add or edit content by hand

**Everything is in [`assets/js/data.js`](assets/js/data.js).** You do not need to
touch HTML to add a lesson, a glossary term, or a download.

### Add a new lesson
Add an object to the `LESSONS` array:

```js
{
  id: "my-lesson",                 // unique slug used in the URL
  title: "My Lesson Title",
  week: 10,
  category: "Doctrine",            // Doctrine | Fathers | Liturgy & Fasting | Scripture | Church Life
  featured: false,                 // true = shows on the home page
  summary: "One or two sentences.",
  duration: "45 min",
  references: ["John 3:16"],
  terms: ["trinity"],              // ids from the GLOSSARY array
  downloads: [
    { type: "ppt", label: "My Slides", file: "downloads/my-lesson.pptx", size: "3 MB" }
  ],
  body: [
    { h2: "A heading" },
    { p: "A paragraph." },
    { quote: "A verse.", cite: "John 1:1" },
    { list: ["point one", "point two"] }
  ],
  quiz: [
    { q: "Question?", options: ["A", "B", "C"], answer: 1 }   // answer = index of correct option
  ]
}
```

The lesson then appears automatically in the **Library, Curriculum, Download
Center,** and (if `featured`) the **Home** page.

### Add a glossary term
Add to the `GLOSSARY` array: `{ id, term, geez, def }`.

### Add a download
Drop the file into `downloads/` and reference it from a lesson's `downloads` array.

---

## 🚀 Run it locally

Any static file server works. From this folder:

```bash
# Python (built in on macOS)
python3 -m http.server 8000
# then open http://localhost:8000
```

> Open the pages through the server (http://localhost:8000), **not** by
> double-clicking the file — some browsers block scripts on `file://`.

---

## 🌐 Deploy to GitHub Pages

1. Commit and push these files to your repository
   (`kidtechera369-beep/stleotc-theology`).
2. In the repo: **Settings → Pages**.
3. Under **Build and deployment**, set **Source = Deploy from a branch**,
   **Branch = `main`** (folder `/root`), then **Save**.
4. Wait ~1 minute. Your site is live at:
   `https://kidtechera369-beep.github.io/stleotc-theology/`

The included `.nojekyll` file ensures all assets are served correctly.

---

## 🎨 Features

- Responsive design with a liturgical palette (maroon, gold, parchment)
- **Light & dark mode** (◐ button, remembers your choice)
- Searchable & filterable Lesson Library
- Single-lesson pages with references, key terms, downloads & **self-test quizzes**
- Searchable Glossary with A–Z index and Ge'ez script
- Auto-generated Curriculum table and Download Center
- Shared header/footer injected by JS — edit the nav in one place (`site.js`)
- SEO meta tags + friendly 404 page

---

Prepared by **Deacon Yonnas**. For doctrinal questions, please consult your parish priest.
