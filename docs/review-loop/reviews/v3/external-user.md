# External-User Review — v3 milestone package (BiteFlow)

**Reviewer seat:** I am not technical. I am a Marathi-speaking senior who
orders food on WhatsApp, and the home cook who would run a kitchen on it.
I judged the v1 videos the same way in
`docs/review-loop/v1/external-user.md` and I judge this v3 package — the
milestones, the business plan, and the planned v3 pitch video — the way a
real customer would: can I follow it, do I understand the money, and would
I trust it with my order, my payment, or my phone number.

**Verdict: NEEDS WORK**

The package fixed the things it could count — ₹ pricing with Indian digit
grouping (`₹1,25,000.50`), Marathi daily-P&L lines, localized order
statuses for the customer. The honest disclosures in the video plan
(trust-based payments, fake/local WhatsApp adapters, Marathi partial) are
the right kind of honesty. But the v3 package ships **three unfixed
failures from my own v1 review**, and the planned video walks around the
money beat instead of through it. The money moment is exactly where I
decide trust; this video plans not to show it.

---

## Blockers

### B1. The walkthrough plan skips the money beat — the one moment trust is decided
- **Doc:** `docs/videos/v3-presentation-plan.md` §2 (Walkthrough, target
  6:00), frames 1–6.
- **What the plan shows:** user row on live Postgres → Marathi menu
  listing → nickname + Indian-grouping currency line → inventory seed
  table → Devanagari round-trip rows → CHECK-constraint catalog line.
- **What it never shows:** the order loop the §2 "Purpose" paragraph
  promises — "cook lists a dish → customer orders → cook accepts →
  customer is updated → **money state is tracked**." There are no frames
  for the order being placed, the cook accepting, status updates going
  out, or the payment-approval moment (COD confirm / P2P screenshot
  approval) — the exact moment a real user decides whether money is safe
  here.
- **Expectation violated:** the v3 video bar itself —
  `v3-presentation-plan.md` header: "complete unhurried walkthrough of
  ACTUAL behavior … one behavior at a time, each shown to completion"
  (reiterated in the §2 pacing rule). The v2 analysis in this same plan
  (§1, video-3) flagged "Ambiguity on money" — the narration never said
  whose account, which rail, or that there is no verified rail. v3's fix
  is to drop the beat, not to show it clearly. That is the opposite of a
  trust walkthrough.
- **What I need:** one unhurried beat showing the payment-approval
  screen in Marathi (`cook_payment_proof` → "1️⃣ पेमेंट मान्य करा 👍"),
  held on screen until the narration finishes: "the cook approves only
  when the money is really in their account — screenshot is a claim, not
  settled funds" (the plan already knows this phrasing from A3/A13; it
  just never schedules it).

### B2. "उघड्या ऑर्डरी पहा" is still on the cook's main menu — the joke I flagged in v1
- **Doc/locale:** `locales/mr.json`, key `cook_home`:
  `👩‍🍳 स्वयंपाकी मेनू: … 2️⃣ उघड्या ऑर्डरी पहा 📦 …`
- **What it says vs what it means:** "उघडं" means uncovered / exposed /
  naked. "Open orders" translated word-for-word, still reading as a
  joke — like the orders are standing there without clothes. My v1 review
  (M1, same path `docs/review-loop/v1/external-user.md`) named this exact
  string and suggested "चालू ऑर्डरी पहा". It is unchanged in the v3
  package.
- **Expectation violated:** the plan's own §1 ("Cross-cutting v2
  findings") claims prior review fixes were absorbed into v3. A failure
  the board already caught, sitting on the screen the cook sees every
  time, shipped unfixed. If this was caught once and still ships, I stop
  trusting that anything else was fixed.
- **Fix:** "2️⃣ चालू ऑर्डरी पहा 📦".

### B3. The cook's entire business/finance section is still English — my v1 blocker, now "disclosed"
- **Doc/locale:** `locales/mr.json` has 70 keys vs 162 in `locales/en.json`;
  every `o_*` (owner/business hub) and `m_*` (marketing hub) key is
  missing, so inventory, recipes, procurement, finance, daily P&L menu
  screens, offers, referrals, campaigns, and win-backs all fall back to
  English. (The new Marathi `o_digest_*` lines — `आजचा नफा-तोटा`,
  `निव्वळ` — are the digest *content*; the menus around it are English.)
- **Expectation violated:** `docs/milestones.md` requires a
  "Marathi/India context, INR" pilot with "1–2 committed pilot cooks",
  and the v3 plan (§4) stakes monetization on the owner addendum being
  "the retention argument" — yet the Marathi cook cannot read the
  business screens where she would read her earnings. "Marathi partial
  (missing keys fall back to English)" in milestones.md names the
  failure; naming it does not make a Marathi cook able to use the money
  screens. My v1 B1 verdict stands: ship the chat; the money flow is not
  ready for a Marathi-only cook until she can read it.

---

## Major

### M1. The P2P instructions name Zelle, Venmo, and Pix to a Marathi/India user
- **Doc/locale:** `locales/mr.json`, `p2p_instructions`:
  "📱 कृपया {cook} ला {total} Zelle, Venmo, UPI किंवा Pix ने पाठवा."
  and `payment_title`: "2️⃣ फोनवरून पेमेंट (Zelle / Venmo / UPI / Pix) 📱".
- **Why it scares me:** I am the India-pilot Marathi user. Zelle, Venmo,
  and Pix do not exist for me. Being told to send money "via Zelle" is
  the moment I conclude this product is not for my country — the same
  reaction my v1 review had to "डॉलरमध्ये किंमत लिहा" (which the package
  *did* fix, now `{cur}`-parameterized — credit where due).
- **Expectation violated:** `docs/business-plan.md` §1 already states
  the rail rule — "UPI in India, Zelle/Venmo/Pix elsewhere." The Marathi
  string for the India pilot should say UPI only.
- **Fix:** Marathi `p2p_instructions` / `payment_title`: "UPI ने पाठवा".

### M2. Narration register for the Marathi frames is unspecified (v1 M7, carried)
- **Doc:** `docs/videos/v3-presentation-plan.md` §2 and §5.
- **Detail:** my v1 review (M7) noted the chat is warm but the voiceover
  suddenly talks about "डेटाबेस", "स्टेट मशीन", "बॅकएंड" — words that
  mean nothing to a senior on WhatsApp. The v3 plan's "Must say" lines are
  board-register ("the same code path as production") with no guidance
  for the Marathi-frame beats. If any of these frames are ever reused for
  a user-facing cut, the register problem returns unexamined.
- **Expectation violated:** the video bar (complete, unhurried, never
  starting mid-thought) implicitly requires narration a viewer can
  follow; the plan specifies *what* to say, not *how* to say it for a
  non-technical ear.

---

## Minor

- **"किचन" in the cook's welcome message** (v1 minor, unfixed):
  `locales/mr.json` `cook_registered`: "🎉 स्वयंपाकी म्हणून नोंदणी झाली!
  चला, तुमचं किचन सुरू करूया." A real person writes
  "तुमचं **स्वयंपाकघर** सुरू करूया". First impression, still wrong.
- **`cook_menu_photo`**: "ग्राहक डोळ्यांनी विकत घेतात! 👀" ("customers
  buy with their eyes") — playful and natural; fine. Noted as working.
- **Section 2 frame 6 (CHECK-constraint catalog line)** is DDL shown to
  prove the migration. Fine for the board; never show it to a cook.
- **Language menu** (`language_menu`): 🌍 with all four language names in
  their own scripts — good, a Marathi reader finds मराठी instantly.

---

## Trust answers (per the rubric)

**(a) Would I trust this with my money / phone number after watching the
planned video?** As a **customer ordering dinner: yes** — the ₹ prices,
the single-digit flow, the kind in-language error handling, and the
cash-on-delivery line ("जेवण आल्यावर … रोख द्या") are all trustworthy,
and the plan discloses the trust-based payment gap honestly. As a
**cook: not yet** — my main menu still jokes at me (B2), and the screens
where I would read my earnings are English (B3).

**(b) Language and locale naturalness in the planned narration beats:**
The Marathi chat strings the video will show (menu listing, order
confirmations, status updates, daily P&L) are natural — warm,
conversational, not word-for-word translated. The planned narration
beats themselves ("must say" lines) are written for the board, not for
me; where they quote Marathi UI, the UI is right, but the narration
gives no register guidance (M2).

**(c) Moments where a real user would get confused, scared, or stuck:**
The payment-approval beat — the scariest screen in the product — is
simply absent from the walkthrough (B1); and a Marathi cook meeting
"Zelle, Venmo, UPI किंवा Pix" (M1) would stall at the payment step
wondering what Zelle is.

**(d) Is "money moves directly between people" explainable to a
non-technical user?** Yes — the plan's §4 "Must say" line is exactly the
right sentence: "BiteFlow takes no commission in this build; money moves
cook↔customer directly, off-platform. That's deliberate — it keeps us out
of payment licensing while the pilot measures demand." A non-technical
cook understands "पैसे थेट तुमच्याकडे येतात, अ‍ॅप काहीही घेत नाही"
(the money comes straight to you; the app takes nothing). The business
model itself is explainable; what is not explainable is why the video
never shows the money changing hands.
