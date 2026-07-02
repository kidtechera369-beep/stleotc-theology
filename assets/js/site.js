/* ==========================================================================
   SITE.JS  —  shared behavior + page renderers
   ========================================================================== */
(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = (s) =>
    String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  const NAV = [
    { href: "index.html", label: "Home" },
    { href: "start-here.html", label: "Start Here" },
    { href: "our-faith.html", label: "Our Faith" },
    { href: "lessons.html", label: "Lessons" },
    { href: "curriculum.html", label: "Curriculum" },
    { href: "glossary.html", label: "Glossary" },
    { href: "resources.html", label: "Resources" },
    { href: "community.html", label: "Community" },
    { href: "downloads.html", label: "Downloads" },
  ];

  /* ---- Header / Footer injection --------------------------------------- */
  function currentPage() {
    const p = location.pathname.split("/").pop();
    return p === "" ? "index.html" : p;
  }

  function buildHeader() {
    let here = currentPage();
    if (here === "faith.html") here = "our-faith.html"; // article pages belong to Our Faith
    if (here === "lesson.html") here = "lessons.html";
    if (here === "creed.html" || here === "feasts-fasts.html") here = "resources.html"; // reference pages belong to Resources
    const links = NAV.map(
      (n) => `<li><a href="${n.href}" class="${n.href === here ? "active" : ""}">${n.label}</a></li>`
    ).join("");
    return `
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="index.html" aria-label="Home">
          <span class="cross" aria-hidden="true">✠</span>
          <span class="brand-text">
            <span class="brand-title">STL Orthodox Lessons</span>
            <span class="brand-sub">Tewahedo · Young Adults</span>
          </span>
        </a>
        <ul class="nav-links" id="navLinks">${links}</ul>
        <div class="nav-actions">
          <button class="icon-btn" id="themeToggle" aria-label="Toggle dark mode" title="Toggle theme">◐</button>
          <button class="icon-btn nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false">☰</button>
        </div>
      </div>
    </header>`;
  }

  function buildFooter() {
    const topics = Array.from(new Set(LESSONS.map((l) => l.category))).sort();
    const topicLinks = topics
      .map((c) => `<li><a href="lessons.html?cat=${encodeURIComponent(c)}">${esc(c)}</a></li>`)
      .join("");
    const navLinks = NAV.map((n) => `<li><a href="${n.href}">${n.label}</a></li>`).join("");
    return `
    <footer class="site-footer">
      <div class="container">
        <div class="footer-grid">
          <div>
            <div class="footer-brand"><span class="cross">✠</span> ${esc(SITE.name)}</div>
            <p style="color:rgba(255,255,255,.75);max-width:42ch;">${esc(SITE.parish)}.</p>
            <p style="color:rgba(255,255,255,.7);margin-top:.6rem;font-size:.9rem">Glory be to the Father, the Son, and the Holy Spirit, one God. Amen.</p>
          </div>
          <div><h4>Explore</h4><ul>${navLinks}</ul></div>
          <div><h4>Topics</h4><ul>${topicLinks}</ul></div>
          <div><h4>About</h4><ul>
            <li>Lessons by ${esc(SITE.author)}</li>
            <li>${esc(SITE.parish)}</li>
          </ul></div>
        </div>
        <div class="footer-bottom">
          <span>© <span id="year"></span> ${esc(SITE.parish)}</span>
          <span>Curriculum follows ${esc(SITE.curriculumSource)}. For doctrinal questions, consult your father confessor.</span>
        </div>
      </div>
    </footer>`;
  }

  function mountChrome() {
    const h = $("#site-header"), f = $("#site-footer");
    if (h) h.outerHTML = buildHeader();
    if (f) f.outerHTML = buildFooter();
    const y = $("#year");
    if (y) y.textContent = new Date().getFullYear();

    const toggle = $("#navToggle"), links = $("#navLinks");
    if (toggle && links)
      toggle.addEventListener("click", () => {
        const open = links.classList.toggle("open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    const themeBtn = $("#themeToggle");
    if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
  }

  /* ---- Theme ----------------------------------------------------------- */
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("stl-theme", t); } catch (e) {}
  }
  function toggleTheme() {
    const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    applyTheme(cur === "dark" ? "light" : "dark");
  }
  (function initTheme() {
    let saved = null;
    try { saved = localStorage.getItem("stl-theme"); } catch (e) {}
    if (saved) applyTheme(saved);
    else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) applyTheme("dark");
  })();

  /* ---- Lesson card ----------------------------------------------------- */
  function lessonCard(l) {
    const dls = (l.downloads || []).length;
    const accent = l.accent ? `style="border-top:3px solid ${esc(l.accent)}"` : "";
    return `
    <article class="card hoverable" ${accent}>
      <div class="card-meta">
        <span class="pill maroon">${esc(l.category)}</span>
        ${l.week ? `<span class="pill">Week ${l.week}</span>` : ""}
        ${l.audience ? `<span class="muted">· ${esc(l.audience)}</span>` : ""}
      </div>
      <h3><a href="lesson.html?id=${l.id}">${esc(l.title)}</a></h3>
      <p>${esc(truncate(l.summary, 170))}</p>
      <div class="card-foot">
        <a class="btn btn-primary btn-sm" href="lesson.html?id=${l.id}">Read lesson →</a>
        ${dls ? `<span class="pill">⤓ ${dls} file${dls > 1 ? "s" : ""}</span>` : ""}
      </div>
    </article>`;
  }
  function truncate(s, n) {
    s = s || "";
    return s.length > n ? s.slice(0, n).replace(/\s+\S*$/, "") + "…" : s;
  }

  /* ---- HOME ------------------------------------------------------------ */
  function renderHome() {
    const feat = $("#featuredLessons");
    if (feat) {
      let items = LESSONS.filter((l) => l.featured);
      if (items.length < 3) items = LESSONS.slice(0, 3);
      feat.innerHTML = items.slice(0, 3).map(lessonCard).join("");
    }
    const stat = $("#statLessons");
    if (stat) stat.textContent = LESSONS.length;
    const gstat = $("#statGuides");
    if (gstat) gstat.textContent = LESSONS.length;
  }

  /* ---- LESSON LIBRARY -------------------------------------------------- */
  function renderLibrary() {
    const grid = $("#lessonGrid");
    if (!grid) return;
    const searchEl = $("#lessonSearch");
    const filterWrap = $("#lessonFilters");
    const countEl = $("#resultCount");

    const categories = ["All", ...Array.from(new Set(LESSONS.map((l) => l.category))).sort()];
    const urlCat = new URLSearchParams(location.search).get("cat");
    let activeCat = categories.includes(urlCat) ? urlCat : "All";

    if (filterWrap) {
      filterWrap.innerHTML = categories
        .map((c) => `<button class="chip ${c === activeCat ? "active" : ""}" data-cat="${esc(c)}">${esc(c)}</button>`)
        .join("");
      filterWrap.addEventListener("click", (e) => {
        const btn = e.target.closest(".chip");
        if (!btn) return;
        activeCat = btn.dataset.cat;
        $$(".chip", filterWrap).forEach((c) => c.classList.toggle("active", c === btn));
        draw();
      });
    }

    function draw() {
      const q = (searchEl?.value || "").trim().toLowerCase();
      const items = LESSONS.filter((l) => {
        const catOk = activeCat === "All" || l.category === activeCat;
        const hay = (l.title + " " + l.summary + " " + l.category + " " +
          (l.verses || []).map((v) => v.ref).join(" ")).toLowerCase();
        return catOk && (!q || hay.includes(q));
      });
      grid.innerHTML = items.length
        ? items.map(lessonCard).join("")
        : `<div class="empty-state"><h3>No lessons found</h3><p>Try a different search or category.</p></div>`;
      if (countEl) countEl.textContent = `${items.length} lesson${items.length === 1 ? "" : "s"}`;
    }
    if (searchEl) searchEl.addEventListener("input", draw);
    draw();
  }

  /* ---- SINGLE LESSON --------------------------------------------------- */
  function listBlock(title, items, cls) {
    if (!items || !items.length) return "";
    return `<h2>${esc(title)}</h2><ul class="${cls || ""}">${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
  }

  function blockHTML(b) {
    if (b.h2) return `<h2>${esc(b.h2)}</h2>`;
    if (b.h3) return `<h3>${esc(b.h3)}</h3>`;
    if (b.p) return `<p>${esc(b.p)}</p>`;
    if (b.quote) return `<div class="verse-block">${b.cite ? `<span class="vref">${esc(b.cite)}</span>` : ""}${esc(b.quote)}</div>`;
    if (b.list) return `<ul>${b.list.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
    return "";
  }

  function renderLesson() {
    const root = $("#lessonRoot");
    if (!root) return;
    const id = new URLSearchParams(location.search).get("id");
    const l = LESSONS.find((x) => x.id === id);

    if (!l) {
      root.innerHTML = `<div class="container empty-state" style="padding:5rem 1rem"><h1>Lesson not found</h1>
        <p>This lesson may have moved.</p><a class="btn btn-primary" href="lessons.html">← Back to Lesson Library</a></div>`;
      return;
    }
    document.title = `${l.title} — ${SITE.shortName}`;

    const idx = LESSONS.findIndex((x) => x.id === id);
    const prev = LESSONS[idx - 1], next = LESSONS[idx + 1];
    const R = (window.READINGS && window.READINGS[id]) || null;

    // ---- main body sections ----
    let body = "";
    if (l.byline) body += `<p class="byline">${esc(l.byline)}</p>`;
    body += listBlock("Lesson Objectives", l.objectives, "check-list");

    if (l.verses && l.verses.length) {
      body += `<h2>Key Bible Verses</h2>` + l.verses.map((v) =>
        `<div class="verse-block">${v.ref ? `<span class="vref">${esc(v.ref)}</span>` : ""}${esc(v.text || v.ref)}</div>`
      ).join("");
    }

    // ---- the full reading (from the lesson slides) ----
    if (R && R.reading && R.reading.length) {
      body += `<h2>The Lesson</h2>` + R.reading.map(blockHTML).join("\n");
    } else {
      body += listBlock("Main Teaching Points", l.teaching);
    }

    if ((l.confess && l.confess.length) || (l.reject && l.reject.length)) {
      body += `<h2>Doctrinal Guardrails</h2><div class="guardrails">
        ${l.confess && l.confess.length ? `<div class="gr-col gr-confess"><h4>✓ We Confess</h4><ul>${l.confess.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>` : ""}
        ${l.reject && l.reject.length ? `<div class="gr-col gr-reject"><h4>✗ We Reject</h4><ul>${l.reject.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>` : ""}
      </div>`;
    }

    if (l.terms && l.terms.length) {
      body += `<h2>Key Terms</h2><dl class="term-defs">` +
        l.terms.map((t) => `<dt>${esc(t.term)}</dt><dd>${esc(t.def)}</dd>`).join("") + `</dl>`;
    }

    // ---- study guide (from slides) — wrapped so it prints as exactly one page ----
    if (R && R.studyGuide) {
      const sg = R.studyGuide;
      let sgInner = `<p class="sg-print-head">${esc(SITE.shortName)} — Study Guide</p>`;
      sgInner += `<h2>Study Guide</h2>`;
      sgInner += `<p class="sg-print-title">${esc(l.title)}</p>`;
      if (sg.overview) sgInner += `<p>${esc(sg.overview)}</p>`;
      if (sg.keyPoints && sg.keyPoints.length)
        sgInner += `<h3>Key Points</h3><ul class="check-list">${sg.keyPoints.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>`;
      if (sg.reviewQuestions && sg.reviewQuestions.length)
        sgInner += `<h3>Review Questions</h3><ol>${sg.reviewQuestions.map((q) => `<li>${esc(q)}</li>`).join("")}</ol>`;
      body += `<div id="sgWrap" class="study-guide">${sgInner}</div>
        <p class="no-print" style="margin-top:.8rem"><button class="btn btn-ghost btn-sm" id="printSG">⤓ Print / save one-page study guide</button></p>`;
    } else {
      body += listBlock("Discussion &amp; Reflection Questions", l.discussion);
    }

    if (l.quiz && l.quiz.length) body += `<h2>Check Your Understanding</h2><div id="quizMount"></div>`;

    if (l.sources && l.sources.length)
      body += `<h2>Sources &amp; Citations</h2><ul class="muted" style="font-size:.92rem">${l.sources.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>`;

    body += `<hr class="divider"><div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
      ${prev ? `<a class="btn btn-ghost btn-sm" href="lesson.html?id=${prev.id}">← ${esc(truncate(prev.title, 28))}</a>` : "<span></span>"}
      ${next ? `<a class="btn btn-ghost btn-sm" href="lesson.html?id=${next.id}">${esc(truncate(next.title, 28))} →</a>` : "<span></span>"}
    </div>`;

    // ---- aside ----
    const dls = (l.downloads || [])
      .map((d) => `<a class="btn btn-ghost btn-sm" href="${esc(d.file)}" download>⤓ ${esc(d.label)}</a>`)
      .join("");
    const refs = (l.verses || []).map((v) => `<li>${esc(v.ref)}</li>`).join("");
    const rel = (l.related || [])
      .map((r) => `<li><a href="lesson.html?id=${r.id}">${esc(r.title)}</a></li>`)
      .join("");

    // ---- "On this page" jump navigation: add ids to each <h2> and build a TOC ----
    let secN = 0;
    const toc = [];
    body = body.replace(/<h2>([\s\S]*?)<\/h2>/g, (m, t) => {
      secN++;
      const id = "sec-" + secN;
      toc.push({ id, label: t.replace(/<[^>]+>/g, "") });
      return `<h2 id="${id}">${t}</h2>`;
    });
    const tocHTML = toc.length > 1
      ? `<div class="lesson-toc"><h4>On this page</h4><ul>${toc.map((x) => `<li><a href="#${x.id}">${x.label}</a></li>`).join("")}</ul></div>`
      : "";

    root.innerHTML = `
      <div class="page-head"><div class="container">
        <div class="breadcrumb"><a href="lessons.html">Lesson Library</a> / ${esc(l.category)}</div>
        <div class="card-meta" style="margin-bottom:.6rem">
          <span class="pill maroon">${esc(l.category)}</span>
          ${l.week ? `<span class="pill">Week ${l.week}</span>` : ""}
          ${l.audience ? `<span class="muted">· ${esc(l.audience)}</span>` : ""}
        </div>
        <h1>${esc(l.title)}</h1>
        <p>${esc(l.summary)}</p>
        <p class="class-note">✠ Taught at our Friday night theology &amp; Bible study class.</p>
      </div></div>
      <section><div class="container">
        <div class="lesson-layout">
          <div class="lesson-body">${body}</div>
          <aside class="lesson-aside">
            ${tocHTML}
            ${dls ? `<div><h4>Lesson Materials</h4><div style="display:grid;gap:.5rem;margin-top:.5rem">${dls}</div></div>` : ""}
            ${refs ? `<div><h4>Scripture</h4><ul class="refs-list">${refs}</ul></div>` : ""}
            ${rel ? `<div><h4>Related Lessons</h4><ul class="refs-list" style="list-style:none">${rel}</ul></div>` : ""}
            <div><h4>Have a question?</h4><p class="muted" style="font-size:.88rem">Ask it in the <a href="community.html">Community</a>, and bring matters of doctrine to your father confessor or parish priest.</p></div>
          </aside>
        </div>
      </div></section>`;

    if (l.quiz && l.quiz.length) mountQuiz($("#quizMount"), l.quiz);

    const printBtn = $("#printSG");
    if (printBtn) {
      printBtn.addEventListener("click", () => {
        document.body.classList.add("sg-print");
        window.print();
      });
      window.addEventListener("afterprint", () => document.body.classList.remove("sg-print"));
    }
  }

  /* ---- QUIZ ------------------------------------------------------------ */
  function mountQuiz(mount, quiz) {
    if (!mount) return;
    mount.innerHTML = `
      <div class="quiz">
        ${quiz.map((item, qi) => `
          <div class="quiz-q" data-q="${qi}" data-answer="${item.answer}">
            <p class="q">${qi + 1}. ${esc(item.q)}</p>
            ${item.options.map((opt, oi) =>
              `<label class="quiz-opt"><input type="radio" name="q${qi}" value="${oi}">${esc(opt)}</label>`).join("")}
          </div>`).join("")}
        <button class="btn btn-primary" id="quizCheck">Check answers</button>
        <div class="quiz-result" id="quizResult" hidden></div>
      </div>`;
    $("#quizCheck", mount).addEventListener("click", () => {
      let score = 0;
      $$(".quiz-q", mount).forEach((qEl) => {
        const ans = Number(qEl.dataset.answer);
        const opts = $$(".quiz-opt", qEl);
        opts.forEach((o) => o.classList.remove("correct", "wrong"));
        if (opts[ans]) opts[ans].classList.add("correct");
        const chosen = qEl.querySelector("input:checked");
        if (chosen) {
          const ci = Number(chosen.value);
          if (ci === ans) score++;
          else if (opts[ci]) opts[ci].classList.add("wrong");
        }
      });
      const res = $("#quizResult", mount);
      res.hidden = false;
      res.textContent = `You scored ${score} / ${quiz.length}${score === quiz.length ? " — Excellent!" : " — review the lesson and try again."}`;
    });
  }

  /* ---- GLOSSARY -------------------------------------------------------- */
  function renderGlossary() {
    const list = $("#glossaryList");
    if (!list) return;
    const searchEl = $("#glossarySearch");
    const idxWrap = $("#alphaIndex");

    const sorted = [...GLOSSARY].sort((a, b) => a.term.localeCompare(b.term));
    const letters = Array.from(new Set(sorted.map((t) => t.term[0].toUpperCase())));
    if (idxWrap) idxWrap.innerHTML = letters.map((L) => `<a href="#letter-${L}">${L}</a>`).join("");

    function draw() {
      const q = (searchEl?.value || "").trim().toLowerCase();
      const items = sorted.filter((t) => !q || (t.term + " " + t.def).toLowerCase().includes(q));
      if (!items.length) { list.innerHTML = `<div class="empty-state"><h3>No terms found</h3></div>`; return; }
      let html = "", last = "";
      items.forEach((t) => {
        const L = t.term[0].toUpperCase();
        if (L !== last && !q) { html += `<h2 id="letter-${L}" style="color:var(--gold-deep);margin-top:1.4rem">${L}</h2>`; last = L; }
        const src = t.source ? `<span class="src">— from <a href="lesson.html?id=${t.source.id}">${esc(t.source.title)}</a></span>` : "";
        html += `<dl class="term-card" id="${t.id}"><dt>${esc(t.term)}</dt><dd>${esc(t.def)} ${src}</dd></dl>`;
      });
      list.innerHTML = html;
    }
    if (searchEl) searchEl.addEventListener("input", draw);
    draw();
    if (location.hash) { const el = $(location.hash); if (el) el.scrollIntoView(); }
  }

  /* ---- CURRICULUM (level / week browser) ------------------------------- */
  function renderCurriculum() {
    const mount = $("#curriculumMount");
    if (!mount || !window.CURRICULA) return;
    const tabWrap = $("#levelTabs");
    let active = window.CURRICULA[0].key;

    if (tabWrap) {
      tabWrap.innerHTML = window.CURRICULA
        .map((c) => `<button class="tab ${c.key === active ? "active" : ""}" data-key="${c.key}">${esc(c.label.split("—")[0].trim())}</button>`)
        .join("");
      tabWrap.addEventListener("click", (e) => {
        const btn = e.target.closest(".tab");
        if (!btn) return;
        active = btn.dataset.key;
        $$(".tab", tabWrap).forEach((t) => t.classList.toggle("active", t === btn));
        draw();
      });
    }

    function field(label, arr) {
      if (!arr || !arr.length) return "";
      if (label === "Memory Verse")
        return `<h5>${label}</h5>` + arr.map((v) => `<p class="mv">${esc(v)}</p>`).join("");
      return `<h5>${label}</h5><ul>${arr.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
    }

    function draw() {
      const lvl = window.CURRICULA.find((c) => c.key === active);
      const label = $("#levelLabel");
      if (label) label.textContent = lvl.label;
      mount.innerHTML = lvl.weeks.map((w) => `
        <details class="week-item">
          <summary><span class="wknum">Week ${w.week}</span> ${esc(w.title)}</summary>
          <div class="week-body">
            ${field("Objectives", w.objectives)}
            ${field("Memory Verse", w.memory_verse)}
            ${field("References", w.references)}
            ${w.body && w.body.length ? `<h5>Lesson Notes</h5>${renderBody(w.body)}` : ""}
          </div>
        </details>`).join("");
    }

    function renderBody(arr) {
      // body items: lines beginning with ### are headings, • are bullets
      let html = "", inList = false;
      const close = () => { if (inList) { html += "</ul>"; inList = false; } };
      arr.forEach((line) => {
        const t = line.trim();
        if (t.startsWith("###")) { close(); html += `<p style="font-weight:600;color:var(--maroon);margin-top:.8rem">${esc(t.replace(/^#+\s*/, ""))}</p>`; }
        else if (t.startsWith("•") || t.startsWith("-")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${esc(t.replace(/^[•-]\s*/, ""))}</li>`; }
        else if (t) { close(); html += `<p>${esc(t)}</p>`; }
      });
      close();
      return html;
    }

    draw();
  }

  /* ---- DOWNLOAD CENTER (grouped by lesson) ----------------------------- */
  const DL_TYPE_LABEL = { ppt: "Slides", pdf: "Study Guide", doc: "Reading" };
  function renderDownloads() {
    const list = $("#downloadList");
    if (!list) return;
    const searchEl = $("#downloadSearch");
    const filterWrap = $("#dlFilters");

    const withFiles = LESSONS.filter((l) => (l.downloads || []).length);
    const categories = ["All", ...Array.from(new Set(withFiles.map((l) => l.category))).sort()];
    let activeCat = "All";

    if (filterWrap) {
      filterWrap.innerHTML = categories
        .map((c) => `<button class="chip ${c === "All" ? "active" : ""}" data-cat="${esc(c)}">${esc(c)}</button>`)
        .join("");
      filterWrap.addEventListener("click", (e) => {
        const btn = e.target.closest(".chip");
        if (!btn) return;
        activeCat = btn.dataset.cat;
        $$(".chip", filterWrap).forEach((c) => c.classList.toggle("active", c === btn));
        draw();
      });
    }

    function draw() {
      const q = (searchEl?.value || "").trim().toLowerCase();
      const items = withFiles.filter((l) => {
        const catOk = activeCat === "All" || l.category === activeCat;
        return catOk && (!q || l.title.toLowerCase().includes(q));
      });
      list.innerHTML = items.length
        ? items.map((l) => {
            const files = l.downloads.map((d) => `
              <a class="dl-file ${esc(d.type)}" href="${esc(d.file)}" download>
                <span class="dl-tag">${esc(d.type.toUpperCase())}</span>
                <span>${esc(DL_TYPE_LABEL[d.type] || "Download")}</span> ⤓
              </a>`).join("");
            return `
            <article class="dl-card">
              <div class="dl-card-head">
                <span class="pill maroon">${esc(l.category)}</span>
                <h3><a href="lesson.html?id=${l.id}">${esc(l.title)}</a></h3>
              </div>
              <div class="dl-files">${files}</div>
            </article>`;
          }).join("")
        : `<div class="empty-state"><h3>No lessons found</h3><p>Try a different search or category.</p></div>`;
      const c = $("#dlCount");
      if (c) c.textContent = `${items.length} lesson${items.length === 1 ? "" : "s"}`;
    }
    if (searchEl) searchEl.addEventListener("input", draw);
    draw();
  }

  /* ---- FAITH ARTICLE (in-depth, from PDFs) ----------------------------- */
  function renderFaithArticle() {
    const root = $("#faithRoot");
    if (!root || !window.FAITH) return;
    const id = new URLSearchParams(location.search).get("id");
    const a = window.FAITH[id];
    if (!a) {
      root.innerHTML = `<div class="container empty-state" style="padding:5rem 1rem"><h1>Article not found</h1>
        <p><a class="btn btn-primary" href="our-faith.html">← Back to Our Faith</a></p></div>`;
      return;
    }
    document.title = `${a.title} — ${SITE.shortName}`;

    let bodyHTML = (a.sections || []).map(blockHTML).join("\n");
    let n = 0; const toc = [];
    bodyHTML = bodyHTML.replace(/<h2>([\s\S]*?)<\/h2>/g, (m, t) => {
      n++; const sid = "fa-" + n; toc.push({ id: sid, label: t.replace(/<[^>]+>/g, "") });
      return `<h2 id="${sid}">${t}</h2>`;
    });
    const tocHTML = toc.length > 1
      ? `<div class="lesson-toc"><h4>On this page</h4><ul>${toc.map((x) => `<li><a href="#${x.id}">${esc(x.label)}</a></li>`).join("")}</ul></div>` : "";

    const ids = Object.keys(window.FAITH);
    const i = ids.indexOf(id);
    const prev = window.FAITH[ids[i - 1]], next = window.FAITH[ids[i + 1]];

    root.innerHTML = `
      <div class="page-head"><div class="container">
        <div class="breadcrumb"><a href="our-faith.html">Our Faith</a> / Reading</div>
        <h1>${esc(a.title)}</h1>
        ${a.summary ? `<p>${esc(a.summary)}</p>` : ""}
      </div></div>
      <section><div class="container">
        <div class="credit-box">Compiled by Dn Yonnas.</div>
        <div class="lesson-layout">
          <div class="lesson-body">
            ${bodyHTML}
            <hr class="divider">
            <p class="muted" style="font-size:.9rem">For doctrinal questions, consult your father confessor or parish priest.</p>
            <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-top:1rem">
              ${prev ? `<a class="btn btn-ghost btn-sm" href="faith.html?id=${prev.id}">← ${esc(truncate(prev.title, 30))}</a>` : "<span></span>"}
              ${next ? `<a class="btn btn-ghost btn-sm" href="faith.html?id=${next.id}">${esc(truncate(next.title, 30))} →</a>` : "<span></span>"}
            </div>
          </div>
          <aside class="lesson-aside">
            ${tocHTML}
            <div><h4>More on the Faith</h4><ul class="refs-list" style="list-style:none">${ids.map((k) => `<li><a href="faith.html?id=${k}">${esc(window.FAITH[k].title)}</a></li>`).join("")}</ul></div>
            <div><h4>Overview</h4><p class="muted" style="font-size:.88rem"><a href="our-faith.html">Return to Our Faith →</a></p></div>
          </aside>
        </div>
      </div></section>`;
  }

  /* ---- OUR FAITH (article cards + deeper reading list) ------------------ */
  function renderFaithIndex() {
    const grid = $("#faithArticles");
    if (!grid || !window.FAITH) return;
    grid.innerHTML = Object.keys(window.FAITH).map((k) => {
      const a = window.FAITH[k];
      return `<article class="card hoverable">
        <span class="pill maroon">In-depth</span>
        <h3><a href="faith.html?id=${k}">${esc(a.title)}</a></h3>
        <p>${esc(truncate(a.summary || "", 150))}</p>
        <div class="card-foot"><a class="btn btn-primary btn-sm" href="faith.html?id=${k}">Read →</a></div>
      </article>`;
    }).join("");
  }

  /* ---- OUR FAITH (deeper reading download list) ------------------------ */
  function renderFaithReading() {
    const list = $("#faithReadingList");
    if (!list) return;
    list.innerHTML = RESOURCES.filter((r) => r.file).map((r) => `
      <div class="dl-item">
        <span class="dl-ico pdf">PDF</span>
        <div class="dl-meta"><strong>${esc(r.title)}</strong><br><small>${esc(r.desc)}</small></div>
        <a class="btn btn-primary btn-sm" href="${esc(r.file)}" download>Download ⤓</a>
      </div>`).join("");
  }

  /* ---- RESOURCES (parish library PDFs) --------------------------------- */
  function renderResources() {
    const list = $("#resourceList");
    if (!list) return;
    list.innerHTML = RESOURCES.filter((r) => r.file).map((r) => `
      <div class="dl-item">
        <span class="dl-ico pdf">PDF</span>
        <div class="dl-meta"><strong>${esc(r.title)}</strong><br><small>${esc(r.desc)}</small></div>
        <a class="btn btn-primary btn-sm" href="${esc(r.file)}" download>Download ⤓</a>
      </div>`).join("");
  }

  /* ---- Boot ------------------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", () => {
    mountChrome();
    renderHome();
    renderLibrary();
    renderLesson();
    renderCurriculum();
    renderGlossary();
    renderDownloads();
    renderResources();
    renderFaithArticle();
    renderFaithIndex();
    renderFaithReading();
  });
})();
