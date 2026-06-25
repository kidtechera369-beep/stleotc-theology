/* ==========================================================================
   FIREBASE CONFIG  —  the ONLY file you edit to turn the Community on.

   1. Create a free Firebase project:  https://console.firebase.google.com
   2. Add a Web App (</> icon) and copy its config values below.
   3. In the console: Build → Authentication → enable "Google" and
      "Email/Password" sign-in providers.
   4. In the console: Build → Firestore Database → Create database
      (Production mode), then paste the security rules from COMMUNITY-SETUP.md.
   5. (Optional) add your email to ADMIN_EMAILS to be able to delete any post.

   Until you replace the placeholder values, the Community page shows
   setup instructions instead of the live forum. Nothing breaks.
   ========================================================================== */

window.FIREBASE_CONFIG = {
  apiKey: "AIzaSyC9VlJ5xFSbQaWTWrjc2ovV9zQBHfctof0",
  authDomain: "stl-eotc.firebaseapp.com",
  projectId: "stl-eotc",
  storageBucket: "stl-eotc.firebasestorage.app",
  messagingSenderId: "91783918899",
  appId: "1:91783918899:web:600fffb1e90272161cfa46",
};

/* Emails that may moderate (delete any post). Add the deacon's email here. */
window.ADMIN_EMAILS = [
  "kidtechera369@gmail.com",
];
