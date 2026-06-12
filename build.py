#!/usr/bin/env python3
"""
Site generator for the STL Orthodox Theology Class website.
Edit LESSONS / GLOSSARY_EXTRA below, then run:  python3 build.py
Regenerates: index.html, lessons.html, downloads.html, glossary.html,
start-here.html, and lessons/*.html.
"""
import os, html, json

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_NAME = "STL Ethiopian Orthodox Tewahedo Theology Class"
TAGLINE = "Debre Nazreth St. Mary &amp; St. Gabriel Ethiopian Orthodox Tewahedo Church"

# ---------------------------------------------------------------
# Standard citations (reused across lessons)
# ---------------------------------------------------------------
CIT_CURRICULUM = ("Kesis Solomon Mulugeta Zewde (PhD), <em>Sunday School Curriculum in English, "
  "Level V (High School and College)</em>, Debre Nazareth St. Mary &amp; St. Gabriel Ethiopian "
  "Orthodox Tewahedo Church, St. Louis, MO")
CIT_SLIDES = "Lesson slides prepared and taught by Dn Yonnas"
CIT_SCRIPTURE = "Holy Scripture (KJV / NKJV / Orthodox Study Bible wording where quoted)"
CIT_SYNAXARIUM = ("E. A. Wallis Budge (trans.), <em>The Book of the Saints of the Ethiopian Church</em> "
  "(the Ethiopic Synaxarium), from British Museum MSS Oriental 660&ndash;661 "
  "(<a href=\"https://archive.org/details/bookofsaintsofet0001unse\">archive.org</a>)")
CIT_DAOUD = ("Marcos Daoud, <em>The Orthodox Church Sacraments</em>, Addis Ababa: "
  "Tinsae Ze Gubae Printing Press, 1952")
CIT_MALATY_GROW = "Fr. Tadros Y. Malaty, <em>Let Me Grow</em>"
CIT_MALATY_DEVIL = "Fr. Tadros Y. Malaty, <em>Worshiping the Devil in the Present Age</em>"

# ---------------------------------------------------------------
# Category themes: accent color, icon (inline SVG), special-section kind
# ---------------------------------------------------------------
ICONS = {
 "trinity": '<svg viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="4.4"/><circle cx="8" cy="14.5" r="4.4"/><circle cx="16" cy="14.5" r="4.4"/></svg>',
 "cross":   '<svg viewBox="0 0 24 24"><path d="M12 3v18M5 9h14M9 9v-2h6v2M12 21l-3-2.2M12 21l3-2.2"/></svg>',
 "book":    '<svg viewBox="0 0 24 24"><path d="M12 5.5C10 3.8 6.5 3.5 3.5 4.5v14c3-1 6.5-.7 8.5 1 2-1.7 5.5-2 8.5-1v-14c-3-1-6.5-.7-8.5 1z"/><path d="M12 5.5v14"/></svg>',
 "chalice": '<svg viewBox="0 0 24 24"><path d="M5 4h14c0 5-2.5 8-7 8s-7-3-7-8zM12 12v6M8 21h8M9 18h6"/></svg>',
 "halo":    '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="6" ry="2.2"/><circle cx="12" cy="13" r="4.5"/><path d="M7 21c1.5-2 8.5-2 10 0"/></svg>',
 "column":  '<svg viewBox="0 0 24 24"><path d="M4 21h16M5 18h14M8 18V8M12 18V8M16 18V8M5 8h14M4 5h16M7 5l5-2.5L17 5"/></svg>',
 "shield":  '<svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 4.5-3.5 7.8-8 9-4.5-1.2-8-4.5-8-9V6z"/><path d="M12 8v6M9.5 10.5h5"/></svg>',
 "ethcross":'<svg viewBox="0 0 24 24"><path d="M12 2v20M2 12h20M7 7l10 10M17 7L7 17"/><circle cx="12" cy="12" r="4"/></svg>',
 "candle":  '<svg viewBox="0 0 24 24"><path d="M10 10h4v11h-4zM12 10V7"/><path d="M12 2c1.6 1.6 1.6 3.2 0 4.5-1.6-1.3-1.6-2.9 0-4.5z"/><path d="M7 21h10"/></svg>',
 "lamp":    '<svg viewBox="0 0 24 24"><path d="M4 13c0 3 3.5 5 8 5s8-2 8-5h-4c0 1.2-1.7 2-4 2s-4-.8-4-2z"/><path d="M14 9c1.3 1.3 1.3 2.7 0 3.8-1.3-1.1-1.3-2.5 0-3.8z"/><path d="M10 21h4"/></svg>',
}

THEMES = {
 "Holy Trinity":                 dict(color="#8a6312", icon="trinity",  special="guardrails"),
 "Christology":                  dict(color="#6e1e1e", icon="cross",    special="guardrails"),
 "Scripture":                    dict(color="#1f4d2e", icon="book",     special="glance"),
 "Sacraments":                   dict(color="#4b2e5e", icon="chalice",  special="signgrace"),
 "Saints":                       dict(color="#1d3a5f", icon="halo",     special="timeline"),
 "Church History":               dict(color="#5d4023", icon="column",   special="timeline"),
 "Apologetics":                  dict(color="#155e63", icon="shield",   special="qa"),
 "Ethiopian Orthodox Tradition": dict(color="#8a2f1d", icon="ethcross", special="timeline"),
 "Fasting":                      dict(color="#56561b", icon="candle",   special="challenge"),
 "Moral & Spiritual Life":       dict(color="#a45a1a", icon="lamp",     special="challenge"),
}

# ---------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------
LESSONS = [
 dict(slug="holy-trinity", title="Lesson on the Holy Trinity",
  category="Holy Trinity", audience="Youth & Young Adults", file="Holy_Trinity_Lesson_Slides.pptx",
  extras=[("Pre-Lesson Reading (DOCX)", "Holy_Trinity_PreReading.docx")],
  summary="An introduction to the Church's confession of one God in three Persons, built on the Nicene Creed. The lesson explains one divine Nature and three distinct Persons, the meaning of Unbegotten, Begotten, and Proceeding, the 'Two Hands of God' teaching of St. Irenaeus, and the Fathers' analogy of fire — always with the reminder that every analogy falls short of the Mystery.",
  objectives=["Confess one God in three Persons according to the Nicene Creed",
    "Explain the eternal distinctions: the Father unbegotten, the Son begotten, the Holy Spirit proceeding",
    "Use the Fathers' analogies (fire, the spoken word) while understanding their limits"],
  verses=["Matthew 28:19 — \"baptizing them in the name of the Father and of the Son and of the Holy Spirit\"",
    "John 10:30 — \"I and My Father are one.\"",
    "Matthew 3:16–17 — the revelation of the Trinity at the Jordan"],
  points=["There is one Divine Nature (Essence) — indivisible and shared fully by the three Persons",
    "The Persons are distinguished only by their eternal relationships, never by rank or time",
    "The Son is eternally begotten of the Father, as a word comes forth from the mind",
    "The Holy Spirit eternally proceeds from the Father — not created, not begotten",
    "The Son and the Spirit are the 'Two Hands' of the Father in creation and salvation (St. Irenaeus)",
    "Unified without confusion, distinguished without separation — the Tewahedo mystery"],
  discussion=["Why do we say analogies like fire can help us but never fully explain the Trinity?",
    "What is the difference between 'begotten' and 'created'? Why does it matter?",
    "How does the Baptism of Christ at the Jordan reveal the three Persons?"],
  guardrails=dict(
    confess=["One God, one divine Essence, three Persons",
      "The Son eternally begotten of the Father — true God of true God",
      "The Holy Spirit eternally proceeding from the Father",
      "The three Persons are equal in glory, honor, and eternity"],
    reject=["Modalism — one Person merely wearing three masks",
      "Tritheism — three separate gods",
      "Arianism — that the Son is a creature or had a beginning",
      "Treating any analogy as a full explanation of the Mystery"]),
  terms=[("Essence (Nature)", "The shared divine substance of God — what makes God, God. There is only one, indivisible."),
    ("Unbegotten", "The Father's personal property: He is the Source (Arche), proceeding from no one."),
    ("Begotten", "The Son's eternal relationship to the Father — coming forth as a word from the mind, outside of time, never created."),
    ("Proceeding", "The Holy Spirit's eternal relationship to the Father — not created, not begotten, eternally proceeding.")],
  quiz=[("How many divine Natures (Essences) are there in God?",
     ["Three natures, one for each Person", "One divine Nature shared fully by three Persons", "One Person with three different names", "Two natures: divine and human"], 1),
    ("Which Person eternally proceeds from the Father?",
     ["The Son", "The Holy Spirit", "Both the Son and the Spirit", "None — all three proceed"], 1),
    ("In St. Irenaeus' teaching, the 'Two Hands of God' are:",
     ["The angels and the prophets", "The Law and the Prophets", "The Son and the Holy Spirit", "The Church and the Scriptures"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, "The Nicene Creed; the teaching of St. Irenaeus and the Church Fathers as presented in the lesson"],
  related=["trinitarianism-monotheism","st-cyril"]),

 dict(slug="trinitarianism-monotheism", title="Trinitarianism and Monotheism: One God in Three Hypostases",
  category="Holy Trinity", audience="Youth & Young Adults", file="Trinitarianism_Monotheism_Lesson_Slides.pptx",
  week="Week 19",
  summary="A defense and explanation of how the Church worships one God while confessing three Hypostases. The lesson answers the accusation that Christians worship three gods, defines 'Hypostasis,' walks through the distinct work of the Father, the Son, and the Holy Spirit in our salvation, and corrects common misunderstandings.",
  objectives=["Show from Scripture that the Christian faith is fully monotheistic",
    "Define 'Hypostasis' and explain the three Hypostases without separation or ranking",
    "Recognize and answer common misunderstandings about the Trinity"],
  verses=["Deuteronomy 6:4 — \"Hear, O Israel: The Lord our God, the Lord is one.\"",
    "John 10:30 — \"I and My Father are one.\"",
    "Matthew 28:19 — baptism in the one Name of the Father, Son, and Holy Spirit"],
  points=["We believe in one God — never three gods, and never one Person wearing three masks",
    "Hypostasis means a real personal distinction within the one God",
    "The Three are equal in honor, divinity, and eternity; none comes before another in time",
    "The Father wills and sends, the Son redeems and restores, the Holy Spirit sanctifies and gives life",
    "Analogies (the sun's disc, light, and heat) help — but God remains greater than every comparison",
    "Baptism is a Trinitarian new birth, not a mere symbol"],
  discussion=["Why do some people misunderstand the Trinity as belief in three gods?",
    "How does Matthew 28:19 show both unity and distinction?",
    "Why is it important to say the Persons are distinct but never divided?"],
  guardrails=dict(
    confess=["One God: the faith is fully monotheistic (Deut 6:4)",
      "Three real Hypostases: Father, Son, and Holy Spirit",
      "Equal in essence, divinity, glory, and worship",
      "Distinct, but never separated; revealed, yet a mystery"],
    reject=["That Christians believe in three gods",
      "That Father, Son, and Spirit are just three names for one Person",
      "That the Son or the Spirit is 'less divine' than the Father",
      "That one Person existed before the others in time"]),
  terms=[("Hypostasis", "A Greek theological term for a real personal distinction within the one God — a distinct personal reality, not a separate god."),
    ("Monotheism", "Belief in one God. Orthodox Trinitarian faith is fully monotheistic."),
    ("Trinity", "The one God eternally existing as Father, Son, and Holy Spirit — one in essence, three in Hypostases.")],
  quiz=[("What does 'Hypostasis' mean in Orthodox teaching?",
     ["A separate god", "A real personal distinction within the one God", "A mode or mask of God", "A created spiritual being"], 1),
    ("How many Gods do Orthodox Christians worship?",
     ["Three", "One", "Two", "One main God and two lesser ones"], 1),
    ("Which statement does the Church REJECT?",
     ["The Father, Son, and Spirit are equal in honor", "The Son is eternally begotten of the Father", "The Son and Spirit are lesser than the Father", "The Three are distinct but never divided"], 2)],
  sources=[CIT_CURRICULUM + " — Week 19: Trinitarianism and Monotheism", CIT_SLIDES, CIT_SCRIPTURE, "The Nicene Creed"],
  related=["holy-trinity","st-cyril"]),

 dict(slug="st-cyril", title="St. Cyril of Alexandria: The Seal of the Fathers",
  category="Christology", audience="Youth & Young Adults", file="St_Cyril_Lesson_Slides.pptx",
  summary="The life and teaching of St. Cyril (Abba Kirillos), 24th Pope of Alexandria, and his defense of the unity of Christ against Nestorius. The lesson explains the error of dividing Christ into two persons, the meaning of Theotokos, the iron-and-fire analogy of the Tewahedo union, the Council of Ephesus (431 AD), and why our Church bears the name Tewahedo.",
  objectives=["Tell who St. Cyril was and why he is called the Seal of the Fathers",
    "Explain the Nestorian error and why the Church rejected it",
    "Confess the Tewahedo union: one incarnate nature of God the Word, without mixture, confusion, change, or division"],
  verses=["John 1:14 — \"And the Word became flesh and dwelt among us\"",
    "Luke 1:43 — \"the mother of my Lord\"",
    "John 10:30 — \"I and My Father are one.\""],
  points=["The Word did not merely dwell in a man — the Word became man",
    "Nestorius divided Christ into two persons and rejected the title Theotokos",
    "If Mary is not the Mother of God, then the One born of her is not truly God — and we are not truly saved",
    "Iron in fire: united and acting as one, without confusion and without separation",
    "At the Council of Ephesus (431 AD) the Church affirmed Theotokos and the one Christ",
    "Our Church is called Tewahedo ('made one') because of this very faith, confessed in every Kidassie"],
  discussion=["How does knowing Christ is both fully God and fully man change your faith?",
    "Why does honoring St. Mary as Theotokos protect the truth about Christ?",
    "How can you defend the unity of Christ when others say He was only a teacher or prophet?"],
  guardrails=dict(
    confess=["One Lord Jesus Christ — perfect in His divinity, perfect in His humanity",
      "One incarnate nature of God the Word (Mia Physis)",
      "United without mixture, without confusion, without change, without division",
      "St. Mary is truly Theotokos — Mother of God"],
    reject=["The Nestorian division of Christ into two persons",
      "That God merely 'dwelt in' the man Jesus as in a house",
      "That St. Mary gave birth only to a man",
      "Any mixing or blending that loses the full divinity or full humanity"]),
  terms=[("Tewahedo", "Ge'ez for 'made one' — the perfect union of divinity and humanity in the one Christ."),
    ("Theotokos", "Greek for 'God-bearer' / Mother of God — the title of St. Mary defended at Ephesus."),
    ("Nestorianism", "The condemned teaching that Christ is two separate persons, one divine and one human."),
    ("Mia Physis", "St. Cyril's formula: 'one incarnate nature of God the Word' — unity without confusion or division.")],
  quiz=[("What was the error of Nestorius?",
     ["He denied that Christ was human", "He divided Christ into two separate persons", "He taught that there are three gods", "He rejected the Old Testament"], 1),
    ("What does 'Theotokos' mean?",
     ["Queen of Heaven", "Mother of God (God-bearer)", "Holy Virgin", "Full of Grace"], 1),
    ("Which council vindicated St. Cyril and affirmed the Theotokos?",
     ["Nicaea (325)", "Constantinople (381)", "Ephesus (431)", "Chalcedon (451)"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, "The Ethiopian Liturgy (Kidassie): \"He made His humanity one with His divinity, without mixture, without confusion, without change, without division\"", "The Acts of the Council of Ephesus (431 AD) as presented in the lesson"],
  related=["early-church-fathers","holy-trinity"]),

 dict(slug="early-church-fathers", title="The Ancient Faith: Early Church Fathers and the Path of the Tewahedo Church",
  category="Church History", audience="Youth & Young Adults", file="Early_Church_Fathers_Lesson_Slides.pptx",
  summary="A journey through the early Church: the Apostolic Sees, the 1,600-year bond between Alexandria and Ethiopia, the three Ecumenical Councils we accept (Nicaea, Constantinople, Ephesus), the conflict at Chalcedon (451 AD), the meaning of Miaphysitism and the Ge'ez word Tewahedo, and the Nine Saints who planted monasticism in Ethiopia.",
  objectives=["Trace the apostolic roots of the Church and the place of Alexandria among the ancient Sees",
    "Explain which councils the Tewahedo Church accepts and why Chalcedon was rejected",
    "Tell the story of the Nine Saints and their monasteries"],
  verses=["Matthew 16:18 — \"on this rock I will build My church\"",
    "Acts 8:26–39 — the baptism of the Ethiopian eunuch",
    "Jude 1:3 — \"contend earnestly for the faith which was once for all delivered to the saints\""],
  points=["Authority in the early Church gathered around the Apostolic Sees, Alexandria among the first",
    "The Ethiopian Church received her bishops from Alexandria for some 1,600 years",
    "We uphold Nicaea I, Constantinople I, and Ephesus I",
    "The Alexandrian delegation rejected Chalcedon's 'in two natures' as endangering the unity of Christ",
    "Miaphysis: one united nature of God the Word incarnate — Tewahedo means 'made one'",
    "The Nine Saints, fleeing after Chalcedon, evangelized Ethiopia and founded her great monasteries"],
  discussion=["Why does apostolic succession matter for trusting what the Church teaches?",
    "What was the real concern behind rejecting the language of Chalcedon?",
    "What can the Nine Saints teach us about turning exile into mission?"],
  timeline=[("c. 33 AD","Pentecost — the Church is born in Jerusalem"),
    ("1st century","St. Mark establishes the See of Alexandria"),
    ("325 AD","Council of Nicaea I — the divinity of the Son confessed against Arius"),
    ("c. 330s AD","St. Frumentius (Abune Selama) consecrated by St. Athanasius — the Ethiopian episcopal line begins"),
    ("381 AD","Council of Constantinople I — the divinity of the Holy Spirit confessed"),
    ("431 AD","Council of Ephesus I — St. Cyril defends the one Christ; Theotokos affirmed"),
    ("451 AD","Council of Chalcedon — the Oriental Orthodox churches reject its formula; the great separation begins"),
    ("late 400s AD","The Nine Saints arrive in Ethiopia, founding monasteries and translating the Scriptures into Ge'ez")],
  terms=[("Apostolic See", "A city-church founded by an Apostle or his direct disciple, e.g., Alexandria, Antioch, Rome."),
    ("Miaphysitism", "The Oriental Orthodox confession of one united incarnate nature of God the Word — not 'monophysitism.'"),
    ("Ge'ez", "The ancient liturgical language of the Ethiopian Church; 'Tewahedo' is a Ge'ez word meaning 'made one.'"),
    ("The Nine Saints", "Monastic missionaries who came to Ethiopia after Chalcedon and founded her great monasteries."),
    ("Chalcedon", "The 451 AD council whose 'in two natures' formula the Oriental Orthodox churches rejected.")],
  quiz=[("Which three councils does the Tewahedo Church accept?",
     ["Nicaea, Chalcedon, Ephesus", "Nicaea I, Constantinople I, Ephesus I", "Ephesus, Chalcedon, Constantinople II", "Only Nicaea"], 1),
    ("What does the Ge'ez word 'Tewahedo' mean?",
     ["Holy", "Orthodox", "Made one / unity", "Faithful"], 2),
    ("Who were the Nine Saints?",
     ["The first nine Patriarchs of Alexandria", "Nine apostles of the Twelve", "Missionary monks who evangelized Ethiopia after Chalcedon", "Nine Ethiopian kings who accepted the faith"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, "Historical material on the councils and the Nine Saints as compiled in the lesson; see also " + CIT_SYNAXARIUM],
  related=["st-cyril","st-tekle-haimanot"]),

 dict(slug="book-of-acts", title="The Book of Acts",
  category="Scripture", audience="Youth & Young Adults", file="Acts_Lesson_Slides.pptx",
  summary="Acts is the 'Gospel of the Holy Spirit' — the story of the Spirit acting through the Apostles to build the Church. The lesson covers Pentecost, St. Peter and St. Paul, the conversion of the Ethiopian eunuch (Acts 8), the cost of witness in St. Stephen's martyrdom, conflicts inside and outside the Church, and the Jerusalem Council as the blueprint for how the Church resolves disputes in Synod.",
  objectives=["See the Holy Spirit as the true main character of Acts",
    "Explain the significance of Acts 8 for the Ethiopian Church",
    "Learn the apostolic pattern: preaching, repentance, baptism, communion, trial, multiplication"],
  verses=["Acts 1:8 — \"you shall receive power when the Holy Spirit has come upon you\"",
    "Acts 2 — the descent of the Holy Spirit at Pentecost",
    "Acts 8:26–39 — Philip and the Ethiopian eunuch; cf. Psalm 68:31"],
  points=["Acts is not a biography of men but of the Holy Spirit working through the Apostles",
    "The Church is born in prayer, worship, and the Breaking of Bread",
    "The Ethiopian eunuch's baptism fulfills 'Ethiopia shall stretch out her hands to God'",
    "Persecution became a refiner's fire — St. Stephen's martyrdom spread the Gospel rather than stopping it",
    "Ananias and Sapphira warn against spiritual counterfeit; Acts 6 shows the Church confronting tribalism",
    "The Jerusalem Council (Acts 15): the Church decides in council, not by private interpretation"],
  discussion=["Why is it important that the Church was born in prayer and not in a committee?",
    "What does the story of the Ethiopian eunuch mean for our identity as Ethiopian Orthodox Christians?",
    "How does the Jerusalem Council guide the Church when conflict arises today?"],
  glance=dict(author="St. Luke, the beloved physician (companion of St. Paul)",
    written="Likely the 60s AD, after the events of Acts 28",
    audience="Theophilus, and the whole Church",
    theme="The Holy Spirit builds, guides, and multiplies the Church"),
  terms=[("Pentecost", "The descent of the Holy Spirit upon the Apostles (Acts 2), fifty days after the Resurrection — the birth of the Church's public witness."),
    ("Tsega", "Grace — in Oriental Orthodox understanding, the divine energy and life-giving power of God, not a mere concept."),
    ("Synod (Council)", "The gathered Church deciding matters of faith together, as in Acts 15 — the opposite of private interpretation."),
    ("Martyr", "A witness unto death; St. Stephen (Acts 6–7) is the first martyr of the Church.")],
  quiz=[("Who is the 'hidden main character' of the Book of Acts?",
     ["St. Peter", "St. Paul", "The Holy Spirit", "St. Luke"], 2),
    ("What Ethiopian connection appears in Acts 8?",
     ["The Nine Saints arrive in Aksum", "Philip baptizes the Ethiopian eunuch, official of Queen Candace", "St. Mark preaches in Ethiopia", "The Ark of the Covenant is mentioned"], 1),
    ("What does the Jerusalem Council (Acts 15) teach about how the Church decides disputes?",
     ["Each believer decides privately", "The majority of members vote", "The Church meets in council with apostolic authority", "Disputes are left unresolved"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["st-luke","book-of-romans"]),

 dict(slug="book-of-romans", title="The Book of Romans",
  category="Scripture", audience="Youth & Young Adults", file="Romans_Lesson_Slides.pptx",
  summary="St. Paul's letter to Rome read through Orthodox eyes: not a courtroom but a hospital. Sin is the sickness, Christ is the Medhanit (Healer), grace is the medicine, and the Church is where recovery happens. The lesson walks through the diagnosis (ch. 1–3), the medicine of grace (4–5), recovery in baptism and the Spirit (6–8), and the healthy life of the community (12–16).",
  objectives=["Read Romans through the Orthodox 'hospital' framework of healing rather than only legal acquittal",
    "Explain faith and works as synergy — two sides of one coin",
    "Understand the Two Adams: death through the first, life through Christ the Second Adam"],
  verses=["Romans 3:23 — \"all have sinned and fall short of the glory of God\"",
    "Romans 5:12–21 — the Two Adams",
    "Romans 6:3–4 — buried with Christ in baptism into newness of life"],
  points=["Justification is healing: we were sick with sin and Christ makes us whole",
    "Paul levels the field — Jew and Gentile alike fall short and need the same Physician",
    "Grace (Tsega) is the life-giving power of God, received through faith",
    "Baptism is the beginning of recovery; the Spirit leads sanctification",
    "'Works of the Law' (rituals like circumcision) are not the same as works of love",
    "St. John Chrysostom had Romans read to him twice a week; St. Cyril taught our organic union with Christ from it"],
  discussion=["How does seeing Romans as a hospital instead of a courtroom change how you read it?",
    "What is the difference between earning salvation and cooperating with grace?",
    "Where do you need the Physician's healing in your own life right now?"],
  glance=dict(author="St. Paul the Apostle",
    written="c. 57 AD from Corinth, near the end of his third missionary journey",
    audience="The Christians in Rome — a church Paul had not founded",
    theme="Christ the Medhanit (Healer): the diagnosis, medicine, and recovery of sin-sick humanity"),
  terms=[("Justification", "In the Orthodox reading: not only a legal status but the healing and restoration of our broken nature in Christ."),
    ("Medhanit", "Savior / Healer — Christ as the Great Physician who restores human nature."),
    ("Synergy", "Cooperation between God's grace and our free response — faith working through love."),
    ("Sanctification", "The lifelong recovery and growth in holiness that follows baptism, led by the Holy Spirit.")],
  quiz=[("In the Oriental Orthodox reading of Romans, the controlling image is:",
     ["A courtroom", "A hospital", "A battlefield", "A marketplace"], 1),
    ("When St. Paul criticizes 'works of the Law,' he means:",
     ["All good deeds", "Acts of love and mercy", "Mosaic rituals such as circumcision", "Prayer and fasting"], 2),
    ("What do the 'Two Adams' of Romans 5 teach?",
     ["Adam had two sons", "The first Adam brought death; Christ the Second Adam brings life", "There were two creations", "Adam returned as Christ"], 1)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, "St. John Chrysostom, <em>Homilies on Romans</em> (as quoted in the lesson); St. Cyril of Alexandria's commentary tradition"],
  related=["book-of-acts","book-of-ephesians"]),

 dict(slug="book-of-ephesians", title="The Book of Ephesians",
  category="Scripture", audience="Youth & Young Adults", file="Ephesians_Lesson_Slides.pptx",
  summary="Ephesians reveals the mystery of the Church — the Body and Bride of Christ. Written from prison, St. Paul shows what God has already done (ch. 1–3), how the Church must live (4–5), and how believers stand in spiritual warfare (6). Salvation is not a private idea but a communal, living reality with Christ as the Head.",
  objectives=["Understand the Church as the living Body and beloved Bride of Christ",
    "See the structure: identity, then life, then warfare",
    "Explain grace in the Orthodox understanding — God's life and power that heals and transforms"],
  verses=["Ephesians 2:8 — \"For by grace you have been saved through faith\"",
    "Ephesians 4:1 — \"walk worthy of the calling with which you were called\"",
    "Ephesians 6:10–11 — \"Put on the whole armor of God\""],
  points=["A body without a head is a corpse — the Church lives only in union with Christ her Head",
    "The Bride image shows salvation as covenant love, not a legal transaction",
    "Chapters 1–3: you are adopted, redeemed, and sealed — before any command is given",
    "Grace does not cancel obedience; it creates and empowers it",
    "The armor of God is mostly defensive: the call is to stand and endure",
    "Salvation is new creation and union — a new humanity gathered into Christ"],
  discussion=["Why is it dangerous to treat faith as purely private and individual?",
    "What does it mean to 'walk worthy' of a calling you did not earn?",
    "Which piece of the armor of God do you most need right now, and why?"],
  glance=dict(author="St. Paul the Apostle",
    written="c. 60–62 AD, during his first imprisonment in Rome (a 'Prison Epistle')",
    audience="The church in Ephesus, and as an encyclical to the whole Body of Christ",
    theme="The mystery of the Church: the Body and Bride of Christ"),
  terms=[("Encyclical", "A letter intended to circulate among many churches, not just one congregation."),
    ("Body of Christ", "The Church as a living organism whose life flows from Christ the Head."),
    ("Grace", "God's own life and power given to heal and transform — creating obedience, not canceling it.")],
  quiz=[("The central revelation of Ephesians is:",
     ["The end times", "The Church — the Body and Bride of Christ", "The Ten Commandments", "The gifts of the Spirit"], 1),
    ("According to Ephesians 2:8, we are saved:",
     ["By our own works", "By grace through faith", "By knowledge", "By the Law"], 1),
    ("The armor of God in Ephesians 6 is mostly:",
     ["Offensive — for attacking", "Defensive — the call is to stand and endure", "Symbolic of Roman culture only", "For clergy only"], 1)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["book-of-colossians","book-of-philippians"]),

 dict(slug="book-of-philippians", title="The Book of Philippians",
  category="Scripture", audience="Youth & Young Adults", file="Philippians_Lesson_Slides.pptx",
  summary="A letter about joy written from chains. St. Paul teaches that joy is not the absence of pain but the presence of Christ: the mind of Christ and His self-emptying humility (ch. 2), pressing toward the prize (ch. 3), and the peace that guards hearts through prayer and thanksgiving (ch. 4).",
  objectives=["Learn how Paul found joy and purpose even in imprisonment",
    "Understand 'work out your salvation' as cooperation with grace (synergy)",
    "Practice the Philippians 4 pattern: rejoice, pray, give thanks, guard the mind"],
  verses=["Philippians 1:21 — \"For to me, to live is Christ, and to die is gain.\"",
    "Philippians 2:5–11 — the mind of Christ, who humbled Himself even to the cross",
    "Philippians 4:6–7 — prayer and thanksgiving, and the peace that guards the heart"],
  points=["Paul's prison became a platform — suffering itself became a witness",
    "The mind of Christ: humility is not weakness; it is the road to glory",
    "'Work out your salvation' means cooperating with the grace God is already working in you",
    "Pride can wear a religious costume — confidence in the flesh cannot replace Christ",
    "Citizenship in heaven shapes our choices on earth",
    "Contentment is learned in every season; strength in Christ is for faithfulness, not ego"],
  discussion=["What is stealing your joy right now, and what would it mean to find joy in Christ instead?",
    "Where is pride blocking peace in your relationships?",
    "How can complaining and arguing poison a church community — and what is the antidote?"],
  glance=dict(author="St. Paul the Apostle (with Timothy in the greeting)",
    written="c. 60–62 AD, during Paul's imprisonment",
    audience="The church in Philippi",
    theme="Joy is not the absence of pain but the presence of Christ"),
  terms=[("Kenosis", "Christ's self-emptying (Phil 2:7): taking the form of a servant, obedient even to death on the cross."),
    ("Synergy", "Working out our salvation as cooperation with the grace God works in us (Phil 2:12–13)."),
    ("Contentment", "Learned steadiness in every season — abundance or need — through Christ who strengthens (Phil 4:11–13).")],
  quiz=[("From where did St. Paul write Philippians?",
     ["A ship", "Prison", "Jerusalem", "Mount Sinai"], 1),
    ("'Work out your own salvation' (Phil 2:12) means:",
     ["Save yourself by effort", "Cooperate with the grace God is already working in you", "Salvation is uncertain", "Work harder than others"], 1),
    ("In Philippians, joy is:",
     ["The absence of pain", "A feeling for good days", "The presence of Christ", "A reward for the perfect"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["book-of-ephesians","book-of-colossians"]),

 dict(slug="book-of-colossians", title="The Book of Colossians",
  category="Scripture", audience="Youth & Young Adults", file="Colossians_Lesson_Slides.pptx",
  summary="Christ is supreme and Christ is enough. St. Paul warns the Colossians against every 'Christ + something' religion — extra rules, spiritual highs, human philosophies, or a reduced Christ — and calls the Church to stay rooted in the One in whom all the fullness of God dwells, putting sin to death and putting on holiness.",
  objectives=["Confess the supremacy of Christ: Creator, Sustainer, Head of the Church, fullness of God",
    "Recognize the four 'Christ +' distortions and how they appear today",
    "Apply Colossians 3: set the mind above, put off the old life, put on love"],
  verses=["Colossians 1:15–17 — the image of the invisible God; in Him all things consist",
    "Colossians 2:9–10 — \"in Him dwells all the fullness of the Godhead bodily; and you are complete in Him\"",
    "Colossians 3:14 — \"put on love, which is the bond of perfection\""],
  points=["Christ is Creator, not created; He holds everything together — including you",
    "Beware teachings that sound deep but quietly move Christ from the center",
    "Fasting and rules serve the faith; they must never replace humility, mercy, and love",
    "Holy Tradition is not the same as human tradition or cultural preference",
    "Reducing Christ to a moral teacher or the sacraments to mere symbols empties the faith",
    "Holiness is not only what you stop — it is what you become"],
  discussion=["What are some 'Christ + something else' teachings you have encountered?",
    "How can we honor fasting and tradition without turning them into the whole faith?",
    "What does 'if Christ is Lord, He is Lord of your Monday too' mean in your week?"],
  glance=dict(author="St. Paul the Apostle",
    written="During Paul's imprisonment (a 'Prison Epistle')",
    audience="The church in Colossae",
    theme="Christ's supremacy and sufficiency against every 'Christ + something' religion"),
  terms=[("Supremacy of Christ", "Christ as Creator, Sustainer, Head of the Church, and fullness of God (Col 1:15–18; 2:9)."),
    ("Holy Tradition", "The living faith handed down in the Church — distinct from human customs or outside philosophies."),
    ("Vain philosophy", "Teaching that sounds wise and spiritual but pulls believers away from Christ's sufficiency (Col 2:8).")],
  quiz=[("The big message of Colossians is:",
     ["Christ is supreme and sufficient", "The Law must be kept", "The end is near", "Spiritual gifts matter most"], 0),
    ("Which is an example of 'Christ + extra rules'?",
     ["Fasting with humility and love", "Treating perfect fasting as the whole faith while ignoring mercy and confession", "Attending the Liturgy", "Reading Scripture daily"], 1),
    ("Colossians 2:9 teaches that in Christ dwells:",
     ["A portion of God's wisdom", "All the fullness of the Godhead bodily", "The spirit of an angel", "Only divine power, not divinity"], 1)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["book-of-philippians","book-of-ephesians"]),

 dict(slug="intercession", title="Intercession of the Saints",
  category="Apologetics", audience="Youth & Young Adults", file="Intercession_Lesson_Slides.pptx",
  summary="Why the Ethiopian Orthodox Church asks for the prayers of the Holy Virgin Mary, the angels, and the saints. The lesson distinguishes Christ's unique propitiatory mediation from the intercessory prayer God Himself commands, walks through the biblical proofs (Abraham, Job, Moses), and answers the most common objections with Scripture.",
  objectives=["Distinguish Christ's propitiatory advocacy from the intercessory prayer of the righteous",
    "Present the Old and New Testament evidence that God asks for and honors intercession",
    "Answer the objection 'there is one Mediator' faithfully and charitably"],
  verses=["1 Timothy 2:5 — one Mediator in the propitiatory sense: Christ alone paid for sin",
    "Job 42:7–8 — \"my servant Job shall pray for you, for him I will accept\"",
    "Romans 15:30 — St. Paul asks the living faithful to strive with him in prayer"],
  points=["Christ alone is the propitiation for our sins — no saint shares in that",
    "God commanded Abimelech to seek Abraham's prayer and Job's friends to seek Job's",
    "Moses' intercession turned away wrath from Israel (Exodus 32)",
    "Death does not end this honor: God spares for David's sake long after David's repose",
    "The saints in heaven know more, not less — their knowledge is perfected (1 Cor 13:12)",
    "We do not worship the saints; we ask their prayers, as we ask our friends on earth"],
  discussion=["If you ask a friend to pray for you, why would you not ask a saint who stands before God?",
    "How does God honoring His saints actually glorify God Himself?",
    "How would you explain intercession gently to a Protestant friend?"],
  qa=[("\"There is one Mediator between God and men\" (1 Tim 2:5) — doesn't that rule out the saints?",
    "Christ's mediation is propitiatory — He alone paid for sin with His blood, and no saint shares in that. The saints' intercession is prayer, the same kind St. Paul asked of living believers (Rom 15:30). Asking prayer never replaces the one Redeemer."),
   ("How can the saints in heaven even hear us?",
    "Their knowledge is perfected, not erased: \"now we see through a glass, darkly; but then face to face\" (1 Cor 13:12). They know more in heaven, not less — and heaven rejoices over one sinner who repents (Luke 15:7)."),
   ("Isn't asking the saints' prayers worshiping them?",
    "No. Worship belongs to God alone. We honor the saints and ask their prayers exactly as we ask friends on earth to pray for us. God Himself honors them by accepting their prayers (Job 42:8; 1 Kings 11:12–13).")],
  terms=[("Intercession", "Prayer offered on behalf of another — commanded and honored by God throughout Scripture."),
    ("Propitiation", "The payment for sin. Christ alone is the propitiation for our sins (1 John 2:1–2)."),
    ("Theosis", "Becoming by grace what God is by nature — the goal of salvation, in which the saints already shine."),
    ("Mediator", "In the unique propitiatory sense, Christ alone; in the sense of praying for others, all the righteous.")],
  quiz=[("What kind of advocacy belongs to Christ ALONE?",
     ["Intercessory prayer", "Propitiatory advocacy — paying for sin by His blood", "Teaching", "Encouragement"], 1),
    ("What did God command Job's friends to do (Job 42)?",
     ["Offer sacrifices alone at home", "Go to Job, who would pray for them — and God would accept him", "Fast for forty days", "Make a pilgrimage"], 1),
    ("When we ask the saints for intercession, we are:",
     ["Worshiping them", "Replacing Christ", "Asking their prayers, as we ask friends on earth", "Doubting God's mercy"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["st-tekle-haimanot","st-luke"]),

 dict(slug="holy-cross", title="The Holy Cross: History, Significance, and Doctrine",
  category="Ethiopian Orthodox Tradition", audience="Youth & Young Adults", file="Holy_Cross_Lesson_Slides.pptx",
  week="Week 2",
  summary="How an instrument of Roman execution became the emblem of victory and salvation. The lesson tells of Queen Helena's finding of the True Cross and Constantine's vision, then shows the Cross in Orthodox dogma, in every sacrament, and in the daily life of the believer who signs themselves with it.",
  objectives=["Tell the history of the finding of the True Cross by Queen Helena",
    "Explain what the Cross testifies about the Incarnation and our redemption",
    "Practice the sign of the Cross with understanding, not habit alone"],
  verses=["1 Corinthians 1:18 — \"the message of the cross... to us who are being saved it is the power of God\"",
    "Galatians 6:14 — \"God forbid that I should boast except in the cross of our Lord\"",
    "Colossians 2:14–15 — the handwriting against us nailed to the cross"],
  points=["The Cross was transformed from a tool of shame into the banner of salvation",
    "Queen Helena, in her eighties, journeyed to Jerusalem and uncovered the True Cross",
    "Constantine's vision — 'By this sign you will conquer' — marked the Cross's public triumph",
    "The Cross confirms the Creed: God truly became man and tasted death in the flesh",
    "Every sacrament is sealed with the Cross — baptismal water, the 36 crosses of Chrismation",
    "The sign of the Cross is spiritual protection, reminding the demons of their defeat at Golgotha"],
  discussion=["Why do Orthodox Christians make the sign of the Cross so often?",
    "What does the Cross prove about who Christ is and what He took on for us?",
    "How is Meskel (the Finding of the True Cross) celebrated in the Ethiopian Church?"],
  timeline=[("c. 33 AD","The Crucifixion of our Lord at Golgotha — the Cross bears the Savior of the world"),
    ("312 AD","Emperor Constantine's vision: a radiant cross and the words 'By this sign you will conquer'"),
    ("c. 326–328 AD","Queen Helena journeys to Jerusalem and uncovers the True Cross"),
    ("Today","Meskel (Meskerem 17) — the Ethiopian Church celebrates the Finding of the True Cross with the Demera bonfire")],
  terms=[("Meskel", "The Ethiopian feast of the Finding of the True Cross (Meskerem 17), celebrated with the Demera bonfire."),
    ("True Cross", "The actual cross of the Crucifixion, uncovered by Queen Helena in Jerusalem."),
    ("Sign of the Cross", "The believer's act of blessing and protection, confessing the Crucified in body and soul."),
    ("Golgotha", "The place of the Crucifixion — where the Devil was defeated.")],
  quiz=[("Who uncovered the True Cross in Jerusalem?",
     ["Empress Theodora", "Queen Helena", "Queen Candace", "St. Mary Magdalene"], 1),
    ("What words accompanied Constantine's vision of the cross?",
     ["'Take up your cross'", "'By this sign you will conquer'", "'It is finished'", "'Come and see'"], 1),
    ("In Chrismation, how many crosses is the believer anointed with?",
     ["3", "12", "36", "40"], 2)],
  sources=[CIT_CURRICULUM + " — Week 2: The Holy Cross", CIT_SLIDES, CIT_SCRIPTURE, "Sayings of St. John Chrysostom and St. Athanasius as quoted in the lesson"],
  related=["holy-trinity","orthodox-fasting"]),

 dict(slug="orthodox-fasting", title="The Purpose and Practice of Fasting",
  category="Fasting", audience="Youth & Young Adults", file="Orthodox_Fasting_Lesson_Slides.pptx",
  week="Week 22",
  summary="Fasting begins in Eden: the very first commandment concerned eating. This lesson traces the shift from the original plant-based diet to meat after the Flood, explains why we fast — to return toward the original state, to purify body and soul, and to grow through self-denial — and surveys the seven fasts of the Orthodox Church.",
  objectives=["Connect fasting to God's first command in the Garden",
    "Explain the spiritual purposes of fasting beyond food rules",
    "Know the seven fasts of the Church and what each remembers"],
  verses=["Genesis 2:16–17 — the first command about eating",
    "Matthew 4:2 — our Lord fasted forty days and forty nights",
    "Joel 2:12 — \"Turn to Me with all your heart, with fasting, with weeping\""],
  points=["The first test of obedience in Eden involved food — fasting reverses Adam's grasping",
    "Fasting is a return toward the pure state of humanity before the Fall",
    "Fasting purifies the body and soul together; it is never mere dieting",
    "Suffering and self-denial, rightly carried, become perseverance and growth",
    "Wednesday remembers the betrayal; Friday remembers the Crucifixion",
    "The Church gives seven fasts as a school of the spiritual life"],
  discussion=["Why is fasting about the heart and not only about food?",
    "Which of the seven fasts do you keep now, and which could you grow into?",
    "How does fasting train us to say no to other temptations?"],
  challenge=["This week, keep the Wednesday and Friday fasts with attention, not autopilot",
    "At one meal you give up, add the prayer you usually skip",
    "Learn the names of the seven fasts of the Church and what each remembers",
    "Pair the fast with mercy: one concrete act of kindness or giving",
    "Ask your father confessor how to grow into the longer fasts"],
  terms=[("Tsom", "Fast / fasting — the Church's school of self-denial, prayer, and return to God."),
    ("Abiy Tsom", "The Great Lent — the longest and most solemn fast, preparing for the Feast of the Resurrection."),
    ("Filseta", "The Fast of the Assumption of St. Mary, beloved especially in the Ethiopian Church."),
    ("Asceticism", "Spiritual training through self-denial — for love of God, never for pride.")],
  quiz=[("What did God's very first commandment to mankind concern?",
     ["Worship", "Eating", "Work", "Marriage"], 1),
    ("Why do we fast on Wednesdays and Fridays?",
     ["They are quiet days", "Wednesday remembers the betrayal of Judas; Friday the Crucifixion", "They were market days", "The apostles chose them at random"], 1),
    ("Fasting in the Orthodox understanding is:",
     ["A diet for health", "Punishment for sin", "Purification of body and soul and a return toward Eden", "Optional for the young"], 2)],
  sources=[CIT_CURRICULUM + " — Week 22: Church Fasts", CIT_SLIDES, CIT_SCRIPTURE],
  related=["guarding-time-senses","penance"]),

 dict(slug="penance", title="The Sacrament of Penance",
  category="Sacraments", audience="Youth & Young Adults", file="Penance_Lesson_Slides.pptx",
  summary="Penance is the sacrament by which a baptized believer who has fallen into sin returns to God through sincere repentance, confession before a priest, and absolution. The lesson covers why we need penance, how Christ instituted it, how it works, how to prepare for confession, and the assurance that all sins sincerely repented can be forgiven.",
  objectives=["Define the Sacrament of Penance and its purpose",
    "Show from Scripture how Christ gave the authority to bind and loose",
    "Learn how to prepare for confession and why it precedes Holy Communion"],
  verses=["Matthew 16:19 — \"whatever you bind on earth shall be bound in heaven\"",
    "Malachi 3:7 — \"Return to Me, and I will return to you\"",
    "Isaiah 1:18 — \"Though your sins are like scarlet, they shall be as white as snow\""],
  points=["Sin separates us from God — as Adam and Eve hid in the Garden",
    "Penance restores the relationship, like the Prodigal Son returning to the Father",
    "Christ instituted penance, giving the apostles authority to bind and loose",
    "The penitent repents, resolves to change, confesses to a priest, and receives absolution",
    "We examine our conscience and pray Psalm 139:23 before confession",
    "Penance prepares us to receive Holy Communion worthily (1 Cor 11:28)"],
  discussion=["Why does confession before a priest help us more than confessing 'privately' alone?",
    "What is the difference between feeling guilty and true repentance?",
    "Why must we examine ourselves before approaching the Eucharist?"],
  signgrace=dict(
    sign=["Sincere confession of sins before the priest",
      "The priest's prayer of absolution",
      "Spiritual counsel and, where needed, a healing discipline (epitimia)"],
    grace=["Forgiveness of the sins confessed with true repentance",
      "Reconciliation with God and with His Church",
      "Strength of grace to resist the same sins",
      "A clean heart prepared for Holy Communion"]),
  terms=[("Absolution", "The loosing of sins through the priest's prayer, by the authority Christ gave (Matt 16:19; John 20:23)."),
    ("Confession", "Naming our sins sincerely before God in the presence of His priest."),
    ("Epitimia", "A spiritual discipline given by the confessor — medicine for healing, not punishment."),
    ("Father Confessor (Yenefs Abat)", "The priest who hears confession and shepherds the soul's healing.")],
  quiz=[("The Sacrament of Penance is:",
     ["A yearly ritual only", "The believer's return to God through repentance, confession, and absolution", "Only for grave sinners", "A replacement for baptism"], 1),
    ("Where does Christ give the authority of binding and loosing?",
     ["Genesis 3", "Psalm 51", "Matthew 16:19", "Revelation 1"], 2),
    ("Why does penance come before Holy Communion?",
     ["Church habit", "To receive the Eucharist worthily, in a state of grace (1 Cor 11:28)", "To make the line shorter", "It is optional"], 1)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, CIT_DAOUD],
  related=["holy-matrimony","orthodox-fasting"]),

 dict(slug="holy-matrimony", title="The Sacrament of Holy Matrimony",
  category="Sacraments", audience="Youth & Young Adults", file="Holy_Matrimony_Lesson_Slides.pptx",
  summary="Holy Matrimony is the sacrament through which bridegroom and bride are united and granted divine grace that sanctifies their union, making it like the unity of Christ and His Church. The lesson covers its institution in both Testaments, its divine goals, the outward signs and invisible grace, and the obligations of husband and wife.",
  objectives=["Define Matrimony as a sacrament, not merely a contract or ceremony",
    "Trace its institution from Genesis through Christ's teaching",
    "Understand the outward signs and the invisible grace of the sacrament"],
  verses=["Genesis 1:27–28 — male and female He created them; be fruitful and multiply",
    "Matthew 19:4–6 — \"what God has joined together, let not man separate\"",
    "Ephesians 5:25 — \"Husbands, love your wives, just as Christ also loved the church\""],
  points=["Marriage was instituted by God in Eden and sealed by Christ as a sacrament",
    "Its goals: the growth of mankind, mutual help, and a holy guard against temptation",
    "Every sacrament has an outward sign and an invisible grace",
    "The grace of Matrimony sanctifies the union as Christ's unity with the Church",
    "Both spouses must be Christians within the Orthodox Church for the sacrament",
    "Matrimony is performed in the Church; faithfulness and unity follow it for life"],
  discussion=["What makes Orthodox marriage different from a civil wedding?",
    "Why does St. Paul compare marriage to Christ and the Church?",
    "How should young people prepare now for a holy marriage later?"],
  signgrace=dict(
    sign=["The vows of bridegroom and bride before the priest",
      "The prayers and blessing of the Church",
      "The crowning and the visible rites of the wedding service"],
    grace=["Sanctification of the union, making it spiritual and perfect",
      "Unity of husband and wife as one flesh, unseparated — as Christ's unity with the Church is everlasting",
      "Divine help to remain faithful and to raise children in the faith"]),
  terms=[("Sacrament (Mystery)", "A holy act through which invisible divine grace is given by means of a visible sign."),
    ("Outward Sign", "What we can see and hear in a sacrament — words, actions, and elements."),
    ("Invisible Grace", "The real divine gift granted through the sacrament, beyond what eyes can see."),
    ("Crowning", "The visible rite of Orthodox marriage, crowning the couple into their new life in Christ.")],
  quiz=[("In the sacrament of Matrimony, the union of husband and wife mirrors:",
     ["A business partnership", "Christ's unity with His Church", "The unity of the apostles", "Angelic life"], 1),
    ("Where was marriage first instituted?",
     ["At Cana", "In the Law of Moses", "By God in Eden (Genesis 1–2)", "By the apostles"], 2),
    ("What is required for the sacrament of Matrimony?",
     ["A civil license only", "Both spouses Christians within the Orthodox Church, joined in the Church", "Only the groom's consent", "A long engagement"], 1)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE, CIT_DAOUD, CIT_CURRICULUM],
  related=["penance","iron-sharpens-iron"]),

 dict(slug="st-tekle-haimanot", title="The Life of Saint Tekle Haimanot",
  category="Saints", audience="Youth & Young Adults", file="St_Tekle_Haimanot_Lesson_Slides.pptx",
  summary="The great Ethiopian saint whose name means 'Plant of Faith' — monk, hermit, missionary, and founder of Debre Libanos. The lesson follows his birth to righteous parents after years of barrenness, his call by the Archangel Michael, the miracle of the six wings at Debre Damo, his evangelization of pagan Damot, and his final vow of standing in prayer for seven years.",
  objectives=["Tell the life of St. Tekle Haimanot from childhood to repose",
    "Explain his mission to Damot and the founding of Debre Libanos (c. 1284)",
    "Draw lessons from his union of apostolic mission and ascetic devotion"],
  verses=["Psalm 1:3 — \"like a tree planted by the rivers of water\"",
    "Matthew 19:21 — \"If you want to be perfect, go, sell what you have... and come, follow Me\"",
    "2 Timothy 4:7 — \"I have fought the good fight, I have finished the race\""],
  points=["Born to Priest Tsega Ze'ab and Egzi'e Haraya after years of faithful prayer",
    "Called as a young deacon by the Archangel Michael to renounce the world",
    "Given six wings when the rope broke at Debre Damo — apostle and ascetic in one",
    "Evangelized the pagan kingdom of Damot, beginning with its prince",
    "Founded Debre Libanos, the spiritual capital of Ethiopian monasticism",
    "Stood in prayer for seven years on one leg — the triumph of spirit over flesh"],
  discussion=["What does his name, 'Plant of Faith,' teach about how faith grows?",
    "Why did monasticism become so central to Ethiopian Christianity?",
    "What 'small vow' of discipline could you keep this month in his spirit?"],
  timeline=[("13th century","Born in Shewa to Priest Tsega Ze'ab and Egzi'e Haraya after years of barrenness and prayer"),
    ("Youth","Ordained deacon; called by the Archangel Michael to renounce the world"),
    ("Monastic years","Trained in the monasteries, including nine years at Debre Damo"),
    ("The descent","The rope breaks at the cliff of Debre Damo — six wings are given, and the mission south begins"),
    ("The mission","Evangelizes the pagan kingdom of Damot, beginning with its prince"),
    ("c. 1284","Founds Debre Libanos in Shewa — the spiritual capital of Ethiopian monasticism"),
    ("Final years","Stands in unceasing prayer for seven years; his repose follows soon after")],
  feast="His major commemoration is kept on Nehase 24 (his repose), with monthly remembrance on the 24th — confirm dates for parish celebration with your priest and the Synaxarium.",
  terms=[("Gädl", "The written 'spiritual combat' or life-story of a saint, e.g., the Gädlä Täklä Haymanot."),
    ("Debre Libanos", "The great monastery founded by St. Tekle Haimanot in Shewa, c. 1284."),
    ("Monasticism", "The consecrated life of prayer, fasting, and renunciation for the Kingdom of God."),
    ("Hermit", "A monk who withdraws into solitude for unceasing prayer.")],
  quiz=[("What does the name Tekle Haimanot mean?",
     ["Servant of God", "Plant of Faith", "Light of Ethiopia", "Son of the Covenant"], 1),
    ("Which great monastery did he found around 1284?",
     ["Debre Damo", "Debre Bizen", "Debre Libanos", "Debre Tabor"], 2),
    ("What was his final great ascetic vow?",
     ["Forty days of silence", "A pilgrimage to Jerusalem", "Standing in prayer for seven years", "Fasting from bread for a year"], 2)],
  sources=[CIT_SYNAXARIUM, CIT_SLIDES, CIT_SCRIPTURE,
    "St. Takla Haymanot resources at <a href=\"https://copticcrew.com/pages/st-takla-haymanot\">copticcrew.com</a> (as cited in the lesson slides)"],
  related=["early-church-fathers","intercession"]),

 dict(slug="st-luke", title="The Life and Legacy of St. Luke the Apostle",
  category="Saints", audience="Youth & Young Adults", file="St_Luke_Lesson_Slides.pptx",
  week="Week 14",
  summary="St. Luke — the beloved physician, evangelist, companion of St. Paul, and according to tradition the first iconographer. The lesson surveys his Gospel's unique parables and miracles, his authorship of Acts, and his martyrdom under Nero after a life poured out in preaching.",
  objectives=["Know who St. Luke was: Gentile convert, physician, evangelist, historian",
    "Identify what is unique to the Gospel of Luke",
    "Tell how his witness continued through Acts and unto martyrdom"],
  verses=["Colossians 4:14 — \"Luke the beloved physician\"",
    "Luke 1:3 — \"it seemed good to me also... to write to you an orderly account\"",
    "Luke 15 — the parables of the lost sheep, the lost coin, and the prodigal son"],
  points=["Not one of the Twelve, yet a tireless apostle and the historian of the early Church",
    "His Gospel traces Christ's lineage back to Adam — salvation for all humanity",
    "Only Luke records the widow of Nain, the Prodigal Son, and the Good Samaritan",
    "He gives the most detailed account of the Nativity and of St. Mary's song",
    "Acts is his second volume — the Spirit's work through the apostles",
    "He continued preaching in Rome after Sts. Peter and Paul were martyred, until his own martyrdom"],
  discussion=["What does St. Luke's careful research teach us about faith and truth?",
    "Why do the 'mercy parables' appear only in Luke — what does that show about his heart?",
    "How can your profession, like Luke's medicine, serve the Gospel?"],
  timeline=[("Early life","A Gentile physician — \"Luke the beloved physician\" (Col 4:14)"),
    ("Discipleship","Counted among the Seventy-Two; ministers alongside the Apostles"),
    ("The Gospel","Writes an orderly, well-researched account of the Lord's life, tracing His lineage to Adam"),
    ("Acts","Writes the Acts of the Apostles — the continuation of his Gospel"),
    ("After Peter & Paul","Continues preaching in Rome after their martyrdom, leading many to Christ"),
    ("Martyrdom","Reported to Nero by idol worshippers; receives the crown of martyrdom")],
  feast="The parish curriculum references the Synaxarium entry for St. Luke at Tahisas 22 (December 31); Budge's translation also recounts his martyrdom under Ṭeqemt — confirm the date for parish celebration with your priest and the Synaxarium.",
  terms=[("Evangelist", "A writer of one of the four Holy Gospels."),
    ("The Seventy-Two", "The wider circle of disciples sent by the Lord (Luke 10); tradition counts St. Luke among them."),
    ("Iconographer", "A painter of holy icons; tradition remembers St. Luke as the first, painting the Theotokos.")],
  quiz=[("What was St. Luke's profession?",
     ["Fisherman", "Tax collector", "Physician", "Tentmaker"], 2),
    ("Which two New Testament books did St. Luke write?",
     ["Luke and Revelation", "Luke and Acts", "Luke and Hebrews", "Acts and James"], 1),
    ("To whom does Luke's genealogy trace the Lord's lineage?",
     ["Abraham", "David", "Moses", "Adam"], 3)],
  sources=[CIT_CURRICULUM + " — Week 14: St. Luke the Apostle (references Synaxarium, Tahisas 22)", CIT_SYNAXARIUM, CIT_SLIDES, CIT_SCRIPTURE],
  related=["book-of-acts","st-tekle-haimanot"]),

 dict(slug="guarding-time-senses", title="Guarding Our Time and Senses: Using Media Wisely",
  category="Moral & Spiritual Life", audience="Youth", file="Guarding_Time_And_Senses_Lesson_Slides.pptx",
  week="Weeks 32 & 34",
  summary="Media shapes our thoughts, habits, and desires — and our senses are gates to the soul. This lesson teaches discernment: media as a constructive tool versus a destructive influence, the preciousness of time as God's unrepeatable gift, a Christian media filter, and the 7-Day Guard Your Time challenge.",
  objectives=["Understand the senses as spiritual gates and media's power over the heart",
    "Apply a Christian filter to what we watch, hear, and scroll",
    "Treat time as a sacred gift: give God the first and best, not the leftovers"],
  verses=["Ephesians 5:16 — \"redeeming the time, because the days are evil\"",
    "Proverbs 4:23 — \"Keep your heart with all diligence\"",
    "1 Corinthians 6:12 — \"All things are lawful for me, but all things are not helpful\""],
  points=["Media is not always bad — the issue is how we use it and what we let it do to the soul",
    "What enters the eyes and ears settles in the heart",
    "Ask not only 'Is this allowed?' but 'Is this beneficial? Is this pure? Does it help my salvation?'",
    "Money can be regained; lost time can never be brought back",
    "Do not give God the weakest part of your day",
    "Technology should be a servant, never a master"],
  discussion=["What type of media wastes the most time for young people today?",
    "Why is it dangerous to say 'it is just entertainment'?",
    "When, where, how, and for how long will you meet with God this week?"],
  challenge=["Limit unnecessary screen time each day this week",
    "Avoid one type of content that weakens your purity",
    "Spend at least 10 minutes daily in prayer",
    "Replace one scrolling session with Scripture or a spiritual book",
    "At week's end, take the Screen-Time Test: compare your time with God to your time on entertainment"],
  terms=[("Watchfulness (Nipsis)", "The sober guarding of heart and senses taught by the Fathers — spiritual alertness."),
    ("Redeeming the time", "Using the unrepeatable gift of time purposefully for God (Eph 5:16)."),
    ("Gates of the soul", "The senses — what we watch, hear, and touch enters and shapes the heart.")],
  quiz=[("In this lesson, the senses are described as:",
     ["Harmless tools", "Gates to the soul", "Obstacles to faith", "Private matters"], 1),
    ("Besides 'Is this allowed?', what should a Christian ask about media?",
     ["Is it popular?", "Is it new?", "Is it beneficial, pure, and helping my salvation?", "Is it free?"], 2),
    ("Which can never be regained once lost?",
     ["Money", "Possessions", "Time", "Reputation"], 2)],
  sources=[CIT_CURRICULUM + " — Week 32: TV and The Internet; Week 34: The Value of Time", CIT_MALATY_GROW, CIT_MALATY_DEVIL, CIT_SLIDES, CIT_SCRIPTURE],
  related=["patience","iron-sharpens-iron"]),

 dict(slug="iron-sharpens-iron", title="Iron Sharpens Iron",
  category="Moral & Spiritual Life", audience="Youth", file="Iron_Sharpens_Iron_Lesson_Slides.pptx",
  summary="\"As iron sharpens iron, so one person sharpens another\" (Proverbs 27:17). A youth lesson on why we were designed for community, not isolation: the power of our words, the patience to love difficult people, and the call to uplift others with compassion over judgment.",
  objectives=["See that nothing extraordinary is built alone — we were designed for one another",
    "Take seriously the power of words for death and life",
    "Choose compassion over judgment in daily relationships"],
  verses=["Proverbs 27:17 — \"As iron sharpens iron, so a man sharpens the countenance of his friend\"",
    "Proverbs 18:21 — \"Death and life are in the power of the tongue\"",
    "Ecclesiastes 4:9–10 — \"Two are better than one... woe to him who is alone when he falls\""],
  points=["No one is a one-man army — Rome was not built alone",
    "Family, friendship, and church are God's design for sharpening us",
    "People are difficult because people are real — love takes time, energy, and sacrifice",
    "'Sticks and stones' is a misconception: words wound and words heal",
    "We are what we repeatedly do — identity is built from habits",
    "Do not look down on anyone unless you are reaching down to lift them up"],
  discussion=["Who has sharpened you the most in your life, and how?",
    "When did someone's words build you up or tear you down?",
    "What would 'compassion over judgment' look like at school this week?"],
  challenge=["Each day this week, say one sentence that builds someone up",
    "Catch yourself once a day before a harsh word — and replace it",
    "Reach out to one person you have been avoiding because they are 'difficult'",
    "Write down one habit you repeat daily — ask if it is sharpening you or dulling you"],
  terms=[("Fellowship", "The shared life of believers who sharpen one another in love."),
    ("Compassion", "Stepping into another's shoes; the love that kills judgment.")],
  quiz=[("\"As iron sharpens iron...\" — where is this verse found?",
     ["Psalm 23", "Proverbs 27:17", "Matthew 5", "Romans 12"], 1),
    ("Proverbs 18:21 teaches that the tongue holds:",
     ["Wisdom and folly", "Death and life", "Silver and gold", "Blessing only"], 1),
    ("What does the lesson say defeats judgment?",
     ["Silence", "Distance", "Compassion", "Debate"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["patience","guarding-time-senses"]),

 dict(slug="patience", title="Patience",
  category="Moral & Spiritual Life", audience="Youth", file="Patience_Lesson_Slides.pptx",
  summary="\"Wait patiently for the Lord. Be brave and courageous\" (Psalm 27:14). A short youth lesson on why nothing good happens overnight: the patience of Moses, Abraham, and Noah, and patience as the testing period in which God develops who you need to become.",
  objectives=["Understand patience as part of how God forms us",
    "Learn from the patience of Moses, Abraham, and Noah",
    "Reframe waiting seasons as development, not delay"],
  verses=["Psalm 27:14 — \"Wait patiently for the Lord. Be brave and courageous.\"",
    "2 Peter 3:8–9 — one day is as a thousand years; the Lord is not slack concerning His promise",
    "James 1:3–4 — the testing of your faith produces patience"],
  points=["Rome was not built in a day — nothing good happens overnight",
    "Moses waited forty years in the wilderness; Abraham received Isaac at one hundred",
    "Noah waited a hundred and fifty days for the waters to recede",
    "Patience is one of life's greatest teachers",
    "Waiting is a testing period in which you become the person who can carry the blessing",
    "God's timing is not slowness but mercy (2 Peter 3:9)"],
  discussion=["What are you waiting for right now, and how are you waiting?",
    "Why does God often make His saints wait?",
    "What could you build in yourself during this waiting season?"],
  challenge=["Memorize Psalm 27:14 this week",
    "Name one thing you are waiting for — pray about it daily instead of worrying",
    "Practice one small act of patience each day (in traffic, in line, with a sibling)",
    "Journal: what is God building in you during this wait?"],
  terms=[("Long-suffering", "The patient endurance that Scripture counts among the fruit of the Spirit (Gal 5:22)."),
    ("Providence", "God's wise care ordering all things — including the timing we do not choose.")],
  quiz=[("Psalm 27:14 calls us to:",
     ["Hurry and act", "Wait patiently for the Lord, with bravery and courage", "Avoid hard things", "Trust only ourselves"], 1),
    ("How old was Abraham when Isaac was born?",
     ["70", "85", "100", "120"], 2),
    ("According to 2 Peter 3:9, the Lord's apparent delay is:",
     ["Forgetfulness", "Slackness", "Patience — not willing that any should perish", "A test with no purpose"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["iron-sharpens-iron","guarding-time-senses"]),

 dict(slug="love-forgiveness", title="Love and Forgiveness: The Transforming Cycle of Grace",
  category="Moral & Spiritual Life", audience="Youth & Young Adults", file="Love_And_Forgiveness_Lesson_Slides.pptx",
  summary="From the Fall to the Cross to a transformed life: how the Fall grieved the heart of a loving Father, how God's plan of salvation answered the dilemma of the unholy living with the Holy, what our forgiveness cost Christ, and why forgiving others is the prerequisite for receiving God's mercy ourselves.",
  objectives=["See the Fall as a broken communion that grieved God's fatherly love, not merely a broken rule",
    "Understand the Cross as God's answer to the dilemma: how can the unholy live with the Holy?",
    "Practice forgiveness of others as the prerequisite for asking God's forgiveness"],
  verses=["Genesis 3:9 — \"Where are you?\" — the Father seeking His hidden children",
    "John 3:16 — \"For God so loved the world that He gave His only begotten Son\"",
    "Matthew 6:14–15 — \"if you forgive men their trespasses, your heavenly Father will also forgive you\"",
    "1 John 4:7 — \"let us love one another, for love is of God\""],
  points=["The Fall was a spiritual separation — God's children hiding, blaming, and exiled from communion",
    "Even in the moment of judgment, God's love provided a path back — He never abandoned His children",
    "Our tradition treasures God's promise to Adam of salvation after 5,500 years — love deferred is not love denied",
    "Love is constant, not conditional — and therefore love inevitably carries suffering, as a mother's love does",
    "Our forgiveness cost Christ everything: the agony of Gethsemane, the Cross, the full weight of every sin",
    "Before asking God to forgive you, forgive your neighbor — mercy received is tied to mercy given",
    "The goal is not only to be forgiven but to be transformed: to learn God's nature, experience it, and emulate it"],
  discussion=["Why does it matter that the Fall hurt God as a Father, not only offended Him as a Judge?",
    "Having seen the depth of His love, is His command to love too much to ask?",
    "Who do you need to forgive before you next ask God for forgiveness?"],
  challenge=["Before your prayers each night this week, name anyone you have not forgiven — and forgive them first",
    "Do one act of unearned kindness for someone who wronged you",
    "Memorize Matthew 6:14–15",
    "Reflect: which of love's faces (sympathy, forgiveness, understanding, patience, fair judgment) is weakest in you?"],
  terms=[("Grace", "God's own life and power freely given — undeserved, transforming, and received through the life of the Church."),
    ("Theosis", "Becoming like God by His grace — united with Him, never becoming God by nature."),
    ("The 5,500-year promise", "The Church's tradition of God's covenant with Adam: that after 5,500 years the Savior would come and restore him.")],
  quiz=[("In this lesson, the Fall of Adam and Eve is presented above all as:",
     ["A broken rule requiring punishment", "A broken communion that grieved a loving Father", "A myth with a moral", "Adam's problem alone"], 1),
    ("According to Matthew 6:14–15, receiving God's forgiveness is tied to:",
     ["Fasting strictly", "Our willingness to forgive others", "Public confession", "Good intentions"], 1),
    ("The goal of the Christian life in this lesson is:",
     ["Only to be forgiven", "To avoid punishment", "To be transformed — learning, experiencing, and emulating God's nature", "To feel loved"], 2)],
  sources=[CIT_SLIDES, CIT_SCRIPTURE],
  related=["penance","iron-sharpens-iron"]),

 dict(slug="great-lent", title="Great Lent and the Victory of the Resurrection",
  category="Fasting", audience="Whole Parish", file="Great_Lent_Lesson_Notes.docx", file_label="Lesson Notes (DOCX)",
  summary="A lesson for the season of Abiy Tsom and Fasika: the three phases of the journey — Great Lent, Holy Week, and the Feast of the Resurrection — followed by the fifty days of celebration until Pentecost. The Church is the hospital of the soul where we find the Body and Blood of Christ, and we, the youth, are her future.",
  objectives=["Know the three phases: Abiy Tsom (prepare, repent, fast, pray), Holy Week (walk with Christ to the Cross), and Fasika (celebrate His victory over death)",
    "Understand theosis rightly: united with God by grace, never becoming God by nature",
    "Receive the Church as the hospital of the soul and the Eucharist as the medicine of immortality"],
  verses=["1 Corinthians 15:54–57 — \"O Death, where is your sting? O Hades, where is your victory?\"",
    "John 6:56 — \"He who eats My flesh and drinks My blood abides in Me, and I in him\"",
    "1 John 2:6 — \"He who says he abides in Him ought himself also to walk just as He walked\""],
  points=["Great Lent is a long season of fasting, prayer, repentance, and self-denial preparing us for the Resurrection",
    "After Fasika we celebrate for fifty days until Pentecost; the Wednesday and Friday fasts are suspended",
    "The Oriental Orthodox Church is the apostolic Church preserved by the Apostles and Church Fathers",
    "St. Athanasius: \"God became man so that man could become god\" — by grace, never by nature",
    "The Church is a hospital that heals and transforms us through her traditions and Sacraments",
    "In Holy Communion we partake of Christ's true Body and Blood and share in His death and Resurrection",
    "We are the future of the Church — the baton was first handed to us by Christ Himself"],
  discussion=["Which phase of the Lenten journey is hardest for you, and why?",
    "What does it mean that the Church is a hospital rather than a courtroom?",
    "What is your role — deacon, mezemuran, student — in carrying the Church's legacy forward?"],
  challenge=["Keep the fast of the season with attention to prayer, not only food",
    "Attend Holy Week services and walk the journey with Christ deliberately",
    "Prepare for Communion through confession during the fast",
    "Invite one newcomer to the Friday theology class"],
  terms=[("Abiy Tsom", "The Great Fast (Great Lent) — the Church's longest fast, preparing for the Feast of the Resurrection."),
    ("Fasika", "The Feast of the Resurrection (Easter) — the victory of Christ over death."),
    ("Hosanna", "Palm Sunday — the Lord's entry into Jerusalem, opening Holy Week."),
    ("Pentecost", "The descent of the Holy Spirit fifty days after the Resurrection — the close of the paschal celebration.")],
  quiz=[("What are the three phases of the lesson's Lenten journey?",
     ["Advent, Christmas, Epiphany", "Great Lent, Holy Week, Fasika", "Fasting, almsgiving, pilgrimage", "Confession, Communion, Chrismation"], 1),
    ("St. Athanasius' saying, 'God became man so that man could become god,' means:",
     ["We become God by nature", "We become equal to God", "We are united with God by grace and grow into His likeness", "Only saints are saved"], 2),
    ("During the fifty days after Fasika:",
     ["The fasting becomes stricter", "The Wednesday and Friday fasts are suspended in celebration", "The Church closes", "A new fast begins immediately"], 1)],
  sources=[CIT_SLIDES.replace("Lesson slides", "Lesson notes"), CIT_SCRIPTURE, "St. Athanasius of Alexandria, <em>On the Incarnation</em> (the famous saying quoted in the lesson)"],
  related=["orthodox-fasting","holy-cross"]),
]

# Extra glossary entries beyond per-lesson terms
GLOSSARY_EXTRA = [
 ("Kidassie", "The Divine Liturgy of the Ethiopian Orthodox Tewahedo Church, in which the faith of the one united Christ is confessed and the Holy Eucharist is celebrated.", None),
 ("Synaxarium", "The Church's book of the saints, read according to the day of the year; the Ethiopic Synaxarium was translated by E. A. Wallis Budge as The Book of the Saints of the Ethiopian Church.", None),
 ("Oriental Orthodox", "The family of churches — Ethiopian, Eritrean, Coptic, Syriac, Armenian, and Indian — holding the first three Ecumenical Councils and the Miaphysite confession.", None),
 ("Deacon (Diakon)", "The first rank of the ordained ministry, serving at the altar and in teaching — as Dn Yonnas serves this class.", None),
 ("Eucharist", "The sacrament of the true Body and Blood of the one Christ, received in the Kidassie.", None),
]

CATEGORIES = sorted({l["category"] for l in LESSONS})
AUDIENCES = sorted({l["audience"] for l in LESSONS})
BY_SLUG = {l["slug"]: l for l in LESSONS}

VERSES_ROTATOR = [
 ("Study to shew thyself approved unto God, a workman that needeth not to be ashamed, rightly dividing the word of truth.", "2 Timothy 2:15"),
 ("Thy word is a lamp unto my feet, and a light unto my path.", "Psalm 119:105"),
 ("Hear, O Israel: The Lord our God, the Lord is one.", "Deuteronomy 6:4"),
 ("And the Word became flesh and dwelt among us.", "John 1:14"),
 ("Wait patiently for the Lord. Be brave and courageous.", "Psalm 27:14"),
 ("Redeeming the time, because the days are evil.", "Ephesians 5:16"),
 ("Ethiopia shall soon stretch out her hands unto God.", "Psalm 68:31"),
]

NAV_ITEMS = [("index.html","Home"),("start-here.html","Start Here"),("lessons.html","Lesson Library"),
             ("curriculum.html","Curriculum"),("glossary.html","Glossary"),("resources.html","Resources"),
             ("downloads.html","Download Center")]

# Verified external Oriental Orthodox resources (checked June 2026)
RESOURCES = [
 ("Official Ethiopian Orthodox Tewahedo Church", [
  ("The Ethiopian Orthodox Tewahedo Church (official site)", "https://www.ethiopianorthodox.org/english/indexenglish.html",
   "The Church's official English site: teachings, history, the Liturgy in English, sermons, and teaching materials for children."),
  ("The 81 Canonical Books of the EOTC", "https://www.ethiopianorthodox.org/english/canonical/books.html",
   "The official listing of the Church's biblical canon — 46 Old Testament and 35 New Testament books."),
  ("EOTC Patriarchate Head Office", "https://eotceth.org/",
   "The Patriarchate of the Ethiopian Orthodox Tewahedo Church in Addis Ababa."),
 ]),
 ("Sunday School & Teaching", [
  ("Mahibere Kidusan — EOTC Sunday School Department", "https://eotcmk.org/e/",
   "English lessons and articles from Mahibere Kidusan, serving under the Sunday Schools Department of the Holy Synod since 1991."),
  ("Mahibere Kidusan USA", "https://us.eotcmk.org/",
   "The US branch of Mahibere Kidusan, with youth and campus ministry resources in English."),
 ]),
 ("Scripture & the Saints", [
  ("The Orthodox Study Bible", "https://store.ancientfaith.com/orthodox-study-bible/",
   "The study Bible quoted in our parish curriculum — Septuagint-based Old Testament with commentary from the Church Fathers."),
  ("The Book of the Saints of the Ethiopian Church (Synaxarium)", "https://archive.org/details/bookofsaintsofet0001unse",
   "E. A. Wallis Budge's translation of the Ethiopic Synaxarium — the source for our saints' lessons."),
 ]),
 ("The Oriental Orthodox Family", [
  ("Coptic Orthodox Church Network", "https://www.copticchurch.net/",
   "Resources from our sister Church of Alexandria, including Fr. Tadros Y. Malaty's 'Introduction to the Coptic Orthodox Church.'"),
  ("Coptic Orthodox Diocese of the Southern United States", "https://www.suscopts.org/literature/literature.php",
   "Free doctrinal literature in English, and publisher of the Coptic Reader prayer app."),
  ("Fr. Tadros Yacoub Malaty — Books in English", "https://st-takla.org/books/en/fr-tadros-yacoub/index.html",
   "The full English library of Fr. Tadros Y. Malaty, whose works are cited in our media and time lesson — hosted with the author's permission."),
  ("The Agpeya — Book of Hours", "https://st-takla.org/Agpeya.html",
   "The Coptic Orthodox prayer book of the seven canonical hours, in English."),
 ]),
]

# Curriculum weeks (extracted from the Level V curriculum) -> taught lessons on this site
WEEK_TO_LESSON = {2: "holy-cross", 14: "st-luke", 19: "trinitarianism-monotheism",
                  22: "orthodox-fasting", 32: "guarding-time-senses", 34: "guarding-time-senses"}
with open(os.path.join(ROOT, "curriculum.json"), encoding="utf-8") as f:
    CURRICULUM = json.load(f)
# Levels I-IV (PreK-Grade 9), extracted from the parish's other curricula
with open(os.path.join(ROOT, "curricula_extra.json"), encoding="utf-8") as f:
    CURRICULA_EXTRA = json.load(f)
LEVEL_LABELS = {lv["key"]: lv["label"] for lv in CURRICULA_EXTRA}
LEVEL_SOURCES = {
 "level-1": "Level I (Pre-KG and KG)", "level-2": "Level II (Grade 2 to Grade 3)",
 "level-3": "Level III (Grade 4 to Grade 6)", "level-4": "Level IV (Grade 7 to Grade 9)",
}

import re as _re
def sg_name(l):
    return _re.sub(r'_Lesson_Slides\.pptx$|_Lesson_Notes\.docx$', '', l["file"]) + "_StudyGuide.pdf"

def theme(l): return THEMES[l["category"]]
def icon_svg(l): return ICONS[theme(l)["icon"]]

def page(title, body, depth=0, active=""):
    p = "../" * depth
    active_attr = ' class="active"'
    nav = "".join(
        f'<a href="{p}{href}"{active_attr if active==href else ""}>{label}</a>'
        for href, label in NAV_ITEMS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — {SITE_NAME}</title>
<link rel="stylesheet" href="{p}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="cross">&#9768; &#10016; &#9768;</div>
  <h1><a href="{p}index.html">{SITE_NAME}</a></h1>
  <p class="tagline">{TAGLINE}</p>
</header>
<nav class="site-nav">{nav}</nav>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="cross">&#10016;</div>
  <p>Lessons by Dn Yonnas &middot; {TAGLINE}</p>
  <p>Curriculum lessons follow the <em>Sunday School Curriculum in English, Level V</em>, compiled by Kesis Solomon Mulugeta Zewde (PhD).</p>
  <p>All teaching is offered in the faith of the Ethiopian Orthodox Tewahedo Church. Questions of doctrine should always be brought to your father confessor or parish priest.</p>
  <p>Glory be to the Father, the Son, and the Holy Spirit, one God. Amen.</p>
</footer>
</body>
</html>
"""

def chip(l):
    week = f'<span class="tag">{html.escape(l["week"])}</span>' if l.get("week") else ""
    return (f'<span class="cat-chip">{icon_svg(l)}{html.escape(l["category"])}</span>'
            f'<span class="tag">{html.escape(l["audience"])}</span>{week}')

def lesson_card(l, depth=0):
    p = "../" * depth
    t = theme(l)
    return f"""<div class="card" style="--accent:{t['color']}" data-title="{html.escape(l['title'].lower())}" data-category="{html.escape(l['category'])}" data-audience="{html.escape(l['audience'])}" data-summary="{html.escape(l['summary'].lower())}">
  <div class="meta">{chip(l)}</div>
  <h3><a href="{p}lessons/{l['slug']}.html">{html.escape(l['title'])}</a></h3>
  <p>{html.escape(l['summary'][:160])}&hellip;</p>
  <div class="links"><a href="{p}lessons/{l['slug']}.html">Read lesson</a> &middot; <a href="{p}downloads/{l['file']}" download>Download slides</a></div>
</div>"""

# ---------------------------------------------------------------
# Special sections per category
# ---------------------------------------------------------------
def special_section(l):
    kind = theme(l)["special"]
    if kind == "glance" and l.get("glance"):
        g = l["glance"]
        rows = "".join(f"<tr><td>{k}</td><td>{html.escape(v)}</td></tr>" for k, v in
                       [("Author", g["author"]), ("Written", g["written"]),
                        ("Audience", g["audience"]), ("Theme", g["theme"])])
        return f'<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>The Book at a Glance</h3><table class="glance">{rows}</table></div>'
    if kind == "signgrace" and l.get("signgrace"):
        s = l["signgrace"]
        sign = "".join(f"<li>{html.escape(x)}</li>" for x in s["sign"])
        grace = "".join(f"<li>{html.escape(x)}</li>" for x in s["grace"])
        return f'''<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>Outward Sign &amp; Invisible Grace</h3>
<div class="signgrace">
<div class="col"><h4>The Outward (Visible) Sign</h4><ul>{sign}</ul></div>
<div class="col"><h4>The Invisible Grace</h4><ul>{grace}</ul></div>
</div></div>'''
    if kind == "timeline" and l.get("timeline"):
        items = "".join(f'<li><span class="tl-label">{html.escape(a)}</span>{html.escape(b)}</li>' for a, b in l["timeline"])
        feast = f'<p class="feast-note">&#10016; {html.escape(l["feast"])}</p>' if l.get("feast") else ""
        title = "Life at a Glance" if l["category"] == "Saints" else "Timeline"
        return f'<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>{title}</h3><ul class="timeline">{items}</ul>{feast}</div>'
    if kind == "guardrails" and l.get("guardrails"):
        g = l["guardrails"]
        c = "".join(f"<li>{html.escape(x)}</li>" for x in g["confess"])
        r = "".join(f"<li>{html.escape(x)}</li>" for x in g["reject"])
        return f'''<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>Doctrinal Guardrails</h3>
<div class="guardrails">
<div class="col confess"><h4>&#10003; We Confess</h4><ul>{c}</ul></div>
<div class="col reject"><h4>&#10007; We Reject</h4><ul>{r}</ul></div>
</div></div>'''
    if kind == "qa" and l.get("qa"):
        blocks = "".join(f'''<div class="qa-block">
<div class="objection"><span class="label">Objection:</span>{html.escape(o)}</div>
<div class="answer"><span class="label">Answer:</span>{html.escape(a)}</div>
</div>''' for o, a in l["qa"])
        return f'<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>Objections &amp; Answers</h3>{blocks}</div>'
    if kind == "challenge" and l.get("challenge"):
        items = "".join(f"<li>{html.escape(x)}</li>" for x in l["challenge"])
        return f'''<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>This Week's Challenge</h3>
<div class="challenge"><strong>Put it into practice:</strong><ul>{items}</ul></div></div>'''
    return ""

def quiz_section(l):
    if not l.get("quiz"): return ""
    fields = ""
    for qi, (q, opts, ans) in enumerate(l["quiz"]):
        labels = "".join(
            f'<label><input type="radio" name="q{qi}" value="{oi}"> {html.escape(o)}</label>'
            for oi, o in enumerate(opts))
        fields += f'<fieldset data-answer="{ans}"><legend>{qi+1}. {html.escape(q)}<span class="result-tag"></span></legend>{labels}</fieldset>'
    n = len(l["quiz"])
    return f'''<div class="lesson-section quiz"><h3><span class="sicon">{icon_svg(l)}</span>Check Your Understanding</h3>
{fields}
<button class="btn" id="gradeBtn" type="button">Check Answers</button><span id="quizScore"></span>
<script>
document.getElementById('gradeBtn').addEventListener('click', function() {{
  var score = 0, sets = document.querySelectorAll('.quiz fieldset');
  sets.forEach(function(fs) {{
    var ans = fs.dataset.answer, sel = fs.querySelector('input:checked');
    var tag = fs.querySelector('.result-tag');
    fs.classList.remove('correct','incorrect');
    if (sel && sel.value === ans) {{ score++; fs.classList.add('correct'); tag.textContent = '✓ Correct'; }}
    else {{ fs.classList.add('incorrect'); tag.textContent = sel ? '✗ Try again' : '✗ No answer'; }}
  }});
  document.getElementById('quizScore').textContent = 'Score: ' + score + ' / {n}';
}});
</script>
</div>'''

def terms_section(l):
    if not l.get("terms"): return ""
    dl = "".join(f"<dt>{html.escape(t)}</dt><dd>{html.escape(d)}</dd>" for t, d in l["terms"])
    return f'<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>Key Terms</h3><dl class="terms">{dl}</dl></div>'

def sources_section(l):
    if not l.get("sources"): return ""
    items = "".join(f"<li>{s}</li>" for s in l["sources"])
    return f'<div class="lesson-section"><h3><span class="sicon">{icon_svg(l)}</span>Sources &amp; Citations</h3><ul>{items}</ul></div>'

def curriculum_links(l):
    weeks = LESSON_TO_WEEKS.get(l["slug"], [])
    if not weeks: return ""
    links = " &middot; ".join(
        f'<a href="../curriculum/week-{n}.html">Week {n}: '
        f'{html.escape(next(w["title"] for w in CURRICULUM if w["week"] == n))}</a>'
        for n in sorted(weeks))
    return f'<p class="meta">&#128214; Curriculum lesson text: {links}</p>'

def lesson_page(l):
    t = theme(l)
    objectives = "".join(f"<li>{html.escape(o)}</li>" for o in l["objectives"])
    verses = "".join(f'<div class="verse-block">{html.escape(v)}</div>' for v in l["verses"])
    points = "".join(f"<li>{html.escape(p)}</li>" for p in l["points"])
    disc = "".join(f"<li>{html.escape(d)}</li>" for d in l["discussion"])
    related = " &middot; ".join(
        f'<a href="{r}.html">{html.escape(BY_SLUG[r]["title"])}</a>'
        for r in l["related"] if r in BY_SLUG)
    body = f"""
<div style="--accent:{t['color']}">
<div class="lesson-head">
  <div class="meta">{chip(l)}</div>
  <h2>{html.escape(l['title'])}</h2>
  <p class="byline">By Dn Yonnas</p>
  <p>{html.escape(l['summary'])}</p>
  {curriculum_links(l)}
</div>
<div class="lesson-section">
  <h3><span class="sicon">{icon_svg(l)}</span>Lesson Objectives</h3>
  <ul>{objectives}</ul>
</div>
<div class="lesson-section">
  <h3><span class="sicon">{icon_svg(l)}</span>Key Bible Verses</h3>
  {verses}
</div>
{special_section(l)}
<div class="lesson-section">
  <h3><span class="sicon">{icon_svg(l)}</span>Main Teaching Points</h3>
  <ul>{points}</ul>
</div>
{terms_section(l)}
<div class="lesson-section">
  <h3><span class="sicon">{icon_svg(l)}</span>Discussion &amp; Reflection Questions</h3>
  <ul>{disc}</ul>
</div>
{quiz_section(l)}
<div class="download-box">
  <strong>Lesson Materials</strong><br>
  <a class="btn" href="../downloads/{l['file']}" download>&#11015; Download {l.get('file_label','Slides (PPTX)')}</a>
  <a class="btn secondary" href="../downloads/{sg_name(l)}" download>&#11015; Study Guide (PDF)</a>
  {"".join(f'<a class="btn secondary" href="../downloads/{ef}" download>&#11015; {elabel}</a>' for elabel, ef in l.get('extras', []))}
</div>
{sources_section(l)}
<div class="lesson-section">
  <h3><span class="sicon">{icon_svg(l)}</span>Related Lessons</h3>
  <p>{related}</p>
  <p><a href="../lessons.html">&larr; Back to the Lesson Library</a></p>
</div>
</div>
"""
    return page(l["title"], body, depth=1)

# ---------------------------------------------------------------
# index.html
# ---------------------------------------------------------------
featured = ["holy-trinity", "st-cyril", "orthodox-fasting"]
featured_cards = "\n".join(lesson_card(BY_SLUG[s]) for s in featured)
verses_json = json.dumps([{"t": v, "r": r} for v, r in VERSES_ROTATOR])
index_body = f"""
<div class="hero">
  <h2>Welcome to Our Digital Classroom</h2>
  <p>This website is the study hub for the theology class of our church. Here you will find every lesson we have taught — with summaries, key Bible verses, key terms, quizzes, discussion questions, and downloadable slides — organized so that students, parents, teachers, and deacons can study, review, and grow in the faith of the Ethiopian Orthodox Tewahedo Church.</p>
  <div class="verse-rotator" id="verseRotator"><span id="verseText"></span><span class="vref" id="verseRef"></span></div>
  <p style="margin-top:1rem;">
  <a class="btn" href="start-here.html">Start Here</a>
  <a class="btn secondary" href="lessons.html">Browse the Lesson Library</a>
  <a class="btn secondary" href="downloads.html">Download Center</a>
  </p>
</div>
<script>
(function() {{
  var verses = {verses_json};
  var start = new Date(new Date().getFullYear(), 0, 0);
  var day = Math.floor((new Date() - start) / 86400000);
  var v = verses[day % verses.length];
  document.getElementById('verseText').textContent = '\\u201C' + v.t + '\\u201D';
  document.getElementById('verseRef').textContent = '\\u2014 ' + v.r;
}})();
</script>
<div class="divider">&#10016; &#10016; &#10016;</div>
<h2 class="section-title">Featured Lessons</h2>
<div class="grid">
{featured_cards}
</div>
<div class="divider">&#10016; &#10016; &#10016;</div>
<h2 class="section-title">How to Use This Site</h2>
<div class="grid">
  <div class="card"><h3>For Students</h3><p>Open any lesson to review what was taught in class. Read the summary, look up the key verses, learn the key terms, and test yourself with the quiz at the bottom of each lesson.</p></div>
  <div class="card"><h3>For Parents</h3><p>Each lesson page shows exactly what your children are learning — the objectives, the Scriptures, and the teaching points — so you can continue the conversation at home.</p></div>
  <div class="card"><h3>For Teachers &amp; Deacons</h3><p>Download the full slide decks from the Download Center. Lessons drawn from the parish curriculum are marked with their week number, with sources cited on every page.</p></div>
</div>
"""

# ---------------------------------------------------------------
# lessons.html
# ---------------------------------------------------------------
cat_opts = "".join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in CATEGORIES)
aud_opts = "".join(f'<option value="{html.escape(a)}">{html.escape(a)}</option>' for a in AUDIENCES)
all_cards = "\n".join(lesson_card(l) for l in sorted(LESSONS, key=lambda x: (x["category"], x["title"])))
lessons_body = f"""
<h2 class="section-title">Lesson Library</h2>
<p>All {len(LESSONS)} lessons taught so far, organized by category. Use the search box or filters to find a lesson.</p>
<div class="filters">
  <input type="search" id="q" placeholder="Search lessons&hellip;">
  <label>Category
    <select id="cat"><option value="">All</option>{cat_opts}</select>
  </label>
  <label>Audience
    <select id="aud"><option value="">All</option>{aud_opts}</select>
  </label>
</div>
<div class="grid" id="lessonGrid">
{all_cards}
</div>
<p id="noResults">No lessons match your search. Try a different word or filter.</p>
<script>
(function() {{
  var q = document.getElementById('q'), cat = document.getElementById('cat'), aud = document.getElementById('aud');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#lessonGrid .card'));
  function apply() {{
    var term = q.value.trim().toLowerCase(), c = cat.value, a = aud.value, shown = 0;
    cards.forEach(function(el) {{
      var ok = (!term || el.dataset.title.indexOf(term) > -1 || el.dataset.summary.indexOf(term) > -1)
        && (!c || el.dataset.category === c)
        && (!a || el.dataset.audience === a);
      el.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    document.getElementById('noResults').style.display = shown ? 'none' : 'block';
  }}
  q.addEventListener('input', apply); cat.addEventListener('change', apply); aud.addEventListener('change', apply);
}})();
</script>
"""

# ---------------------------------------------------------------
# downloads.html
# ---------------------------------------------------------------
rows = "\n".join(
    f"""<tr><td><a href="lessons/{l['slug']}.html">{html.escape(l['title'])}</a></td><td>{html.escape(l['category'])}</td><td><a href="downloads/{l['file']}" download>{l.get('file_label','Slides')}</a></td><td><a href="downloads/{sg_name(l)}" download>Study Guide</a></td></tr>"""
    for l in sorted(LESSONS, key=lambda x: (x["category"], x["title"])))

LIBRARY = [
 ("Doctrine & Dogma", [
  ("Dogma_Kesis_Solomon.pdf", "Dogma — Kesis Solomon", "An overview of the unchanging dogmas of the Church."),
  ("We_Believe_In_One_God_Part1.pdf", "We Believe in One God — Part 1", "The oneness of God: God is one and has no partners."),
  ("We_Believe_In_One_God_Part2.pdf", "We Believe in One God — Part 2", "Continuing the doctrine of the oneness of God."),
  ("We_Believe_In_One_God_Part3.pdf", "We Believe in One God — Part 3", "Continuing the doctrine of the oneness of God."),
  ("We_Believe_In_One_God_Part4.pdf", "We Believe in One God — Part 4", "Continuing the doctrine of the oneness of God."),
  ("We_Believe_In_One_God_Part5.pdf", "We Believe in One God — Part 5", "Concluding the doctrine of the oneness of God."),
  ("Divinity_Of_Our_Lord_Jesus_Christ.pdf", "The Divinity of Our Lord Jesus Christ", "The scriptural witness that Christ is true God."),
  ("Divinity_Of_The_Holy_Spirit.pdf", "The Divinity of the Holy Spirit", "The scriptural witness that the Holy Spirit is true God."),
  ("EOTC_Doctrine_Virgin_Mary_And_Intercession.pdf", "The EOTC Doctrine on the Virgin Mary and Intercession", "The Church's official teaching on the Theotokos and the intercession of the saints."),
  ("EOTC_Our_Beliefs_And_Values.pdf", "EOTC — Our Beliefs and Values", "A summary of what the Ethiopian Orthodox Tewahedo Church believes and lives."),
 ]),
 ("The Sacraments", [
  ("Seven_Sacraments_Holy_Orders.pdf", "The Seven Sacraments: Holy Orders", "The sacrament of ordination — bishops, priests, and deacons."),
 ]),
 ("Handbooks", [
  ("Sunday_School_Students_Handbook.pdf", "Sunday School Students Handbook", "The parish handbook for Sunday School students."),
  ("Sunday_School_Parents_Handbook.pdf", "Sunday School Parents Handbook", "The parish handbook for parents."),
 ]),
]
lib_sections = ""
for sec_title, items in LIBRARY:
    lib_rows = "\n".join(
        f"""<tr><td><a href="downloads/library/{f}" download>{html.escape(t)}</a></td><td>{html.escape(d)}</td></tr>"""
        for f, t, d in items)
    lib_sections += f"""<h2 class="section-title">{sec_title}</h2>
<table class="dl"><tr><th>Document</th><th>About</th></tr>{lib_rows}</table>"""

downloads_body = f"""
<h2 class="section-title">Download Center</h2>
<p>Slides and a printable study guide for every lesson, plus the Parish Library of doctrinal documents below. Click any link to download.</p>
<table class="dl">
  <tr><th>Lesson</th><th>Category</th><th>Slides / Notes</th><th>Study Guide (PDF)</th></tr>
{rows}
</table>
<div class="divider">&#10016; &#10016; &#10016;</div>
<h2 class="section-title">The Parish Library</h2>
<p>Doctrinal and teaching documents from our parish's Sunday School program (from the parish course materials compiled under Kesis Solomon Mulugeta Zewde (PhD), Debre Nazareth St. Mary &amp; St. Gabriel EOTC). These are the Church's own teaching documents — excellent for deeper study and teacher preparation.</p>
{lib_sections}
"""

# ---------------------------------------------------------------
# glossary.html
# ---------------------------------------------------------------
gloss = {}
for l in LESSONS:
    for t, d in l.get("terms", []):
        if t not in gloss:
            gloss[t] = (d, l)
for t, d, _ in GLOSSARY_EXTRA:
    if t not in gloss:
        gloss[t] = (d, None)

entries = ""
current_letter = ""
for t in sorted(gloss.keys(), key=lambda s: s.lower()):
    d, src = gloss[t]
    letter = t[0].upper()
    if letter != current_letter:
        current_letter = letter
        entries += f'<h3 class="glossary-letter">{letter}</h3>'
    link = f' <span class="src">&mdash; from <a href="lessons/{src["slug"]}.html">{html.escape(src["title"])}</a></span>' if src else ""
    entries += f"<dt>{html.escape(t)}</dt><dd>{html.escape(d)}{link}</dd>"
glossary_body = f"""
<h2 class="section-title">Glossary of Key Terms</h2>
<p>Theological terms used across our lessons — from Ge'ez words of our Tewahedo heritage to the language of the Councils. Each entry links to the lesson where it is taught.</p>
<dl class="glossary">
{entries}
</dl>
"""

# ---------------------------------------------------------------
# start-here.html
# ---------------------------------------------------------------
PATH = [
 ("The Faith of the Church", "Begin with who God is — one God in three Persons — and who Christ is.",
  ["holy-trinity","trinitarianism-monotheism","st-cyril"]),
 ("The Story of the Church", "How the faith came down to us: the Fathers, the councils, and the Cross.",
  ["early-church-fathers","holy-cross"]),
 ("The Life of the Church", "The holy mysteries and disciplines that heal and feed the believer.",
  ["penance","holy-matrimony","orthodox-fasting","great-lent"]),
 ("The Scriptures", "Walk through the New Testament with the mind of the Church.",
  ["book-of-acts","book-of-romans","book-of-ephesians","book-of-philippians","book-of-colossians"]),
 ("The Saints and Their Prayers", "The cloud of witnesses who intercede for us and show us the way.",
  ["st-luke","st-tekle-haimanot","intercession"]),
 ("Living the Faith Daily", "Practical lessons for the spiritual life of a young Orthodox Christian.",
  ["love-forgiveness","guarding-time-senses","iron-sharpens-iron","patience"]),
]
stages = ""
for stage_title, stage_desc, slugs in PATH:
    links = " &middot; ".join(f'<a href="lessons/{s}.html">{html.escape(BY_SLUG[s]["title"])}</a>' for s in slugs)
    stages += f'<li><h3>{html.escape(stage_title)}</h3><p>{html.escape(stage_desc)}</p><p class="stage-lessons">{links}</p></li>'
start_body = f"""
<h2 class="section-title">Start Here: A Path Through the Lessons</h2>
<p>New to the class, or want to study in order? Follow this path. It moves from the foundations of the faith, through the story and life of the Church, into the Scriptures, the saints, and daily Christian living. Take your time — these lessons are meant to be prayed as much as studied.</p>
<ol class="path">
{stages}
</ol>
<div class="hero">
  <h3 style="color:var(--maroon);margin-top:0;">About These Lessons</h3>
  <p>Lessons marked with a week number follow our parish's general Sunday School class curriculum — the <em>Sunday School Curriculum in English, Level V (High School and College)</em>, compiled by Kesis Solomon Mulugeta Zewde (PhD) for Debre Nazareth St. Mary &amp; St. Gabriel EOTC — a full formation course that includes theology alongside the commandments, Scripture, and Christian living. Saints' lives draw on the Ethiopic Synaxarium (<em>The Book of the Saints of the Ethiopian Church</em>). Full citations appear at the bottom of every lesson page.</p>
</div>
"""

# ---------------------------------------------------------------
# curriculum pages
# ---------------------------------------------------------------
LESSON_TO_WEEKS = {}
for wk, slug in WEEK_TO_LESSON.items():
    LESSON_TO_WEEKS.setdefault(slug, []).append(wk)

def curriculum_body_html(w):
    """Render body paragraphs: '### X' -> subheading, '• ' runs -> lists."""
    out, ul = [], []
    def flush():
        nonlocal ul
        if ul:
            out.append("<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in ul) + "</ul>")
            ul = []
    for p in w["body"]:
        if p.startswith("### "):
            flush()
            out.append(f"<h4>{html.escape(p[4:])}</h4>")
        elif p.startswith("• "):
            ul.append(p[2:])
        else:
            flush()
            out.append(f"<p>{html.escape(p)}</p>")
    flush()
    return "\n".join(out)

def curriculum_week_page(w, level_label="Level V Curriculum", level_source="Level V (High School and College)", taught_map=True):
    n = w["week"]
    objectives = "".join(f"<li>{html.escape(o)}</li>" for o in w["objectives"])
    memory = "".join(f'<div class="verse-block">{html.escape(m)}</div>' for m in w["memory_verse"])
    refs = "".join(f"<li>{html.escape(r)}</li>" for r in w["references"])
    taught = ""
    if taught_map and n in WEEK_TO_LESSON:
        l = BY_SLUG[WEEK_TO_LESSON[n]]
        taught = (f'<div class="download-box"><strong>Taught in our class</strong><br>'
                  f'Dn Yonnas has taught this curriculum lesson — see '
                  f'<a href="../lessons/{l["slug"]}.html">{html.escape(l["title"])}</a> '
                  f'for the slides, quiz, and study material.</div>')
    body = f"""
<div class="lesson-head">
  <div class="meta"><span class="tag">{html.escape(level_label)}</span> <span class="tag">Week {n}</span></div>
  <h2>Week {n}: {html.escape(w['title'])}</h2>
  <p class="byline">From the Sunday School Curriculum in English, {html.escape(level_source)} — compiled by Kesis Solomon Mulugeta Zewde (PhD)</p>
</div>
<div class="lesson-section">
  <h3>Objectives</h3>
  <ul>{objectives}</ul>
</div>
<div class="lesson-section">
  <h3>Memory Verse</h3>
  {memory}
</div>
{taught}
<div class="lesson-section">
  <h3>Lesson Text</h3>
  {curriculum_body_html(w)}
</div>
<div class="lesson-section">
  <h3>References</h3>
  <ul>{refs}</ul>
  <p><em>Source:</em> Kesis Solomon Mulugeta Zewde (PhD), <em>Sunday School Curriculum in English, {html.escape(level_source)}</em>, Debre Nazareth St. Mary &amp; St. Gabriel Ethiopian Orthodox Tewahedo Church, St. Louis, MO — Week {n}.</p>
  <p><a href="../curriculum.html">&larr; Back to the Curriculum</a></p>
</div>
"""
    return page(f"Week {n}: {w['title']}", body, depth=1)

def week_card(w, href, week_tag, taught=False):
    obj = html.escape(w["objectives"][0]) if w["objectives"] else ""
    taught_link = ""
    if taught:
        l = BY_SLUG[WEEK_TO_LESSON[w["week"]]]
        taught_link = f'<br><a href="lessons/{l["slug"]}.html">Taught in class &rarr;</a>'
    return f"""<div class="card" data-title="{html.escape(w['title'].lower())}" data-summary="{obj.lower()}">
  <div class="meta"><span class="tag">{week_tag}</span>{'<span class="tag">Taught in class</span>' if taught else ''}</div>
  <h3><a href="{href}">{html.escape(w['title'])}</a></h3>
  <p>{obj}</p>
  <div class="links"><a href="{href}">Read the lesson</a>{taught_link}</div>
</div>"""

def curriculum_index():
    cards = "".join(
        week_card(w, f"curriculum/week-{w['week']}.html", f"Week {w['week']}", taught=w["week"] in WEEK_TO_LESSON)
        for w in CURRICULUM)
    level_sections = ""
    for lv in CURRICULA_EXTRA:
        lv_cards = "".join(
            week_card(w, f"curriculum/{lv['key']}-week-{w['week']}.html", f"Week {w['week']}")
            for w in lv["weeks"])
        level_sections += f"""
<div class="divider">&#10016; &#10016; &#10016;</div>
<h2 class="section-title">{html.escape(lv['label'])}</h2>
<div class="grid level-grid">{lv_cards}</div>"""
    body = f"""
<h2 class="section-title">The Parish Curriculum Library</h2>
<p>The complete Sunday School curricula of our parish for every age level, compiled by Kesis Solomon Mulugeta Zewde (PhD) — a full formation course of the Ten Commandments, Christian living, Scripture, the saints, Church fasts, and theology woven throughout. Each week includes objectives, a memory verse, the lesson text, and references. The search box covers all levels.</p>
<div class="filters">
  <input type="search" id="cq" placeholder="Search all curriculum weeks&hellip;">
</div>
<h2 class="section-title">Level V — High School &amp; College (our class)</h2>
<p>Weeks marked &ldquo;Taught in class&rdquo; link to the matching theology-class lesson with slides and a quiz.</p>
<div class="grid" id="weekGrid">
{cards}
</div>
{level_sections}
<p id="noResults">No weeks match your search.</p>
<script>
(function() {{
  var q = document.getElementById('cq');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.grid .card'));
  q.addEventListener('input', function() {{
    var term = q.value.trim().toLowerCase(), shown = 0;
    cards.forEach(function(el) {{
      var ok = !term || el.dataset.title.indexOf(term) > -1 || el.dataset.summary.indexOf(term) > -1;
      el.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    document.getElementById('noResults').style.display = shown ? 'none' : 'block';
  }});
}})();
</script>
"""
    return page("Curriculum", body, active="curriculum.html")

# ---------------------------------------------------------------
# write files
# ---------------------------------------------------------------
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

write("index.html", page("Home", index_body, active="index.html"))
write("start-here.html", page("Start Here", start_body, active="start-here.html"))
write("lessons.html", page("Lesson Library", lessons_body, active="lessons.html"))
write("glossary.html", page("Glossary", glossary_body, active="glossary.html"))
write("downloads.html", page("Download Center", downloads_body, active="downloads.html"))
def resources_page():
    sections = ""
    for title, items in RESOURCES:
        cards = "".join(
            f'''<div class="card"><h3><a href="{url}">{html.escape(name)}</a></h3><p>{html.escape(desc)}</p>
<div class="links"><a href="{url}">Visit &rarr;</a></div></div>'''
            for name, url, desc in items)
        sections += f'<h2 class="section-title">{html.escape(title)}</h2><div class="grid">{cards}</div><div class="divider">&#10016;</div>'
    body = f"""
<h2 class="section-title">On This Site</h2>
<div class="grid">
  <div class="card"><h3><a href="creed.html">The Nicene Creed</a></h3><p>The confession of faith we recite in every Kidassie, with links to the lessons that teach it.</p><div class="links"><a href="creed.html">Read &rarr;</a></div></div>
  <div class="card"><h3><a href="feasts-fasts.html">Feasts &amp; Fasts of the Church</a></h3><p>The seven fasts and the major feasts of our Lord, with Ethiopian and Gregorian dates.</p><div class="links"><a href="feasts-fasts.html">Read &rarr;</a></div></div>
</div>
<div class="divider">&#10016;</div>
<h2 class="section-title">Trusted Orthodox Resources</h2>
<p>A vetted collection of official and trustworthy Ethiopian Orthodox Tewahedo and Oriental Orthodox resources for deeper study. These are the kinds of sources our lessons draw from. As always, bring questions of doctrine to your father confessor or parish priest.</p>
{sections}
<div class="hero">
  <h3 style="color:var(--maroon);margin-top:0;">A Word of Guidance</h3>
  <p>Not everything online that calls itself &ldquo;Orthodox&rdquo; teaches the faith of the Ethiopian Orthodox Tewahedo Church. When studying from the internet, prefer official Church sources like those above, note whether a site is Oriental Orthodox (our family of churches) or from another tradition, and verify anything surprising with a priest before teaching it to others.</p>
</div>
"""
    return page("Resources", body, active="resources.html")

def creed_page():
    body = """
<h2 class="section-title">The Nicene Creed</h2>
<p>The Creed of the 318 Fathers of Nicaea (325 AD), completed at Constantinople (381 AD) — the confession of faith we recite in every Kidassie. Note that in the Orthodox confession the Holy Spirit proceeds <em>from the Father</em>; the Church does not accept the later Latin addition (&ldquo;and the Son&rdquo;). The wording below is a standard English rendering; for liturgical use, follow the translation in our parish service book.</p>
<div class="lesson-section">
<p>We believe in one God, the Father Almighty, Maker of heaven and earth, and of all things visible and invisible.</p>
<p>And in one Lord Jesus Christ, the only-begotten Son of God, begotten of the Father before all worlds; Light of Light, true God of true God, begotten, not made, being of one essence with the Father, by Whom all things were made; Who for us men and for our salvation came down from heaven, and was incarnate of the Holy Spirit and of the Virgin Mary, and became man; and He was crucified for us under Pontius Pilate, and suffered, and was buried; and the third day He rose again, according to the Scriptures; and ascended into heaven, and sits at the right hand of the Father; and He shall come again with glory to judge the living and the dead; Whose kingdom shall have no end.</p>
<p>And we believe in the Holy Spirit, the Lord, the Giver of Life, Who proceeds from the Father; Who with the Father and the Son together is worshipped and glorified; Who spoke by the prophets.</p>
<p>And we believe in one, holy, universal, and apostolic Church. We confess one baptism for the remission of sins; and we look for the resurrection of the dead, and the life of the world to come. Amen.</p>
</div>
<div class="lesson-section">
<h3>Study the Creed</h3>
<p>The Creed is taught across our lessons: <a href="lessons/holy-trinity.html">the Holy Trinity</a> (one essence, three Persons), <a href="lessons/trinitarianism-monotheism.html">Trinitarianism and Monotheism</a> (one God, three Hypostases), and <a href="lessons/st-cyril.html">St. Cyril of Alexandria</a> (the one incarnate Christ).</p>
</div>
"""
    return page("The Nicene Creed", body)

def feasts_page():
    body = """
<h2 class="section-title">Feasts &amp; Fasts of the Church</h2>
<p>A quick reference to the Church's calendar of feasting and fasting. Ethiopian calendar dates are given with their usual Gregorian equivalents; movable feasts depend on the date of Fasika each year. <strong>Always confirm this year's dates with the parish calendar and your priest</strong> — this page is a study aid, not a liturgical calendar.</p>

<h2 class="section-title">The Seven Fasts</h2>
<div class="lesson-section"><ul>
<li><strong>Wednesdays &amp; Fridays</strong> — kept year-round (except the fifty days after Fasika): Wednesday remembers the betrayal of the Lord; Friday, His Crucifixion.</li>
<li><strong>Abiy Tsom (the Great Lent)</strong> — the longest and most solemn fast, preparing for Holy Week and the Feast of the Resurrection.</li>
<li><strong>Tsome Nebiyat (the Fast of the Prophets / Advent)</strong> — preparing for the Nativity of our Lord.</li>
<li><strong>Tsome Hawaryat (the Fast of the Apostles)</strong> — following Pentecost, in the apostles' footsteps before their mission.</li>
<li><strong>Tsome Nineveh (the Fast of Nineveh)</strong> — three days, remembering Nineveh's repentance at the preaching of Jonah.</li>
<li><strong>Filseta (the Fast of the Assumption of St. Mary)</strong> — Nehase 1–16, beloved especially in the Ethiopian Church, ending with the feast of her Assumption.</li>
<li><strong>Gahad (the Eves of Nativity and Epiphany)</strong> — the vigil fasts before Genna and Timket.</li>
</ul>
<p>For the meaning and practice of fasting, see <a href="lessons/orthodox-fasting.html">our fasting lesson</a> and <a href="lessons/great-lent.html">the Great Lent lesson</a>.</p></div>

<h2 class="section-title">Major Feasts of Our Lord</h2>
<div class="lesson-section"><ul>
<li><strong>Genna (Nativity)</strong> — Tahsas 29 (January 7): the birth of our Lord in the flesh.</li>
<li><strong>Timket (Epiphany)</strong> — Tir 11 (January 19): the Baptism of our Lord in the Jordan and the revelation of the Holy Trinity.</li>
<li><strong>Hosanna (Palm Sunday)</strong> — movable: the Lord's entry into Jerusalem.</li>
<li><strong>Siklet (the Crucifixion, Good Friday)</strong> — movable: the saving Passion and Cross.</li>
<li><strong>Fasika (the Resurrection)</strong> — movable: the Feast of Feasts, Christ's victory over death.</li>
<li><strong>Erget (the Ascension)</strong> — movable, forty days after Fasika.</li>
<li><strong>Paraclete (Pentecost)</strong> — movable, fifty days after Fasika: the descent of the Holy Spirit.</li>
<li><strong>Debre Tabor (the Transfiguration)</strong> — Nehase 13 (August 19).</li>
<li><strong>Meskel (the Finding of the True Cross)</strong> — Meskerem 17 (September 27), with the Demera bonfire; see <a href="lessons/holy-cross.html">the Holy Cross lesson</a>.</li>
</ul></div>
"""
    return page("Feasts & Fasts", body)

write("creed.html", creed_page())
write("feasts-fasts.html", feasts_page())
write("resources.html", resources_page())
write("curriculum.html", curriculum_index())
for w in CURRICULUM:
    write(f"curriculum/week-{w['week']}.html", curriculum_week_page(w))
for lv in CURRICULA_EXTRA:
    for w in lv["weeks"]:
        write(f"curriculum/{lv['key']}-week-{w['week']}.html",
              curriculum_week_page(w, level_label=lv["label"],
                                   level_source=LEVEL_SOURCES[lv["key"]], taught_map=False))
for l in LESSONS:
    write(f"lessons/{l['slug']}.html", lesson_page(l))
print(f"\nDone: {6 + len(CURRICULUM) + len(LESSONS)} pages generated.")
