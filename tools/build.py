#!/usr/bin/env python3
"""Build a static, content-preserving redesign from the public Haarfillers pages."""
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "source"
ASSETS.mkdir(parents=True, exist_ok=True)
BASE = "https://www.haarfillers.com"
BOOK = "https://booking.sarasinclinic.com/appointment/locations?strict_subcategory_id=58"
PRIORITY = {"/", "/mannen/", "/vrouwen/", "/voor-en-na/", "/prijzen/", "/faq/", "/sarasin-clinic/", "/sarasin-clinic/gent/", "/sarasin-clinic/beveren/", "/sarasin-clinic/ons-team/", "/reviews/", "/videos/"}
SHORT_TITLES = {
    "/": "Haarverlies verdient een persoonlijk plan.",
    "/mannen/": "Haarfillers voor mannen.",
    "/vrouwen/": "Haarfillers voor vrouwen.",
    "/voor-en-na/": "Resultaten die je zelf kunt bekijken.",
    "/prijzen/": "Duidelijkheid over de prijs.",
    "/faq/": "Antwoorden over haarverlies.",
    "/sarasin-clinic/": "Persoonlijke zorg, dichtbij.",
    "/sarasin-clinic/gent/": "Welkom in Gent.",
    "/sarasin-clinic/beveren/": "Welkom in Beveren.",
    "/sarasin-clinic/ons-team/": "De mensen achter Sarasin.",
    "/reviews/": "Ervaringen van onze bezoekers.",
    "/videos/": "Zie hoe de behandeling verloopt.",
}
HERO_DECKS = {
    "/": "Een rustige plek om je haarverlies te begrijpen, echte resultaten te bekijken en samen een persoonlijk plan te maken.",
    "/mannen/": "Van een terugtrekkende haarlijn tot een dunnere kruin: ontdek hoe een persoonlijk behandelplan begint.",
    "/vrouwen/": "Haarverlies kan verschillende oorzaken hebben. We bekijken jouw situatie zorgvuldig, stap voor stap.",
    "/voor-en-na/": "Bekijk foto's uit de bestaande Sarasin Clinic galerij en lees wat realistische verwachtingen zijn.",
    "/prijzen/": "Bekijk de prijs per behandelzone en bespreek het aantal sessies tijdens een gratis consultatie.",
    "/faq/": "Heldere informatie over haaruitval, haarfillers, behandelingen en verwachtingen.",
    "/sarasin-clinic/": "Maak kennis met de mensen en plekken achter je behandeling in Gent en Beveren.",
    "/sarasin-clinic/gent/": "Ontdek de privépraktijk in Sint-Martens-Latem, vlak bij Gent.",
    "/sarasin-clinic/beveren/": "Ontdek onze praktijk in Beveren, vlak bij Antwerpen.",
    "/sarasin-clinic/ons-team/": "Bekijk wie je begeleidt tijdens je consultatie en behandeling.",
    "/reviews/": "Lees bestaande ervaringen van bezoekers en ontdek hoe zij Sarasin Clinic beleven.",
    "/videos/": "Echte behandelbeelden maken de stappen, de omgeving en de ervaring concreter.",
}
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; SarasinRedesign/1.0)"})


def get_pages():
    response = session.get(f"{BASE}/wp-json/wp/v2/pages?per_page=100&_fields=id,link,slug,title", timeout=30)
    response.raise_for_status()
    return [p for p in response.json() if p["link"].startswith(BASE)]


def path_for(url):
    path = urlparse(url).path
    return path if path.endswith("/") else path + "/"


def source_asset(url):
    if not url:
        return None
    if url.startswith("//"):
        url = "https:" + url
    parsed = urlparse(url)
    if parsed.netloc not in {"www.haarfillers.com", "haarfillers.com"}:
        return url
    if "/wp-content/uploads/" not in parsed.path:
        return url
    key = hashlib.sha1(url.encode()).hexdigest()[:10]
    suffix = Path(unquote(parsed.path)).suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif"}:
        suffix = ".jpg"
    filename = f"{key}{suffix}"
    dest = ASSETS / filename
    if not dest.exists():
        try:
            r = session.get(url, timeout=25)
            if r.ok and len(r.content) < 10_000_000 and r.headers.get("content-type", "").startswith("image/"):
                dest.write_bytes(r.content)
        except requests.RequestException:
            pass
    return "/assets/source/" + filename if dest.exists() else url


def clean_fragment(node):
    frag = BeautifulSoup(str(node), "html.parser")
    for el in frag.find_all(["script", "style", "noscript", "input", "svg"]):
        el.decompose()
    for comment in frag.find_all(string=lambda x: isinstance(x, Comment)):
        comment.extract()
    for el in frag.find_all(True):
        if el.parent is None:
            continue
        if el.name in {"iframe", "video", "audio"}:
            # Preserve the original video link as a readable link where available.
            src = el.get("src") or el.get("data-src")
            if src:
                a = frag.new_tag("a", href=src, target="_blank", rel="noopener")
                a.string = "Bekijk de video"
                el.replace_with(a)
            else:
                el.decompose()
            continue
        if el.name == "img":
            src = el.get("src") or el.get("data-src")
            if src:
                el["src"] = source_asset(src)
            el.attrs = {k: v for k, v in el.attrs.items() if k in {"src", "alt", "width", "height"}}
            el["loading"] = "lazy"
            continue
        if el.name == "a":
            href = el.get("href", "#")
            if href.startswith(BASE):
                href = path_for(href)
            if "clone-of-haarfillers-mannen" in href:
                href = "/vrouwen/"
            el.attrs = {"href": href}
            if href.startswith("http"):
                el["rel"] = "noopener"
            continue
        if el.name in {"div", "section", "span", "figure", "figcaption", "button", "form"}:
            if el.name == "figure":
                el.attrs = {}
            else:
                el.unwrap()
            continue
        if el.name not in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "strong", "em", "br", "hr", "small", "sup", "sub"}:
            el.unwrap()
        else:
            el.attrs = {}
    return frag


def extract(page):
    url = page["link"]
    r = session.get(url, timeout=30)
    r.raise_for_status()
    if urlparse(r.url).netloc not in {"www.haarfillers.com", "haarfillers.com"}:
        title_text = BeautifulSoup(page["title"]["rendered"], "html.parser").get_text(" ", strip=True)
        return {"path": path_for(url), "title": title_text, "description": "", "intro": "", "body": "",
                "images": [], "headings": [], "source_url": url, "source_text": "", "redirect": r.url}
    soup = BeautifulSoup(r.text, "html.parser")
    editor = soup.select_one("#tve_editor") or soup.select_one("#content") or soup.body
    title = soup.find("h1") or soup.find("h2")
    title_text = title.get_text(" ", strip=True) if title else BeautifulSoup(page["title"]["rendered"], "html.parser").get_text(" ", strip=True)
    description = soup.find("meta", attrs={"name": "description"})
    description = description.get("content", "") if description else ""
    frag = clean_fragment(editor)
    # An editorial hero carries the original heading; leave the complete source body below it.
    original = frag.find("h1")
    if original:
        original.decompose()
    # Fix an old footer-like link in the source body if it appears there.
    images = [img.get("src") for img in frag.find_all("img") if img.get("src")]
    headings = [h.get_text(" ", strip=True) for h in frag.find_all(["h2", "h3"])]
    paragraphs = [p.get_text(" ", strip=True) for p in frag.find_all("p")]
    intro = next((p for p in paragraphs if len(p) > 75), description)
    return {"path": path_for(url), "title": title_text, "description": description,
            "intro": intro, "body": str(frag), "images": images, "headings": headings,
            "source_url": url, "source_text": editor.get_text(" ", strip=True)}


def category(path):
    if path == "/": return "home"
    if path.startswith("/mannen/"): return "men"
    if path.startswith("/vrouwen/"): return "women"
    if path.startswith("/haartransplantatie/") or path == "/haartransplantatie/": return "transplant"
    if path.startswith("/sarasin-clinic/") or path == "/sarasin-clinic/": return "clinic"
    if path in {"/voor-en-na/", "/reviews/", "/videos/", "/prijzen/"}: return "feature"
    return "guide"


def hero_image(page):
    path = page["path"]
    curated = {
        "/": "/assets/consultation-illustration.png",
        "/mannen/": "https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-man_06.jpg",
        "/vrouwen/": "https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-vrouw_03.jpg",
        "/voor-en-na/": "https://www.haarfillers.com/wp-content/uploads/2023/09/2023-09_haarfiller-man_04.jpg",
        "/sarasin-clinic/gent/": "https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_01.jpg",
        "/sarasin-clinic/beveren/": "https://www.haarfillers.com/wp-content/uploads/2025/02/sarasin-clinic_Beveren_interieur_04-768x1024.jpg",
        "/sarasin-clinic/": "https://www.haarfillers.com/wp-content/uploads/2025/02/SarasinClinic-Beveren-voorkant.jpg",
        "/sarasin-clinic/ons-team/": "https://www.haarfillers.com/wp-content/uploads/2026/09/karen-sarasin.png",
        "/prijzen/": "https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_02.jpg",
        "/reviews/": "https://www.haarfillers.com/wp-content/uploads/2025/02/sarasin-clinic_Beveren_interieur_01-768x1024.jpg",
        "/videos/": "/assets/hairfiller-treatment-poster.jpg",
        "/faq/": "/assets/consultation-illustration.png",
    }
    if path in curated: return source_asset(curated[path])
    for image in page["images"]:
        low = image.lower()
        if not any(x in low for x in ["review", "zone", "logo", ".svg"]): return image
    return "/assets/treatment-process.png"


def escape(s): return html.escape(s or "", quote=True)


def nav():
    return '''<header class="site-header"><a class="brand" href="/" aria-label="Haarfillers home"><span class="brand-mark">S</span><span>SARASIN<span class="brand-small">HAARFILLERS</span></span></a>
    <nav class="desktop-nav" aria-label="Hoofdnavigatie"><a href="/mannen/">Voor mannen</a><a href="/vrouwen/">Voor vrouwen</a><a href="/voor-en-na/">Resultaten</a><a href="/prijzen/">Prijzen</a><a href="/sarasin-clinic/">De clinic</a></nav>
    <a class="header-cta" href="''' + BOOK + '''">Boek consultatie <span aria-hidden="true">↗</span></a><button class="menu-toggle" aria-label="Open menu" aria-expanded="false">☰</button></header>
    <nav class="mobile-nav" aria-label="Mobiele navigatie" hidden><a href="/mannen/">Voor mannen</a><a href="/vrouwen/">Voor vrouwen</a><a href="/voor-en-na/">Resultaten</a><a href="/prijzen/">Prijzen</a><a href="/sarasin-clinic/">De clinic</a><a href="/faq/">Veelgestelde vragen</a><a href="''' + BOOK + '''">Boek consultatie ↗</a></nav>'''


def footer():
    return '''<footer class="site-footer"><div class="footer-top"><div><p class="footer-name">SARASIN</p><p>Haarfillers met persoonlijk advies in Gent en Beveren.</p></div><div><h2>Ontdek</h2><a href="/mannen/">Voor mannen</a><a href="/vrouwen/">Voor vrouwen</a><a href="/voor-en-na/">Resultaten</a><a href="/prijzen/">Prijzen</a><a href="/faq/">FAQ</a></div><div><h2>Bezoek</h2><a href="/sarasin-clinic/gent/">Sint-Martens-Latem (Gent)</a><a href="/sarasin-clinic/beveren/">Beveren</a><a href="/sarasin-clinic/ons-team/">Ons team</a><a href="mailto:welcome@sarasinclinic.com">welcome@sarasinclinic.com</a></div></div><div class="footer-bottom"><span>© 2026 Sarasin Clinic · BE 0681.553.375</span><a href="/privacy-policy/">Privacy Policy</a><a href="/cookie-policy-eu/">Cookiebeleid</a><span>Beeldmateriaal: echte Sarasin-resultaten waar vermeld; behandelingsillustratie is gegenereerd.</span></div></footer>'''


def visual_strip(page):
    images = [i for i in page["images"] if i and "/source/" in i and not any(k in i.lower() for k in ["review", "zone"])]
    uniq = list(dict.fromkeys(images))[:4]
    if len(uniq) < 2: return ""
    return '<section class="visual-strip" aria-label="Beelden bij dit onderwerp"><div class="visual-strip-inner">' + ''.join(f'<figure><img src="{escape(src)}" alt="Beeld bij haarfillers en haarverlies" loading="lazy"></figure>' for src in uniq) + '</div></section>'


def feature_module(page):
    path = page["path"]
    if path == "/":
        man = source_asset("https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-man_06.jpg")
        woman = source_asset("https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-vrouw_03.jpg")
        return f'''<section class="feature-module pathway-module"><div class="module-heading"><p class="section-kicker">KIES JOUW ROUTE</p><h2>Begin bij jouw verhaal.</h2><p>Haarverlies ziet er bij iedereen anders uit. Lees verder over de behandeling, of start met een persoonlijke consultatie.</p></div><div class="pathway-grid"><a href="/mannen/"><img src="{escape(man)}" alt="Haarfiller foto uit de Sarasin Clinic mannengalerij"><span>Voor mannen</span><strong>Behoud en versterk het haar dat er is.</strong><em>Ontdek de behandeling ↗</em></a><a href="/vrouwen/"><img src="{escape(woman)}" alt="Haarfiller foto uit de Sarasin Clinic vrouwengalerij"><span>Voor vrouwen</span><strong>Een plan dat rekening houdt met jouw haarverlies.</strong><em>Ontdek de behandeling ↗</em></a></div></section>'''
    if path == "/prijzen/":
        zones = [
            ("Kleine zone", "1 handpalm · 1 ml", "€210", "https://www.haarfillers.com/wp-content/uploads/2022/06/SarasinClinic_hairfiller_tekening-zone1-200x249-1.png"),
            ("Middelgrote zone", "2 handpalmen · 2 ml", "€310", "https://www.haarfillers.com/wp-content/uploads/2022/06/SarasinClinic_hairfiller_tekening-zone2-200x249-1.png"),
            ("Grote zone", "3 handpalmen · 3 ml", "€415", "https://www.haarfillers.com/wp-content/uploads/2022/06/SarasinClinic_hairfiller_tekening-zone3-200x249-1.png"),
        ]
        cards = ''.join(f'<div class="price-card"><img src="{escape(source_asset(im))}" alt="Illustratie {escape(name.lower())}"><div><h3>{name}</h3><p>{size}</p><strong>{price}</strong><span>per sessie</span></div></div>' for name,size,price,im in zones)
        return '<section class="feature-module price-module"><div class="module-heading"><p class="section-kicker">TRANSPARANTE PRIJZEN</p><h2>Een helder overzicht per zone.</h2><p>Het aantal behandelingen en de geschikte zone worden tijdens een consultatie besproken.</p></div><div class="price-grid">'+cards+'</div></section>'
    if path in {"/mannen/", "/vrouwen/"}:
        poster = "/assets/hairfiller-women-poster.jpg" if path == "/vrouwen/" else "/assets/hairfiller-treatment-poster.jpg"
        video = "/assets/hairfiller-women.mp4" if path == "/vrouwen/" else "/assets/hairfiller-treatment.mp4"
        return f'''<section class="feature-module journey-module"><div class="module-heading"><p class="section-kicker">ZO VERLOOPT HET</p><h2>Vier momenten in je behandeltraject.</h2><p>Bekijk echte Sarasin Clinic beelden van de hoofdhuid en de behandeling.</p></div><div class="journey-layout"><div class="journey-steps"><p><strong>01 · Consultatie</strong><span>We bekijken je hoofdhuid, haarverlies en verwachtingen.</span></p><p><strong>02 · Persoonlijk plan</strong><span>De behandelaar bespreekt of haarfillers passend zijn.</span></p><p><strong>03 · Behandeling</strong><span>De injecties worden in de gekozen zones toegediend.</span></p><p><strong>04 · Opvolging</strong><span>We evalueren het verloop en bespreken eventuele onderhoudssessies.</span></p></div><figure><video controls preload="none" poster="{poster}" aria-label="Sarasin Clinic haarfiller behandelvideo"><source src="{video}" type="video/mp4">Je browser ondersteunt deze video niet.</video><figcaption>Beeld uit een bestaande Sarasin Clinic behandelvideo.</figcaption></figure></div></section>'''
    if path == "/voor-en-na/":
        urls = [
            "https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-vrouw_03.jpg",
            "https://www.haarfillers.com/wp-content/uploads/2022/12/2022-12-23_SarasinClinic_Haarfiller-man_06.jpg",
            "https://www.haarfillers.com/wp-content/uploads/2023/09/2023-09_haarfiller-man_04.jpg",
            "https://www.haarfillers.com/wp-content/uploads/2023/09/2023-09_haarfiller-vrouw_01.jpg",
        ]
        tiles = ''.join(f'<figure><img src="{escape(source_asset(u))}" alt="Haarfiller resultaat uit de Sarasin Clinic galerij" loading="lazy"><figcaption>Foto uit de bestaande Sarasin Clinic resultatengalerij</figcaption></figure>' for u in urls)
        return '<section class="feature-module results-module"><div class="module-heading"><p class="section-kicker">ECHTE RESULTATEN</p><h2>Bekijk de verandering van dichtbij.</h2><p>De beelden komen uit de bestaande Sarasin Clinic galerij. Resultaten verschillen per persoon.</p></div><div class="results-grid">'+tiles+'</div></section>'
    if path == "/sarasin-clinic/":
        places = [
            ("Sint-Martens-Latem", "Kortrijksesteenweg 20, 9830 Sint-Martens-Latem", "/sarasin-clinic/gent/", "https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_01.jpg"),
            ("Beveren", "Gentseweg 436, 9120 Beveren", "/sarasin-clinic/beveren/", "https://www.haarfillers.com/wp-content/uploads/2025/02/sarasin-clinic_Beveren_interieur_04-768x1024.jpg"),
        ]
        return '<section class="feature-module places-module"><div class="module-heading"><p class="section-kicker">TWEE LOCATIES</p><h2>Een plek waar je je op je gemak voelt.</h2></div><div class="places-grid">'+''.join(f'<a href="{link}"><img src="{escape(source_asset(im))}" alt="Sarasin Clinic {name}"><h3>{name} ↗</h3><p>{address}</p></a>' for name,address,link,im in places)+'</div></section>'
    if path == "/sarasin-clinic/ons-team/":
        people = [
            ("Karen Sarasin", "Esthetisch verpleegkundige", "https://www.haarfillers.com/wp-content/uploads/2026/09/karen-sarasin.png"),
            ("Dr. Van Gasse", "Arts", "https://www.haarfillers.com/wp-content/uploads/2026/09/Dr.-Van-Gasse.png"),
            ("Dr. Zin Mar Aung", "Arts", "https://www.haarfillers.com/wp-content/uploads/2026/09/Dr.Zin-Mar-Aung.png"),
            ("Nurse Hayat", "Esthetisch verpleegkundige", "https://www.haarfillers.com/wp-content/uploads/2026/09/Nurse-Hayat.png"),
            ("Dr. Debeuf", "Arts", "https://www.haarfillers.com/wp-content/uploads/2026/09/Dr.-Debeuf.png"),
            ("Dr. Monné", "Arts", "https://www.haarfillers.com/wp-content/uploads/2026/09/Dr.-Monne.png"),
        ]
        return '<section class="feature-module team-module"><div class="module-heading"><p class="section-kicker">HET TEAM</p><h2>De mensen achter je behandeling.</h2></div><div class="team-grid">'+''.join(f'<figure><img src="{escape(source_asset(im))}" alt="{escape(name)}"><figcaption><strong>{escape(name)}</strong><span>{role}</span></figcaption></figure>' for name,role,im in people)+'</div></section>'
    if path == "/faq/":
        topics = [
            ("Wat zijn haarfillers?", "Zo werkt de behandeling en voor wie ze bedoeld is.", "/faq/wat-zijn-haarfillers/", "✦"),
            ("Waarom verlies ik haar?", "Lees over oorzaken van zichtbaar haarverlies.", "/faq/veel-haarverlies/", "↘"),
            ("Welke behandeling past?", "Vergelijk mogelijke routes en verwachtingen.", "/faq/haaruitval-behandeling/", "○"),
            ("Hoe groeit haar?", "Begrijp de haarcyclus en wat normaal is.", "/faq/hoe-snel-groeien-haren/", "⌁"),
        ]
        cards = ''.join(f'<a href="{link}"><span class="topic-icon" aria-hidden="true">{icon}</span><h3>{name}</h3><p>{desc}</p><span class="topic-arrow" aria-hidden="true">↗</span></a>' for name,desc,link,icon in topics)
        return '<section class="feature-module topics-module"><div class="module-heading"><p class="section-kicker">INFORMATIEHUB</p><h2>Begin met de vraag die jij hebt.</h2><p>De volledige vragen en antwoorden staan verderop op deze pagina.</p></div><div class="topic-grid">'+cards+'</div><p class="illustration-note">De consultatiefoto bovenaan is een illustratie, geen echte Sarasin-patiënt of behandelaar.</p></section>'
    if path in {"/sarasin-clinic/gent/", "/sarasin-clinic/beveren/"}:
        gent = path.endswith("gent/")
        name = "Sint-Martens-Latem (Gent)" if gent else "Beveren"
        address = "Kortrijksesteenweg 20, 9830 Sint-Martens-Latem" if gent else "Gentseweg 436, 9120 Beveren"
        first = "https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_03.jpg" if gent else "https://www.haarfillers.com/wp-content/uploads/2025/02/sarasin-clinic_Beveren_interieur_01-768x1024.jpg"
        second = "https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_05.jpg" if gent else "https://www.haarfillers.com/wp-content/uploads/2025/02/sarasin-clinic_Beveren_interieur_03-768x1024.jpg"
        map_url = "https://www.google.com/maps/search/?api=1&query=" + ("Kortrijksesteenweg+20+9830+Sint-Martens-Latem" if gent else "Gentseweg+436+9120+Beveren")
        return f'''<section class="feature-module location-module"><div class="module-heading"><p class="section-kicker">BEZOEK ONS</p><h2>Voel je welkom in {name}.</h2></div><div class="location-layout"><div class="location-photos"><img src="{escape(source_asset(first))}" alt="Interieur Sarasin Clinic {name}"><img src="{escape(source_asset(second))}" alt="Behandelruimte Sarasin Clinic {name}"></div><div class="location-details"><p class="section-kicker">CONTACTGEGEVENS</p><h3>{name}</h3><p>{address}</p><p><a href="tel:+32476689799">+32 476 68 97 99</a><br><a href="mailto:welcome@sarasinclinic.com">welcome@sarasinclinic.com</a></p><a class="button-primary" href="{BOOK}">Boek een afspraak ↗</a><a class="inline-link" href="{map_url}" target="_blank" rel="noopener">Plan je route ↗</a></div></div></section>'''
    if path == "/reviews/":
        shots = [f"https://www.haarfillers.com/wp-content/uploads/2026/01/haarfiller_review_{i}.png" for i in (1,2,3,4)]
        gallery = ''.join(f'<figure><img src="{escape(source_asset(u))}" alt="Bestaande Sarasin Clinic reviewafbeelding" loading="lazy"></figure>' for u in shots)
        return '<section class="feature-module review-feature"><div class="module-heading"><p class="section-kicker">ERVARINGEN</p><h2>Lees hoe bezoekers hun bezoek beleefden.</h2><p>De beoordelingen komen uit de bestaande Sarasin Clinic reviewcollectie. Sommige gaan over de clinic in het algemeen; ervaringen met haarfillers vind je in de volledige inhoud hieronder.</p></div><div class="review-mosaic">'+gallery+'</div></section>'
    if path == "/videos/":
        return '''<section class="feature-module video-feature"><div class="module-heading"><p class="section-kicker">BEKIJK DE BEHANDELING</p><h2>Zie de stappen in plaats van ze alleen te lezen.</h2><p>Twee bestaande Sarasin Clinic video's tonen hoe de hoofdhuid wordt voorbereid en hoe een behandeling verloopt.</p></div><div class="video-grid"><figure><video controls preload="none" poster="/assets/hairfiller-treatment-poster.jpg" aria-label="Haarfiller behandeling"><source src="/assets/hairfiller-treatment.mp4" type="video/mp4">Je browser ondersteunt deze video niet.</video><figcaption><strong>Behandeling in beeld</strong><span>Haarfiller behandeling bij Sarasin Clinic</span></figcaption></figure><figure><video controls preload="none" poster="/assets/hairfiller-women-poster.jpg" aria-label="Haarfiller behandeling bij een vrouw"><source src="/assets/hairfiller-women.mp4" type="video/mp4">Je browser ondersteunt deze video niet.</video><figcaption><strong>Behandeling bij vrouwen</strong><span>Hoofdhuid en behandelzone van dichtbij</span></figcaption></figure></div></section>'''
    return ""


def home_essentials():
    topics = [
        ("Wat zijn haarfillers?", "Hair Fillers bevatten onder andere hyaluronzuur en een complex van biomimetische peptiden. De behandeling wordt met kleine injecties in de hoofdhuid toegepast."),
        ("Voor wie is de behandeling bedoeld?", "Haarfillers kunnen worden besproken bij beginnend of matig haarverlies, zowel bij mannen als vrouwen. Tijdens een consultatie bekijken we de conditie van je hoofdhuid en haarzakjes."),
        ("Hoe ziet een behandeltraject eruit?", "Na de analyse bespreekt de behandelaar de geschikte zones en het aantal sessies. Een behandeling duurt gemiddeld 30 minuten; opvolging en eventuele onderhoudssessies zijn persoonlijk."),
    ]
    items = ''.join(f'<details class="essential-item"><summary><span>{escape(question)}</span><span class="essential-plus" aria-hidden="true"></span></summary><p>{escape(answer)}</p></details>' for question,answer in topics)
    return f'''<section class="home-essentials" aria-labelledby="essentials-title"><div class="essentials-intro"><h2 id="essentials-title">Haarfillers, helder uitgelegd.</h2><p>De belangrijkste informatie op één plek. Verdiep je daarna in de behandeling die bij jouw situatie past.</p><a href="/faq/">Bekijk alle vragen <span aria-hidden="true">↗</span></a></div><div class="essentials-list">{items}</div></section>'''


def home_reviews():
    quotes = [
        ("Heel vriendelijke ontvangst, en duidelijke uitleg. Ik kwam voor de hairfiller behandeling, en ben nu heel benieuwd naar het resultaat", "Anja", "Ervaring met een haarfillerbehandeling"),
        ("Heel vriendelijke ontvangst en je wordt heel goed begeleid en geïnformeerd over wat er precies gaat gebeuren tijdens de behandeling. Zeer aan te raden !", "Wendy N.", "Ervaring met Sarasin Clinic"),
        ("Een zeer vriendelijke ontvangst gevolgd door een professionele analyse. Ik voelde ook het enthousiasme voor het vak wat altijd veel vertrouwen geeft. Ik boek snel mijn volgende sessie in.", "Edward R.", "Ervaring met Sarasin Clinic"),
    ]
    cards = ''.join(f'<figure class="home-review"><blockquote>“{escape(quote)}”</blockquote><figcaption><strong>{escape(name)}</strong><span>{escape(context)}</span></figcaption></figure>' for quote,name,context in quotes)
    return f'''<section class="home-reviews" aria-labelledby="home-reviews-title"><div class="home-reviews-head"><div><h2 id="home-reviews-title">Ervaringen, in eigen woorden.</h2><p>Reacties uit de bestaande Sarasin Clinic reviewcollectie. Sommige ervaringen gaan over de clinic in het algemeen.</p></div><a href="/reviews/">Bekijk alle reviews <span aria-hidden="true">↗</span></a></div><div class="home-review-grid">{cards}</div></section>'''


def page_html(page):
    if page.get("redirect"):
        dest = escape(page["redirect"])
        return f'<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={dest}"><meta name="robots" content="noindex"><title>Afspraak boeken | Sarasin Clinic</title></head><body><p>Je wordt doorgestuurd naar de boekingspagina. <a href="{dest}">Open de boekingspagina</a>.</p></body></html>'
    path = page["path"]
    is_home = path == "/"
    label = {"home":"SARASIN CLINIC", "men":"VOOR MANNEN", "women":"VOOR VROUWEN", "clinic":"ONZE CLINIC", "feature":"ONTDEK MEER", "guide":"HAAR & HOOFDHUID", "transplant":"BEHANDELINGEN"}[category(path)]
    photo = hero_image(page)
    title = escape(page["title"])
    display_title = escape(SHORT_TITLES.get(path, page["title"]))
    desc = escape(HERO_DECKS.get(path, page["intro"][:400]))
    caption = "Illustratieve consultatiescène · geen Sarasin-patiënt of medewerker" if path in {"/", "/faq/"} else "Sarasin Clinic · Gent & Beveren"
    route_class = "route-" + (path.strip("/").replace("/", "-") or "home")
    priority_css = '<link rel="stylesheet" href="/assets/priority.css">' if path in PRIORITY else ''
    head = f'''<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#18352d"><meta name="robots" content="noindex,follow"><title>{title} | Sarasin Clinic</title><meta name="description" content="{escape(page['description'] or page['intro'][:150])}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css">{priority_css}<script defer src="/assets/site.js"></script></head><body class="page-{category(path)} {route_class}">'''
    hero = f'''<section class="hero"><div class="hero-photo"><img src="{escape(photo)}" alt="{display_title}" fetchpriority="high"></div><div class="hero-shade"></div><div class="hero-inner"><p class="hero-kicker">{label}</p><h1>{display_title}</h1><p class="hero-intro">{desc}</p><div class="hero-actions"><a class="button-primary" href="{BOOK}">Boek gratis consultatie <span aria-hidden="true">↗</span></a><a class="button-text" href="/voor-en-na/">Bekijk resultaten <span aria-hidden="true">↗</span></a></div></div><div class="hero-caption">{caption}</div></section>'''
    if is_home:
        quick = '''<section class="quick-facts"><div><span class="fact-icon">⌁</span><strong>Persoonlijk behandelplan</strong><p>Start met een gratis consultatie.</p></div><div><span class="fact-icon">◷</span><strong>30 minuten</strong><p>Gemiddelde behandeltijd.</p></div><div><span class="fact-icon">€</span><strong>Vanaf €210</strong><p>Per sessie, afhankelijk van de zone.</p></div></section>'''
        process = '''<section class="process-feature"><div class="process-image"><video controls preload="none" poster="/assets/hairfiller-treatment-poster.jpg" aria-label="Sarasin Clinic behandelvideo"><source src="/assets/hairfiller-treatment.mp4" type="video/mp4">Je browser ondersteunt deze video niet.</video></div><div class="process-copy"><p class="section-kicker">DE BEHANDELING</p><h2>Van analyse tot persoonlijk plan.</h2><p>Een consultatie brengt je haarconditie en verwachtingen in kaart. Daarna bespreekt de behandelaar of haarfillers voor jou geschikt zijn en hoe een behandeltraject kan verlopen.</p><p class="image-disclosure">Echte beelden uit een bestaande Sarasin Clinic behandelvideo.</p><a class="inline-link" href="/videos/">Bekijk alle video's ↗</a></div></section>'''
    else:
        quick = ""
        process = ""
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span>{title}</span></div>'
    contents = ''.join(f'<a href="#section-{i}">{escape(h)}</a>' for i,h in enumerate(page["headings"][:12],1) if h)
    body = BeautifulSoup(page["body"], "html.parser")
    for p in body.find_all("p"):
        plain = p.get_text(" ", strip=True)
        if len(plain) > 1200 and plain.count("★") >= 10:
            details = body.new_tag("details", attrs={"class": "review-archive"})
            summary = body.new_tag("summary")
            summary.string = "Lees alle ervaringen en reviews"
            details.append(summary)
            p.wrap(details)
    for i,h in enumerate(body.find_all("h2"),1): h["id"] = f"section-{i}"
    article_lead = f'<div class="article-lead"><p class="section-kicker">VOLLEDIGE INFORMATIE</p><h2>{title}</h2><p>Lees hieronder alle informatie van de bestaande website over dit onderwerp.</p></div>' if path in PRIORITY and not is_home else ''
    article = home_essentials() + home_reviews() if is_home else f'''<section class="article-shell">{breadcrumb}{article_lead}<div class="article-grid"><aside class="article-aside"><p>Op deze pagina</p><nav aria-label="Op deze pagina">{contents}</nav><a href="{BOOK}">Maak een afspraak ↗</a></aside><article class="source-content">{body}</article></div></section>'''
    nearby = '''<section class="next-steps"><p class="section-kicker">VERDER LEZEN</p><h2>Een volgende stap, op jouw tempo.</h2><div><a href="/voor-en-na/"><span>01</span><strong>Bekijk echte resultaten</strong><span>↗</span></a><a href="/prijzen/"><span>02</span><strong>Ontdek de prijzen</strong><span>↗</span></a><a href="/sarasin-clinic/ons-team/"><span>03</span><strong>Maak kennis met het team</strong><span>↗</span></a></div></section>'''
    closing_photo = source_asset("https://www.haarfillers.com/wp-content/uploads/2022/11/SarasinClinic_interieur_Gent_06.jpg") if path in PRIORITY else "/assets/treatment-process.png"
    closing_alt = "Interieur Sarasin Clinic Gent" if path in PRIORITY else "Illustratieve behandeling in een clinic"
    closing = f'''<section class="closing"><div><p class="section-kicker">SARASIN CLINIC</p><h2>Goed advies begint met goed kijken.</h2><p>Vertel ons wat je merkt aan je haar. Tijdens een gratis consultatie bekijken we samen wat voor jou passend is.</p><a class="button-primary" href="{BOOK}">Boek gratis consultatie ↗</a></div><img src="{escape(closing_photo)}" alt="{closing_alt}" loading="lazy"></section>'''
    strip = "" if path in PRIORITY else visual_strip(page)
    return head + nav() + hero + quick + process + feature_module(page) + strip + article + nearby + closing + footer() + '</body></html>'


def main():
    pages = get_pages()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(extract, pages))
    index = []
    for page in results:
        target = ROOT / page["path"].lstrip("/") / "index.html"
        if page["path"] == "/": target = ROOT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_html(page), encoding="utf-8")
        index.append({k: page[k] for k in ["path", "title", "source_url", "source_text"]})
    routes = {p["path"] for p in index}
    aliases = {
        "/haargroei-supplementen/": "/faq/haargroei-supplementen/",
        "/haaruitval-behandeling/": "/faq/haaruitval-behandeling/",
        "/wat-zijn-haarfillers/": "/faq/wat-zijn-haarfillers/",
        "/faq/haaruitval-stress/": "/haarfillers/haaruitval-stress/",
        "/vrouwen/haaruitval-na-zwangerschap/": "/vrouwen/haaruitval-na-bevalling/",
        "/vrouwen/haaruitval-vrouwen-overgang/": "/vrouwen/haaruitval-menopauze/",
        "/haaruitval-stress/": "/haarfillers/haaruitval-stress/",
        "/veel-haarverlies/": "/faq/veel-haarverlies/",
        "/hoe-snel-groeien-haren/": "/faq/hoe-snel-groeien-haren/",
        "/dun-haar-hoofdhuid-te-zien/": "/faq/dun-haar-hoofdhuid-te-zien/",
        "/mannen/oorzaken-haaruitval/": "/mannen/oorzaken-haarverlies/",
        "/mannen/haaruitval-oorzaken-en-oplossingen/": "/mannen/oorzaken-haarverlies/",
        "/vrouwen/haaruitval/kruin/": "/vrouwen/haaruitval/",
        "/vrouwen/haaruitval/schildklier/": "/vrouwen/oorzaken-haaruitval/",
        "/vrouwen/haaruitval/haarkliniek-gent/": "/sarasin-clinic/gent/",
    }
    for page in results:
        target = ROOT / page["path"].lstrip("/") / "index.html" if page["path"] != "/" else ROOT / "index.html"
        soup = BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser")
        changed = False
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("/") or href.startswith("//"):
                continue
            parsed = urlparse(href)
            route = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
            if route == "/boek-afspraak/":
                a["href"] = BOOK
            elif route not in routes and not Path(parsed.path).suffix:
                a["href"] = aliases.get(route, BASE + href)
            else:
                continue
            changed = True
        if changed:
            target.write_text(str(soup), encoding="utf-8")
    (ROOT / "content-inventory.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    # Public review deployment duplicates the live copy, so it deliberately has no sitemap.
    print(f"Built {len(results)} routes; downloaded {len(list(ASSETS.iterdir()))} source images")


if __name__ == "__main__": main()
