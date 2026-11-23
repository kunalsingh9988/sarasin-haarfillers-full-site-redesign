# Sarasin Haarfillers minisite

Static Dutch site built from the public Haarfillers site and the main Sarasin Clinic Hairfiller material.

## Run locally

```sh
python3 -m http.server 8787
```

To rebuild with Python and the `requests` and `beautifulsoup4` packages installed:

```sh
python3 tools/build.py
```

The generator imports the existing Haarfillers routes and the Dutch clinic resources listed in `tools/clinic_content.py`. That file also holds the patient questions and treatment-team data. `content-inventory.json` records source URLs. Separate clinical approval is still pending for the patient answers and inherited treatment claims.

## Brand and imagery

- The site uses the exact Sarasin wordmark vector from the public [webshop](https://www.sarasin.shop/) with a separate Clinic line.
- The waiting area, reception and treatment-room photos come from the official [Beveren location page](https://sarasinclinic.com/the-clinic/beveren/). The Beveren page links to Sarasin Clinic’s [Beveren sneak peek](https://www.youtube.com/watch?v=mkb5j9Rtv8U).
- The four doctors listed for Hairfiller and their RIZIV numbers are sourced from the [Sarasin Clinic team](https://sarasinclinic.com/over-ons/team/). The doctor cards link to the most specific official profile available.
- Existing patient results come from the clinic’s public photo gallery. Illustrative consultation images are identified where used.

## Search access

`tools/build.py` generates the canonical URLs, sitemap, and robots.txt for the public Vercel host. Booking, thank-you, and policy pages are excluded from the sitemap. If the indexed hostname changes, update `PUBLIC_SITE` and regenerate before publishing. Google and OpenAI decide when to crawl and which pages to show. Actual crawl records require Search Console or hosting logs.
