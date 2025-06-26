#!/usr/bin/env python3
"""
Generate 10,000 test email addresses for load testing
"""

import csv
import random
import string
from pathlib import Path

def generate_test_emails(count=10000):
    """Generate test email addresses"""
    
    # Common domains for realistic testing
    domains = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
        "protonmail.com", "aol.com", "live.com", "msn.com", "me.com",
        "mac.com", "fastmail.com", "zoho.com", "tutanota.com", "mail.com",
        "yandex.com", "qq.com", "163.com", "126.com", "sohu.com",
        "naver.com", "daum.net", "hanmail.net", "rediffmail.com", "inbox.com",
        "hushmail.com", "guerrillamail.com", "mailinator.com", "10minutemail.com",
        "tempmail.org", "sharklasers.com", "getairmail.com", "mailnesia.com",
        "maildrop.cc", "mailcatch.com", "mailnull.com", "mailmetrash.com",
        "example.com", "domain.com", "company.org", "service.net", "website.co.uk",
        "business.com", "enterprise.io", "platform.dev", "system.local", "site.info"
    ]
    
    # Common name patterns
    first_names = [
        "john", "jane", "bob", "alice", "charlie", "diana", "edward", "fiona",
        "george", "helen", "ivan", "julia", "kevin", "lisa", "michael", "nancy",
        "oliver", "patricia", "quentin", "rachel", "steven", "tracy", "ursula",
        "victor", "wendy", "xavier", "yvonne", "zachary", "alex", "brittany",
        "cameron", "danielle", "ethan", "faith", "gabriel", "hannah", "isaac",
        "jasmine", "kyle", "lauren", "mason", "nora", "owen", "paige", "quinn",
        "riley", "sophia", "tristan", "una", "vaughn", "willow", "xander",
        "yara", "zane", "avery", "blake", "casey", "dakota", "emery", "finley",
        "gracie", "hayden", "indigo", "jordan", "kendall", "lennon", "morgan",
        "nash", "oakley", "peyton", "rowan", "sage", "tatum", "urban", "violet",
        "wilder", "xena", "yarrow", "zeus", "atlas", "blaze", "cove", "dune",
        "echo", "flint", "grove", "harbor", "iris", "jade", "kestrel", "lagoon",
        "marsh", "north", "ocean", "pierce", "quill", "ridge", "tide", "vapor",
        "winter", "xerxes", "zenith", "alpine", "brook", "canyon", "delta", "glen"
    ]
    
    last_names = [
        "smith", "johnson", "williams", "brown", "jones", "garcia", "miller",
        "davis", "rodriguez", "martinez", "hernandez", "lopez", "gonzalez",
        "wilson", "anderson", "thomas", "taylor", "moore", "jackson", "martin",
        "lee", "perez", "thompson", "white", "harris", "sanchez", "clark",
        "ramirez", "lewis", "robinson", "walker", "young", "allen", "king",
        "wright", "scott", "torres", "nguyen", "hill", "flores", "green",
        "adams", "nelson", "baker", "hall", "rivera", "campbell", "mitchell",
        "carter", "roberts", "gomez", "phillips", "evans", "turner", "diaz",
        "parker", "cruz", "edwards", "collins", "reyes", "stewart", "morris",
        "rogers", "reed", "cook", "morgan", "bell", "murphy", "bailey", "cooper",
        "richardson", "cox", "ward", "torres", "peterson", "gray", "ramirez",
        "james", "watson", "brooks", "kelly", "sanders", "price", "bennett",
        "wood", "barnes", "ross", "henderson", "coleman", "jenkins", "perry",
        "powell", "long", "patterson", "hughes", "flores", "washington", "butler",
        "simmons", "foster", "gonzales", "bryant", "alexander", "russell", "griffin",
        "diaz", "hayes", "myers", "ford", "hamilton", "graham", "sullivan",
        "wallace", "woods", "cole", "west", "jordan", "owens", "reynolds",
        "fisher", "ellis", "harrison", "gibson", "mcdonald", "cruz", "marshall",
        "ortiz", "gomez", "murray", "freeman", "wells", "webb", "simpson",
        "stevens", "tucker", "porter", "hunter", "hicks", "crawford", "henry",
        "boyd", "mason", "morales", "kennedy", "warren", "dixon", "ramos", "reyes",
        "burns", "gordon", "shaw", "holmes", "rice", "robertson", "hunt", "black",
        "daniels", "palmer", "mills", "nichols", "grant", "knight", "ferguson",
        "rose", "stone", "hawkins", "dunn", "perkins", "hudson", "spencer",
        "gardner", "stephens", "payne", "pierce", "berry", "matthews", "arnold",
        "wagner", "willis", "ray", "watkins", "olson", "carroll", "duncan",
        "snyder", "hart", "cunningham", "bradley", "lane", "andrews", "ruiz",
        "harper", "fox", "riley", "armstrong", "carpenter", "weaver", "greene",
        "lawrence", "elliott", "chavez", "sims", "austin", "peters", "kelley",
        "franklin", "lawson", "fields", "gutierrez", "ryan", "schmidt", "carr",
        "vasquez", "castillo", "wheeler", "chapman", "oliver", "montgomery",
        "richards", "williamson", "johnston", "banks", "meyer", "bishop", "mccoy",
        "howell", "alvarez", "morrison", "hansen", "fernandez", "garza", "harvey",
        "little", "burton", "stanley", "nguyen", "george", "jacobs", "reid",
        "kim", "fuller", "lynch", "dean", "gilbert", "garrett", "romero",
        "welch", "larson", "frazier", "burke", "hanson", "day", "mendoza",
        "moreno", "bowman", "medina", "fowler", "brewer", "hoffman", "carlson",
        "silva", "pearson", "holland", "douglas", "fleming", "jensen", "vargas",
        "byrd", "davidson", "hopkins", "may", "terry", "herrera", "wade",
        "soto", "walters", "curtis", "neal", "caldwell", "lowe", "jennings",
        "barnett", "graves", "jimenez", "horton", "shelton", "barrett", "obrien",
        "castro", "sutton", "gregory", "mckinney", "lucas", "miles", "craig",
        "rodriquez", "chambers", "holt", "lambert", "fletcher", "watts", "bates",
        "hale", "rhodes", "pena", "beck", "newman", "haynes", "mcdaniel",
        "mendez", "bush", "vaughn", "parks", "dawson", "santiago", "norris",
        "hardy", "love", "steele", "curry", "powers", "schultz", "barker",
        "guzman", "page", "munoz", "ball", "keller", "chandler", "weber",
        "leonard", "walsh", "lyons", "ramsey", "wolfe", "schneider", "mullins",
        "benson", "sharp", "bowen", "daniel", "barber", "cummings", "hines",
        "baldwin", "griffith", "valdez", "hubbard", "salazar", "reeves", "warner",
        "stevenson", "burgess", "santos", "tate", "cross", "garner", "mann",
        "mack", "moss", "thornton", "dennis", "mcgee", "farmer", "delgado",
        "aguilar", "vega", "glover", "manning", "cohen", "harmon", "rodgers",
        "robbins", "newton", "todd", "blair", "higgins", "ingram", "reese",
        "cannon", "strickland", "townsend", "potter", "goodwin", "walton",
        "rowe", "hampton", "orlando", "patton", "swanson", "joseph", "paul",
        "morgan", "wolfe", "figueroa", "ballard", "tucker", "hinton", "acosta",
        "huff", "weiss", "daugherty", "fitzgerald", "dodson", "britton", "barrera",
        "avila", "sharp", "finley", "hurley", "rosales", "huang", "frye",
        "salinas", "ayers", "lamb", "rosa", "cardona", "powers", "zamora",
        "swain", "lu", "ewing", "york", "hauser", "mcconnell", "gilmore",
        "brito", "foreman", "stout", "valencia", "merrill", "mayer", "alford",
        "mcpherson", "acevedo", "donovan", "barrera", "albert", "cote", "reilly",
        "compton", "raymond", "mooney", "mcgowan", "craft", "cleveland", "clemons",
        "wynn", "nielsen", "baird", "stanton", "snider", "rosales", "bright",
        "witt", "stuart", "hays", "holden", "rutledge", "kinney", "clements",
        "castaneda", "slater", "hahn", "emerson", "conrad", "burks", "delaney",
        "pate", "lancaster", "sweet", "justice", "tyson", "sharpe", "whitfield",
        "talley", "macias", "irwin", "burris", "ratliff", "mccray", "madden",
        "kaufman", "beach", "goff", "cash", "bolton", "mcfadden", "levine",
        "good", "byers", "kirkland", "kidd", "workman", "carney", "dale",
        "mcleod", "holcomb", "england", "finch", "head", "burt", "hendrix",
        "sosa", "haney", "franks", "sargent", "nieves", "downs", "rasmussen"
    ]
    
    emails = []
    
    # Generate emails using various patterns
    for i in range(count):
        # Different email generation patterns
        pattern = i % 8
        
        if pattern == 0:
            # firstname.lastname@domain
            first = random.choice(first_names)
            last = random.choice(last_names)
            domain = random.choice(domains)
            email = f"{first}.{last}@{domain}"
        elif pattern == 1:
            # firstname@domain
            first = random.choice(first_names)
            domain = random.choice(domains)
            email = f"{first}@{domain}"
        elif pattern == 2:
            # firstname_lastname@domain
            first = random.choice(first_names)
            last = random.choice(last_names)
            domain = random.choice(domains)
            email = f"{first}_{last}@{domain}"
        elif pattern == 3:
            # firstname+tag@domain
            first = random.choice(first_names)
            tag = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            domain = random.choice(domains)
            email = f"{first}+{tag}@{domain}"
        elif pattern == 4:
            # firstname123@domain
            first = random.choice(first_names)
            number = random.randint(1, 999)
            domain = random.choice(domains)
            email = f"{first}{number}@{domain}"
        elif pattern == 5:
            # firstname.lastname123@domain
            first = random.choice(first_names)
            last = random.choice(last_names)
            number = random.randint(1, 99)
            domain = random.choice(domains)
            email = f"{first}.{last}{number}@{domain}"
        elif pattern == 6:
            # random string@domain
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            domain = random.choice(domains)
            email = f"{username}@{domain}"
        else:
            # firstname.lastname.year@domain
            first = random.choice(first_names)
            last = random.choice(last_names)
            year = random.randint(1990, 2024)
            domain = random.choice(domains)
            email = f"{first}.{last}.{year}@{domain}"
        
        emails.append(email.lower())
    
    return emails

def main():
    """Generate and save test emails"""
    print("Generating 10,000 test email addresses...")
    
    emails = generate_test_emails(10000)
    
    # Save to CSV
    csv_path = Path(__file__).parent / "test_emails_10k.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['email'])  # Header
        for email in emails:
            writer.writerow([email])
    
    print(f"Generated {len(emails)} test emails")
    print(f"Saved to: {csv_path}")
    
    # Show some examples
    print("\nSample emails:")
    for i, email in enumerate(emails[:10]):
        print(f"  {i+1:2d}. {email}")

if __name__ == "__main__":
    main() 