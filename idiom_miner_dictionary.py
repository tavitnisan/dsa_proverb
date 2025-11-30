#!/usr/bin/env python3
from pathlib import Path
import string
import csv
from collections import Counter

# --- CONFIGURATION ---

# 25 IDIOMS PER LANGUAGE (The Gold Standard)
IDIOMS = {
    "en": [
        "wild goose chase", "count your chickens", "wolf in sheep", "black sheep",
        "hold your horses", "beat a dead horse", "dark horse", "cows come home",
        "bull by the horns", "bull in a china shop", "pig in a poke", "when pigs fly",
        "needle in a haystack", "last straw", "make hay", "wheat from the chaff",
        "reap what you sow", "grist for the mill", "run of the mill", "sitting duck",
        "chicken out", "headless chicken", "eggs in one basket", "walking on eggshells",
        "kill the goose"
    ],
    "tr": [
        "damlaya damlaya göl", "sakla samanı", "dereyi görmeden", "görünen köy",
        "komşu komşunun", "tatlı dil yılanı", "aç ayı oynamaz", "besle kargayı",
        "kaz gelecek yerden", "atı alan üsküdar", "eşeğin aklına karpuz", "pirince giderken",
        "kurt dumanlı havayı", "sütten ağzı yanan", "üzüm üzüme baka", "tavşan dağa küsmüş",
        "horoz ölür", "el elin eşeğini", "it ürür kervan", "meyve veren ağaç",
        "bal tutan", "keskin sirke", "öküz öldü", "çam sakızı çoban", "ayıkla pirincin"
    ],
    "de": [
        "hund begraben", "katze im sack", "schwarze schaf", "geschenkten gaul",
        "ist mir wurst", "schwein haben", "flinte ins korn", "eulen nach athen",
        "stier bei den hörnern", "hahn im korb", "schwalbe macht keinen sommer", "mit den hühnern schlafen",
        "blindes huhn", "perlen vor die säue", "elefant im porzellanladen", "gras wachsen hören",
        "ins gras beißen", "pferde stehlen", "blatt vor den mund", "steppt der bär",
        "ochs am berg", "radieschen von unten", "tomaten auf den augen", "höhle des löwen",
        "korn und spreu"
    ],
    "fr": [
        "nos moutons", "poules auront des dents", "peau de l'ours", "avoir le cafard",
        "chèvre et le chou", "charrue avant les boeufs", "raconter des salades", "tomber dans les pommes",
        "carottes sont cuites", "sur le champignon", "aiguille dans une botte", "vache à lait",
        "taureau par les cornes", "vole un oeuf", "un tiens vaut mieux", "fouetter un chat",
        "confiture aux cochons", "faim de loup", "faire l'autruche", "doux comme un agneau",
        "poule aux oeufs", "chair de poule", "sur ses grands chevaux", "poser un lapin",
        "dindon de la farce"
    ],
    "es": [
        "pájaro en mano", "como una cabra", "otro perro con ese hueso", "no por mucho madrugar",
        "oveja con su pareja", "casa por la ventana", "boca cerrada no entran", "camarón que se duerme",
        "gato por liebre", "agua a su molino", "carne en el asador", "ser pan comido",
        "toro por los cuernos", "burro grande", "margaritas a los cerdos", "dos pájaros de un tiro",
        "ojos que no ven", "perro ladrador", "siembra vientos", "oveja negra",
        "memoria de pez", "vendérsela la moto", "aguja en un pajar", "gallina de los huevos",
        "gato encerrado"
    ],
    "it": [
        "bocca al lupo", "sano come un pesce", "due piccioni con una fava", "non dire gatto",
        "gallina vecchia", "testa di rapa", "capitare a fagiolo", "prendere in castagna",
        "patata bollente", "chi dorme non piglia", "buongiorno si vede", "erba del vicino",
        "piove sul bagnato", "tutto fa brodo", "raccogliere quello che si semina", "fieno mentre c'è il sole",
        "carro davanti ai buoi", "seminare zizzania", "pollice verde", "tagliare i ponti",
        "gallina dalle uova", "ago in un pagliaio", "pecora nera", "chiudere la stalla",
        "caval donato"
    ],
    "nl": [
        "koe bij de horens", "haringen in een ton", "zwarte schaap", "gegeven paard",
        "kat van huis", "hond in de pot", "hoge bomen", "vogel in de hand",
        "oude koeien", "aap uit de mouw", "kippen op stok", "kat in de zak",
        "vooruit met de geit", "schaapjes op het droge", "hazenpad kiezen", "varkentje wassen",
        "kaal als de neten", "kraait geen haan", "kip zonder kop", "mierenneuker",
        "mug een olifant", "vis in het water", "uiltje knappen", "bloemetjes buiten",
        "abraham de mosterd"
    ],
    "pl": [
        "skóry na niedźwiedziu", "tureckim kazaniu", "zrobić kogoś w konia", "muchy w nosie",
        "flaki z olejem", "zbity pies", "wilk w owczej", "kota w worku",
        "darowanemu koniowi", "gdzie kucharek sześć", "jaka praca taka płaca", "kto rano wstaje",
        "wilka z lasu", "igły w stogu", "kulą w płot", "wystawić kogoś do wiatru",
        "języka w gębie", "dużej chmury mały", "kłamstwo ma krótkie", "czarna owca",
        "między wrony", "koń by się uśmiał", "wół do karety", "zbijać bąki",
        "gruszki na wierzbie"
    ],
    "el": [
        "agourída méli", "gáidaros ton peteinó", "leípei i gáta", "kamíla de vlépei",
        "laloún polloí kokóroi", "fasoúli to fasoúli", "gia ta panigíria", "koutaliá neró",
        "lýkos ki an egérase", "chelidóni den férnei", "fórtose ston kókora", "sigá ta avgá",
        "pollá kerásia", "mílo káto apó", "psári vromáei", "píre to máti",
        "lýko na fyláei", "káne to kaló", "péride óchi", "mavró próvato",
        "psýllous sta áchyra", "megálo psári", "gáta ti glóssa", "kóta líra",
        "petáei gaídaros"
    ],
    "ru": [
        "shkuru neubitogo medvedya", "volk v ovechey", "kota v meshke", "darovanomu konyu",
        "dyma bez ognya", "bab s vozu", "yabloko ot yabloni", "pervy blin komom",
        "tsyplyat po oseni", "rabota ne volk", "tikhoy omute", "goloden kak volk",
        "kak s gusya", "puganaia vorona", "dvumya zaytsami", "ne vse kotu",
        "lyubish katatsya", "semi nyanek", "kto rano vstaet", "lozhka degtya",
        "ne plyuy v kolodets", "chto poseesh", "khleb vsemu golova", "slovo ne vorobey",
        "belaya vorona"
    ]
}

# STOPWORDS (Noise to ignore)
STOPWORDS = {
    "en": {"the", "a", "an", "is", "in", "it", "to", "and", "of", "that", "this", "my", "your"},
    "tr": {"bir", "ve", "bu", "şu", "o", "da", "de", "mi", "mı", "için", "ile"},
    "de": {"der", "die", "das", "ein", "eine", "ist", "und", "in", "zu", "den", "dem"},
    "fr": {"le", "la", "les", "un", "une", "et", "est", "dans", "de", "du", "ce"},
    "es": {"el", "la", "los", "las", "un", "una", "y", "es", "en", "de", "que"},
    "it": {"il", "la", "lo", "i", "gli", "le", "un", "uno", "una", "e", "è", "di"},
    "nl": {"de", "het", "een", "en", "is", "in", "van", "dat", "die"},
    "pl": {"i", "w", "z", "na", "do", "jest", "się", "to", "o"},
    "ru": {"и", "в", "не", "на", "я", "что", "с", "это", "как"},
    "el": {"το", "η", "ο", "και", "είναι", "σε", "από", "θα", "που"}
}

BASE_DIR = Path("data/opensubs_raw/by_lang")
THRESHOLD_RATIO = 0.6  # Must match 60% of significant words

def clean_tokens(text, lang):
    """Splits text, removes punctuation, filters stopwords."""
    # Lowercase
    text = text.lower()
    # Replace punctuation with space
    for char in string.punctuation:
        text = text.replace(char, " ")
    
    tokens = text.split()
    stops = STOPWORDS.get(lang, set())
    
    # Return only content words
    return [t for t in tokens if t not in stops]

def get_anchors(idiom_phrase, lang):
    """Pre-processes an idiom definition into a set of anchor roots."""
    return clean_tokens(idiom_phrase, lang)

def check_match(line_tokens, idiom_anchors):
    """
    Checks if line_tokens contains enough of idiom_anchors.
    Uses 'startswith' to handle suffixes (agglutination).
    """
    if not idiom_anchors: return False
    
    hits = 0
    for anchor in idiom_anchors:
        # Check if this anchor exists as a prefix in any word in the line
        # e.g. Anchor "tavuk" matches line word "tavuklar"
        match_found = False
        for word in line_tokens:
            if word.startswith(anchor):
                match_found = True
                break
        if match_found:
            hits += 1
            
    # Calculate Ratio
    ratio = hits / len(idiom_anchors)
    return ratio >= THRESHOLD_RATIO

def process_language(lang):
    file_path = BASE_DIR / lang / f"{lang}.txt"
    if not file_path.exists():
        print(f"Skipping {lang} (File not found)")
        return None

    print(f"Scanning {lang.upper()} using {len(IDIOMS[lang])} idioms...")
    
    # Pre-process idioms into anchor sets
    idiom_data = []
    for raw_idiom in IDIOMS[lang]:
        anchors = get_anchors(raw_idiom, lang)
        idiom_data.append( {"phrase": raw_idiom, "anchors": anchors, "count": 0} )
    
    total_lines = 0
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                total_lines += 1
                
                # Fast Check: Skip line if it's too short
                if len(line) < 5: continue
                
                # Tokenize line once per iteration
                line_tokens = clean_tokens(line, lang)
                if not line_tokens: continue
                
                # Check against all idioms
                # Optimization: Check if line contains *any* anchor from the first idiom? 
                # No, just iterate. 25 checks is fast.
                
                for item in idiom_data:
                    if check_match(line_tokens, item["anchors"]):
                        item["count"] += 1
                
                if i % 2000000 == 0 and i > 0:
                    print(f"  -> {i:,} lines...")
                    
    except Exception as e:
        print(f"Error in {lang}: {e}")
        return None

    return {"lang": lang, "lines": total_lines, "data": idiom_data}

def main():
    all_results = []
    
    for lang in IDIOMS.keys():
        res = process_language(lang)
        if res:
            all_results.append(res)
            
    # Write Final CSV
    with open("final_idiom_stats.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Language", "Idiom", "Count", "Frequency_Per_Million"])
        
        for res in all_results:
            total_lines = res["lines"]
            for item in res["data"]:
                freq = (item["count"] / total_lines) * 1_000_000 if total_lines > 0 else 0
                writer.writerow([res["lang"], item["phrase"], item["count"], f"{freq:.2f}"])
                
    # Write Summary Report
    with open("final_research_report.txt", "w", encoding="utf-8") as f:
        f.write("FINAL RURAL IDIOM RESEARCH REPORT\n")
        f.write("=================================\n\n")
        
        for res in all_results:
            f.write(f"LANGUAGE: {res['lang'].upper()}\n")
            f.write(f"Total Lines: {res['lines']:,}\n")
            
            # Calculate Total Rural Density
            total_hits = sum(item["count"] for item in res["data"])
            density = (total_hits / res["lines"]) * 1_000_000
            f.write(f"TOTAL RURAL DENSITY: {density:.2f} idioms/million lines\n")
            f.write("-" * 40 + "\n")
            
            # Sort by most frequent
            sorted_idioms = sorted(res["data"], key=lambda x: x["count"], reverse=True)
            for item in sorted_idioms:
                f.write(f"{item['count']:<6} | {item['phrase']}\n")
            f.write("\n")
            
    print("\n[SUCCESS] Data saved to 'final_idiom_stats.csv' and 'final_research_report.txt'")

if __name__ == "__main__":
    main()
