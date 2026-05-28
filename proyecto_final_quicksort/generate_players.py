#!/usr/bin/env python3
"""
Generate a synthetic chess players CSV in the same format as
top_chess_players_aug_2020.csv.

Usage:
    python3 generate_players.py -n 97000000 -o big_players.csv
    python3 generate_players.py -n 5000000              # writes generated_players.csv
"""

import argparse
import random
import sys

# ── Name pools ────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Magnus","Fabiano","Garry","Ding","Hikaru","Levon","Maxime","Anish","Wesley",
    "Shakhriyar","Teimour","Sergey","Peter","Alexander","Vladimir","Viswanathan",
    "Boris","Mikhail","Vasily","Anatoly","Robert","Paul","Tigran","Mikhail",
    "Jan","Daniil","Richard","Leinier","Pentala","Ernesto","Wang","Bu","Yu",
    "Wei","Ni","Li","Zhang","Chen","Liu","Lin","Zhao","Sun","Zhou","Wu",
    "Ivan","Alexei","Dmitri","Evgeny","Igor","Andrei","Nikita","Pavel",
    "Carlos","Pablo","Diego","Luis","Jorge","Miguel","Eduardo","Juan",
    "Ahmed","Ali","Omar","Hassan","Mohamed","Yusuf","Ibrahim","Khalid",
    "James","John","David","Michael","Robert","William","Thomas","Charles",
    "Arjun","Vidit","Praggnanandhaa","Nihal","Gukesh","Leon","Vincent","Marc",
    "Nodirbek","Abdusattorov","Javokhir","Shamsiddin","Jakhongir","Mukhammad",
    "Alireza","Parham","Bardiya","Amin","Borna","Luka","Matej","Stefan",
    "Oleksandr","Kirill","Vasyl","Bogdan","Denys","Serhiy","Andriy","Yuriy",
    "Kateryna","Mariya","Hou","Ju","Nana","Antoaneta","Almira","Viktoria",
    "Anna","Alexandra","Irina","Elena","Natalia","Ekaterina","Tatiana","Olga",
]

LAST_NAMES = [
    "Carlsen","Caruana","Kasparov","Liren","Nakamura","Aronian","Vachier-Lagrave",
    "Giri","So","Mamedyarov","Radjabov","Karjakin","Svidler","Grischuk","Kramnik",
    "Anand","Spassky","Tal","Smyslov","Karpov","Fischer","Morphy","Petrosian",
    "Botvinnik","Nepomniachtchi","Rapport","Dominguez","Harikrishna","Inarkiev",
    "Hao","Xiangzhi","Yangyi","Yi","Hua","Fei","Jian","Ming","Peng","Tao",
    "Ivanchuk","Shirov","Bareev","Gelfand","Morozevich","Almasi","Leko","Polgar",
    "Rodriguez","Garcia","Martinez","Lopez","Hernandez","Gonzalez","Perez","Sanchez",
    "Naiditsch","Eljanov","Wojtaszek","Duda","Swierz","Kovalev","Fedoseev",
    "Erigaisi","Adhiban","Sarin","Firouzja","Maghsoodloo","Tabatabaei","Deac",
    "Abdusattorov","Sindarov","Yakubboev","Sarana","Esipenko","Keymer","Gukesh",
    "Tari","Hansen","Grandelius","Hillarp Persson","Lagno","Muzychuk","Ushenina",
    "Zhao","Koneru","Humpy","Harika","Vaishali","Pragg","Rausis","Vocaturo",
    "Smith","Johnson","Williams","Brown","Jones","Miller","Davis","Wilson",
    "Moore","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin",
]

FEDERATIONS = [
    "RUS","USA","CHN","IND","ARM","AZE","GER","FRA","NED","UKR","POL","CZE",
    "HUN","SRB","GEO","ESP","ITA","ISR","EGY","IRN","KAZ","UZB","BLR","LTU",
    "LAT","EST","SVK","AUT","SUI","NOR","SWE","DEN","FIN","BEL","GBR","POR",
    "TUR","GRE","BUL","ROU","CRO","SLO","BIH","NOR","ISL","ARG","BRA","CUB",
    "VIE","PHI","MAS","INA","THA","JPN","KOR","MGL","KGZ","TKM","TJK","AZE",
]

TITLES = ["GM","IM","FM","CM","WGM","WIM","WFM","WCM","","","","","","","",""]


def random_name():
    return f"{random.choice(LAST_NAMES)}, {random.choice(FIRST_NAMES)}"


def random_rating(title, base_min, base_max):
    r = random.randint(base_min, base_max)
    # ~15% chance of being unrated (0)
    return r if random.random() > 0.15 else 0


def title_rating_range(title):
    ranges = {
        "GM":  (2500, 2900),
        "IM":  (2400, 2550),
        "FM":  (2300, 2450),
        "CM":  (2200, 2350),
        "WGM": (2300, 2500),
        "WIM": (2200, 2400),
        "WFM": (2100, 2300),
        "WCM": (2000, 2200),
        "":    (1000, 2300),
    }
    return ranges.get(title, (1000, 2300))


def generate_player(fide_id):
    title = random.choice(TITLES)
    lo, hi = title_rating_range(title)
    std   = random_rating(title, lo, hi)
    rapid = random_rating(title, lo, hi)
    blitz = random_rating(title, lo, hi)

    # At least one rating must be non-zero (mirrors the filter in quicksort.cpp)
    while std == 0 and rapid == 0 and blitz == 0:
        std   = random_rating(title, lo, hi)
        rapid = random_rating(title, lo, hi)
        blitz = random_rating(title, lo, hi)

    name       = random_name()
    federation = random.choice(FEDERATIONS)
    gender     = random.choice(["M", "M", "M", "F"])  # realistic ratio
    year       = random.randint(1940, 2010)
    inactive   = "i" if random.random() < 0.08 else ""

    return (fide_id, name, federation, gender, year, title, std, rapid, blitz, inactive)


def main():
    parser = argparse.ArgumentParser(description="Generate a synthetic chess players CSV")
    parser.add_argument("-n", "--num-players", type=int, default=1_000_000,
                        help="Number of players to generate (default: 1_000_000)")
    parser.add_argument("-o", "--output", default="generated_players.csv",
                        help="Output CSV filename (default: generated_players.csv)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    n = args.num_players
    out = args.output

    print(f"Generating {n:,} players -> {out}", file=sys.stderr)

    BATCH = 100_000
    with open(out, "w", buffering=1 << 20) as f:
        f.write("Fide id,Name,Federation,Gender,Year_of_birth,Title,"
                "Standard_Rating,Rapid_rating,Blitz_rating,Inactive_flag\n")

        for i in range(n):
            fide_id = 10_000_000 + i
            p = generate_player(fide_id)
            # Quote the name field (may contain a comma)
            line = (f'{p[0]},"{p[1]}",{p[2]},{p[3]},{p[4]},{p[5]},'
                    f'{p[6]},{p[7]},{p[8]},{p[9]}\n')
            f.write(line)

            if (i + 1) % BATCH == 0:
                pct = (i + 1) / n * 100
                print(f"  {i+1:>{len(str(n))}}/{n}  ({pct:.1f}%)", file=sys.stderr)

    print(f"Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
