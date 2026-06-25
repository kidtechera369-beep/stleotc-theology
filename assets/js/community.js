/* ==========================================================================
   COMMUNITY.JS  —  Firebase-powered forum (ES module)
   Loaded as <script type="module"> on community.html.
   Reads window.FIREBASE_CONFIG (assets/js/firebase-config.js).
   Degrades gracefully to a setup notice when not configured.
   ========================================================================== */

const VERSION = "10.12.2";
const root = document.getElementById("community");
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const cfg = window.FIREBASE_CONFIG || {};
const ADMINS = (window.ADMIN_EMAILS || []).map((e) => String(e).toLowerCase());
const configured = cfg.apiKey && cfg.apiKey !== "REPLACE_ME" && cfg.projectId && cfg.projectId !== "REPLACE_ME";

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

  const state = { user: null, unsub: null };
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
    mount.innerHTML = `
      ${state.user ? `
      <form id="newThread" class="card thread-form">
        <h3>Ask a question or start a discussion</h3>
        <input type="text" id="ntTitle" placeholder="Title — e.g. How do we keep the Fast of Nineveh?" maxlength="140" required>
        <textarea id="ntBody" placeholder="Share your question or thought…" rows="4" required></textarea>
        <div><button class="btn btn-primary btn-sm" type="submit">Post</button></div>
      </form>` : `<div class="notice notice-soft">Please sign in above to post a question. You can still read every discussion.</div>`}
      <div id="threadList" class="thread-list"><p class="muted">Loading discussions…</p></div>`;

    if (state.user) {
      document.getElementById("newThread").onsubmit = async (e) => {
        e.preventDefault();
        const title = document.getElementById("ntTitle").value.trim();
        const body = document.getElementById("ntBody").value.trim();
        if (!title || !body) return;
        try {
          const ref = await F.addDoc(F.collection(db, "threads"), {
            title, body,
            authorName: state.user.displayName || state.user.email,
            authorId: state.user.uid,
            createdAt: F.serverTimestamp(),
            replyCount: 0,
          });
          go(`community.html?thread=${ref.id}`);
        } catch (ex) { alert(ex.message); }
      };
    }

    const q = F.query(F.collection(db, "threads"), F.orderBy("createdAt", "desc"));
    state.unsub = F.onSnapshot(q, (snap) => {
      const list = document.getElementById("threadList");
      if (!list) return;
      if (snap.empty) { list.innerHTML = `<div class="empty-state"><h3>No discussions yet</h3><p>Be the first to ask a question.</p></div>`; return; }
      list.innerHTML = snap.docs.map((d) => {
        const t = d.data();
        return `<a class="thread-row" href="community.html?thread=${d.id}" data-id="${d.id}">
          <div class="tr-main">
            <h3>${esc(t.title)}</h3>
            <p>${esc(snippet(t.body))}</p>
            <span class="tr-meta">${esc(t.authorName || "Member")} · ${timeAgo(t.createdAt)}</span>
          </div>
          <div class="tr-count"><strong>${t.replyCount || 0}</strong><span>repl${(t.replyCount || 0) === 1 ? "y" : "ies"}</span></div>
        </a>`;
      }).join("");
      list.querySelectorAll(".thread-row").forEach((a) => a.addEventListener("click", (e) => {
        e.preventDefault(); go(a.getAttribute("href"));
      }));
    }, (err) => {
      const list = document.getElementById("threadList");
      if (list) list.innerHTML = `<div class="notice notice-warn"><p>${esc(err.message)}</p><p class="muted">Make sure Firestore security rules are published (see COMMUNITY-SETUP.md).</p></div>`;
    });
  }

  /* ---- thread detail ---- */
  function showThread(id) {
    const mount = document.getElementById("forumMount");
    mount.innerHTML = `<p><a href="community.html" id="backLink">← All discussions</a></p>
      <div id="threadDetail"><p class="muted">Loading…</p></div>`;
    document.getElementById("backLink").onclick = (e) => { e.preventDefault(); go("community.html"); };

    const tref = F.doc(db, "threads", id);
    state.unsub = F.onSnapshot(tref, (d) => {
      const detail = document.getElementById("threadDetail");
      if (!detail) return;
      if (!d.exists()) { detail.innerHTML = `<div class="empty-state"><h3>Discussion not found</h3><p>It may have been removed.</p></div>`; return; }
      const t = d.data();
      const canDel = isAdmin() || (state.user && state.user.uid === t.authorId);
      detail.innerHTML = `
        <article class="thread-op card">
          <h2>${esc(t.title)}</h2>
          <p class="op-meta">${esc(t.authorName || "Member")} · ${timeAgo(t.createdAt)}</p>
          <div class="op-body">${paras(t.body)}</div>
          ${canDel ? `<div class="op-actions"><button class="btn btn-ghost btn-sm" id="delThread">Delete</button></div>` : ""}
        </article>
        <h3 class="replies-h">Replies</h3>
        <div id="replyList" class="reply-list"><p class="muted">Loading replies…</p></div>
        ${state.user ? `
        <form id="replyForm" class="card thread-form">
          <textarea id="rfBody" placeholder="Write a reply…" rows="3" required></textarea>
          <div><button class="btn btn-primary btn-sm" type="submit">Reply</button></div>
        </form>` : `<div class="notice notice-soft">Sign in above to reply.</div>`}`;

      if (canDel) document.getElementById("delThread").onclick = async () => {
        if (!confirm("Delete this discussion and its replies?")) return;
        try { await F.deleteDoc(tref); go("community.html"); } catch (ex) { alert(ex.message); }
      };
      if (state.user) document.getElementById("replyForm").onsubmit = async (e) => {
        e.preventDefault();
        const body = document.getElementById("rfBody").value.trim();
        if (!body) return;
        try {
          await F.addDoc(F.collection(db, "threads", id, "replies"), {
            body,
            authorName: state.user.displayName || state.user.email,
            authorId: state.user.uid,
            createdAt: F.serverTimestamp(),
          });
          await F.updateDoc(tref, { replyCount: F.increment(1) });
          document.getElementById("rfBody").value = "";
        } catch (ex) { alert(ex.message); }
      };
    });

    // replies realtime
    const rq = F.query(F.collection(db, "threads", id, "replies"), F.orderBy("createdAt", "asc"));
    const unsubR = F.onSnapshot(rq, (snap) => {
      const rl = document.getElementById("replyList");
      if (!rl) return;
      if (snap.empty) { rl.innerHTML = `<p class="muted">No replies yet. Be the first to respond.</p>`; return; }
      rl.innerHTML = snap.docs.map((r) => {
        const x = r.data();
        const canDel = isAdmin() || (state.user && state.user.uid === x.authorId);
        return `<div class="reply">
          <div class="reply-meta">${esc(x.authorName || "Member")} · ${timeAgo(x.createdAt)}</div>
          <div class="reply-body">${paras(x.body)}</div>
          ${canDel ? `<button class="reply-del" data-rid="${r.id}">Delete</button>` : ""}
        </div>`;
      }).join("");
      rl.querySelectorAll(".reply-del").forEach((b) => b.onclick = async () => {
        if (!confirm("Delete this reply?")) return;
        try {
          await F.deleteDoc(F.doc(db, "threads", id, "replies", b.dataset.rid));
          await F.updateDoc(tref, { replyCount: F.increment(-1) });
        } catch (ex) { alert(ex.message); }
      });
    });
    // chain unsub
    const prev = state.unsub;
    state.unsub = () => { if (prev) prev(); unsubR(); };
  }

  /* ---- helpers ---- */
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
