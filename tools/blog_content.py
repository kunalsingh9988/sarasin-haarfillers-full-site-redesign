"""Dutch patient guides based on Sarasin Clinic and public medical sources."""

from dataclasses import dataclass

TREATMENT = "https://sarasinclinic.com/behandelingen/hairfiller/"
THUISARTS = "https://www.thuisarts.nl/haaruitval/ik-heb-haaruitval-wat-kan-zijn"
AAD = "https://www.aad.org/public/diseases/hair-loss/insider/begin"
PRP = "https://sarasinclinic.com/behandelingen/haaruitval/prp/"


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    category: str
    description: str
    answer: str
    image: str
    alt: str
    credit: str
    sections: tuple[tuple[str, str], ...]
    links: tuple[tuple[str, str], ...]
    sources: tuple[tuple[str, str], ...]

    @property
    def path(self):
        return f"/blog/{self.slug}/"


POSTS = (
    Post(
        "waarom-valt-mijn-haar-uit", "Waarom valt mijn haar uit?", "Haaruitval",
        "Lees wat meer haren in je borstel of zichtbaar dunner haar kunnen betekenen, welke oorzaken mogelijk zijn en wanneer je hulp kunt vragen.",
        "Je haar kan uitvallen door erfelijke aanleg, ziekte, een bevalling, bepaalde medicijnen of andere oorzaken. Merk je duidelijk meer haarverlies, wordt je haar dunner of ontstaan er kale plekken? Dan kan je huisarts helpen uitzoeken wat er speelt.",
        "/assets/source/393161444f.png", "Vrouw houdt bruin haar opzij", "Sarasin Clinic",
        (
            ("Wat is het verschil tussen uitval en dunner wordend haar?",
             "Meer losse haren op je kussen of in de douche kunnen betekenen dat je tijdelijk meer haren verliest. Een steeds zichtbaardere hoofdhuid of een bredere scheiding wijst op een verandering in de dichtheid. De twee kunnen tegelijk voorkomen."),
            ("Welke veranderingen zijn nuttig om te noteren?",
             "Noteer wanneer het begon, of het plots of geleidelijk gebeurde, en of je overal haar verliest of op één plek. Vermeld ook recente ziekte, een bevalling en nieuwe medicatie. Bespreek vermoedelijke bijwerkingen met je arts voordat je iets aan je medicatie verandert."),
            ("Hoe kies je een volgende stap?",
             "De aanpak hangt af van de oorzaak. Je huisarts kan je hoofdhuid bekijken en zo nodig verder onderzoek of een verwijzing bespreken. Als Hairfiller daarna een optie is die je wilt verkennen, kan de clinic uitleggen wat een consult inhoudt."),
        ),
        (("Wanneer laat ik haaruitval onderzoeken?", "/blog/wanneer-haaruitval-laten-onderzoeken/"),
         ("Meer over mogelijke oorzaken", "/faq/veel-haarverlies/")),
        (("Thuisarts · Haaruitval en mogelijke oorzaken", THUISARTS), ("Sarasin Clinic · Hairfiller", TREATMENT)),
    ),
    Post(
        "wanneer-haaruitval-laten-onderzoeken", "Wanneer laat ik haaruitval onderzoeken?", "Haaruitval",
        "Weet bij plots haarverlies, kale plekken of hoofdhuidklachten wanneer je je huisarts belt en welke informatie nuttig is voor je afspraak.",
        "Maak een afspraak met je huisarts als je plots veel meer haar verliest, kale plekken krijgt of merkt dat je haar zichtbaar dunner wordt. Vertel het ook als je hoofdhuid pijnlijk, rood of schilferig is, of als je je zorgen maakt.",
        "/assets/source/3f7fd8c9b4.jpg", "Losse haren op een lichte ondergrond", "Sarasin Clinic",
        (
            ("Waar let een arts op?",
             "Je arts vraagt hoe lang de verandering al opvalt, hoe snel ze is ontstaan en of haarverlies ook bij familieleden voorkomt. Het patroon, de conditie van de hoofdhuid en eventuele andere klachten kunnen helpen kiezen welk onderzoek nodig is."),
            ("Wat neem je mee naar je afspraak?",
             "Schrijf op wanneer je de verandering voor het eerst merkte en welke geneesmiddelen of supplementen je gebruikt. Foto’s kunnen helpen om het verloop te beschrijven als je ze al hebt, zeker wanneer de verandering van week tot week lastig te zien is."),
            ("Wanneer bespreek je Hairfiller?",
             "Bij plots plaatselijk haarverlies of een pijnlijke, ontstoken hoofdhuid heeft een medische beoordeling voorrang. Zodra de oorzaak besproken is, kun je met je behandelaar bekijken welke opties passen."),
        ),
        (("Lees meer over plotselinge haaruitval", "/vrouwen/plotseling-haaruitval/"),
         ("Lees wat er tijdens een haarconsult gebeurt", "/blog/is-haarfiller-geschikt-voor-mij/")),
        (("Thuisarts · Wanneer bel je bij haaruitval?", THUISARTS), ("Sarasin Clinic · Hairfiller", TREATMENT)),
    ),
    Post(
        "mijn-haarscheiding-wordt-breder", "Mijn haarscheiding wordt breder. Wat betekent dat?", "Haaruitval",
        "Een bredere haarscheiding, dunnere paardenstaart of zichtbaardere hoofdhuid? Lees wat die veranderingen kunnen betekenen.",
        "Een bredere haarscheiding kan erop wijzen dat het haar bovenop dunner wordt. Erfelijke haarverdunning is één mogelijke verklaring. Laat aanhoudende of opvallende veranderingen beoordelen zodat je weet welke oorzaak aannemelijk is.",
        "/assets/source/421b3e41ed.png", "Behandelaar houdt het haar opzij om de hoofdhuid te bekijken", "Sarasin Clinic",
        (
            ("Welke veranderingen vallen vaak samen op?",
             "Je merkt misschien ook minder volume wanneer je je haar samenbindt of ziet je hoofdhuid duidelijker bij helder licht. Het is nuttig om op te merken of het vooral bij de scheiding, de kruin of op meerdere plekken gebeurt."),
            ("Hoe volg je het verloop?",
             "Als je foto’s maakt, gebruik dan dezelfde scheiding, belichting en hoek. Noteer wanneer je de verandering begon te zien. Foto’s kunnen een gesprek ondersteunen, terwijl een beoordeling van de hoofdhuid helpt bij het vaststellen van de oorzaak."),
            ("Welke informatie helpt bij een consult?",
             "Vertel of meer haren uitvallen dan je gewend bent, of je hoofdhuid klachten geeft, en of haarverdunning in je familie voorkomt. Bij plotselinge kale plekken of duidelijke hoofdhuidklachten kun je eerst bij je huisarts terecht."),
        ),
        (("Lees over haarverlies bij vrouwen", "/faq/kennisbank/haarverlies-vrouwen/"),
         ("Wanneer laat ik haaruitval onderzoeken?", "/blog/wanneer-haaruitval-laten-onderzoeken/")),
        (("American Academy of Dermatology · Tekenen van haarverlies", AAD), ("Sarasin Clinic · Hairfiller", TREATMENT)),
    ),
    Post(
        "is-haarfiller-geschikt-voor-mij", "Is Hairfiller geschikt voor mij?", "Behandeling",
        "Lees wat Sarasin Clinic tijdens een haarconsult bespreekt en welke vragen je kunt stellen over geschiktheid, alternatieven en verwachtingen.",
        "Of Hairfiller bij je past hangt af van de oorzaak en het patroon van je haarverlies, je medische voorgeschiedenis en je verwachtingen. Tijdens het consult bespreek je of behandeling passend is, of dat verder onderzoek of een andere aanpak meer zin heeft.",
        "/assets/beveren-waiting.webp", "Wachtruimte van Sarasin Clinic Beveren", "Sarasin Clinic Beveren",
        (
            ("Wat gebeurt er bij het eerste consult?",
             "Je vertelt wat je aan je haar merkt en sinds wanneer. De behandelaar bekijkt je hoofdhuid en bespreekt je medische voorgeschiedenis. Samen neem je door wat je van een behandeling verwacht en welke vervolgstap daarbij past."),
            ("Wat is Hairfiller?",
             "Sarasin Clinic beschrijft Hairfiller als een behandeling waarbij een product met hyaluronzuur en peptiden in de hoofdhuid wordt geïnjecteerd. Vraag wat in jouw situatie het doel zou zijn en hoe de behandelaar het effect zou beoordelen."),
            ("Welke vragen stel je voordat je beslist?",
             "Vraag naar de voorgestelde behandelzones, mogelijke risico’s, alternatieven, totale kosten en het moment waarop jullie het verloop evalueren. Geef aan als je al andere haarbehandelingen gebruikt of medicatie inneemt."),
        ),
        (("Lees de volledige behandelinfo", "/haarfiller-behandeling/"),
         ("Maak kennis met de behandelende artsen", "/sarasin-clinic/ons-team/#haarfiller-artsen")),
        (("Sarasin Clinic · Hairfiller", TREATMENT), ("Thuisarts · Haaruitval", THUISARTS)),
    ),
    Post(
        "haarfiller-sessies-en-resultaat", "Hoeveel Hairfiller-sessies heb ik nodig en wanneer zie ik resultaat?", "Behandeling",
        "Ontdek wat je tijdens een consult kunt vragen over het aantal Hairfiller-sessies, onderhoud, evaluatie en voor-en-nafoto’s.",
        "Sarasin Clinic beschrijft Hairfiller als een reeks behandelingen. Het aantal sessies, het interval en het evaluatiemoment bespreek je tijdens het consult. Er is geen vaste termijn waarop iedereen resultaat ziet.",
        "/assets/beveren-treatment.webp", "Behandelstoel bij Sarasin Clinic Beveren", "Sarasin Clinic Beveren",
        (
            ("Hoe wordt een behandelplan opgesteld?",
             "Tijdens het consult bespreek je de behandelzones, de voorgestelde hoeveelheid en hoeveel afspraken de behandelaar adviseert. Vraag wanneer je samen evalueert en op basis waarvan een vervolg wordt voorgesteld."),
            ("Hoe beoordeel je het verloop?",
             "Vraag of de behandelaar foto’s gebruikt bij de opvolging. Vergelijk beelden met hetzelfde licht, dezelfde hoek en dezelfde haarstyling. De voorbeelden uit de kliniek laten individuele trajecten zien."),
            ("Wanneer komt onderhoud ter sprake?",
             "Bespreek bij de evaluatie of onderhoud in jouw situatie zinvol is. Vraag welke verandering de behandelaar verwacht te volgen en welke kosten bij vervolgafspraken horen."),
        ),
        (("Bekijk de voor-en-nafoto’s", "/voor-en-na/"), ("Bekijk de behandelprijzen", "/prijzen/")),
        (("Sarasin Clinic · Behandelprocedure en resultaten", TREATMENT),),
    ),
    Post(
        "wat-kost-haarfiller", "Wat kost Hairfiller per sessie?", "Behandeling",
        "Lees hoe de behandelzone en het aantal sessies samen de kosten bepalen. Bekijk de prijzen en neem gerichte vragen mee naar je consult.",
        "De prijs per sessie hangt volgens Sarasin Clinic af van de behandelzone en de nodige hoeveelheid. De totale kosten hangen ook af van het aantal afspraken en eventueel onderhoud. Vraag vooraf een overzicht voor jouw behandelplan.",
        "/assets/beveren-reception.webp", "Ontvangstbalie bij Sarasin Clinic Beveren", "Sarasin Clinic Beveren",
        (
            ("Wat bepaalt de prijs per sessie?",
             "Op de prijspagina staan bedragen per behandelzone. Welke zone bij jouw haarverlies past en hoeveel product ervoor nodig is, bespreek je met je behandelaar."),
            ("Wat vraag je over de totale kosten?",
             "Vraag hoeveel sessies het voorstel omvat, wat elke sessie kost, wat inbegrepen is en of een evaluatie of onderhoud apart wordt aangerekend."),
            ("Wat als je nog twijfelt?",
             "Gebruik het consult om alternatieven te bespreken. Je kunt vragen waarom een specifieke zone of behandeling wordt voorgesteld en wanneer jullie samen evalueren of je doorgaat."),
        ),
        (("Bekijk de actuele prijzen per zone", "/prijzen/"), ("Lees over sessies en resultaat", "/blog/haarfiller-sessies-en-resultaat/")),
        (("Sarasin Clinic · Prijs en behandelprocedure", TREATMENT),),
    ),
    Post(
        "haarfiller-nazorg", "Wanneer mag ik mijn haar wassen na Hairfiller?", "Nazorg",
        "Welke vragen stel je over haar wassen, kleuren en sporten na Hairfiller? Lees wat je vooraf met je behandelaar kunt afspreken.",
        "Op de behandelpagina adviseert Sarasin Clinic om na Hairfiller 24 uur te wachten met haar wassen. Volg de persoonlijke instructies bij je afspraak als die afwijken. Vraag ook wanneer je je haar weer mag kleuren of stylingproducten mag gebruiken.",
        "/assets/price-treatment-scalp.webp", "Behandelaar met handschoenen bij de hoofdhuid", "Sarasin Clinic",
        (
            ("Welke afspraken maak je vooraf?",
             "Vraag de clinic hoe je je hoofdhuid voorbereidt en of je vooraf rekening moet houden met bepaalde producten of andere behandelingen. Bespreek medicatie en gevoeligheden met je behandelaar."),
            ("Wat vraag je over je gewone routine?",
             "Neem je geplande wasbeurten, kappersafspraak, sport en sauna of zwemmen door als die snel na je afspraak vallen. Vraag om de instructies op papier of digitaal, zodat je ze thuis kunt nalezen."),
            ("Met wie neem je contact op bij klachten?",
             "Vraag vóór je vertrekt welke reacties je kunt verwachten, bij welke klachten je contact opneemt en hoe je de clinic bereikt. Neem contact op als je klachten erger worden of je niet weet hoe je ze moet beoordelen."),
        ),
        (("Lees de voor- en nazorg van Sarasin Clinic", "/haarfiller-behandeling/"), ("Lees de veelgestelde vragen", "/faq/#nazorg")),
        (("Sarasin Clinic · Voor- en nazorg", TREATMENT),),
    ),
    Post(
        "haarfiller-of-prp", "Hairfiller of PRP bij haaruitval?", "Behandeling",
        "Vergelijk wat Hairfiller en PRP inhouden en welke vragen je kunt stellen over geschiktheid, sessies en opvolging.",
        "Bij Hairfiller wordt een product in de hoofdhuid geïnjecteerd. Bij PRP wordt plasma met bloedplaatjes uit je eigen bloed gebruikt. Welke optie past, hangt af van de oorzaak van het haarverlies en wat je behandelaar na beoordeling adviseert.",
        "/assets/beveren-treatment.webp", "Behandelruimte van Sarasin Clinic in Beveren", "Sarasin Clinic Beveren",
        (
            ("Waarin verschillen de behandelingen?",
             "Hairfiller en PRP gebruiken verschillend materiaal. Voor PRP wordt eerst bloed afgenomen en verwerkt. Vraag wat beide opties in jouw situatie praktisch betekenen en welke voorbereiding erbij hoort."),
            ("Hoe bespreek je het verwachte resultaat?",
             "Vraag welk doel realistisch is, hoe de behandelaar vooruitgang beoordeelt en wat de onzekerheden zijn voor jouw type haarverlies. Bespreek ook eventuele risico’s, kosten en onderhoud."),
            ("Welke vraag stel je eerst?",
             "Begin met de vraag waardoor je haaruitval waarschijnlijk wordt veroorzaakt. Zo kun je bespreken of verder onderzoek nodig is voordat je een behandeling vergelijkt."),
        ),
        (("Lees de volledige PRP-behandelinfo", "/faq/kennisbank/prp/"), ("Lees de volledige Hairfiller-behandelinfo", "/haarfiller-behandeling/")),
        (("Sarasin Clinic · Hairfiller", TREATMENT), ("Sarasin Clinic · PRP tegen haaruitval", PRP)),
    ),
)
