/* ==========================================================================
   COMMUNITY.JS  —  Firebase-powered forum (ES module)
   Loaded as <script type="module"> on community.html.
   Reads window.FIREBASE_CONFIG (assets/js/firebase-config.js).
   Degrades gracefully to a setup notice when not configured.

   Features: categories, search + sort, reactions, best-answer, and an
   anonymous posting option (name is never written to public docs when anon).
   ========================================================================== */

const VERSION = "10.12.2";
const root = document.getElementById("community");
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const cfg = window.FIREBASE_CONFIG || {};
const ADMINS = (window.ADMIN_EMAILS || []).map((e) => String(e).toLowerCase());
const configured = cfg.apiKey && cfg.apiKey !== "REPLACE_ME" && cfg.projectId && cfg.projectId !== "REPLACE_ME";

/* Sections members can post in. The "anon" section forces anonymous posting. */
const CATEGORIES = [
  { id: "general",   label: "General",         emoji: "💬" },
  { id: "scripture", label: "Scripture",       emoji: "📖" },
  { id: "prayer",    label: "Prayer Requests", emoji: "🕯️" },
  { id: "feasts",    label: "Feasts & Fasts",  emoji: "✝️" },
  { id: "lessons",   label: "Lessons",         emoji: "🎓" },
  { id: "youth",     label: "Youth",           emoji: "🌱" },
  { id: "anon",      label: "Anonymous",       emoji: "🕊️", forcesAnon: true },
];
const CAT_BY_ID = Object.fromEntries(CATEGORIES.map((c) => [c.id, c]));
const catLabel = (id) => CAT_BY_ID[id] ? `${CAT_BY_ID[id].emoji} ${CAT_BY_ID[id].label}` : "💬 General";

/* Reaction palette. `key` is what's stored; `title` is the hover label. */
const REACTIONS = [
  { key: "pray",  emoji: "🙏", title: "Amen" },
  { key: "cross", emoji: "✝️", title: "Glory to God" },
  { key: "candle",emoji: "🕯️", title: "Praying for you" },
  { key: "heart", emoji: "❤️", title: "Love" },
  { key: "up",    emoji: "👍", title: "Agree" },
];
const REACTION_BY_KEY = Object.fromEntries(REACTIONS.map((r) => [r.key, r]));

if (!root) {
  /* not on the community page */
} else if (!configured) {
  renderSetupNotice();
} else {
  boot().catch((err) => {
    console.error(err);
    root.innerHTML = `<div class="container"><div class="notice notice-warn">
      <h3>The Community could not load</h3>
      <p>${esc(err && err.message ? err.message : "Unknown error")}</p>
      <p class="muted">Check the Firebase config and that Authentication &amp; Firestore are enabled. See COMMUNITY-SETUP.md.</p>
    </div></div>`;
  });
}

/* -------------------------------------------------------------------------- */
function renderSetupNotice() {
  root.innerHTML = `
  <div class="container">
    <div class="notice">
      <h2>The Community is almost ready</h2>
      <p>This forum runs on a free Firebase project. Once it is connected, members will be able to sign in, ask questions, and reply to one another here.</p>
      <h3>To turn it on (one-time setup)</h3>
      <ol class="steps-plain">
        <li>Create a free project at <strong>console.firebase.google.com</strong>.</li>
        <li>Add a Web App and copy its config into <code>assets/js/firebase-config.js</code>.</li>
        <li>Enable <strong>Google</strong> and <strong>Email/Password</strong> sign-in (Authentication).</li>
        <li>Create a <strong>Firestore</strong> database and paste the security rules from <code>COMMUNITY-SETUP.md</code>.</li>
        <li>Add the deacon's email to <code>ADMIN_EMAILS</code> for moderation.</li>
      </ol>
      <p class="muted">Full step-by-step instructions are in <strong>COMMUNITY-SETUP.md</strong> in the project folder.</p>
    </div>
  </div>`;
}

/* -------------------------------------------------------------------------- */
async function boot() {
  const [{ initializeApp }, auth, fs] = await Promise.all([
    import(`https://www.gstatic.com/firebasejs/${VERSION}/firebase-app.js`),
    import(`https://www.gstatic.com/firebasejs/${VERSION}/firebase-auth.js`),
    import(`https://www.gstatic.com/firebasejs/${VERSION}/firebase-firestore.js`),
  ]);

  const app = initializeApp(cfg);
  const A = auth, F = fs;
  const authClient = A.getAuth(app);
  const db = F.getFirestore(app);

  const state = { user: null, unsub: null, threads: [] };
  const ui = { category: "all", q: "", sort: "new" };   // list filters (persist across navigation)
  const isAdmin = () => state.user && ADMINS.includes((state.user.email || "").toLowerCase());
  const threadId = () => new URLSearchParams(location.search).get("thread");

  // shell
  root.innerHTML = `
    <div class="page-head"><div class="container">
      <div class="breadcrumb"><a href="index.html">Home</a> / Community</div>
      <h1>Community</h1>
      <p>A place to ask questions and learn together in the faith. Be kind, be reverent, and bring matters of doctrine to your father confessor as well.</p>
      <div id="authBar" class="auth-bar"></div>
    </div></div>
    <section><div class="container" id="forumMount"></div></section>`;

  A.onAuthStateChanged(authClient, (u) => { state.user = u; renderAuthBar(); route(); });

  window.addEventListener("popstate", route);

  /* ---- auth ---- */
  function renderAuthBar() {
    const bar = document.getElementById("authBar");
    if (!bar) return;
    if (state.user) {
      bar.innerHTML = `<span class="who">Signed in as <strong>${esc(state.user.displayName || state.user.email)}</strong>${isAdmin() ? ' <span class="pill maroon">moderator</span>' : ""}</span>
        <button class="btn btn-ghost btn-sm" id="signOut">Sign out</button>`;
      document.getElementById("signOut").onclick = () => A.signOut(authClient);
    } else {
      bar.innerHTML = `<span class="who muted">Sign in to post and reply.</span>
        <button class="btn btn-primary btn-sm" id="googleIn">Sign in with Google</button>
        <button class="btn btn-ghost btn-sm" id="emailIn">Use email</button>`;
      document.getElementById("googleIn").onclick = googleSignIn;
      document.getElementById("emailIn").onclick = showEmailForm;
    }
  }

  async function googleSignIn() {
    try { await A.signInWithPopup(authClient, new A.GoogleAuthProvider()); }
    catch (e) { alert(e.message); }
  }

  function showEmailForm() {
    const bar = document.getElementById("authBar");
    bar.innerHTML = `
      <form id="emailForm" class="email-form">
        <div class="ef-tabs">
          <button type="button" class="ef-tab active" data-mode="signin">Sign in</button>
          <button type="button" class="ef-tab" data-mode="signup">Create account</button>
        </div>
        <input type="text" id="efName" placeholder="Your name" autocomplete="name" style="display:none">
        <input type="email" id="efEmail" placeholder="Email" autocomplete="email" required>
        <input type="password" id="efPass" placeholder="Password (6+ characters)" autocomplete="current-password" required>
        <div class="ef-actions">
          <button type="submit" class="btn btn-primary btn-sm" id="efSubmit">Sign in</button>
          <button type="button" class="btn btn-ghost btn-sm" id="efCancel">Cancel</button>
        </div>
        <p class="ef-error" id="efError" hidden></p>
      </form>`;
    let mode = "signin";
    const name = document.getElementById("efName");
    bar.querySelectorAll(".ef-tab").forEach((t) => t.onclick = () => {
      mode = t.dataset.mode;
      bar.querySelectorAll(".ef-tab").forEach((x) => x.classList.toggle("active", x === t));
      name.style.display = mode === "signup" ? "" : "none";
      document.getElementById("efSubmit").textContent = mode === "signup" ? "Create account" : "Sign in";
    });
    document.getElementById("efCancel").onclick = renderAuthBar;
    document.getElementById("emailForm").onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById("efEmail").value.trim();
      const pass = document.getElementById("efPass").value;
      const err = document.getElementById("efError");
      err.hidden = true;
      try {
        if (mode === "signup") {
          const cred = await A.createUserWithEmailAndPassword(authClient, email, pass);
          const nm = name.value.trim();
          if (nm) await A.updateProfile(cred.user, { displayName: nm });
        } else {
          await A.signInWithEmailAndPassword(authClient, email, pass);
        }
      } catch (ex) { err.hidden = false; err.textContent = ex.message; }
    };
  }

  /* ---- routing ---- */
  function route() {
    if (state.unsub) { state.unsub(); state.unsub = null; }
    const id = threadId();
    if (id) showThread(id); else showList();
  }
  function go(url) { history.pushState({}, "", url); route(); }

  /* ---- thread list ---- */
  function showList() {
    const mount = document.getElementById("forumMount");
    const displayName = () => state.user.displayName || state.user.email;

    mount.innerHTML = `
      ${state.user ? `
      <form id="newThread" class="card thread-form">
        <h3>Ask a question or start a discussion</h3>
        <input type="text" id="ntTitle" placeholder="Title — e.g. How do we keep the Fast of Nineveh?" maxlength="140" required>
        <textarea id="ntBody" placeholder="Share your question or thought…" rows="4" required></textarea>
        <div class="nt-row">
          <label class="nt-field">Section
            <select id="ntCat">${CATEGORIES.map((c) => `<option value="${c.id}">${c.emoji} ${esc(c.label)}</option>`).join("")}</select>
          </label>
          <label class="nt-anon"><input type="checkbox" id="ntAnon"> Post anonymously</label>
          <button class="btn btn-primary btn-sm" type="submit">Post</button>
        </div>
      </form>` : `<div class="notice notice-soft">Please sign in above to post a question. You can still read every discussion.</div>`}

      <div class="forum-toolbar">
        <input type="search" id="forumSearch" class="forum-search" placeholder="Search discussions…" value="${esc(ui.q)}">
        <label class="forum-sort">Sort
          <select id="forumSort">
            <option value="new">Newest</option>
            <option value="replies">Most replies</option>
            <option value="unanswered">Unanswered</option>
          </select>
        </label>
      </div>
      <div class="cat-chips" id="catChips">
        <button class="chip" data-cat="all">All</button>
        ${CATEGORIES.map((c) => `<button class="chip" data-cat="${c.id}">${c.emoji} ${esc(c.label)}</button>`).join("")}
      </div>

      <div id="threadList" class="thread-list"><p class="muted">Loading discussions…</p></div>`;

    if (state.user) {
      const anonBox = document.getElementById("ntAnon");
      const catSel = document.getElementById("ntCat");
      // Selecting the Anonymous section forces & locks the anonymous checkbox.
      const syncAnonLock = () => {
        const forced = CAT_BY_ID[catSel.value] && CAT_BY_ID[catSel.value].forcesAnon;
        if (forced) { anonBox.checked = true; anonBox.disabled = true; }
        else { anonBox.disabled = false; }
      };
      catSel.onchange = syncAnonLock; syncAnonLock();

      document.getElementById("newThread").onsubmit = async (e) => {
        e.preventDefault();
        const title = document.getElementById("ntTitle").value.trim();
        const body = document.getElementById("ntBody").value.trim();
        if (!title || !body) return;
        const category = catSel.value;
        const anon = anonBox.checked || (CAT_BY_ID[category] && CAT_BY_ID[category].forcesAnon) || false;
        try {
          const ref = await F.addDoc(F.collection(db, "threads"), {
            title, body, category, anon,
            // Anonymous posts never store the real name — only the uid, which
            // only a moderator can map back via the Firebase console.
            authorName: anon ? "Anonymous" : displayName(),
            authorId: state.user.uid,
            createdAt: F.serverTimestamp(),
            lastReplyAt: F.serverTimestamp(),
            replyCount: 0,
            bestReplyId: null,
          });
          go(`community.html?thread=${ref.id}`);
        } catch (ex) { alert(ex.message); }
      };
    }

    // toolbar + chips wiring (re-render from cached snapshot, no refetch)
    const search = document.getElementById("forumSearch");
    const sortSel = document.getElementById("forumSort");
    sortSel.value = ui.sort;
    search.oninput = () => { ui.q = search.value; renderThreads(); };
    sortSel.onchange = () => { ui.sort = sortSel.value; renderThreads(); };
    document.querySelectorAll("#catChips .chip").forEach((b) => b.onclick = () => {
      ui.category = b.dataset.cat; syncChips(); renderThreads();
    });
    syncChips();

    const q = F.query(F.collection(db, "threads"), F.orderBy("createdAt", "desc"));
    state.unsub = F.onSnapshot(q, (snap) => {
      state.threads = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
      renderThreads();
    }, (err) => {
      const list = document.getElementById("threadList");
      if (list) list.innerHTML = `<div class="notice notice-warn"><p>${esc(err.message)}</p><p class="muted">Make sure Firestore security rules are published (see COMMUNITY-SETUP.md).</p></div>`;
    });

    function syncChips() {
      document.querySelectorAll("#catChips .chip").forEach((b) =>
        b.classList.toggle("active", b.dataset.cat === ui.category));
    }

    function renderThreads() {
      const list = document.getElementById("threadList");
      if (!list) return;
      let items = state.threads.slice();
      if (ui.category !== "all") items = items.filter((t) => (t.category || "general") === ui.category);
      const term = ui.q.trim().toLowerCase();
      if (term) items = items.filter((t) =>
        (t.title || "").toLowerCase().includes(term) || (t.body || "").toLowerCase().includes(term));
      if (ui.sort === "replies") items.sort((a, b) => (b.replyCount || 0) - (a.replyCount || 0));
      else if (ui.sort === "unanswered") items = items.filter((t) => !(t.replyCount > 0));

      if (!items.length) {
        list.innerHTML = state.threads.length
          ? `<div class="empty-state"><h3>No matching discussions</h3><p>Try a different section or search.</p></div>`
          : `<div class="empty-state"><h3>No discussions yet</h3><p>Be the first to ask a question.</p></div>`;
        return;
      }
      list.innerHTML = items.map((t) => `
        <a class="thread-row" href="community.html?thread=${t.id}" data-id="${t.id}">
          <div class="tr-main">
            <div class="tr-badges">
              <span class="pill maroon cat-pill">${catLabel(t.category)}</span>
              ${t.bestReplyId ? `<span class="pill green">✓ Answered</span>` : ""}
            </div>
            <h3>${esc(t.title)}</h3>
            <p>${esc(snippet(t.body))}</p>
            <span class="tr-meta">${esc(authorLabel(t))} · ${timeAgo(t.createdAt)}</span>
          </div>
          <div class="tr-count"><strong>${t.replyCount || 0}</strong><span>repl${(t.replyCount || 0) === 1 ? "y" : "ies"}</span></div>
        </a>`).join("");
      list.querySelectorAll(".thread-row").forEach((a) => a.addEventListener("click", (e) => {
        e.preventDefault(); go(a.getAttribute("href"));
      }));
    }
  }

  /* ---- thread detail ---- */
  function showThread(id) {
    const mount = document.getElementById("forumMount");
    mount.innerHTML = `<p><a href="community.html" id="backLink">← All discussions</a></p>
      <div id="threadDetail"><p class="muted">Loading…</p></div>`;
    document.getElementById("backLink").onclick = (e) => { e.preventDefault(); go("community.html"); };

    const tref = F.doc(db, "threads", id);
    // Local cache of the three live data sources; any update re-renders the view.
    const data = { thread: null, threadExists: false, replies: [], reactions: new Map() };

    const unsubT = F.onSnapshot(tref, (d) => {
      data.threadExists = d.exists();
      data.thread = d.exists() ? d.data() : null;
      renderDetail();
    });
    const rq = F.query(F.collection(db, "threads", id, "replies"), F.orderBy("createdAt", "asc"));
    const unsubR = F.onSnapshot(rq, (snap) => {
      data.replies = snap.docs.map((r) => ({ id: r.id, ...r.data() }));
      renderDetail();
    });
    const xq = F.collection(db, "threads", id, "reactions");
    const unsubX = F.onSnapshot(xq, (snap) => {
      // targetId -> { key -> Set(uid) }
      const map = new Map();
      snap.docs.forEach((doc) => {
        const r = doc.data();
        if (!r || !r.targetId || !r.type) return;
        if (!map.has(r.targetId)) map.set(r.targetId, {});
        const bucket = map.get(r.targetId);
        (bucket[r.type] = bucket[r.type] || new Set()).add(r.uid);
      });
      data.reactions = map;
      renderDetail();
    });

    state.unsub = () => { unsubT(); unsubR(); unsubX(); };

    /* render the OP + replies + reaction bars from the cached `data` */
    function renderDetail() {
      const detail = document.getElementById("threadDetail");
      if (!detail) return;
      if (!data.threadExists) {
        detail.innerHTML = `<div class="empty-state"><h3>Discussion not found</h3><p>It may have been removed.</p></div>`;
        return;
      }
      const t = data.thread;
      const canManage = isAdmin() || (state.user && state.user.uid === t.authorId); // thread owner / mod
      const canDelOp = canManage;

      // best answer floats to the top of the reply list
      const replies = data.replies.slice().sort((a, b) => {
        if (a.id === t.bestReplyId) return -1;
        if (b.id === t.bestReplyId) return 1;
        return 0;
      });

      detail.innerHTML = `
        <article class="thread-op card">
          <div class="tr-badges">
            <span class="pill maroon cat-pill">${catLabel(t.category)}</span>
            ${t.bestReplyId ? `<span class="pill green">✓ Answered</span>` : ""}
          </div>
          <h2>${esc(t.title)}</h2>
          <p class="op-meta">${esc(authorLabel(t))} · ${timeAgo(t.createdAt)}</p>
          <div class="op-body">${paras(t.body)}</div>
          ${reactionBar(id)}
          ${canDelOp ? `<div class="op-actions"><button class="btn btn-ghost btn-sm" id="delThread">Delete discussion</button></div>` : ""}
        </article>

        <h3 class="replies-h">Replies</h3>
        <div class="reply-list">
          ${replies.length ? replies.map((x) => {
            const best = x.id === t.bestReplyId;
            const canDelReply = isAdmin() || (state.user && state.user.uid === x.authorId);
            return `<div class="reply${best ? " reply-best" : ""}" data-rid="${x.id}">
              ${best ? `<div class="best-flag">✓ Best answer</div>` : ""}
              <div class="reply-meta">${esc(authorLabel(x))} · ${timeAgo(x.createdAt)}</div>
              <div class="reply-body">${paras(x.body)}</div>
              ${reactionBar(x.id)}
              <div class="reply-actions">
                ${canManage ? `<button class="linkbtn mark-best" data-rid="${x.id}">${best ? "Unmark answer" : "Mark as answer"}</button>` : ""}
                ${canDelReply ? `<button class="linkbtn reply-del" data-rid="${x.id}">Delete</button>` : ""}
              </div>
            </div>`;
          }).join("") : `<p class="muted">No replies yet. Be the first to respond.</p>`}
        </div>

        ${state.user ? `
        <form id="replyForm" class="card thread-form">
          <textarea id="rfBody" placeholder="Write a reply…" rows="3" required></textarea>
          <div class="nt-row">
            ${t.anon ? `<span class="muted nt-anon-note">Replies in this discussion are posted anonymously.</span>`
                     : `<label class="nt-anon"><input type="checkbox" id="rfAnon"> Reply anonymously</label>`}
            <button class="btn btn-primary btn-sm" type="submit">Reply</button>
          </div>
        </form>` : `<div class="notice notice-soft">Sign in above to reply.</div>`}`;

      wireDetail(t);
    }

    function wireDetail(t) {
      const detail = document.getElementById("threadDetail");
      const displayName = () => state.user.displayName || state.user.email;

      const delBtn = document.getElementById("delThread");
      if (delBtn) delBtn.onclick = async () => {
        if (!confirm("Delete this discussion and its replies?")) return;
        try { await F.deleteDoc(tref); go("community.html"); } catch (ex) { alert(ex.message); }
      };

      detail.querySelectorAll(".mark-best").forEach((b) => b.onclick = async () => {
        const rid = b.dataset.rid;
        const next = t.bestReplyId === rid ? null : rid;
        try { await F.updateDoc(tref, { bestReplyId: next }); } catch (ex) { alert(ex.message); }
      });

      detail.querySelectorAll(".reply-del").forEach((b) => b.onclick = async () => {
        if (!confirm("Delete this reply?")) return;
        try {
          if (t.bestReplyId === b.dataset.rid) await F.updateDoc(tref, { bestReplyId: null });
          await F.deleteDoc(F.doc(db, "threads", id, "replies", b.dataset.rid));
          await F.updateDoc(tref, { replyCount: F.increment(-1) });
        } catch (ex) { alert(ex.message); }
      });

      // reactions (event-delegated)
      detail.querySelectorAll(".react-btn").forEach((b) => b.onclick = () => toggleReaction(b.dataset.target, b.dataset.key));

      const form = document.getElementById("replyForm");
      if (form) form.onsubmit = async (e) => {
        e.preventDefault();
        const body = document.getElementById("rfBody").value.trim();
        if (!body) return;
        const anonInput = document.getElementById("rfAnon");
        const anon = t.anon || (anonInput && anonInput.checked) || false;
        try {
          await F.addDoc(F.collection(db, "threads", id, "replies"), {
            body, anon,
            authorName: anon ? "Anonymous" : displayName(),
            authorId: state.user.uid,
            createdAt: F.serverTimestamp(),
          });
          await F.updateDoc(tref, { replyCount: F.increment(1), lastReplyAt: F.serverTimestamp() });
          document.getElementById("rfBody").value = "";
        } catch (ex) { alert(ex.message); }
      };
    }

    /* a row of reaction buttons for a given target (thread id or reply id) */
    function reactionBar(targetId) {
      const bucket = data.reactions.get(targetId) || {};
      const mine = state.user ? myReaction(targetId) : null;
      const btns = REACTIONS.map((r) => {
        const count = bucket[r.key] ? bucket[r.key].size : 0;
        const active = mine === r.key;
        return `<button class="react-btn${active ? " active" : ""}${count ? " has" : ""}" data-target="${targetId}" data-key="${r.key}" title="${esc(r.title)}"${state.user ? "" : " disabled"}>
          <span class="re-emoji">${r.emoji}</span>${count ? `<span class="re-count">${count}</span>` : ""}
        </button>`;
      }).join("");
      return `<div class="react-bar">${btns}</div>`;
    }

    function myReaction(targetId) {
      const bucket = data.reactions.get(targetId);
      if (!bucket || !state.user) return null;
      for (const key of Object.keys(bucket)) if (bucket[key].has(state.user.uid)) return key;
      return null;
    }

    async function toggleReaction(targetId, key) {
      if (!state.user) return;
      const docId = `${state.user.uid}__${targetId}`;
      const ref = F.doc(db, "threads", id, "reactions", docId);
      const current = myReaction(targetId);
      try {
        if (current === key) {
          await F.deleteDoc(ref);                       // tap same emoji again → remove
        } else {
          await F.setDoc(ref, { uid: state.user.uid, targetId, type: key, createdAt: F.serverTimestamp() });
        }
      } catch (ex) { alert(ex.message); }
    }
  }

  /* ---- helpers ---- */
  function authorLabel(o) {
    if (o && o.anon) return "🕊️ Anonymous";
    return (o && o.authorName) || "Member";
  }
  function snippet(s) { s = (s || "").replace(/\s+/g, " ").trim(); return s.length > 140 ? s.slice(0, 140) + "…" : s; }
  function paras(s) { return (s || "").split(/\n{2,}/).map((p) => `<p>${esc(p).replace(/\n/g, "<br>")}</p>`).join(""); }
  function timeAgo(ts) {
    if (!ts || !ts.toDate) return "just now";
    const d = ts.toDate(), diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return Math.floor(diff / 60) + "m ago";
    if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
    if (diff < 604800) return Math.floor(diff / 86400) + "d ago";
    return d.toLocaleDateString();
  }
}
