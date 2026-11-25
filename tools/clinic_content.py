"""Verified clinic sources and Dutch editorial copy for the Hairfiller minisite."""

from html import escape

CLINIC = "https://sarasinclinic.com"
BEVEREN = "/assets/beveren-waiting.webp"
BOOK_LABEL = "Plan een haarconsult"

CONCERNS = (
    ("dunner-haar", "Mijn haar wordt dunner", "Waarom valt mijn haar uit?",
     "Dunner haar kan verschillende oorzaken hebben, zoals erfelijke aanleg, hormonale veranderingen of een periode van ziekte. Wanneer je haar anders aanvoelt of je hoofdhuid zichtbaarder wordt, kan een arts helpen de oorzaak te achterhalen.",
     "/blog/waarom-valt-mijn-haar-uit/", "Lees over oorzaken van haarverlies"),
    ("plots-haarverlies", "Ik verlies plots meer haar", "Wanneer laat ik haaruitval onderzoeken?",
     "Bespreek haaruitval met je huisarts of dermatoloog als die plots begint, als je kale plekken krijgt of als je hoofdhuid jeukt, pijn doet of ontstoken aanvoelt. Ook bij aanhoudende haaruitval is het zinvol om de oorzaak te laten beoordelen.",
     "/blog/wanneer-haaruitval-laten-onderzoeken/", "Lees over plotselinge haaruitval"),
    ("bredere-scheiding", "Mijn scheiding wordt breder", "Wat betekent het als mijn scheiding breder wordt?",
     "Een bredere scheiding kan betekenen dat het haar bovenop geleidelijk dunner wordt. Er zijn meerdere mogelijke oorzaken. Wanneer je de verandering voor het eerst opmerkte en of er ook meer haren uitvallen, helpt bij de beoordeling.",
     "/blog/mijn-haarscheiding-wordt-breder/", "Lees over dunner wordend haar"),
)

ANSWERS = (
    ("geschikt", "Is Hairfiller geschikt voor mij?",
     "Dat hangt af van de oorzaak en het patroon van je haarverlies, je medische voorgeschiedenis en je verwachtingen. Tijdens het consult bespreek je of Hairfiller een optie is en of verder onderzoek of een andere aanpak meer zin heeft.",
     "/blog/is-haarfiller-geschikt-voor-mij/", "Lees over de behandeling"),
    ("consult", "Wat gebeurt er tijdens een haarconsult?",
     "Je vertelt wat je merkt en sinds wanneer. De behandelaar bekijkt je hoofdhuid, bespreekt je voorgeschiedenis en legt uit welke vervolgstap bij je situatie past. Je kunt vragen stellen over alternatieven, risico’s en kosten.",
     "/#home-treatment-title", "Bekijk jouw haartraject"),
    ("sessies", "Hoeveel Hairfiller-sessies heb ik nodig?",
     "Het aantal sessies wordt individueel besproken. Vraag tijdens het consult naar de voorgestelde behandeling, het evaluatiemoment en eventuele onderhoudssessies.",
     "/prijzen/", "Bekijk de prijzen per behandelzone"),
    ("resultaat", "Wat kan ik verwachten van Hairfiller?",
     "Het resultaat kan verschillen per persoon en hangt onder meer af van de oorzaak van haarverlies. De behandelaar bespreekt wat voor jou realistisch is en hoe jullie het verloop opvolgen.",
     "/voor-en-na/", "Bekijk voorbeelden uit de kliniek"),
    ("risicos", "Zijn er risico’s of bijwerkingen?",
     "Bij injecties kunnen bijvoorbeeld roodheid, zwelling of een blauwe plek ontstaan. Bespreek vooraf je medische voorgeschiedenis, mogelijke bijwerkingen en wanneer je contact moet opnemen met de kliniek.",
     CLINIC + "/veelgestelde-vragen/wat-zijn-de-risico-en-complicaties-bij-een-hair-filler/", "Lees meer over risico’s"),
    ("nazorg", "Welke nazorg is nodig na Hairfiller?",
     "Volg de persoonlijke instructies van je behandelaar. Vraag vooraf wanneer je je haar weer mag wassen of kleuren en bij welke klachten je de clinic moet bellen.",
     "/blog/haarfiller-nazorg/", "Lees over voorbereiding en nazorg"),
    ("alternatieven", "Wat is het verschil tussen Hairfiller en PRP?",
     "Bij Hairfiller wordt een product in de hoofdhuid geïnjecteerd. Bij PRP wordt een concentraat uit je eigen bloed gebruikt. Welke aanpak besproken wordt, hangt af van de oorzaak van haarverlies en je situatie.",
     "/blog/haarfiller-of-prp/", "Lees over PRP en haaruitval"),
)

DOCTORS = (
    ("Dr. Van Gasse", "1-05198-89-000", "Dr.-Van-Gasse.png", "Sint-Martens-Latem en Beveren",
     ("Geneeskunde en tandheelkunde aan KU Leuven. Fellowship esthetische geneeskunde aan het Harley Street Institute in Londen.",),
     CLINIC + "/over-ons/team/dr-van-gasse/"),
    ("Dr. Zin Mar Aung", "1-09103-11-000", "Dr.Zin-Mar-Aung.png", "Sint-Martens-Latem",
     ("Actief in esthetische behandelingen sinds 2023.",
      "Opleiding aan Shanghai Jiao Tong University",
      "Master of Medicine (Surgery), 2018",
      "Doctoraatsopleiding in chirurgie afgerond, 2022"),
     CLINIC + "/over-ons/team/"),
    ("Dr. Valérie Debeuf", "1-10769-36-000", "Dr.-Debeuf.png", "Sint-Martens-Latem en Beveren",
     ("Opleiding geneeskunde aan KU Leuven, gevolgd door verdere opleiding in medische gelaatsesthetiek.",),
     CLINIC + "/over-ons/team/dr-debeuf/"),
    ("Dr. Monné", "1-15526-85-000", "Dr.-Monne.png", "Sint-Martens-Latem",
     ("Actief in esthetische behandelingen sinds 2025.",), CLINIC + "/over-ons/team/"),
)

# Dutch Hairfiller treatment tree and directly related articles in the clinic sitemap.
SOURCE_GROUPS = {
    "Hairfiller en haarverlies": (
        "/behandelingen/hairfiller/",
        "/behandelingen/haaruitval/",
        "/behandelingen/hairfiller/haarverlies-mannen/",
        "/behandelingen/hairfiller/haarverlies-vrouwen/",
        "/behandelingen/hairfiller/haaruitval-vrouwen-oorzaak/",
        "/behandelingen/hairfiller/mannen/",
        "/behandelingen/hairfiller/vrouw/",
        "/behandelingen/hairfiller/hair-booster/",
        "/behandelingen/hairfiller/haarkliniek-gent/",
        "/behandelingen/hairfiller/haarkliniek-antwerpen/",
    ),
    "Artikels over haarverlies en behandelingen": (
        "/dr-cyj-haarfiller-vs-alopecia/",
        "/led-therapie-tegen-haaruitval/",
        "/werkt-prp-tegen-haaruitval/",
        "/hydra-roller-tegen-haarverlies/",
        "/fact-check-botox-haarfillers/",
    ),
    "Alternatieven en resultaten": (
        "/behandelingen/haaruitval/prp/",
        "/behandelingen/hairfiller/haarimplantatie/",
        "/behandelingen/hairfiller/haartransplantatie-vrouwen-belgie/",
        "/behandelingen/hairfiller/haartransplantatie-gent/",
        "/voor-na/hair-filler/",
    ),
}


def clinic_route(source):
    if source == "/behandelingen/hairfiller/":
        return "/haarfiller-behandeling/"
    slug = source.strip("/").replace("/", "-") if source == "/voor-na/hair-filler/" else source.strip("/").split("/")[-1]
    return "/faq/kennisbank/" + slug + "/"


def answer_card(identifier, question, body, url, label, icon):
    return (f'<article class="patient-answer" id="{identifier}"><h3>{escape(question)}</h3>'
            f'<p>{escape(body)}</p><a class="inline-link" href="{escape(url, quote=True)}">'
            f'{escape(label)} {icon("arrow-right")}</a></article>')
