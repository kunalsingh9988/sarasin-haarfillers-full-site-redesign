# Sarasin Haarfillers — full-site redesign

This is a public, static review build of [Haarfillers.com](https://www.haarfillers.com/), generated on 19 November 2026. It covers 56 public WordPress page routes. The live website and its booking service are unchanged.

## Design

The redesign uses a forest green, warm ivory, and muted gold visual system across every page. It adds image-led heroes, a consistent navigation and footer, visual summaries for key treatment pages, a prices comparison, a treatment journey, a real-results gallery, team and clinic visual sections, and easier in-page reading navigation. The original page copy is retained in the article area. Extra visual summaries are additive.

The twelve primary routes (`/`, `/mannen/`, `/vrouwen/`, `/voor-en-na/`, `/prijzen/`, `/faq/`, `/sarasin-clinic/`, both locations, `/sarasin-clinic/ons-team/`, `/reviews/`, and `/videos/`) receive a second editorial pass with purpose-built hero copy and modules. The original titles and full source information remain visible below the new visual introductions.

The user supplied [NeoYou's Dr. CYJ page](https://neoyou.netlify.app/en/dr-cyj-hair-fillers/) and [Dokter Frodo](https://www.dokterfrodo.nl/en) as inspiration. Their content, branding, and imagery were not copied. The direction uses clear treatment steps and pricing, real clinic photography, and practitioner-led trust cues.

## Content and image provenance

- `content-inventory.json` records the source URL and original rendered text for each generated route.
- `assets/source/` holds 143 images downloaded from the existing public Haarfillers.com pages. This includes the site's existing result, staff, clinic, and zone images. No patient result was generated or retouched.
- `assets/treatment-process.png` is an AI-generated illustrative treatment image. It is labeled as an illustration wherever featured prominently; it must not be presented as a real Sarasin patient or staff member.
- `assets/consultation-illustration.png` is an AI-generated consultation scene used on the homepage and FAQ hero. Both heroes explicitly label it as illustrative.
- `assets/hairfiller-treatment.mp4` and `assets/hairfiller-women.mp4` are unaltered treatment videos downloaded from the existing Haarfillers.com uploads. Their poster frames were extracted locally from those videos.
- Existing medical and pricing wording is reproduced from the live pages, including any source inconsistencies. Clinical, legal, price, and consent review is needed before using this as the primary production site.

## Run and rebuild

The deployed site is plain HTML, CSS, and JavaScript. No framework or runtime dependency is required to serve it.

```bash
python3 -m http.server 8787
```

To regenerate from the live source, install `requests` and `beautifulsoup4`, then run:

```bash
python3 tools/build.py
```

The build intentionally has `noindex,follow` because it duplicates the live site's text. Booking links lead to Sarasin Clinic's existing booking system.

## Verification

On 19 November 2026, the build generated 56 routes, and a static link and asset audit found zero broken local routes and zero missing local images. The homepage, men, and prices pages were reviewed in a desktop browser. Responsive CSS is included, but physical phone testing and a full treatment booking were not performed.
