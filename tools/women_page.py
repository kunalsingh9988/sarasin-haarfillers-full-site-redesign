"""Editorial Hairfiller route. Render treatment copy from the existing Dutch source."""
from __future__ import annotations

from html import escape
from urllib.parse import urlparse

from bs4 import BeautifulSoup

MEDIA = "/assets/women/"
WOMEN_STILL = "/assets/hairfiller-women-poster.jpg"
LONGEVITY = "https://www.sarasin.shop/pages/skin-longevity-wat-is-het-en-hoe-werkt-het"
CLINIC_CARE = "https://sarasinclinic.com/behandelingen/hairfiller/"
ANATOMY = "https://commons.wikimedia.org/wiki/File:Gray944.png"
VIDEO_THUMBNAILS = {
    "OeLGZdJCpUE": ("Hairfiller uitgelegd", "Animatie van haarzakjes en haargroeisignalen", "video-behandeling.webp"),
    "M76uytFjRjo": ("Voor en na bij een vrouw", "Behandelaar toont een eerdere hoofdhuidfoto op een telefoon", "video-resultaat.webp"),
}
RESULT_ALT = {
    "59c9b97482": "Middenscheiding bij lang bruin haar",
    "23b6205d2a": "Kruin bij donker haar",
    "fe5b164a47": "Bovenkant van het hoofd bij lichtblond haar",
    "9e591cbf99": "Middenscheiding bij donkerbruin haar, van bovenaf gefotografeerd",
    "09e10fb52c": "Haarlijn bij de slaap, van opzij gefotografeerd",
    "ba40f20970": "Bovenkant van het hoofd bij lang, lichtbruin haar",
    "59b809deea": "Close-up van een scheiding bij lichtbruin haar met blonde lokken",
}


def _source_blocks(body):
    soup = BeautifulSoup(body, "html.parser")
    editor = soup.find(id="tve_editor") or soup
    preface = []
    blocks = {}
    current = preface
    for element in editor.find_all(recursive=False):
        if element.name == "h2" and element.get("id"):
            current = blocks.setdefault(element["id"], [])
        current.append(element)
    return preface, blocks


def _html(elements):
    return "\n".join(str(element) for element in elements)


def _photo(name, alt, placement, *, priority=False, caption="Illustratieve fotografie"):
    sizes = "(max-width: 720px) calc(100vw - 32px), (max-width: 1600px) 50vw, 820px"
    widths = (480, 960, 1440) if name in {"hero", "closing"} else (480, 960)
    candidates = ", ".join(f"{MEDIA}{name}-{width}.webp {width}w" for width in widths)
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    if placement == "concern":
        sizes = "(max-width: 520px) 40vw, (max-width: 1600px) 30vw, 460px"
    if placement == "routine":
        sizes = "(max-width: 720px) 55vw, 30vw"
    caption_html = f"\n        <figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f'''<figure class="wf-photo wf-photo--{placement}">
        <img src="{MEDIA}{name}-960.webp" srcset="{candidates}" sizes="{sizes}"
             alt="{escape(alt)}" decoding="async" {loading}>{caption_html}
    </figure>'''


def _disclosure(label, content, icon):
    return f'''<details class="wf-disclosure"><summary><span>{escape(label)}</span>
        {icon("plus", "wf-expand")}{icon("minus", "wf-collapse")}</summary>
        <div class="wf-disclosure-body">{content}</div></details>'''


def _result_photos(images):
    photos = []
    for index, image in enumerate(images, 1):
        # The clinic supplied complete comparison photographs. Keep their bytes and dimensions.
        file_stem = image["src"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        thumb = image["src"]
        if file_stem in RESULT_ALT:
            image["alt"] = f"{RESULT_ALT[file_stem]} voor en na Hairfiller bij Sarasin Clinic"
            thumb = f"{MEDIA}thumb-{file_stem}.webp"
        elif not image.get("alt"):
            image["alt"] = f"Voor en na Hairfiller bij Sarasin Clinic, foto {index}"
        image["loading"] = "lazy"
        image["decoding"] = "async"
        photos.append(f'''<figure class="wf-case" data-case data-thumbnail="{escape(thumb)}">
            <a class="wf-original" href="{escape(image['src'])}">{image}</a>
            <figcaption>Resultaat {index} · Voor en na</figcaption>
        </figure>''')
    return "".join(photos)


def _videos(video_links, icon):
    cards = []
    for link in video_links:
        video_id = urlparse(link["href"]).path.rsplit("/", 1)[-1]
        label, alt, filename = VIDEO_THUMBNAILS.get(video_id, ("Video van Sarasin Clinic", "Behandelaar bij de hoofdhuid", ""))
        thumbnail = MEDIA + filename if filename else WOMEN_STILL
        description = link.get_text(" ", strip=True).removeprefix("Video · ")
        cards.append(f'''<a class="wf-video-card" href="{escape(link['href'])}" data-youtube="{escape(video_id)}">
            <span class="wf-video-thumb"><img src="{thumbnail}" alt="{escape(alt)}"
                width="480" height="360" loading="lazy" decoding="async">{icon("play")}</span>
            <span><strong>{escape(label)}</strong><small>{escape(description)}</small></span>
        </a>''')
    return "".join(cards)


def _pricing(block):
    table = next(element for element in block if element.name == "table")
    diagrams = [element for element in block if element.name == "img"]
    cards = []
    for row, diagram in zip(table.select("tbody tr"), diagrams, strict=True):
        zone, price = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        title, _, volume = zone.partition(" (")
        diagram["decoding"] = "async"
        cards.append(f'''<li><div>{diagram}</div><h3>{escape(title)}</h3>
            <p>{escape(volume.rstrip(')'))}</p><p class="wf-price">{escape(price)} <small>per sessie</small></p></li>''')
    description = next(element for element in block[1:] if element.name == "p")
    return f'''{description}<h3 class="wf-sr-only" id="t-1769769421106">Haarfiller prijzen per zone</h3>
        <ul class="wf-price-grid" id="{escape(table.get('id', 'prijzen-per-zone'))}" role="list">{''.join(cards)}</ul>
        <p class="wf-small">Tijdens je consultatie krijg je een indicatie van de kosten en de grootte van de te behandelen zone.</p>'''


def _faq(elements, icon):
    items = []
    title = None
    answer = []
    for element in elements:
        if element.name in {"h3", "h4", "h5", "h6"}:
            if title:
                items.append(_disclosure(title, _html(answer), icon))
            title = element.get_text(" ", strip=True)
            answer = []
        else:
            answer.append(element)
    if title:
        items.append(_disclosure(title, _html(answer), icon))
    return "".join(items)


def render_women(body, heading, intro, book, book_label, icon):
    preface, blocks = _source_blocks(body)
    treatment = blocks["t-1769769421101"]
    suitability = blocks["t-1769769421102"]
    benefits = blocks["t-1769769421103"]
    result = blocks["t-1769769421104"]
    pricing = blocks["t-1769769421105"]
    faq = blocks["t-1771585826171"]
    expert = blocks["t-1769769421110"]
    feedback = blocks["t-1769769421111"]
    related = blocks["t-1769769421112"]
    video_links = [element for element in suitability if element.name == "a" and "youtube.com/embed/" in element.get("href", "")]
    results = [element for element in result if element.name == "img"]
    research = [element for element in feedback if "1832134" in element.get_text()]
    reviews = [element for element in feedback[1:] if element not in research]
    suitability_copy = [element for element in suitability[1:] if element not in video_links]
    facts = (
        ("euro", "Richtprijs per sessie", "Vanaf €210"),
        ("clock-3", "Behandeltijd", "30 minuten"),
        ("chart-no-axes-combined", "Effect volgens de clinic", "Na 3–6 maanden"),
        ("list-checks", "Hersteltijd", "Geen geplande hersteltijd"),
    )
    strip = "".join(f'<div>{icon(symbol)}<dt>{label}</dt><dd>{value}</dd></div>' for symbol, label, value in facts)
    concerns = (
        ("thinning", "Dunner wordend haar", "Je scheiding kan breder lijken wanneer je haar geleidelijk dunner wordt.",
         "Close-up van lichtbruin haar met een zichtbare middenscheiding"),
        ("volume", "Minder volume", "Misschien voelt je paardenstaart dunner aan of valt je haar anders dan vroeger.",
         "Zijaanzicht van een vrouw die haar fijne, donkere paardenstaart vasthoudt"),
        ("hormones", "Hormonale veranderingen", "De clinic noemt onder meer de periode na zwangerschap en de overgang.",
         "Vrouw met zilvergrijs haar bij een raam"),
    )
    cards = "".join(f'''<article class="wf-concern">{_photo(name, alt, "concern", caption="")}
        <h3>{label}</h3><p>{description}</p></article>''' for name, label, description, alt in concerns)
    steps = (
        ("Persoonlijke consultatie", "We bespreken wat je merkt en wat je verwacht."),
        ("Haar- en hoofdhuidanalyse", "We bekijken je hoofdhuid, haarverlies en mogelijke oorzaken."),
        ("Persoonlijk behandelplan", "Je behandelaar bespreekt of Hairfiller past en welke zones in aanmerking komen."),
        ("Behandeling en opvolging", "We evalueren het verloop en bespreken eventuele onderhoudssessies."),
    )
    timeline = "".join(f'<li><span>{number:02d}</span><h3>{label}</h3><p>{content}</p></li>'
                       for number, (label, content) in enumerate(steps, 1))

    def booking(label=book_label):
        return f'<a class="button-primary wf-book" href="{escape(book)}">{escape(label)} {icon("arrow-up-right")}</a>'

    def jump(url, label, symbol="arrow-right"):
        return f'<a class="wf-link" href="{escape(url)}">{escape(label)} {icon(symbol)}</a>'

    sections = (
        ("haaruitval", "Haaruitval", False), ("t-1769769421101", "Behandeling", False),
        ("resultaten", "Resultaten", True), ("t-1769769421105", "Prijzen", True),
        ("voor-en-nazorg", "Nazorg", True), ("t-1771585826171", "Veelgestelde vragen", True),
    )
    desktop_only = ' class="wf-desktop-jump"'
    navigation = "".join(f'<a href="#{anchor}"{"" if mobile else desktop_only}>{label}</a>'
                         for anchor, label, mobile in sections)
    review_intro = [element for element in preface if "4,8 op 5" in element.get_text()]
    guide_material = [element for element in preface if element not in review_intro and element.name != "hr"]
    keep = lambda elements: _html(element for element in elements if element.name != "a")
    treatment_medicine = [element for element in treatment[1:] if element.name == "p"]
    qualifying_text = next(element for element in suitability_copy if element.name == "p")
    benefit_list = next(element for element in benefits if element.name == "ul")
    body_copy = keep(element for element in benefits[1:] if element is not benefit_list)
    benefit_rows = "".join(
        f'<li>{icon(symbol)}<span>{item.decode_contents()}</span></li>'
        for symbol, item in zip(("syringe", "clock-3", "images", "sprout", "chart-no-axes-combined", "clipboard-list"),
                                benefit_list.find_all("li", recursive=False), strict=True)
    )
    return f'''
    <section class="wf-hero wf-wrap" aria-labelledby="wf-title">
      <div class="wf-hero-copy">
        <nav class="wf-breadcrumb" aria-label="Broodkruimelpad"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Voor vrouwen</span></nav>
        <p class="wf-kicker">Hairfiller in Gent en Beveren</p>
        <h1 id="wf-title">{heading}</h1>
        <p class="wf-lead">{intro}</p>
        <div class="wf-actions">{booking()}{jump('#resultaten', 'Bekijk voor en na')}</div>
      </div>
      {_photo("hero", "Vrouw met los bruin haar in zacht daglicht", "hero", priority=True)}
    </section>
    <section class="wf-facts" aria-label="Hairfiller in het kort"><dl class="wf-wrap">{strip}</dl></section>
    <nav class="wf-sticky" aria-label="Op deze pagina" id="pagina-informatie"><div class="wf-wrap">{navigation}</div></nav>
    <section class="wf-section wf-wrap wf-split wf-understanding" id="haaruitval">
      {_photo("understanding", "Vrouw met donkerblond haar bekijkt een haarlok bij het raam", "portrait")}
      <div class="wf-copy" id="tve_editor">
        <h2>Als je haar verandert</h2>
        <p class="wf-lead">Merk je dat je haar dunner aanvoelt of anders valt? Samen bekijken we wat er bij jou speelt.</p>
        {qualifying_text}
        {_disclosure("Meer over haaruitval en deze behandeling", _html(guide_material), icon)}
      </div>
    </section>
    <section class="wf-section wf-concerns" id="t-1769769421102">
      <div class="wf-wrap">
        <div class="wf-section-head"><h2>Wat merk je aan je haar?</h2><p>Haarverlies ziet er niet voor iedereen hetzelfde uit.</p></div>
        <div class="wf-concern-grid">{cards}</div><p class="wf-small">Illustratieve fotografie</p>
        {_disclosure("Voor wie zijn haarfillers geschikt?", _html(element for element in suitability_copy if element is not qualifying_text), icon)}
      </div>
    </section>
    <section class="wf-section wf-wrap wf-split wf-clinical" id="t-1769769421101">
      <div class="wf-copy">
        <h2>Wat is Hairfiller?</h2>
        {treatment_medicine[0]}
        {treatment_medicine[-1]}
        {booking()}
      </div>
      <figure class="wf-photo wf-photo--clinical"><img src="/assets/price-treatment-hairline.webp" alt="Behandelaar met een blauwe handschoen bij de haarlijn" loading="lazy" decoding="async"><figcaption>Beeld uit een Sarasin Clinic-behandelvideo</figcaption></figure>
    </section>
    <section class="wf-section wf-science" id="werking">
      <div class="wf-wrap wf-split">
        <figure class="wf-photo wf-photo--anatomy"><img src="{MEDIA}anatomy.webp" width="600" height="511" alt="Anatomische doorsnede van de huid met een haarzakje, talgklier en haarspiertje" loading="lazy" decoding="async"><figcaption>Anatomie van een haarzakje · <a href="{ANATOMY}">H. V. Carter, Gray’s Anatomy</a></figcaption></figure>
        <div class="wf-copy"><h2>Hoe werkt Hairfiller?</h2>
          <p class="wf-lead">De samenstelling combineert hyaluronzuur met zeven biomimetische peptiden.</p>
          {_html(treatment_medicine[1:-1])}
          <div class="wf-sources">{_html(research)}</div>
        </div>
      </div>
    </section>
    <section class="wf-section wf-results" id="resultaten" aria-labelledby="wf-results-title">
      <div class="wf-wrap wf-results-layout">
        <div class="wf-results-copy">
          <h2 id="wf-results-title">Haarfiller resultaten bij vrouwen</h2>
          <p class="wf-lead">Bekijk echte voor-en-nafoto’s van Sarasin Clinic.</p>
          <p>Resultaten verschillen per persoon. Tijdens het consult bespreken we wat je in jouw situatie mag verwachten.</p>
        </div>
        <div class="wf-case-list">{_result_photos(results)}</div>
        <div class="wf-results-actions">
          <div class="wf-result-controls" data-gallery-controls hidden>
            <div class="wf-result-nav">
              <button class="wf-circle wf-prev" type="button" aria-label="Vorig resultaat">{icon("arrow-right")}</button>
              <span class="wf-result-count" aria-live="polite"></span>
              <button class="wf-circle wf-next" type="button" aria-label="Volgend resultaat">{icon("arrow-right")}</button>
            </div>
            <div class="wf-thumbnails" role="group" aria-label="Kies een resultaat"></div>
          </div>
          {jump('/voor-en-na/', 'Bekijk alle resultaten')}
        </div>
        <dialog class="wf-dialog wf-photo-dialog" aria-label="Voor-en-nafoto op groot formaat">
          <div class="wf-dialog-bar"><strong>Voor en na</strong><button class="wf-circle wf-dialog-close" type="button" aria-label="Sluit foto" autofocus>{icon("x")}</button></div>
          <div class="wf-dialog-body"></div>
        </dialog>
      </div>
    </section>
    <section class="wf-section wf-wrap wf-benefits" id="t-1769769421103">
      <div class="wf-section-head"><h2>Wat zijn de voordelen?</h2><p class="wf-lead">Een behandeling die wordt afgestemd op jouw situatie.</p></div>
      <ul class="wf-benefit-list" role="list">{benefit_rows}</ul>
      {_disclosure("De voordelen volgens Sarasin Clinic", body_copy, icon)}
    </section>
    <section class="wf-section wf-journey" id="t-1769769421104">
      <div class="wf-wrap">
        <div class="wf-journey-top"><div class="wf-section-head"><h2>Jouw behandeltraject</h2><p class="wf-lead">Van het eerste gesprek tot de opvolging.</p>{booking()}</div>
          <figure class="wf-photo wf-photo--journey"><img src="/assets/clinic-media/beveren-onthaal.webp" alt="Ontvangstbalie van Sarasin Clinic Beveren" width="768" height="1024" loading="lazy" decoding="async"><figcaption>Sarasin Clinic Beveren</figcaption></figure>
        </div>
        <ol class="wf-timeline" role="list">{timeline}</ol>
        {_disclosure(result[0].get_text(" ", strip=True), _html(element for element in result[1:] if element.name == "p"), icon)}
      </div>
    </section>
    <section class="wf-section wf-wrap wf-videos" id="behandelvideos">
      <div class="wf-section-head"><h2>Hoe ziet een behandeling eruit?</h2>{jump('/videos/', 'Bekijk de videobibliotheek')}</div>
      <div class="wf-video-layout">
        <figure class="wf-primary-video"><video controls playsinline preload="none" poster="{WOMEN_STILL}" aria-label="Sarasin Clinic Hairfillerbehandeling bij een vrouw" aria-describedby="journey-video-description">
          <source src="/assets/hairfiller-women.mp4" type="video/mp4">Je browser ondersteunt deze video niet.</video>
          <figcaption><strong>Haarfillers bij vrouwen</strong><span id="journey-video-description">Een Hairfillerbehandeling bij een vrouw, met close-ups van de haarlijn en de hoofdhuid.</span></figcaption>
        </figure>
        <div class="wf-support-videos">{_videos(video_links, icon)}</div>
      </div>
      <dialog class="wf-dialog wf-video-dialog" aria-labelledby="wf-video-title">
        <div class="wf-dialog-bar"><strong id="wf-video-title">Video</strong><button class="wf-circle wf-dialog-close" type="button" aria-label="Sluit video" autofocus>{icon("x")}</button></div>
        <div class="wf-dialog-body"></div>
        <p class="wf-video-fallback"><a class="wf-link" target="_blank" rel="noopener">Open op YouTube {icon("arrow-up-right")}</a></p>
      </dialog>
    </section>
    <section class="wf-section wf-pricing" id="t-1769769421105">
      <div class="wf-wrap"><div class="wf-section-head"><h2>Wat kost Hairfiller voor vrouwen?</h2></div>
      {_pricing(pricing)}{booking()}</div>
    </section>
    <section class="wf-section wf-wrap wf-care" id="voor-en-nazorg">
      <div class="wf-section-head"><h2>Voorbereiding en nazorg</h2><p>Volg de aanwijzingen die je behandelaar voor jouw situatie meegeeft.</p></div>
      <div class="wf-care-grid">
        {_disclosure("Voor je behandeling", f'<p>Kom met een schone hoofdhuid en laat gel, haarlak en haarvezels achterwege. Bespreek medicatie, gevoeligheden en eventuele pijnstilling vooraf met je behandelaar.</p>{jump("/haarfiller-behandeling/#voorzorg-hair-filler", "Lees de volledige voorbereiding")}', icon)}
        {_disclosure("Na je behandeling", f'<p>Sarasin vraagt om je haar de eerste 24 uur niet te wassen en geen stylingproducten te gebruiken. Wacht 48 uur met sporten of intens zweten.</p><p>Vermijd meteen na de behandeling warme douches, de sauna en de zonnebank. Raak de hoofdhuid zo weinig mogelijk aan en masseer of krab de behandelde zone niet.</p>{jump("/haarfiller-behandeling/#nazorg-hairfiller", "Lees alle nazorginstructies")}', icon)}
      </div><p class="wf-small">{jump(CLINIC_CARE, "Voor- en nazorg bij Sarasin Clinic", "arrow-up-right")}</p>
    </section>
    <section class="wf-section wf-longevity" id="skin-longevity">
      <div class="wf-wrap wf-split">
        <div class="wf-longevity-media">
          {_photo("routine", "Vrouw met opgestoken rossig haar raakt haar gezicht aan tijdens haar verzorgingsroutine", "routine")}
          <figure class="wf-photo wf-photo--product"><img src="{MEDIA}cleanser.webp" alt="Sarasin Hydrating Milk Cleanser" width="960" height="960" loading="lazy" decoding="async"><figcaption>Sarasin Hydrating Milk Cleanser</figcaption></figure>
        </div>
        <div class="wf-copy"><h2>Skin Longevity 360°</h2>
          <p class="wf-lead">De visie van Sarasin op huidverzorging, in de clinic en thuis.</p>
          <p>Skin Longevity 360° brengt klinische expertise, dagelijkse huidverzorging en leefstijl samen. Vraag bij je consult welke verzorging bij je hoofdhuid en behandeling past.</p>
          <div class="wf-actions">{jump(LONGEVITY, 'Ontdek de Sarasin-methode', 'arrow-up-right')}{jump('https://www.sarasin.shop/products/hydrating-milk-cleanser', 'Bekijk de webshop', 'arrow-up-right')}</div>
        </div>
      </div>
    </section>
    <section class="wf-section wf-wrap wf-expert" id="t-1769769421110">
      <figure class="wf-photo wf-photo--expert"><img src="{MEDIA}karen.webp" alt="Karen Sarasin, esthetisch verpleegkundige en oprichter van Sarasin Clinic" width="400" height="400" loading="lazy" decoding="async"></figure>
      <div class="wf-copy">
        <h2>Karen Sarasin</h2>
        <p class="wf-lead">Esthetisch verpleegkundige (BScN) en oprichter van Sarasin Clinic</p>
        {keep(expert[1:])}
        <div class="wf-actions">{booking()}{jump('https://sarasinclinic.com/the-team/karen-sarasin/', 'Bekijk diploma’s en profiel', 'arrow-up-right')}</div>
      </div>
    </section>
    <section class="wf-section wf-reviews" id="t-1769769421111">
      <div class="wf-wrap wf-reading">
        <h2>Ervaringen met Hairfiller</h2>
        {_disclosure("Lees de bestaande reviews", _html([*review_intro, *reviews]), icon)}
      </div>
    </section>
    <section class="wf-section wf-wrap wf-faq" id="t-1771585826171">
      <div class="wf-section-head"><h2>Veelgestelde vragen</h2><p>Over de behandeling, de nazorg en wat je mag verwachten.</p></div>
      <div>{_faq(faq[1:], icon)}</div>
    </section>
    <section class="wf-section wf-wrap wf-related" id="t-1769769421112">
      <h2>Verder lezen</h2><div class="wf-related-links">{''.join(jump(a['href'], a.get_text(' ', strip=True)) for a in related[1:] if a.name == 'a')}{jump('/sarasin-clinic/ons-team/', 'Ons team')}</div>
    </section>
    <section class="wf-closing" aria-labelledby="wf-closing-title">
      {_photo("closing", "Vrouw met los krullend haar aan een raam", "closing")}
      <div class="wf-closing-copy"><h2 id="wf-closing-title">Goed advies begint met goed kijken.</h2>
        <p>Vertel ons wat je merkt aan je haar. Tijdens een gratis consultatie bekijken we samen wat voor jou passend is.</p>
        {booking()}
      </div>
    </section>
    <div class="wf-mobile-book" hidden>{booking()}</div>
    '''
