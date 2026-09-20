<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="assets/card-dark.svg?v=8">
  <source media="(prefers-color-scheme: light)" srcset="assets/card-light.svg?v=8">
  <img src="assets/card-dark.svg?v=8" width="100%" alt="A glowing cyan-to-blue line flows across the top of the card, the same line that runs through the profile picture, with a bright point of light travelling along it. Abdullah Al Tamimi. The role beneath the name cycles through four: technical founder and product engineer; founder at LeafleX and Nashrati; AI and automation and full-stack developer; healthcare, education and government software. Building the layer between authoritative data and the person who has to act on it. What I build: healthcare, GS1 pack verification, MedDRA-coded adverse-event reporting and E2B/CIOMS export; education, teacher and institutional analytics over Moodle without recomputing its grades; government, citizen-feedback intelligence with classification, personas and root-cause tracing; interface, Arabic-first and right-to-left by default, down to the relational model underneath. Stack, interface: TypeScript, React, Vite, Tailwind, Framer Motion, i18next, Leaflet, JavaScript. Systems: Python, FastAPI, Node.js, PHP, PostgreSQL, Supabase, Docker, Kubernetes. AI and data: Claude, LangChain, Ollama, YOLO, MongoDB, Redis, Git, GitHub. Selected work in two columns: Nashrati, official drug leaflets turned into something a patient can act on — scan the pack, verify it, read it against your own profile — in React 19, Supabase, OpenAI, GS1 DataMatrix and MedDRA, shown as two Arabic phone screens. AQABA AQUA AI, flash-flood sediment risk to Gulf of Aqaba coral reefs — rainfall and terrain to a marine plume to reef exposure, hours ahead — in FastAPI, XGBoost, PostGIS, React, MapLibre and RAG, shown as its overview map. Across the full width below them, LCMS GATE, teacher and institution reporting over a real Moodle with saved templates, AND/OR filters and per-question statistics, in FastAPI, React 19, a PHP plugin, PostgreSQL and Docker, shown as its reports hub. Then Terhal, Ma'an governorate beyond Petra: plan a trip and book a local guide at a price you can see up front, in FastAPI, PostgreSQL, React 18, Leaflet and OpenAI vision. VOC-360, a national citizen-experience platform that ingests public feedback, classifies it and traces each issue to its root cause, in FastAPI, PostgreSQL, Redis, Docker and pandas. Beneath the work, a wide panel carries the portfolio: a globe, the address helpful-khapse-79c621.netlify.app, case studies, live screens and the thinking behind each build, and a Visit chip. How I work, four principles set on the same glowing line: founder mindset, better everyday, ideas to impact, progress over perfection. Architecture, animated: a band of light crosses the request row and each step lights as the light reaches it — scan, GS1 DataMatrix, to profile, Supabase row-level security, to smart view, OpenAI, to report, MedDRA to E2B — then a pulse returns along the dashed path beneath, where the official leaflet stays the authoritative source at every step; the platform beneath is PostgreSQL, Supabase Auth, OpenAI and i18next for Arabic and English right-to-left. Last, this year: the contribution calendar GitHub publishes, redrawn in the card's colours, with the year's contribution count, active days and longest streak beside it.">
</picture>

<!-- ?v= on every asset URL busts GitHub's camo proxy. Camo keys its cache on the
     image URL rather than on the bytes behind it, so an edited file keeps serving
     the old image until camo's own TTL expires and no browser refresh can reach
     it. Bumping this number changes the URL and forces a fresh fetch. Bump it
     whenever a change to the card has to show immediately.

     The card is one image, and an image served through GitHub's proxy cannot
     carry links, so the row below is separate: one small image per link, drawn
     from the card's own materials by tools/build.py, each wrapped in an <a>. -->

<p align="center">
  <a href="https://helpful-khapse-79c621.netlify.app/" title="Portfolio — case studies, live screens and the thinking behind each build"><picture><source media="(prefers-color-scheme: light)" srcset="assets/link-portfolio-light.svg?v=8"><img height="44" src="assets/link-portfolio-dark.svg?v=8" alt="Portfolio"></picture></a>
  <a href="https://www.linkedin.com/in/abdulla-tamimi" title="Abdullah Al Tamimi on LinkedIn"><picture><source media="(prefers-color-scheme: light)" srcset="assets/link-linkedin-light.svg?v=8"><img height="44" src="assets/link-linkedin-dark.svg?v=8" alt="LinkedIn"></picture></a>
  <a href="mailto:tamimiabdulla418@gmail.com" title="tamimiabdulla418@gmail.com"><picture><source media="(prefers-color-scheme: light)" srcset="assets/link-email-light.svg?v=8"><img height="44" src="assets/link-email-dark.svg?v=8" alt="Email"></picture></a>
  <a href="https://www.linkedin.com/company/leaflexx" title="LeafleX"><picture><source media="(prefers-color-scheme: light)" srcset="assets/link-leaflex-light.svg?v=8"><img height="44" src="assets/link-leaflex-dark.svg?v=8" alt="LeafleX"></picture></a>
  <a href="https://github.com/abdullatam/abdullatam" title="abdullatam/abdullatam, the repository that draws this card"><picture><source media="(prefers-color-scheme: light)" srcset="assets/link-build-light.svg?v=8"><img height="44" src="assets/link-build-dark.svg?v=8" alt="How it's built"></picture></a>
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=abdullatam&background=050B1A&border=1E3A5F&stroke=1E3A5F&ring=18D7FF&fire=635BFF&currStreakNum=F5F7FF&sideNums=F5F7FF&currStreakLabel=18D7FF&sideLabels=94A3B8&dates=94A3B8&excludeDaysLabel=94A3B8" width="100%" alt="GitHub contribution streak: total contributions, current streak and longest streak.">
</p>

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/abdullatam/abdullatam/output/snake-dark.svg?v=8">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/abdullatam/abdullatam/output/snake-light.svg?v=8">
  <img src="https://raw.githubusercontent.com/abdullatam/abdullatam/output/snake-dark.svg?v=8" width="100%" alt="A snake crawling the contribution graph and eating the squares, drawn in cyan.">
</picture>

<details>
<summary><b>The longer version</b></summary>

<br>

**Portfolio — [helpful-khapse-79c621.netlify.app](https://helpful-khapse-79c621.netlify.app/)** ·
the same work with the screens, the case studies and the decisions behind each one.

### Nashrati — the patient layer over official drug leaflets

Jordan mandated electronic drug leaflets. The leaflet became digital; it did not become
readable. A patient still gets a wall of regulatory prose that answers a regulator's question,
not theirs: *can I take this with my blood-pressure medicine?*

**Nashrati does not author leaflets.** The official governmental leaflet stays the authoritative
source and is always cited as the source. Nashrati builds the patient journey on top of it.

- A **GS1 DataMatrix** scanner that parses GTIN, serial, batch and expiry straight off the pack.
- An AI **Smart View** that restates the *official* leaflet against the patient's own profile —
  conditions, allergies, current medications, lifestyle.
- A 5-step adverse-reaction wizard in plain language (*"I had to see a doctor"*) that maps to
  **MedDRA 27.0** preferred terms behind the scenes, captures dechallenge/rechallenge, and
  exports **E2B / CIOMS XML**.
- A pharmacist console publishing structured dosage guidance with a mandatory, immutable source
  attribution — *Official Leaflet* or *Physician's Prescription* — logged for accountability.

React 19 · TypeScript · Vite · Tailwind · Supabase (Postgres, Auth, RLS) · OpenAI · i18next
(Arabic/English, full RTL) · `html5-qrcode` + `bwip-js`. **Sole builder.** Private repository ·
published leaflet renderings: [Clinton® (Etoricoxib)](https://abdullatam.github.io/clinton-leaflet/) ·
[Clavudar®](https://abdullatam.github.io/clavudar-leaflet/) ·
[Flagyl®](https://abdullatam.github.io/flagyl-leaflet/)

The hardest part wasn't the code. It was drawing the line between *presenting a regulator's
document* and *giving medical advice*, and keeping every screen on the right side of it.

### AQABA AQUA AI — flash-flood sediment risk to the Gulf of Aqaba

A flood in the desert is a marine event. Rain falls on a wadi ninety kilometres inland, and
hours later the sediment is on a coral reef. The platform forecasts that whole chain —
rainfall → wadi runoff → coastal outlet → probabilistic marine plume → reef exposure → alerts —
over five catchments (4,656 km²) and eight reef zones, against the October 2016 Aqaba–Eilat
flood that moved roughly 24,400 tonnes of sediment.

**My scope: the exposure engine, RAG, reports, site scoring and coral health** — and the
screens over them: reef zones, alerts, reports, site scoring, the assistant, and the scenario
drawer on the dashboard. I also did the rebrand pass that rebuilt the frontend on the
AQABA AQUA AI identity.

Two constraints worth stating, because they are the same instinct as everything else here:
the LLM layer **explains and retrieves but never computes a number**, and every figure carries
its provenance and its caveat — Model honesty, Provenance and Limitations are first-class
screens, not a footnote.

FastAPI · XGBoost · scikit-learn · xarray / geopandas / rasterio · Supabase (Postgres + PostGIS) ·
Docker · React · MapLibre GL · TanStack Query · Zustand · i18next (EN/AR). Data: NASA GPM IMERG,
Copernicus ERA5-Land and DEM GLO-30, GEBCO/GMRT bathymetry, Allen Coral Atlas reef habitat.

Built for **Blue Horizons** — The Core Hacks, HTU's first blue-economy hackathon, with Aqaba
Development Corporation and backed by the Crown Prince Foundation. **Contributor on a
six-person team** (47 of 259 commits).
[Repo](https://github.com/mahdianagreh/AAA-Ocean-hackathon-)

### LCMS GATE — the control plane around Moodle

Universities don't need a new LMS. Moodle already is the academic system of record. What's
missing is everything *around* the course. The governing rule: nothing in the platform computes
a second answer to a question Moodle already answers — it presents and explains Moodle's verdict.

**I own the reporting and analytics surface**: the report engine (saved templates, AND/OR filter
groups, column controls, a CSV export that matches what's on screen), per-question quiz
statistics carried through a new Moodle plugin contract, video watch analytics from measured
viewing rather than a completion tick, institutional prediction models with visible thresholds
and action plans, the data-viz primitives the platform renders on, and Arabic/English copy for
every reporting surface.

FastAPI · React 19 · TypeScript · PHP (`local_lcms_gate`) · Postgres · Docker · Helm/Kubernetes ·
pytest. **Contributor on a team** (~110 commits); architecture and the Moodle seam are shared work.

### Terhal · ترحال — tourism revenue that reaches the town

Petra takes roughly 900,000 visitors a year. Almost all arrive from Amman, spend four hours in
the Siq, and leave. Ma'an governorate has Jordan's highest unemployment rate, and Shobak's
crusader castle is an hour away seeing close to none of it.

I built **the provider side**: six guide-facing screens on the shared backend, the role-gating
entry flow that splits tourist from guide, a camera guide backed by OpenAI vision, and a
Ma'an-specialist chat assistant. I rebuilt the tourist frontend onto the Terhal design system and
wired the landmark gallery, profile and reviews endpoints.

FastAPI · Postgres · React 18 · Tailwind · Leaflet · OpenAI. **Repository owner, provider-side
lead.** Built for the Ma'an Hackathon for Entrepreneurship (Irada Program).

### VoC-360 — national citizen-experience intelligence

A microservice platform turning citizen complaints into something a minister can act on:
ingestion → NLP, personas, archetypes, root-cause → BI and experience layers.

I worked the **intelligence/BI layer and the Minister View**: unified the CXI score onto a single
persisted, coverage-flagged number instead of competing calculations; made sector scope **fail
closed** on an unresolvable crosswalk rather than silently widening; moved the default snapshot
period to a rolling window; and took a hot snapshot path from parse-many to parse-once/slice-many
for a measured **4.77×** speedup. On the front end, the root-cause decision brief and the Minister
View severity-report cards. Team platform under the 9XAI program.

### More

| Project | What it is |
|---|---|
| **[Tammy AI](https://tammy-ai.com/)** | Live product. An AI that holds the thread across sessions — three memory tiers behind one interface: Redis for the live conversation, MongoDB for sessions and profiles, Pinecone for semantic recall and RAG, with a query classifier choosing the tier and a context builder working to a hard token budget. Voice in and out. FastAPI · SSE · Claude → OpenAI fallback · LangChain · Speechmatics. Built with Tamer Masri and Omar. [Repo](https://github.com/abdullatam/tammyai) |
| **Moodle Team 1 — Course Builder & Player** | Rebuilt the essential parts of how Moodle represents a course — availability trees, completion rules, reuse — by understanding it, not copying it. My scope: copy, backup, restore, `.mbz` import, date-shifting, and the honest ledger of what information gets lost. FastAPI · SQLite · React |
| **Nasher AI** | AI content platform for government. Built the full bilingual frontend from scratch and ran the RAG pipeline, backend and frontend together locally. Authored the Ministry Alignment Report. React · FastAPI · RAG |
| **Traffic monitoring & forecasting** | 9XAI hackathon, solo repo. A reproducible data sandbox for Wasfi Al-Tal / Mecca St, Amman — 22 detectors × 14 days, signal logs, labelled events — a SUMO simulation network, YOLO live plate detection (NMS + spatial tracking + majority vote) served as an annotated MJPEG stream, and a bilingual what-if signal-timing simulator. |
| **[HTUFoundIt](https://github.com/abdullatam/HTUFoundIt-Frontend)** | Lost-and-found platform for Al-Hussein Technical University. React · Auth0 · Node.js · Express · PostgreSQL · [backend](https://github.com/abdullatam/HTUFoundIt-Backend) |
| **[LeafleX](https://github.com/abdullatam/LeafleX-1)** | The predecessor to Nashrati and the reason I know this domain: a builder for Jordan's newly mandated digital leaflets, converting unstructured pharmaceutical leaflets into structured, JFDA/HL7-compliant XML. |

### How the card is drawn

`tools/build.py` draws `assets/card-{dark,light}.svg` and the link buttons from one set of
definitions — content at the top of the file, a palette per theme, icons from `tools/icons/`,
screenshots from `tools/shots/`. Edit the content, run `python3 tools/build.py`, bump the `?v=`
in this README so camo refetches, and push.

</details>
