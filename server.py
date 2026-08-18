"""
Persona 5 Royal Web Save Editor — High-Performance Local Web Backend
Serves a sleek, highly responsive Persona 5 Phantom Thief web application
with auto-save discovery, search-by-name dropdowns, human-friendly selectors,
and zero raw ID requirements.
"""

import os
import re
import sys
import json
import base64
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Project paths (frozen PyInstaller vs source script)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PROJECT_ROOT = Path(sys._MEIPASS)
    WEB_APP_DIR = PROJECT_ROOT / "web-app"
else:
    # Depth-aware: this file ships BOTH at project root (main.py imports
    # "server") and under web-app/ (dev sibling). The root copy sits one
    # level higher, so __file__-relative math differs per location.
    _HERE = Path(__file__).resolve().parent
    if (_HERE / "web-app").is_dir() and (_HERE / "core").is_dir():
        PROJECT_ROOT = _HERE          # root copy
        WEB_APP_DIR = _HERE / "web-app"
    else:
        PROJECT_ROOT = _HERE.parent   # web-app copy
        WEB_APP_DIR = _HERE

sys.path.insert(0, str(PROJECT_ROOT))

from core.editor import SaveEditor, CONFIDANT_ARCANA_MAP, ROMANCEABLE_CONFIDANTS
from core import instances  # noqa: E402
from core.environment import (
    discover_steam_save_dirs,
    list_save_files,
    check_running_processes,
    create_timestamped_backup,
    list_backups,
    restore_backup,
)

PORT = 3000

# Cached reference tables for human-readable search & autocompletion
def build_reference_db():
    ed = SaveEditor()
    CONFIDANT_PROFILES = {
        'Fool': {'name': 'Igor', 'role': 'Prison Master', 'type': 'story', 'unlock': 'Wild Talk / Persona Fusion', 'img': 'igor.png', 'unlock_date': '4/11'},
        'Magician': {'name': 'Morgana', 'role': 'Phantom Guide / Mona', 'type': 'party', 'unlock': 'Infiltration Tools / Pickpocket', 'img': 'morgana.png', 'unlock_date': '4/15'},
        'Priestess': {'name': 'Makoto Niijima', 'role': 'Queen / Strategist', 'type': 'romance', 'unlock': 'Shadow Calc / Analysis', 'img': 'makoto.png', 'unlock_date': '6/24'},
        'Empress': {'name': 'Haru Okumura', 'role': 'Noir / Heiress', 'type': 'romance', 'unlock': 'Vegetable Gardening / SP Veggies', 'img': 'haru.png', 'unlock_date': '10/30'},
        'Emperor': {'name': 'Yusuke Kitagawa', 'role': 'Fox / Artist', 'type': 'party', 'unlock': 'Skill Card Duplication', 'img': 'yusuke.png', 'unlock_date': '6/18'},
        'Hierophant': {'name': 'Sojiro Sakura', 'role': 'Leblanc Owner / Boss', 'type': 'social', 'unlock': 'Master Coffee & Curry Brewing', 'img': 'sojiro.png', 'unlock_date': '4/20'},
        'Lovers': {'name': 'Ann Takamaki', 'role': 'Panther / Model', 'type': 'romance', 'unlock': 'Baton Pass / Girl Talk', 'img': 'ann.png', 'unlock_date': '5/6'},
        'Chariot': {'name': 'Ryuji Sakamoto', 'role': 'Skull / Track Star', 'type': 'party', 'unlock': 'Insta-Kill / Dash Ambush', 'img': 'ryuji.png', 'unlock_date': '4/12'},
        'Justice': {'name': 'Goro Akechi', 'role': 'Crow / Detective Prince', 'type': 'story_deadline', 'unlock': 'Sleuth Instinct (Deadline: 11/17)', 'img': 'akechi.png', 'unlock_date': '6/10'},
        'Hermit': {'name': 'Futaba Sakura', 'role': 'Oracle / Hacker', 'type': 'romance', 'unlock': 'Position Hack / Moral Support', 'img': 'futaba.png', 'unlock_date': '8/31'},
        'Fortune': {'name': 'Chihaya Mifune', 'role': 'Shinjuku Fortune Teller', 'type': 'romance', 'unlock': 'Affinity & Money Luck Reading', 'img': 'chihaya.png', 'unlock_date': '6/22'},
        'Strength': {'name': 'Caroline & Justine', 'role': 'Velvet Wardens', 'type': 'story', 'unlock': 'Special Guillotine / Paid Fusion', 'img': 'twins.png', 'unlock_date': '5/18'},
        'Hanged Man': {'name': 'Munehisa Iwai', 'role': 'Airsoft Shop Owner', 'type': 'social', 'unlock': 'Custom Gun Modifications', 'img': 'iwai.png', 'unlock_date': '5/6'},
        'Death': {'name': 'Tae Takemi', 'role': 'Yongen Clinic Doctor', 'type': 'romance', 'unlock': 'Clinic Medicine Discount & SP Adhesives', 'img': 'takemi.png', 'unlock_date': '4/18'},
        'Temperance': {'name': 'Sadayo Kawakami', 'role': 'Homeroom Teacher / Maid', 'type': 'romance', 'unlock': 'Housework Slack-off & Special Massage', 'img': 'kawakami.png', 'unlock_date': '5/24'},
        'Devil': {'name': 'Ichiko Ohya', 'role': 'Paparazzi Journalist', 'type': 'romance', 'unlock': 'Palace Security Alert Reduction', 'img': 'ohya.png', 'unlock_date': '6/23'},
        'Tower': {'name': 'Shinya Oda', 'role': 'Gamer Kid / King', 'type': 'social', 'unlock': 'Down Shot / Bullet Hail', 'img': 'shinya.png', 'unlock_date': '9/4'},
        'Star': {'name': 'Hifumi Togo', 'role': 'Kanda Shogi Master', 'type': 'romance', 'unlock': 'Togo System / Battle Party Swap', 'img': 'hifumi.png', 'unlock_date': '6/25'},
        'Moon': {'name': 'Yuuki Mishima', 'role': 'Phan-Site Admin', 'type': 'social', 'unlock': 'EXP Share & Backup Party EXP', 'img': 'mishima.png', 'unlock_date': '5/6'},
        'Sun': {'name': 'Toranosuke Yoshida', 'role': 'Shibuya Politician', 'type': 'social', 'unlock': 'Extortion / Smooth Talk Negotiations', 'img': 'yoshida.png', 'unlock_date': '5/6'},
        'Judgement': {'name': 'Sae Niijima', 'role': 'Prosecutor / Inquisitor', 'type': 'story', 'unlock': 'Story Progression Arcana', 'img': 'sae.png', 'unlock_date': '7/9'},
        'Faith': {'name': 'Kasumi Yoshizawa', 'role': 'Violet / Gymnast', 'type': 'romance_deadline', 'unlock': 'Chaotic Foil (Rank 5 Cap until Jan)', 'img': 'kasumi.png', 'unlock_date': '5/30'},
        'Councillor': {'name': 'Dr. Takuto Maruki', 'role': 'Shujin Counselor', 'type': 'story_deadline', 'unlock': 'Flow / Detox (Req: Rank 9 by 11/18)', 'img': 'maruki.png', 'unlock_date': '5/13'}
    }

    db = {
        "personas": [],
        "skills": [],
        "traits": [],
        "items": [],
        "confidants": list(CONFIDANT_ARCANA_MAP.keys()),
        "confidant_profiles": CONFIDANT_PROFILES,
        "romanceable": list(ROMANCEABLE_CONFIDANTS),
        "story_locked_confidants": list(SaveEditor.CONFIDANT_STORY_LOCKED),
        "point_thresholds": SaveEditor.CONFIDANT_POINT_THRESHOLDS,
    }
    
    # Personas — filter out cut-content / legacy entries. The raw table
    # (464 ids) contains: id 0, "RESERVE"/"???"/blank names, "P5 Unused"
    # (0x167), and the compendium dead bits (P5-legacy duplicate entries the
    # game never uses in any context). Serving these lets users equip
    # persona ids with no Royal record/model -> Velvet Room / battle crash.
    # IDs >232 (Raoul 0x16B, William 0xF2, DLC space) are VALID for stock
    # editing (verified in oracle saves) — keep them.
    BAD_PERSONA_NAMES = {"", "RESERVE", "???", "BLANK", "----------", "P5 Unused"}
    ptable = ed._load_table("Personas.txt") or {}
    for pid, name in sorted(ptable.items()):
        if pid == 0 or name in BAD_PERSONA_NAMES or pid in SaveEditor.PC31_STOCK_LEGACY_IDS:
            continue
        if name.startswith("Lab "):  # dev/test-only personas, not in NAME.TBL
            continue
        db["personas"].append({"id": pid, "name": name})

    # Skills — strip dummy/placeholder slots: 0x0000-0x0009 (BLANK) plus
    # named placeholders and cut-content markers. They pass table validation
    # but produce corrupt persona cards / broken skill menus in battle.
    BAD_SKILL_NAMES = {"", "BLANK", "RESERVE", "----------", "not used"}
    # Names the game's own NAME.TBL does NOT contain (verified 2026-08-16
    # against the extracted EN name table). These are item names, test
    # skills, and dev strings that leaked into the Ruimusume dump.
    NON_SKILL_PREFIXES = (
        "adam skill", "ally", "roulette:", "shoes", "juice bar", "juicer bar",
        "energy drink", "soda", "ration", "drug store", "special coffee",
        "new curry", "sup hp", "sup sp", "support plus", "all-out lv",
        "dark akechi", "charisma speak",
    )
    # Skill ids whose dump name is not the game's name (corrected to the
    # NAME.TBL spelling) — dropdown display only; ids are unchanged.
    SKILL_NAME_FIXES = {
        123: "Med Burn", 126: "Med Freeze", 129: "Med Shock", 134: "Med Dizzy",
        137: "Med Confuse", 142: "Med Fear", 145: "Med Forget", 148: "Med Brainwash",
        153: "Med Sleep", 156: "Med Rage", 159: "Med Despair", 164: "Med All Ail",
        516: "Royal Jelly", 295: "Ultimate Support",
    }
    # Exact ids that are dev/test strings with no real skill definition.
    NON_SKILL_IDS = {658, 659, 660, 677, 734, 735, 751, 753, 663}
    stable = ed._load_table("Skill ID.txt") or {}
    for sid, name in sorted(stable.items()):
        nl = name.lower()
        if sid <= 0x09 or name in BAD_SKILL_NAMES or name.lower().startswith("unused:"):
            continue
        if sid in NON_SKILL_IDS or any(nl.startswith(p) for p in NON_SKILL_PREFIXES):
            continue
        db["skills"].append({"id": sid, "name": SKILL_NAME_FIXES.get(sid, name)})

    # Traits — same treatment as skills: 200 of 300 rows are RESERVE/blank
    # placeholders (verified 2026-08-16). Serve only the 100 named traits;
    # id 0 is offered as an explicit "None (unset)" option. Names corrected
    # to the game's NAME.TBL spelling (Savior/Skillful/Deathly Illness).
    BAD_TRAIT_NAMES = {"", "RESERVE", "???", "BLANK", "----------"}
    TRAIT_NAME_FIXES = {9: "Savior Bloodline", 73: "Skillful Combo", 102: "Deathly Illness"}
    ttable = ed._load_table("Traits.txt") or {}
    for tid, name in sorted(ttable.items()):
        if tid == 0:
            db["traits"].append({"id": 0, "name": "None (unset)"})
        elif name not in BAD_TRAIT_NAMES:
            db["traits"].append({"id": tid, "name": TRAIT_NAME_FIXES.get(tid, name)})

    # Skill metadata (element/cost/area) from the game's SKILL.TBL via
    # data/SkillMeta.txt (generated 2026-08-16 from decoded game fixture;
    # verified: Agi=4SP, Hassou Tobi=25%HP, Myriad Truths=40SP).
    skill_meta = {}
    meta_path = os.path.join(PROJECT_ROOT, "data", "SkillMeta.txt")
    try:
        with open(meta_path, encoding="utf-8") as mf:
            for ln in mf.read().splitlines()[1:]:
                pcol = ln.split("	")
                if len(pcol) >= 6 and pcol[0].strip().isdigit():
                    skill_meta[int(pcol[0])] = {
                        "element": int(pcol[1]),
                        "costtype": int(pcol[2]),
                        "cost": float(pcol[3]),
                        "area": int(pcol[4]),
                        "passive": int(pcol[5]),
                    }
    except OSError:
        pass
    db["skill_meta"] = skill_meta

    # Dedupe by NAME across all three lists (verified 2026-08-16): the
    # Ruimusume dumps carry one row per persona-slot, so one trait/skill/
    # persona can appear under several ids (e.g. "Ultimate Vessel" x9 =
    # ids 0x119-0x121, a single trait per the P5R Compendium; the corpus
    # of 12 real saves uses the LOWEST ids in each group — 0x119, and the
    # compendium-space persona ids). Keep the lowest id per name: it is the
    # canonical entry and the one real saves write.
    def _dedupe_by_name(items):
        seen = set()
        out = []
        for it in items:
            key = it["name"].lower()
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out

    db["personas"] = _dedupe_by_name(db["personas"])
    # Full id->name map for the compendium grid (2026-08-16): party personas
    # whose names duplicate earlier ids (Satanael 0xD3, Carmen 0xDF, the
    # 0xE1-0xE8 block) are dropped by the dropdown dedupe but must still
    # render with their real names in the grid.
    db["persona_names"] = {
        pid: name for pid, name in sorted(ptable.items())
        if pid != 0 and name not in BAD_PERSONA_NAMES
    }
    db["skills"] = _dedupe_by_name(db["skills"])
    db["traits"] = _dedupe_by_name(db["traits"])
        
    # Items & Categories (100% Authentic In-Game 1-9 P5R Category Sequence)
    db["items"] = []
    data_dir = PROJECT_ROOT / "data"
    
    # Strict In-Game Category Order:
    # 1. Consumables (0x2000)
    # 2. Infiltration Tools & Materials (0x6000)
    # 3. Skill Cards (0x4000)
    # 4. Melee Weapons (0x1000)
    # 5. Ranged Weapons (0x7000)
    # 6. Protectors & Outfits (0x5000)
    # 7. Accessories (0x3000)
    # 8. Materials & Treasures (0x8000)
    # 9. Key Items & Story Essentials (0x9000)
    CATEGORY_MAPPING = [
        (0x2000, "Items.txt", "Consumable"),
        (0x6000, "Tools&materials.txt", "Infiltration"),
        (0x4000, "Skill Cards.txt", "SkillCard"),
        (0x1000, "Weapon melee.txt", "Melee"),
        (0x7000, "Weapon ranged.txt", "Ranged"),
        (0x5000, "Clothes.txt", "Protector"),
        (0x3000, "Accessories.txt", "Accessory"),
        (0x8000, "Treasure.txt", "Treasure"),
        (0x9000, "Keyitems&essentials.txt", "KeyItem"),
    ]

    seen_ids = set()
    # Item name fixes verified against the game's NAME.TBL (2026-08-16).
    ITEM_NAME_FIXES = {
        8270: "Money Distributor", 8271: "Item Distributor",
        8304: "Discharge Crystal", 8398: "Hifumi's Chocolate",
        8529: "Old Man's Elixir", 12400: "Vajra Belt",
        12417: "Blazing Horns", 12418: "Inferno Horns",
        12642: "Judgment Cross", 12736: "Spiral Rasetsu Anklet",
        12782: "Dazzling Netsuke", 8420: "Sakura Amezaiku",
        8375: "Oh! Shiruko",
    }
    for prefix, fname, cat in CATEGORY_MAPPING:
        p = data_dir / fname
        if not p.exists():
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for idx, line in enumerate(f):
                    parts = line.strip().split("\t")
                    en_name = None
                    if len(parts) >= 4:
                        en_name = parts[3].strip()
                    elif len(parts) == 1 and parts[0]:
                        en_name = parts[0].strip()

                    if (
                        en_name
                        and en_name not in ["EN_NAME", "BLANK", "RESERVE", "----------", "使用禁止", "Unused", "unused", "Unused Item"]
                        and "RESERVE" not in en_name
                        and "BLANK" not in en_name
                        and not en_name.lower().startswith("unused")
                    ):
                        iid = prefix | (idx & 0x0FFF)
                        if iid not in seen_ids:
                            seen_ids.add(iid)
                            # raw hex placeholder rows (e.g. "0x1E2") never
                            # resolve to a real item -- exclude them.
                            if re.match(r"^0x[0-9A-Fa-f]+$", en_name):
                                continue
                            db["items"].append({
                                "id": iid,
                                "name": ITEM_NAME_FIXES.get(iid, en_name),
                                "category": cat
                            })
        except Exception as e:
            print(f"[P5R] Error loading {fname}: {e}")

    return db

REFERENCE_DB = build_reference_db()
BUILD_ID = "audit-2026-08-16"
CURRENT_EDITOR = None
CURRENT_FILE_PATH = None

class P5RWebHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_APP_DIR / "static"), **kwargs)

    def log_message(self, format, *args):  # noqa: A002
        pass

    def handle_error(self, request, client_address):
        """Capture handler exceptions to a file (frozen exe has no console)."""
        import traceback
        try:
            err_path = os.path.join(
                os.environ.get("TEMP", "."), "P5R_handler_errors.log"
            )
            with open(err_path, "a", encoding="utf-8") as fh:
                fh.write(
                    f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"from {client_address}: {self.command} {self.path}\n"
                )
                traceback.print_exc(file=fh)
        except Exception:
            pass

    def do_GET(self):
        global CURRENT_EDITOR, CURRENT_FILE_PATH
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            template_path = WEB_APP_DIR / "templates" / "index.html"
            with open(template_path, "rb") as f:
                self.wfile.write(f.read())
            return
        elif parsed.path == "/game" or parsed.path == "/game/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            game_index = PROJECT_ROOT / "p5r-game-client" / "index.html"
            with open(game_index, "rb") as f:
                self.wfile.write(f.read())
            return
        elif parsed.path.startswith("/game/"):
            rel_file = parsed.path[len("/game/"):]
            game_dir = PROJECT_ROOT / "p5r-game-client"
            game_file = (game_dir / rel_file).resolve()
            try:
                game_file.relative_to(game_dir.resolve())
            except ValueError:
                self.send_json(400, {"error": "Invalid game asset path."})
                return
            if game_file.exists() and game_file.is_file():
                self.send_response(200)
                if rel_file.endswith(".css"):
                    self.send_header("Content-type", "text/css; charset=utf-8")
                elif rel_file.endswith(".js"):
                    self.send_header("Content-type", "application/javascript; charset=utf-8")
                else:
                    self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(game_file, "rb") as f:
                    self.wfile.write(f.read())
                return
        elif parsed.path == "/api/build":
            self.send_json(200, {"build": BUILD_ID})
            return
        elif parsed.path == "/api/state":
            self.send_json(200, {
                "pid": os.getpid(),
                "save": CURRENT_FILE_PATH or "",
            })
            return
        elif parsed.path == "/api/database":
            self.send_json(200, REFERENCE_DB)
            return
        elif parsed.path == "/api/discovery":
            dirs = discover_steam_save_dirs()
            saves = []
            if dirs:
                for s in list_save_files(dirs[0]):
                    saves.append(str(s))
            self.send_json(200, {"discovered_dirs": [str(d) for d in dirs], "saves": saves})
            return
        elif parsed.path == "/api/backups":
            if not CURRENT_FILE_PATH or not os.path.exists(CURRENT_FILE_PATH):
                self.send_json(200, {"backups": []})
                return
            backups = [p.name for p in list_backups(Path(CURRENT_FILE_PATH))]
            self.send_json(200, {"backups": backups})
            return

        super().do_GET()

    def do_POST(self):
        global CURRENT_EDITOR, CURRENT_FILE_PATH
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = {}
        if body:
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                pass

        if parsed.path == "/api/load":
            path_str = data.get("path", "").strip()
            if not path_str:
                self.send_json(400, {"error": "Save file path is required."})
                return
            p = Path(path_str).resolve()
            if not p.is_file():
                self.send_json(400, {"error": "Save file not found."})
                return
            try:
                with open(p, "rb") as f:
                    raw = f.read()
                CURRENT_EDITOR = SaveEditor(raw)
                CURRENT_FILE_PATH = str(p)
                instances.update_save(CURRENT_FILE_PATH)

                # Assemble clean full payload
                hdr = CURRENT_EDITOR.parser.header
                names = CURRENT_EDITOR.parser.player_names
                quick_info = CURRENT_EDITOR.get_quick_info()
                integrity = CURRENT_EDITOR.integrity_report()
                confidants = CURRENT_EDITOR.get_confidant_ranks()
                social = CURRENT_EDITOR.get_social_stats()
                party = CURRENT_EDITOR.get_party_stats()

                # Only show members who have actually joined the story.
                # Un-joined slots (Makoto/Futaba/Haru/Akechi/Kasumi before
                # their join dates) are seeded placeholders — hiding them
                # prevents both story spoilers and unsafe edits.
                party = [p for p in party if p.get("joined", False)]

                # Get equipped persona info for each party member
                party_personas = []
                for entry in party:
                    slot = entry["slot"]
                    p_info = CURRENT_EDITOR.get_equipped_persona(slot)
                    party_personas.append({
                        "slot": slot,
                        "name": entry.get("name", f"Member {slot}"),
                        "level": entry.get("level", 1),
                        "hp": entry.get("hp", 100),
                        "sp": entry.get("sp", 50),
                        "persona": p_info
                    })

                # Parse accurate playtime from authoritative quick_info seconds
                playtime_sec = quick_info.get("playtime") or hdr.playtime or 0
                if playtime_sec > 500000: # if raw unscaled counter, normalize from quick_info
                    playtime_sec = quick_info.get("playtime", 0)

                # Get Joker's full 12-slot stock persona inventory
                joker_stock = CURRENT_EDITOR.get_persona_stock(0)
                inventory = CURRENT_EDITOR.get_inventory()
                compendium = CURRENT_EDITOR.get_compendium()

                resp = {
                    "file_path": CURRENT_FILE_PATH,
                    "header": {
                        "fname": hdr.fname,
                        "lname": hdr.lname,
                        "group_name": names.group_name_utf8,
                        "money": CURRENT_EDITOR.get_money(),
                        "day": quick_info.get("day", str(hdr.day)),
                        "level": quick_info.get("level", "22"),
                        "playtime": f"{playtime_sec // 3600}h {(playtime_sec % 3600) // 60}m"
                    },
                    "social_stats": social,
                    "confidants": confidants,
                    "party": party_personas,
                    "joker_stock": joker_stock,
                    "inventory": inventory,
                    "compendium": compendium,
                    "integrity": integrity
                }
                _conflicts = instances.find_conflicts(CURRENT_FILE_PATH)
                if _conflicts:
                    resp["notice"] = (
                        "This save is also open in another window — last save wins."
                    )
                self.send_json(200, resp)
            except Exception as e:
                self.send_json(500, {"error": f"Failed to load save: {str(e)}"})

        elif parsed.path == "/api/save":
            if not CURRENT_EDITOR or not CURRENT_FILE_PATH:
                self.send_json(400, {"error": "No save file loaded."})
                return

            p5r_run, _ = check_running_processes()
            if p5r_run:
                self.send_json(409, {"error": "P5R.exe is currently running! Please close the game before saving."})
                return

            try:
                # 1. Automatic Timestamped Backup
                p = Path(CURRENT_FILE_PATH)
                backup_path = create_timestamped_backup(p)

                # 2. Apply Header Edits
                hdr_in = data.get("header", {})
                CURRENT_EDITOR.set_player_names(
                    hdr_in.get("fname", ""),
                    hdr_in.get("lname", ""),
                    hdr_in.get("group_name", "")
                )
                if "money" in hdr_in:
                    CURRENT_EDITOR.set_money(int(hdr_in["money"]))

                # 3. Apply Social Stats
                soc_in = data.get("social_stats", {})
                if soc_in:
                    def _extract_stat_rank(val):
                        if isinstance(val, dict):
                            return int(val.get("rank", 5))
                        return int(val) if val is not None else 5

                    CURRENT_EDITOR.set_social_stats(
                        _extract_stat_rank(soc_in.get("Knowledge", 5)),
                        _extract_stat_rank(soc_in.get("Charm", 5)),
                        _extract_stat_rank(soc_in.get("Proficiency", 5)),
                        _extract_stat_rank(soc_in.get("Kindness", 5)),
                        _extract_stat_rank(soc_in.get("Guts", 5)),
                    )

                # 4. Apply Confidants
                conf_in = data.get("confidants", {})
                for cname, cdata in conf_in.items():
                    if cname in CONFIDANT_ARCANA_MAP:
                        arc_id = CONFIDANT_ARCANA_MAP[cname]
                        rank = int(cdata.get("rank", 0)) if isinstance(cdata, dict) else int(cdata)
                        CURRENT_EDITOR.set_confidant_rank(arc_id, rank, auto_unlock=True)

                # 5. Apply Party & Persona
                party_in = data.get("party", [])
                for member in party_in:
                    slot = member.get("slot")
                    if slot is not None:
                        CURRENT_EDITOR.set_party_stat(
                            slot,
                            level=int(member.get("level", 1)),
                            hp=int(member.get("hp", 100)),
                            sp=int(member.get("sp", 50))
                        )
                        pers = member.get("persona")
                        if pers and "persona_id" in pers:
                            # Safely extract skills
                            raw_skills = pers.get("skills", [0]*8)
                            parsed_skills = []
                            for s in raw_skills:
                                if isinstance(s, dict):
                                    parsed_skills.append(int(s.get("id", 0)))
                                else:
                                    parsed_skills.append(int(s) if s is not None else 0)

                            # Safely extract stats
                            raw_stats = pers.get("stats", [10]*5)
                            parsed_stats = []
                            if isinstance(raw_stats, dict):
                                parsed_stats = [
                                    int(raw_stats.get("st", 10)),
                                    int(raw_stats.get("ma", 10)),
                                    int(raw_stats.get("en", 10)),
                                    int(raw_stats.get("ag", 10)),
                                    int(raw_stats.get("lu", 10))
                                ]
                            elif isinstance(raw_stats, list):
                                parsed_stats = [int(st) if st is not None else 10 for st in raw_stats]
                            else:
                                parsed_stats = [10]*5

                            CURRENT_EDITOR.set_equipped_persona(
                                slot,
                                persona_id=int(pers.get("persona_id", 0)),
                                level=int(pers.get("level", 1)),
                                trait_id=int(pers.get("trait_id", 0)),
                                exp=int(pers.get("exp", 0)),
                                skills=parsed_skills,
                                stats=parsed_stats,
                                flags=int(pers.get("flags", 1))
                            )

                # 5b. Apply Joker's 12-slot Persona Stock
                stock_in = data.get("joker_stock", [])
                for s_entry in stock_in:
                    s_slot = s_entry.get("slot")
                    if s_slot is not None and 0 <= s_slot < 12:
                        pid = int(s_entry.get("persona_id", 0))

                        # Safely extract skills
                        raw_skills = s_entry.get("skills", [0]*8)
                        parsed_skills = []
                        for s in raw_skills:
                            if isinstance(s, dict):
                                parsed_skills.append(int(s.get("id", 0)))
                            else:
                                parsed_skills.append(int(s) if s is not None else 0)

                        # Safely extract stats
                        raw_stats = s_entry.get("stats", [10]*5)
                        parsed_stats = []
                        if isinstance(raw_stats, dict):
                            parsed_stats = [
                                int(raw_stats.get("st", 10)),
                                int(raw_stats.get("ma", 10)),
                                int(raw_stats.get("en", 10)),
                                int(raw_stats.get("ag", 10)),
                                int(raw_stats.get("lu", 10))
                            ]
                        elif isinstance(raw_stats, list):
                            parsed_stats = [int(st) if st is not None else 10 for st in raw_stats]
                        else:
                            parsed_stats = [10]*5

                        CURRENT_EDITOR.set_persona_stock_slot(
                            member_slot=0,
                            stock_k=s_slot,
                            persona_id=pid,
                            level=int(s_entry.get("level", 1)),
                            trait_id=int(s_entry.get("trait_id", 0)),
                            exp=int(s_entry.get("exp", 0)),
                            skills=parsed_skills,
                            stats=parsed_stats,
                            flags=int(s_entry.get("flags", 1))
                        )

                # 5c. Apply Active Inventory Items
                inv_in = data.get("inventory", [])
                for entry in inv_in:
                    slot = entry.get("slot")
                    if slot is not None and 0 <= slot < 30:
                        iid = int(entry.get("item_id", 0))
                        qty = int(entry.get("quantity", 0))
                        CURRENT_EDITOR.set_inventory_slot(slot, iid, qty)

                # 5d. Apply Compendium Registrations
                if data.get("unlock_compendium"):
                    CURRENT_EDITOR.unlock_compendium_100()
                elif "compendium" in data and isinstance(data["compendium"], dict):
                    comp = data["compendium"]
                    if comp and comp.get("supported"):
                        registered_list = set(comp.get("registered", []))
                        for pid in range(1, CURRENT_EDITOR.PC31_COMPENDIUM_MAX_ID + 1):
                            is_reg = pid in registered_list
                            CURRENT_EDITOR.set_compendium_registration(pid, is_reg)
                        # Sanitize any rogue bytes in the gap
                        d_tmp = bytearray(CURRENT_EDITOR.parser.data_payload)
                        for gap_start, gap_end in ((0x09460, 0x09940), (0x21970, 0x21E50)):
                            if gap_end <= len(d_tmp):
                                d_tmp[gap_start:gap_end] = b"\x00" * (gap_end - gap_start)
                        CURRENT_EDITOR.parser.data_payload = bytes(d_tmp)

                # 6. Repack & Sign
                out_bytes = CURRENT_EDITOR.save_to_bytes()
                p.write_bytes(out_bytes)

                # Reload for fresh integrity validation
                CURRENT_EDITOR = SaveEditor(p.read_bytes())
                integrity = CURRENT_EDITOR.integrity_report()

                resp = {
                    "status": "success",
                    "backup": backup_path.name,
                    "integrity": integrity,
                    "message": "Save file successfully re-signed and saved!"
                }
                _conflicts = instances.find_conflicts(CURRENT_FILE_PATH)
                if _conflicts:
                    resp["notice"] = (
                        "This save is also open in another window — last save wins."
                    )
                self.send_json(200, resp)
            except Exception as e:
                self.send_json(500, {"error": f"Failed to save file: {str(e)}"})

        elif parsed.path == "/api/restore":
            backup_name = data.get("backup_name", "")
            if not CURRENT_FILE_PATH or not backup_name:
                self.send_json(400, {"error": "Missing backup file or save path."})
                return
            if not re.fullmatch(r"[A-Za-z0-9_.\-]+", backup_name):
                self.send_json(400, {"error": "Invalid backup name."})
                return
            try:
                p = Path(CURRENT_FILE_PATH)
                backup_zip = p.parent / "backups" / backup_name
                safety = restore_backup(p, backup_zip)
                CURRENT_EDITOR = SaveEditor(p.read_bytes())
                self.send_json(200, {"status": "success", "safety_backup": safety.name})
            except Exception as e:
                self.send_json(500, {"error": f"Restore failed: {str(e)}"})

        elif parsed.path == "/api/emergency-rescue":
            action = data.get("action")
            if not CURRENT_EDITOR:
                self.send_json(400, {"error": "No save loaded."})
                return
            if action == "third_semester":
                res = CURRENT_EDITOR.unlock_third_semester()
                self.send_json(200, res)
            else:
                self.send_json(400, {"error": "Unknown emergency action."})

    def send_json(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

def start_server():
    server = HTTPServer(("127.0.0.1", PORT), P5RWebHandler)
    print(f"[P5R] Persona 5 Royal Web App running at http://127.0.0.1:{PORT}")
    print("[P5R] Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[P5R] Server stopped.")

def main():
    start_server()


if __name__ == "__main__":
    main()
