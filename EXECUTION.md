# Execution plan: AI automation for trucking → recurring revenue → SaaS

Based on the ChatGPT plan you shared, adjusted to your situation: Serbia, paušalac, full-time US dispatcher, about 15 hours a week (2–3 hours on weekdays plus a longer weekend block).

**Goal:** $3,000–5,000/month in recurring revenue (MRR) within 6–9 months, then grow toward $10k.

---

## 1. What I agree with in that plan, and what I'd change

**Agree:**
- Niche down to trucking and sell a **managed monthly service**, not one-off automations.
- Start with **document extraction, reminders and reporting**. Keep negotiation, accepting loads and messages to brokers under human approval.
- Build one small feature at a time; no complex agents before a customer needs them.
- Never use your employer's data.
- Turn the agency into SaaS **only after** 3+ clients use the same core system.

**Change:**

| ChatGPT plan | Adjustment for you |
|---|---|
| 5 clients at $800–1,000/month | A 1–3 truck owner-operator won't pay that. **Target dispatch agencies (10+ dispatchers) and carriers with 10–50 trucks.** Serbia and the Balkans have hundreds of US dispatch agencies; you speak their language and know their work. |
| Start with n8n + Supabase | **Start with the demo already built in this repo** (`dispatch_assistant/`). Add n8n later for client-specific connections (Gmail, Google Sheets, Slack, WhatsApp). |
| Agency only | Keep **1–2 dispatch trucks** on the side if you can (optional). That's cash flow plus a live testing ground for your own tool. |
| Not mentioned | **Paušal limit 6M RSD/year (~$4,500–5,000/month).** At $3–5k MRR you'll hit it, so plan the switch to knjigaš or DOO with your bookkeeper around month 4–6. |

**Prices to test (not market facts):**
- **Pilot:** €200–400 one-time for 30 days, in exchange for a testimonial.
- **Small dispatch agency or small carrier:** €300–600 setup + €150–300/month.
- **Larger agency (10+ dispatchers) or 20–50 truck carrier:** €800–1,500 setup + €400–1,000/month.
- What the monthly fee covers: hosting, AI usage within an allowance, fixing errors within 24 hours, one small improvement each month, and a monthly report showing hours saved.

**Path to $3–5k MRR:** about 4–6 large clients, or 10–15 small ones, or a mix.

---

## 2. The product: Dispatch Operations Assistant

| Version | Features | Status |
|---|---|---|
| **v0.1 (demo)** | Rate con PDF upload → AI extraction → review/approve → searchable loads → morning report → error log | ✅ Built in `dispatch_assistant/` |
| v0.2 | Login, multiple dispatchers, a company account per client, export to CSV/Google Sheets | Weeks 3–4 |
| v0.3 | Email inbox import: rate cons forwarded to an address are processed automatically | Weeks 5–6 |
| v0.4 | Reminders: broker hasn't replied, POD missing, load delivered but not invoiced (Telegram/WhatsApp/email) | Weeks 6–8 |
| v0.5 | Invoice + factoring packet generator (rate con + BOL + POD → one PDF) | Weeks 8–10 |
| v1.0 | Hosted online, one shared code base for all clients, Stripe-alternative billing (Paddle/Lemon Squeezy) | Month 4+ |

**Build rule:** the next feature comes from what pilot clients ask for, not from this list.

---

## 3. 90-day plan (about 15 hours a week)

### Days 1–14: make the demo real
- [ ] Run the demo on your computer (see `dispatch_assistant/README.md`)
- [ ] Get a Claude API key and $10–20 credit; test it on 10+ **synthetic** rate cons in different layouts (create them yourself from public rate con templates found online, filled with fake data)
- [ ] Note what the AI gets wrong; we fix prompts and rules together
- [ ] Put it online so you can show it with a link (we can do this together; about $5–20/month)
- [ ] Record a **2-minute demo video** (screen recording, can be faceless): "Rate con PDF in, load in the system and invoice-ready in 10 seconds"
- **Deliverable:** a working demo at a public link + the demo video

### Days 15–30: first paying pilot
- [ ] Build a list of **40 targets**: 25 Serbian/Balkan dispatch agencies (LinkedIn, Facebook groups, job ads that say "US dispatcher"; agencies posting job ads have growing workloads) + 15 small US carriers (outside your employer's network)
- [ ] Contact **5–8 a day** (messages below), aiming for **8–10 conversations**
- [ ] In each conversation ask: *Which task eats the most dispatcher time? What do you type in twice? What gets forgotten? Which report takes too long?*
- [ ] Offer a 30-day pilot with a clear scope and price
- **Target:** 1 paying pilot

### Days 31–60: make it repeatable
- [ ] Onboarding checklist, a support channel (WhatsApp/Telegram group), and a weekly check-in
- [ ] Measure for the pilot: documents processed, minutes saved per document, errors found
- [ ] Build the most-requested feature (probably v0.3 email import or v0.4 reminders)
- [ ] A second and third client on **the same code base**, configured, not rebuilt
- **Target:** 2–3 paying clients

### Days 61–90: recurring revenue
- [ ] Turn pilots into monthly contracts (written agreement, invoice from your paušal)
- [ ] Write a case study: "Agency X saves Y hours a week" (with permission)
- [ ] Ask each client for one referral
- [ ] Post content 3x a week: demo clips, before/after, lessons learned
- **Target:** €1,500–3,000 MRR (stretch goal, not a promise)

### Months 4–9
- Grow to 6–12 clients, standardize onboarding, start the paušal → knjigaš/DOO switch, and consider leaving the job only once MRR has exceeded your salary for 3 months in a row.

---

## 4. Weekly schedule (15 hours)

| When | What |
|---|---|
| Mon–Fri, 1 hour before work | Outreach and follow-ups (5–8 contacts a day), replying to leads |
| Mon–Fri, 1–1.5 hours after work | Building with Claude Code, client support |
| Weekend, 3–4 hours | One bigger feature, the demo video or content, weekly review |

**Rule from the plan, and it's correct:** once the demo works, spend **more time talking to potential customers than building.**

---

## 5. Budget for the first 90 days (estimate)

| Item | Monthly |
|---|---|
| Claude subscription (for Claude Code) | your current plan |
| Claude API usage (testing + pilots) | $5–30 |
| Hosting + domain | $5–20 |
| Google Workspace or a professional email (optional) | ~$7 |
| **Total extra** | **about $20–60/month** |

Don't pay for courses, ads, branding or extra AI tools before the first paying client.

---

## 6. Outreach messages

**Serbian, to a dispatch agency (LinkedIn/Facebook/email):**
> Zdravo [ime], i ja radim u dispečingu za US loadove. Imam alat koji iz rate con PDF-a za par sekundi izvuče sve podatke o loadu (broker, rate, pickup/delivery, reference), označi šta nedostaje i svako jutro napravi izveštaj šta treba uraditi. Dispečeri tako ne kucaju ručno svaki load. Imam demo od 2 minuta. Da li bi vam bilo zanimljivo da pogledate? Tražim 2–3 agencije za probni period od 30 dana po sniženoj ceni.

(In English: "Hi [name], I also work as a dispatcher on US loads. I built a tool that pulls all the load details out of a rate con PDF in a few seconds (broker, rate, pickup/delivery, references), flags what's missing, and creates a report every morning of what needs to be done, so dispatchers don't type every load by hand. I have a 2-minute demo. Would you be interested in taking a look? I'm looking for 2–3 agencies for a 30-day trial at a reduced price.")

**English, to a US carrier:**
> Hi [name], I'm a US freight dispatcher who builds automation for small fleets. I made a tool that turns rate con PDFs into load records in seconds, flags missing info, and gives you a morning report: today's pickups, overdue deliveries, loads ready to invoice. Here's a 2-minute demo: [link]. I'm taking on 2–3 pilot fleets this month at a reduced price. Worth a quick call?

---

## 7. Rules

1. Never use your employer's data, clients or brokers, and don't work on this during work hours.
2. A human approves everything that leaves the system (emails, load acceptance, invoices).
3. One code base for all clients; customize through settings, not separate copies.
4. Every client signs a short agreement (scope, price, data handling, support times).
5. Track weekly: **conversations held, pilots, MRR, hours saved for clients.**

## 8. This week (first execution steps)

1. **Today:** run the demo on your computer following `dispatch_assistant/README.md`. If you get stuck, send me the error.
2. **Tomorrow:** create a Claude API key, add $10 credit, and test on 3–5 synthetic rate cons in different layouts. Tell me what it got wrong.
3. **Day 3:** start the list of 40 targets (spreadsheet: name, type, contact, channel, status).
4. **Day 4–5:** send the first 10 messages using the scripts above.
5. **Weekend:** we put the demo online together and you record the 2-minute video.
