# Community Forum — Setup Guide

The Community page (`community.html`) is a real, multi-user forum: members sign in,
post questions, and reply to one another, and everything is stored in **Firebase**
(Google's free backend). The website itself stays static — it just talks to Firebase
from the browser.

Until you complete the steps below, the Community page shows a friendly
"almost ready" notice instead of the live forum. Nothing else on the site is affected.

---

## 1. Create a free Firebase project
1. Go to **https://console.firebase.google.com** and sign in with a Google account.
2. Click **Add project**, name it (e.g. `stl-community`), and finish. (Google Analytics is optional.)

## 2. Add a Web App and copy the config
1. In the project, click the **`</>`** (Web) icon to "Add app."
2. Give it a nickname; you do **not** need Firebase Hosting.
3. Firebase shows a `firebaseConfig = { ... }` object. Copy those values into
   [`assets/js/firebase-config.js`](assets/js/firebase-config.js), replacing each `REPLACE_ME`.

```js
window.FIREBASE_CONFIG = {
  apiKey: "AIza...",
  authDomain: "stl-community.firebaseapp.com",
  projectId: "stl-community",
  storageBucket: "stl-community.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abc123",
};
```
> These values are **safe to commit** — Firebase web keys are public identifiers.
> Real protection comes from the Security Rules in step 5.

## 3. Turn on sign-in methods
In the console: **Build → Authentication → Get started → Sign-in method**, then enable:
- **Google**
- **Email/Password**

## 4. Authorize your domain
In **Authentication → Settings → Authorized domains**, add your site's domain
(e.g. `kidtechera369-beep.github.io`). `localhost` is already allowed for testing.

## 5. Create the database and paste the rules
1. **Build → Firestore Database → Create database** → **Production mode** → pick a location.
2. Open the **Rules** tab, replace everything with the rules below, and **Publish**:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() { return request.auth != null; }
    function isAdmin() {
      return signedIn() && request.auth.token.email in [
        "kidtechera369@gmail.com"   // <-- the deacon's email(s); match ADMIN_EMAILS
      ];
    }
    function isOwner() {
      return signedIn() && resource.data.authorId == request.auth.uid;
    }

    match /threads/{thread} {
      allow read: if true;
      allow create: if signedIn()
        && request.resource.data.authorId == request.auth.uid
        && request.resource.data.title is string
        && request.resource.data.title.size() <= 140
        && request.resource.data.body is string
        && request.resource.data.body.size() <= 5000
        && request.resource.data.category is string
        && request.resource.data.category.size() <= 24
        && request.resource.data.anon is bool;

      // Anyone signed in may bump the reply counter / last-reply time.
      allow update: if signedIn()
        && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['replyCount', 'lastReplyAt']);
      // Only the thread owner or a moderator may set the "best answer".
      allow update: if (isAdmin() || isOwner())
        && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['bestReplyId']);

      allow delete: if isAdmin() || isOwner();

      match /replies/{reply} {
        allow read: if true;
        allow create: if signedIn()
          && request.resource.data.authorId == request.auth.uid
          && request.resource.data.body is string
          && request.resource.data.body.size() <= 5000
          && request.resource.data.anon is bool;
        allow delete: if isAdmin() || isOwner();
      }

      // One reaction document per user per target (doc id is "<uid>__<targetId>").
      match /reactions/{reaction} {
        allow read: if true;
        allow create, update: if signedIn()
          && request.resource.data.uid == request.auth.uid
          && request.resource.data.type is string
          && request.resource.data.type.size() <= 16
          && request.resource.data.targetId is string;
        allow delete: if signedIn() && resource.data.uid == request.auth.uid;
      }
    }
  }
}
```

> **After updating these rules, you must re-publish them** in the Firebase console
> (**Firestore Database → Rules → Publish**), or the new features (reactions,
> best-answer, categories, anonymous posting) will be blocked.

## 6. Set the moderator email(s)
- In [`assets/js/firebase-config.js`](assets/js/firebase-config.js), uncomment and set
  `window.ADMIN_EMAILS` (e.g. `["kidtechera369@gmail.com"]`).
- Use the **same** email(s) in the `isAdmin()` list in the rules above.
- Moderators can delete any post; everyone else can delete only their own.

---

## Test it
1. Run the site locally (`python3 -m http.server 8000`) and open
   `http://localhost:8000/community.html`.
2. Sign in with Google or create an email account, post a question, and reply.
3. Open it in another browser/incognito to confirm posts are shared and live.

## What members can do
- **Read** every discussion without signing in.
- **Post** a question and **reply** after signing in (Google or email).
- **Choose a section** (General, Scripture, Prayer Requests, Feasts & Fasts,
  Lessons, Youth, Anonymous) and **filter / search / sort** the discussion list.
- **React** to a post or reply (🙏 ✝️ 🕯️ ❤️ 👍) — one reaction per person.
- **Mark a best answer** — the asker or a moderator can flag the reply that
  resolved a question; it floats to the top with an "Answered" badge.
- **Post anonymously** — a checkbox on any post (always on in the Anonymous
  section). Anonymous posts show "Anonymous" to other members; the real name is
  **never written** to the public document, so only a moderator can identify the
  author via the Firebase console (Authentication → look up the uid).
- **Delete** their own posts; moderators can delete anything.

## Cost
Firebase's free **Spark** plan is generous (roughly 50k reads / 20k writes per day) —
far more than a parish forum needs. No credit card required.

## Notes
- Threads are stored in the `threads` collection; replies in each thread's
  `replies` subcollection. Reply counts are kept on each thread.
- To add basic spam protection later, enable **Firebase App Check**.
