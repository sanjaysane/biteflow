# External-User Review — v1 walkthrough videos

**Reviewer seat:** I am not technical. I am a Marathi-speaking senior citizen who orders food on WhatsApp, and a homeowner who would try a design chat on WhatsApp. I judge these videos the way a real customer would: can I follow it, do I understand the money, and would I trust it with my order, my payment, or my room photo.

**Verdict: NEEDS WORK**

The happy paths work and the Marathi *chat* is mostly warm and natural. But the videos break trust exactly where money appears: the whole money section of the cook's app is in English, and every price is in dollars for an audience with Indian (+91) phone numbers. A Marathi-only senior cannot use the money parts. Ship the chat; do not ship the money flow yet.

---

## Blockers

### B1. The entire Business / Finance section is in English — the money part of my own kitchen is unreadable
- **Video:** `biteflow-cook-mr.mp4`, ~02:30–03:05 (Step 7 · payout)
- **What I see:** I press "3️⃣ व्यवसाय" and the bot answers in full English:
  `📊 *Business*` → `1️⃣ Inventory 📦 | 2️⃣ Recipes 📖 | 3️⃣ Procurement 🚚 | 4️⃣ Finance 💰 | 5️⃣ Marketing 📣`
  then `💰 *Finance*` → `1️⃣ Today's P&L 📊 | 2️⃣ Weekly food-cost projection 🔮 | 3️⃣ Log capex 🏗️ | 4️⃣ Log opex 🧾 | 5️⃣ COD vs P2P 🤝`
  then `🤝 *COD vs P2P* (completed, last 7 days): • COD: $17.00 collected, $0.00 still out • P2P: $0.00 verified, $0.00 awaiting proof review`
- **Why it blocks me:** I am a Marathi speaker who chose Marathi. The one screen that tells me about my earnings, my costs, and who owes me money is a wall of English I cannot read. I would be afraid to press anything here — what if I press the wrong thing and lose money? Words like "capex", "opex", "P&L", "P2P" mean nothing to me.
- **What makes it worse:** the voiceover itself admits it — *"हा भाग अजून मराठीत भाषांतरित झालेला नाही, म्हणून संदेश इंग्रजीत येतात"* ("this part is not translated into Marathi yet, so the messages come in English"). If the video has to apologize for it, it is not ready for me.

### B2. Every price is in US dollars, but I am shown Indian phone numbers
- **Videos:** all four; clearest at `biteflow-cook-mr.mp4` ~00:40 ("🍛 पदार्थाचं नाव काय?") → bot asks `"मिसळ पाव" ची किंमत? डॉलरमध्ये किंमत लिहा, उदा. 8.50 💰` ("write the price **in dollars**"), and `roomlens-prospect-mr.mp4` ~01:50–02:40 (`Aria Chair — $189.00`, `किंमत: $189.00`).
- **What I experience:** I am a senior in India (the customers' numbers start with +91). I think in rupees. The bot tells me to type my वडा पाव price in dollars; the chair costs "$189.00" which is roughly ₹16,000 — I have to do that math myself and I cannot. My first thought watching this: "this is for America, not for me."
- **Why it blocks me:** I cannot trust any price on screen. The closing card says "Prices shown in USD (real engine behavior)" — but that card is in English, at the very end, and it flashes by. Nobody watching casually will read it. For a Marathi user this is not a footnote; it is the whole experience.

---

## Major

### M1. "उघड्या ऑर्डरी पहा" — my menu button says "naked orders"
- **Video:** `biteflow-cook-mr.mp4`, ~00:25 and every main-menu appearance after (~03:05, ~03:20): `2️⃣ उघड्या ऑर्डरी पहा 📦`
- **What it says vs what it means:** In Marathi, "उघडं" means uncovered / exposed / naked. This is "open orders" translated word-for-word. It reads as a joke — like the orders are standing there without clothes. A real person would write **"चालू ऑर्डरी पहा"** or **"सुरू असलेल्या ऑर्डरी पहा"** (orders in progress).
- **Why it matters:** This is on the main menu, which I see constantly. Every time I see it I trust the app a little less — if they got this wrong, what else did they get wrong?

### M2. The room preview photo has English burned into the picture
- **Video:** `roomlens-prospect-mr.mp4`, ~01:30–02:20 (designer draft + prospect preview)
- **What I see:** The "preview of the chair in my room" is an image with English text printed on it: *"Your room, with our furniture: Aria Chair — $189.00"* — and the chair itself has "Aria Chair" written across it in English.
- **Why it matters:** The voiceover proudly says the preview comes *"सोबत मराठी कॅप्शन"* (with a Marathi caption) — and the caption below the photo is indeed Marathi (`✨ पाहा, तुमच्याच खोलीत Aria Chair!`). But the photo itself is English. As a Marathi-only reader, the thing I'm supposed to look at hardest is the thing I can't read. It also makes the product feel half-finished.

### M3. The order summary says "Total", not "एकूण"
- **Video:** `roomlens-prospect-mr.mp4`, ~02:35–02:45 (booking): `🧾 तुमची ऑर्डर: Aria Chair × 1 — $189.00 / Total — $189.00`
- **Why it matters:** This is the screen where I decide to spend money. "Total" is a plain English word — and confusingly, the BiteFlow Marathi chat gets this right (`एकूण: $17.00`), so the product already knows the word. Note: this same `Total — $189.00` string also appears in the **English** designer video, so this isn't a Marathi fallback problem — the string itself is wrong everywhere.

### M4. My order tracking says "received" — from whose side?
- **Video:** `roomlens-prospect-mr.mp4`, ~02:55–03:05 (tracking): `📦 तुमच्या ऑर्डरी: #9: received — $189.00`
- **Why it matters:** Two problems. First, it's English in a Marathi chat. Second, "received" is backwards for me: *I* haven't received anything — the *designer* received *my* order. As the buyer I read this and think "received what? by whom?" I expect something like "ऑर्डर मिळाली" (order received — from the designer's view) or a status that speaks to me, like "तयार होत आहे".

### M5. The "preview" looks like a brown rectangle drawn by a child — I would not trust it with my room photo or ₹16,000
- **Video:** `roomlens-prospect-mr.mp4`, ~01:30–02:20
- **What I see:** The Aria Chair is a flat brown rounded rectangle pasted on grey static. It does not look like furniture in a room; it looks like a sticker. The closing card says "Visualization is preset compositing, not true AR" — honest, but the visual still kills the pitch.
- **Why it matters:** The whole promise is "see furniture in YOUR room before you buy." The demo image looks fake, so as a homeowner I assume the real thing will look fake too, and I will not send my room photo or confirm a $189 order. The voiceover's honesty about it ("हे खरं ऑग्मेंटेड रिअॅलिटी नाही") helps a little, but honesty about a bad picture doesn't make the picture good.

### M6. RoomLens never shows me how I pay — the scariest screen is missing
- **Video:** `roomlens-prospect-mr.mp4`, ~02:25–02:50 (booking)
- **What I experience:** I press `1️⃣ ऑर्डर पक्की करा 👍` on a $189.00 order and get `🎉 ऑर्डर #9 झाली!` — congratulations, order placed. But nobody asked me for money, nobody told me when money leaves my hands, and nobody told me how. As a homeowner this is where I freeze: *am I about to be charged?*
- **Contrast:** BiteFlow handles this beautifully — `✅ ऑर्डर झाली! जेवण आल्यावर $17.00 रोख द्या` (pay cash when the food arrives). No prepayment, no fear. RoomLens needs its equivalent moment: even one line like "पैसे डिलिव्हरीच्या वेळी" (payment at delivery) would unblock me.

### M7. The voiceover talks about "database" and "state machine" — I get lost
- **Videos:** `biteflow-cook-mr.mp4` ~00:55 ("डेटाबेसमध्ये मेनूमध्ये नोंद होते"), ~01:45 ("स्टेट मशीन स्वतः स्वयंपाक्याला पुश करतं"); `roomlens-prospect-mr.mp4` ~00:55 ("मीडिया स्टोअरमध्ये सेव्ह होतो", "बॅकएंड दोन गोष्टी करतं")
- **What I experience:** The chat bubbles are written for me. The voice suddenly is not — it explains "डेटाबेस" (database), "स्टेट मशीन" (state machine), "पुश" (push), "बॅकएंड" (backend), "कंपोझिटिंग इंजिन" (compositing engine). I am a senior who uses WhatsApp; these words mean nothing and I tune out for those sentences. The narration is otherwise lovely, warm Marathi ("एक गंमत पहा", "हाच खरा लाइव्ह क्षण") — it just needs to stay in my world: "यादीत नोंद होते" (it gets noted in the list), "संदेश आपोआप जातो" (the message goes by itself).

---

## Minor

- **"किचन" in a Marathi sentence** — `biteflow-cook-mr.mp4` ~00:20: `🎉 स्वयंपाकी म्हणून नोंदणी झाली! चला, तुमचं किचन सुरू करूया.` The word "किचन" (kitchen, in English letters' clothing) sits inside pure Marathi. A real person says **"तुमचं स्वयंपाकघर सुरू करूया"**. Small, but it's the welcome message — first impressions.
- **"परफेक्ट — ग्राहकाला पाठवा"** — `roomlens-prospect-mr.mp4` ~01:25 (designer side): `3️⃣ परफेक्ट — ग्राहकाला पाठवा ✨`. "परफेक्ट" is English wearing Devanagari clothes. A real person writes **"छान! ग्राहकाला पाठवा"** or **"मस्त — ग्राहकाला पाठवा"**.
- **"(COD)" in the order alert** — `biteflow-cook-mr.mp4` ~01:25, ~03:08: `एकूण: $17.00 (COD)`. Harmless — I can guess it means cash — but a real person would write `एकूण: $17.00 (रोख)`.
- **"उत्पादन" feels like a textbook** — `roomlens-prospect-mr.mp4` ~01:20: `ठेवण्यासाठी उत्पादन निवडा:` ("select the product to place"). "उत्पादन" is correct but stiff; in chat a person says **"वस्तू निवडा"**.
- **Typing "काय?" just re-shows the menu with no explanation** — `biteflow-cook-mr.mp4` ~03:20: I type `काय?` and the bot silently repeats the main menu. Graceful, but as a senior I typed a word and got no answer — one line like "मला फक्त क्रमांक समजतात" (I only understand numbers) would teach me the rules.
- **Typing "help" shows my order, not help** — `biteflow-customer-en.mp4` (transcript s11): I type `help` and get `📦 Order #5: Completed ✅ / Total: $17.00`. That's not help; it's confusing.
- **Number formats wobble** — sometimes `1️⃣ हो ➕`, sometimes `1. 👩‍🍳 +9198…`. Never confusing about what to type, just inconsistent.
- **Closing cards are English-only** — `biteflow-cook-mr.mp4` ~03:25 ("Simulated WhatsApp client · local run… Prices shown in USD"), `roomlens-prospect-mr.mp4` ~03:05 ("Visualization is preset compositing, not true AR"). These are aimed at the video's audience, not the chat user, so I don't count them as product leaks — but a Marathi viewer of a Marathi video meets a wall of English at the end.

---

## The English leaks, judged as a Marathi-only reader

| Leak (from LEAKS.md) | Blocks me? | Why |
|---|---|---|
| Whole Business/Finance menu in English (Inventory, Today's P&L, Log capex/opex, COD vs P2P…) | **Blocks** | It's the money screen; I can't read any of it and I'm afraid to touch it. |
| `Total` in the RoomLens order summary | **Blocks** | It's on the "do I spend money" screen; and BiteFlow already uses "एकूण", so I know they know the word. |
| `received` in order tracking | **Blocks** | English + backwards point of view — I don't know what was received or by whom. |
| `(COD)` in the cook's order alert | Harmless | I can guess it means cash-on-delivery from context. |
| `STOP` opt-out keyword | Harmless | It's explained in Marathi right where it appears: "(कधीही सोडण्यासाठी STOP लिहा.)" |
| Brand/proper nouns (Zelle, Venmo, UPI, Pix, Casa Studio, Aria Chair) | Harmless | Names are names; nobody expects "एरिया खुर्ची". |
| Prices in USD | **Blocks** (see B2) | I think in rupees; dollar prices make every amount untrustworthy. |

---

## Prices in USD — what I expected

Yes, confusing — see B2. What I'd expect as a Marathi-speaking user with an Indian number: **₹ prices, or at minimum a rupee figure next to the dollar one**. When the bot says "डॉलरमध्ये किंमत लिहा" (type the price in dollars), I don't just get confused — I conclude the service isn't for my country and stop watching. Currency is not a footnote for a food-ordering demo; it's the first thing a cook or customer looks at.

---

## Trust: would I send money / share my room photo?

**BiteFlow — I would order food.** Trust is built in three moments: (1) the language switch is instant and total — `✅ भाषा बदलली!` and everything flips to Marathi, which tells me "this was made for me"; (2) the price-entry mistake is handled in kind Marathi — `हं, ती बरोबर किंमत नाही. 8.50 सारखा अंक लिहा` ("hmm, that's not a right price, write a number like 8.50") — patient, like a person; (3) the money moment is cash-on-delivery — `जेवण आल्यावर $17.00 रोख द्या` — I pay when food is in my hand, so there is nothing to fear. The daily profit note in clean Marathi (`आजचा नफा-तोटा`, `निव्वळ`) also builds trust. **Trust breaks** at the Business/Finance menu (B1): the moment I want to understand my earnings, the app stops speaking my language — exactly where a cook is most vulnerable.

**RoomLens — I would not share my room photo yet, and I would not confirm the order.** Two reasons: the preview picture looks fake (M5) — I don't believe what I'd be buying — and the booking flow never tells me how payment works (M6). The "free preview" promise (`अगदी मोफत!`) and the photo-quality check do build trust, and the Marathi chat itself is lovely (`📸 छान! तुमच्या खोलीचा एक स्पष्ट फोटो पाठवा (लाइट लावा, फोन हलवू नका)`). But a homeowner's rule is simple: no clear payment story, no order.

---

## Reply-with-a-number UX: is it obvious what to type?

**Yes, almost everywhere.** Every bot message ends with an explicit instruction — `क्रमांक लिहा`, `लिहा:`, `पदार्थाचा क्रमांक लिहा, किंवा बिलासाठी 0`, `1 ते 9 मधला अंक लिहा` — and the options are numbered. The demo proves the guardrails work: typing `abc` for a price gets a polite Marathi correction; typing `9` when only `1` exists gets `माफ करा, तो बरोबर पर्याय नव्हता`; typing `काय?` safely returns the menu. A senior who can type a single digit can drive the whole thing. The only gap is M7's minor: when I type a *word*, nobody tells me words don't work — one teaching line would close the loop.

---

## What worked (so I don't only complain)

- The Marathi chat copy is genuinely warm and human: `🎉 स्वयंपाकी म्हणून नोंदणी झाली!`, `😞 माफ करा, स्वयंपाकी ऑर्डर #7 घेऊ शकला नाही. तुमची थाळी रिकामी केली आहे` ("your thali has been emptied" — a lovely, human metaphor for clearing a cart), `हरकत नाही — ऑर्डर रद्द झाली`, `💳 पैसे कसे देणार? 1️⃣ डिलिव्हरीवर रोख 💵`.
- The Marathi voiceover (narration) is natural, conversational Marathi — it sounds like a person, not a translation, until it hits the technical words (M7).
- Devanagari renders correctly on screen in every frame I checked; nothing was garbled or broken.
- Error handling is consistently kind and in-language — this is the strongest trust signal in all four videos.
- The decline/cancel paths are graceful in both products — no pressure, easy restart (`पुन्हा सुरू करण्यासाठी कधीही खोलीचा फोटो पाठवा!`).
