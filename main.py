import sys, os, sqlite3, subprocess, shlex, json
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QPixmap, QFont, QIcon, QAction, QPainter, QColor, QLinearGradient, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget, QLineEdit,
    QFileDialog, QMessageBox, QFrame, QScrollArea, QGridLayout, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox, QSplitter, QGraphicsBlurEffect
)

APP_NAME = "GAMESVERSE"

def resource_path(relative_path):
    """Resolve bundled resources in development and in a PyInstaller build."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / APP_NAME
DB_PATH = APP_DIR / "gamesverse.db"
ART_DIR = APP_DIR / "artwork"
APP_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR.mkdir(parents=True, exist_ok=True)

CONSOLES = {
    "Sony": ["PlayStation", "PlayStation 2", "PlayStation 3", "PlayStation 4", "PlayStation 5", "PS one", "PSP", "PS Vita"],
    "Microsoft": ["Xbox", "Xbox 360", "Xbox One", "Xbox Series X|S"],
    "Nintendo": ["Color TV-Game", "NES / Famicom", "SNES / Super Famicom", "Nintendo 64", "GameCube", "Wii", "Wii U", "Nintendo Switch", "Game Boy", "Game Boy Color", "Game Boy Advance", "Nintendo DS", "Nintendo 3DS", "Virtual Boy"],
    "Sega": ["SG-1000", "Master System", "Mega Drive / Genesis", "Sega CD / Mega-CD", "32X", "Saturn", "Dreamcast", "Game Gear", "Pico"],
    "Atari": ["Atari 2600", "Atari 5200", "Atari 7800", "Atari Lynx", "Atari Jaguar", "Atari XEGS", "Atari VCS (2021)"],
    "NEC": ["PC Engine / TurboGrafx-16", "PC Engine CD", "SuperGrafx", "PC-FX"],
    "SNK": ["Neo Geo AES", "Neo Geo MVS", "Neo Geo CD", "Neo Geo Pocket", "Neo Geo Pocket Color"],
    "Bandai": ["WonderSwan", "WonderSwan Color", "SwanCrystal", "Playdia"],
    "Panasonic / 3DO": ["3DO Interactive Multiplayer"],
    "Philips": ["CD-i"],
    "Mattel": ["Intellivision", "HyperScan"],
    "Coleco": ["ColecoVision"],
    "Magnavox": ["Odyssey", "Odyssey 2 / Videopac"],
    "Commodore": ["Commodore 64", "Amiga", "CDTV", "Amiga CD32"],
    "Autres systèmes": ["Arcade (MAME)", "MSX", "MSX2", "ZX Spectrum", "Amstrad CPC", "Commodore VIC-20", "Apple II", "DOS / PC rétro", "Autre"]
}
EXTENSIONS = {
    ".iso":"PlayStation 2", ".cso":"PSP", ".pbp":"PSP", ".cue":"PlayStation",
    ".bin":"PlayStation", ".chd":"PlayStation", ".nes":"NES", ".sfc":"SNES",
    ".smc":"SNES", ".n64":"Nintendo 64", ".z64":"Nintendo 64", ".gba":"Game Boy Advance",
    ".gbc":"Game Boy Color", ".gb":"Game Boy", ".nds":"Nintendo DS", ".3ds":"Nintendo 3DS",
    ".gcm":"GameCube", ".wbfs":"Wii", ".wud":"Wii U", ".xci":"Switch", ".nsp":"Switch",
    ".gen":"Mega Drive", ".md":"Mega Drive", ".sms":"Master System", ".gg":"Game Gear",
    ".a26":"Atari 2600", ".a52":"Atari 5200", ".a78":"Atari 7800", ".jag":"Jaguar",
    ".zip":"Autre", ".7z":"Autre"
}

STYLE = """
QMainWindow, QWidget { background:#090a12; color:#f3f2ff; font-family:'Segoe UI'; }
QLabel { color:#f3f2ff; background:transparent; }
QLineEdit, QComboBox { background:#151727; border:1px solid #2c3150; border-radius:9px; padding:10px; color:#fff; }
QPushButton { background:#20233a; color:#f7f5ff; border:1px solid #35395e; border-radius:10px; padding:10px 15px; font-weight:600; }
QPushButton:hover { background:#34305d; border:1px solid #8b68ff; }
QPushButton#primary { background:#7048e8; border:1px solid #9c7aff; }
QPushButton#primary:hover { background:#8967f2; }
QListWidget { background:#101321; border:0; outline:0; padding:8px; }
QListWidget::item { padding:13px 12px; border-radius:8px; color:#b9bbd0; }
QListWidget::item:selected { background:#292348; color:white; }
QFrame#panel { background:#111426; border:1px solid #242943; border-radius:16px; }
QScrollArea { border:0; }
"""

def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS games(
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, console TEXT NOT NULL,
        path TEXT UNIQUE NOT NULL, artwork TEXT DEFAULT '', favorite INTEGER DEFAULT 0
    )""")
    existing = {row[1] for row in con.execute("PRAGMA table_info(games)")}
    if "franchise" not in existing:
        con.execute("ALTER TABLE games ADD COLUMN franchise TEXT DEFAULT ''")
    if "genre" not in existing:
        con.execute("ALTER TABLE games ADD COLUMN genre TEXT DEFAULT 'Non classé'")
    con.execute("""CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS owned_licenses(
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, publisher TEXT DEFAULT '',
        platform TEXT DEFAULT '', purchase_source TEXT DEFAULT '', reference TEXT DEFAULT '', notes TEXT DEFAULT ''
    )""")
    con.commit()
    return con

class AddGameDialog(QDialog):
    def __init__(self, parent=None, path=""):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un jeu")
        self.setMinimumWidth(460)
        self.path = path
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title = QLineEdit(Path(path).stem if path else "")
        self.console = QComboBox()
        all_consoles = [c for group in CONSOLES.values() for c in group]
        self.console.addItems(all_consoles)
        ext_console = EXTENSIONS.get(Path(path).suffix.lower(), "Autre") if path else "Autre"
        self.console.setCurrentText(ext_console)
        self.franchise = QLineEdit(self.guess_franchise(Path(path).stem) if path else "")
        self.franchise.setPlaceholderText("Ex. Pokémon, Mario, Final Fantasy…")
        self.genre = QComboBox()
        self.genre.addItems(["Non classé", "Action", "Aventure", "RPG", "JRPG", "Plateforme", "Combat", "Course", "Sport", "Stratégie", "Simulation", "Puzzle", "Horreur", "Arcade", "Autre"])
        self.art = QLineEdit()
        art_row = QHBoxLayout()
        art_row.addWidget(self.art)
        browse = QPushButton("Choisir…")
        browse.clicked.connect(self.pick_art)
        art_row.addWidget(browse)
        form.addRow("Nom du jeu", self.title)
        form.addRow("Console", self.console)
        form.addRow("Licence / collection", self.franchise)
        form.addRow("Genre", self.genre)
        form.addRow("Jaquette", art_row)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def guess_franchise(title):
        t = title.casefold()
        rules = [
            (("pokemon", "pokémon"), "Pokémon"), (("mario", "luigi", "yoshi", "wario"), "Mario"),
            (("zelda",), "The Legend of Zelda"), (("final fantasy",), "Final Fantasy"),
            (("sonic",), "Sonic"), (("kirby",), "Kirby"), (("metroid",), "Metroid"),
            (("dragon quest",), "Dragon Quest"), (("resident evil",), "Resident Evil"),
            (("street fighter",), "Street Fighter"), (("tekken",), "Tekken"),
            (("crash bandicoot",), "Crash Bandicoot"), (("spyro",), "Spyro"),
            (("halo",), "Halo"), (("forza",), "Forza"), (("persona",), "Persona")
        ]
        for needles, franchise in rules:
            if any(n in t for n in needles):
                return franchise
        return ""

    def pick_art(self):
        f, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if f: self.art.setText(f)

class GameCard(QFrame):
    def __init__(self, game, selected_cb, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.game = game
        self.setFixedSize(178, 254)
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(7)
        cover = QLabel()
        cover.setFixedSize(156, 178)
        cover.setAlignment(Qt.AlignCenter)
        if game[4] and Path(game[4]).exists():
            pix = QPixmap(game[4]).scaled(156,178,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation)
            cover.setPixmap(pix)
        else:
            cover.setText("GAMES\nVERSE")
            cover.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #30205c,stop:1 #132b55); border-radius:10px; color:#c9baff; font-size:20px; font-weight:900;")
        v.addWidget(cover)
        name = QLabel(game[1]); name.setWordWrap(True)
        name.setStyleSheet("font-weight:700; font-size:13px;")
        v.addWidget(name)
        sub = QLabel(game[2]); sub.setStyleSheet("color:#9298b7; font-size:11px;")
        v.addWidget(sub)
        self.mousePressEvent = lambda e: selected_cb(game)

class GAMESVERSE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GAMESVERSE — ONE APP. EVERY GENERATION.")
        self.resize(1380, 860)
        self.setMinimumSize(1100, 700)
        self.current_game = None
        self.emulator_paths = {}
        self._load_settings()
        root = QWidget(); self.setCentralWidget(root)
        outer = QHBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        sidebar = QFrame(); sidebar.setFixedWidth(235)
        sidebar.setStyleSheet("background:#0d0f1c; border-right:1px solid #20243b;")
        side = QVBoxLayout(sidebar); side.setContentsMargins(18,24,18,20); side.setSpacing(9)
        brand = QLabel("◉  GAMESVERSE")
        brand.setStyleSheet("font-size:21px; font-weight:900; letter-spacing:1px; color:#c6b4ff; padding:8px 3px 20px;")
        side.addWidget(brand)
        tagline = QLabel("ONE APP. EVERY GENERATION.")
        tagline.setStyleSheet("font-size:9px; letter-spacing:1.4px; color:#737b9e; padding:0 4px 20px;")
        side.addWidget(tagline)
        self.nav = QListWidget()
        self.nav.addItems(["Accueil", "Bibliothèque", "Collections", "Mes licences", "Store", "Consoles", "Téléchargements", "Favoris", "Paramètres"])
        self.nav.setCurrentRow(0)
        side.addWidget(self.nav,1)
        foot = QLabel("GAMESVERSE  •  OPEN SOURCE 0.5.0")
        foot.setStyleSheet("color:#666d8e; font-size:10px; padding:8px 3px;")
        side.addWidget(foot)
        outer.addWidget(sidebar)

        content = QWidget()
        self.content_layout = QVBoxLayout(content); self.content_layout.setContentsMargins(28,24,28,24); self.content_layout.setSpacing(18)
        top = QHBoxLayout()
        self.page_title = QLabel("Bienvenue dans votre univers")
        self.page_title.setStyleSheet("font-size:25px; font-weight:800;")
        top.addWidget(self.page_title); top.addStretch()
        self.search = QLineEdit(); self.search.setPlaceholderText("Rechercher un jeu…"); self.search.setFixedWidth(280)
        self.search.textChanged.connect(self.refresh_library)
        top.addWidget(self.search)
        self.content_layout.addLayout(top)
        self.pages = QStackedWidget()
        self.content_layout.addWidget(self.pages,1)
        outer.addWidget(content,1)

        self.home = self.build_home()
        self.library = self.build_library()
        self.collections = self.build_collections()
        self.licenses = self.build_licenses()
        self.store = self.build_store()
        self.consoles = self.build_consoles()
        self.downloads = self.simple_page("Téléchargements", "Les téléchargements de jeux et de modules apparaîtront ici.")
        self.favorites = self.build_favorites()
        self.settings = self.build_settings()
        for p in [self.home,self.library,self.collections,self.licenses,self.store,self.consoles,self.downloads,self.favorites,self.settings]:
            self.pages.addWidget(p)
        self.nav.currentRowChanged.connect(self.change_page)
        self.refresh_library()
        self.refresh_home()

    def _load_settings(self):
        con = db()
        self.emulator_paths = {k:v for k,v in con.execute("SELECT key,value FROM settings WHERE key LIKE 'emu:%'")}
        self.emulator_paths = {k[4:]:v for k,v in self.emulator_paths.items()}

    def save_emulator(self, console, path):
        con=db(); con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(f"emu:{console}",path)); con.commit(); con.close()
        self.emulator_paths[console]=path

    def change_page(self, index):
        titles=["Bienvenue dans votre univers","Ma bibliothèque","Collections","Mes licences","Store","Toutes les consoles","Téléchargements","Mes favoris","Paramètres"]
        self.pages.setCurrentIndex(max(0,index)); self.page_title.setText(titles[max(0,index)])

    def panel(self):
        f=QFrame(); f.setObjectName("panel"); return f

    def build_home(self):
        page=QWidget(); v=QVBoxLayout(page); v.setSpacing(18)
        hero=self.panel(); hero.setMinimumHeight(285)
        h=QHBoxLayout(hero); h.setContentsMargins(30,28,30,28)
        left=QVBoxLayout()
        eyebrow=QLabel("VOTRE UNIVERS DE JEUX, RÉUNI AU MÊME ENDROIT")
        eyebrow.setStyleSheet("color:#a995ff; letter-spacing:2px; font-size:10px; font-weight:800;")
        left.addWidget(eyebrow)
        title=QLabel("ONE APP.\nEVERY GENERATION.")
        title.setStyleSheet("font-size:38px; font-weight:900; line-height:1.1;")
        left.addWidget(title)
        desc=QLabel("Retrouvez vos jeux, vos consoles et vos aventures dans une seule bibliothèque.")
        desc.setWordWrap(True); desc.setStyleSheet("color:#a7abc5; font-size:14px;")
        left.addWidget(desc)
        row=QHBoxLayout()
        b=QPushButton("＋  Ajouter des jeux"); b.setObjectName("primary"); b.clicked.connect(self.add_games)
        row.addWidget(b)
        b2=QPushButton("Explorer la bibliothèque"); b2.clicked.connect(lambda:self.nav.setCurrentRow(1)); row.addWidget(b2)
        left.addLayout(row); left.addStretch()
        h.addLayout(left,2)
        portal=QLabel("✦")
        portal.setAlignment(Qt.AlignCenter)
        portal.setStyleSheet("font-size:150px; color:#8c6cff; background:qradialgradient(cx:0.5,cy:0.5,radius:0.7,stop:0 #38276b,stop:0.35 #191b39,stop:1 #111426); border-radius:130px;")
        portal.setFixedSize(250,250)
        h.addWidget(portal,1,Qt.AlignCenter)
        v.addWidget(hero)
        label=QLabel("RÉCEMMENT AJOUTÉS"); label.setStyleSheet("font-size:12px; letter-spacing:2px; color:#9a9fbe; font-weight:800;")
        v.addWidget(label)
        self.home_recent=QHBoxLayout(); v.addLayout(self.home_recent)
        v.addStretch()
        return page

    def build_library(self):
        page=QWidget(); v=QVBoxLayout(page)
        row=QHBoxLayout()
        self.filter_console=QComboBox(); self.filter_console.addItem("Toutes les consoles")
        self.filter_console.addItems([c for g in CONSOLES.values() for c in g])
        self.filter_console.currentTextChanged.connect(self.refresh_library)
        row.addWidget(self.filter_console); row.addStretch()
        add=QPushButton("＋ Ajouter un jeu"); add.setObjectName("primary"); add.clicked.connect(self.add_games); row.addWidget(add)
        v.addLayout(row)
        self.library_scroll=QScrollArea(); self.library_scroll.setWidgetResizable(True)
        self.library_inner=QWidget(); self.library_grid=QGridLayout(self.library_inner); self.library_grid.setAlignment(Qt.AlignTop|Qt.AlignLeft); self.library_grid.setSpacing(15)
        self.library_scroll.setWidget(self.library_inner); v.addWidget(self.library_scroll,1)
        self.hero_detail=self.panel(); self.hero_detail.setMinimumHeight(155)
        hd=QHBoxLayout(self.hero_detail); hd.setContentsMargins(18,14,18,14)
        self.detail_art=QLabel("Sélectionnez un jeu"); self.detail_art.setFixedSize(92,120); self.detail_art.setAlignment(Qt.AlignCenter)
        self.detail_art.setStyleSheet("background:#1c2040; border-radius:8px; color:#a995ff;")
        hd.addWidget(self.detail_art)
        info=QVBoxLayout(); self.detail_title=QLabel("Votre prochaine aventure vous attend"); self.detail_title.setStyleSheet("font-size:20px; font-weight:800;")
        self.detail_sub=QLabel("Choisissez un jeu pour afficher ses détails."); self.detail_sub.setStyleSheet("color:#a2a7c0;")
        info.addWidget(self.detail_title); info.addWidget(self.detail_sub); info.addStretch()
        actions=QHBoxLayout()
        self.play_btn=QPushButton("▶  Jouer"); self.play_btn.setObjectName("primary"); self.play_btn.clicked.connect(self.launch_current); self.play_btn.setEnabled(False)
        self.fav_btn=QPushButton("☆ Favori"); self.fav_btn.clicked.connect(self.toggle_favorite); self.fav_btn.setEnabled(False)
        self.art_btn=QPushButton("Changer la jaquette"); self.art_btn.clicked.connect(self.change_art); self.art_btn.setEnabled(False)
        self.del_btn=QPushButton("Retirer"); self.del_btn.clicked.connect(self.remove_current); self.del_btn.setEnabled(False)
        for x in [self.play_btn,self.fav_btn,self.art_btn,self.del_btn]: actions.addWidget(x)
        info.addLayout(actions); hd.addLayout(info,1)
        v.addWidget(self.hero_detail)
        return page

    def build_collections(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        note = QLabel("Catalogue de licences GAMESVERSE : retrouvez les jeux par saga, console, année et genre. Les fiches catalogue ne contiennent pas les fichiers des jeux. Enregistrez vos achats dans « Mes licences ».")
        note.setWordWrap(True)
        note.setStyleSheet("color:#a4a9c2; padding:5px;")
        layout.addWidget(note)
        filters = QHBoxLayout()
        self.catalog_search = QLineEdit()
        self.catalog_search.setPlaceholderText("Rechercher Pokémon, Mario, Final Fantasy…")
        self.catalog_search.textChanged.connect(self.refresh_catalogue)
        filters.addWidget(self.catalog_search, 2)
        self.catalog_franchise = QComboBox()
        self.catalogue = json.loads(resource_path("catalogue.json").read_text(encoding="utf-8"))
        self.catalog_franchise.addItems(["Toutes les licences"] + sorted({g["franchise"] for g in self.catalogue}, key=str.casefold))
        self.catalog_franchise.currentTextChanged.connect(self.refresh_catalogue)
        filters.addWidget(self.catalog_franchise, 1)
        self.catalog_console = QComboBox()
        self.catalog_console.addItem("Toutes les consoles")
        self.catalog_console.addItems([c for group in CONSOLES.values() for c in group])
        self.catalog_console.currentTextChanged.connect(self.refresh_catalogue)
        filters.addWidget(self.catalog_console, 1)
        layout.addLayout(filters)
        self.catalog_scroll = QScrollArea()
        self.catalog_scroll.setWidgetResizable(True)
        self.catalog_inner = QWidget()
        self.catalog_grid = QGridLayout(self.catalog_inner)
        self.catalog_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.catalog_grid.setSpacing(12)
        self.catalog_scroll.setWidget(self.catalog_inner)
        layout.addWidget(self.catalog_scroll, 1)
        self.refresh_catalogue()
        return page

    def refresh_catalogue(self, *_):
        if not hasattr(self, "catalog_grid"):
            return
        while self.catalog_grid.count():
            item = self.catalog_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        term = self.catalog_search.text().casefold().strip()
        franchise = self.catalog_franchise.currentText()
        console = self.catalog_console.currentText()
        rows = [g for g in self.catalogue
                if (franchise == "Toutes les licences" or g["franchise"] == franchise)
                and (console == "Toutes les consoles" or g["console"] == console)
                and (not term or term in " ".join(str(v) for v in g.values()).casefold())]
        groups = {}
        for game in rows:
            groups.setdefault(game["franchise"], []).append(game)
        pos = 0
        for series, games in groups.items():
            header = QLabel(f"{series.upper()}  •  {len(games)} jeux catalogués")
            header.setStyleSheet("font-size:17px; font-weight:900; color:#bba7ff; padding:10px 3px;")
            self.catalog_grid.addWidget(header, pos, 0, 1, 3)
            pos += 1
            for game in games:
                card = self.panel()
                card.setMinimumHeight(112)
                box = QVBoxLayout(card)
                title = QLabel(game["title"])
                title.setStyleSheet("font-size:13px; font-weight:800;")
                meta = QLabel(f'{game["console"]}  •  {game["year"]}  •  {game["genre"]}')
                meta.setStyleSheet("font-size:11px; color:#a995ff;")
                status = QLabel("Catalogue uniquement — importer un fichier de jeu obtenu légalement pour jouer")
                status.setStyleSheet("font-size:10px; color:#858ba9;")
                box.addWidget(title)
                box.addWidget(meta)
                box.addWidget(status)
                self.catalog_grid.addWidget(card, pos // 3, pos % 3)
                pos += 1
        if not rows:
            empty = QLabel("Aucun jeu trouvé dans cette sélection.")
            empty.setStyleSheet("color:#8f95b3; padding:24px;")
            self.catalog_grid.addWidget(empty, 0, 0)

    def build_licenses(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Centralisez les jeux que vous possédez et les plateformes où vous les avez obtenus. Cette liste est un inventaire personnel : elle ne vérifie pas les achats et ne crée pas de droit de téléchargement de ROM.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color:#a4a9c2; padding:5px;")
        layout.addWidget(intro)
        form_box = self.panel()
        form = QGridLayout(form_box)
        self.license_title = QLineEdit(); self.license_title.setPlaceholderText("Ex. Pokémon Émeraude")
        self.license_publisher = QLineEdit(); self.license_publisher.setPlaceholderText("Ex. Nintendo / The Pokémon Company")
        self.license_platform = QComboBox(); self.license_platform.addItems([c for group in CONSOLES.values() for c in group])
        self.license_source = QComboBox(); self.license_source.addItems(["Cartouche / disque physique", "Nintendo eShop", "Steam", "GOG", "Epic Games Store", "Xbox", "PlayStation Store", "Autre"])
        self.license_ref = QLineEdit(); self.license_ref.setPlaceholderText("Référence de commande (facultatif, sans mot de passe)")
        add = QPushButton("Ajouter à mes licences"); add.setObjectName("primary"); add.clicked.connect(self.add_license)
        form.addWidget(QLabel("Jeu"),0,0); form.addWidget(self.license_title,0,1)
        form.addWidget(QLabel("Éditeur"),0,2); form.addWidget(self.license_publisher,0,3)
        form.addWidget(QLabel("Console"),1,0); form.addWidget(self.license_platform,1,1)
        form.addWidget(QLabel("Provenance"),1,2); form.addWidget(self.license_source,1,3)
        form.addWidget(QLabel("Référence facultative"),2,0); form.addWidget(self.license_ref,2,1,1,2); form.addWidget(add,2,3)
        layout.addWidget(form_box)
        self.license_scroll = QScrollArea(); self.license_scroll.setWidgetResizable(True)
        self.license_inner = QWidget(); self.license_grid = QGridLayout(self.license_inner); self.license_grid.setAlignment(Qt.AlignTop); self.license_grid.setSpacing(10)
        self.license_scroll.setWidget(self.license_inner); layout.addWidget(self.license_scroll,1)
        self.refresh_licenses()
        return page

    def add_license(self):
        title = self.license_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Licence", "Saisissez le nom du jeu."); return
        con = db()
        con.execute("INSERT INTO owned_licenses(title,publisher,platform,purchase_source,reference) VALUES(?,?,?,?,?)",
                    (title, self.license_publisher.text().strip(), self.license_platform.currentText(), self.license_source.currentText(), self.license_ref.text().strip()))
        con.commit(); con.close()
        self.license_title.clear(); self.license_publisher.clear(); self.license_ref.clear()
        self.refresh_licenses()

    def refresh_licenses(self):
        if not hasattr(self, "license_grid"): return
        while self.license_grid.count():
            item = self.license_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        con = db(); rows = con.execute("SELECT id,title,publisher,platform,purchase_source,reference FROM owned_licenses ORDER BY title COLLATE NOCASE").fetchall(); con.close()
        if not rows:
            empty = QLabel("Aucune licence enregistrée. Ajoutez les jeux que vous possédez pour garder votre collection organisée.")
            empty.setStyleSheet("color:#858ba9; padding:18px;"); self.license_grid.addWidget(empty,0,0); return
        for i, row in enumerate(rows):
            card = self.panel(); box = QHBoxLayout(card)
            info = QVBoxLayout(); title = QLabel(row[1]); title.setStyleSheet("font-size:15px;font-weight:800;")
            meta = QLabel(" • ".join(x for x in [row[2],row[3],row[4]] if x)); meta.setStyleSheet("color:#a995ff;font-size:11px;")
            ref = QLabel(("Réf. : " + row[5]) if row[5] else "Aucune référence enregistrée"); ref.setStyleSheet("color:#858ba9;font-size:10px;")
            info.addWidget(title); info.addWidget(meta); info.addWidget(ref); box.addLayout(info,1)
            remove = QPushButton("Retirer")
            remove.clicked.connect(lambda checked=False, rid=row[0]: self.remove_license(rid))
            box.addWidget(remove); self.license_grid.addWidget(card,i,0)

    def remove_license(self, license_id):
        con=db(); con.execute("DELETE FROM owned_licenses WHERE id=?",(license_id,)); con.commit(); con.close(); self.refresh_licenses()

    def build_store(self):
        page = QWidget()
        v = QVBoxLayout(page)
        intro = QLabel("Une sélection de jeux gratuits, homebrew et open source provenant de leurs créateurs ou sites officiels. GAMESVERSE n'héberge pas de ROM commerciales.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color:#a4a9c2; padding:5px;")
        v.addWidget(intro)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        grid = QGridLayout(inner)
        grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid.setSpacing(14)
        items = [
            ("SuperTux", "PC • Plateforme", "Jeu de plateforme open source gratuit pour Windows, macOS et Linux.", "Téléchargement officiel", "https://www.supertux.org/download"),
            ("OpenTTD", "PC • Gestion / stratégie", "Jeu de gestion de transport open source. Téléchargement depuis le site du projet.", "Téléchargement officiel", "https://www.openttd.org/downloads"),
            ("Homebrew NES", "NES • Jeux indépendants", "Découvrir des créations originales et jeux homebrew gratuits pour NES. Vérifier la licence et les conditions de chaque créateur.", "Explorer le catalogue", "https://itch.io/games/free/tag-homebrew/tag-nes"),
            ("Homebrew Game Boy", "Game Boy • Jeux indépendants", "Découvrir des jeux indépendants pour Game Boy. Vérifier les conditions de chaque jeu.", "Explorer le catalogue", "https://itch.io/games/free/tag-homebrew/tag-gameboy"),
            ("Homebrew rétro", "Multi-systèmes • Jeux indépendants", "Catalogue de créations homebrew gratuites pour différentes machines rétro. Les licences dépendent de chaque auteur.", "Explorer le catalogue", "https://itch.io/games/free/tag-homebrew"),
        ]
        for i, (name, category, description, button_text, url) in enumerate(items):
            card = self.panel()
            card.setMinimumHeight(190)
            box = QVBoxLayout(card)
            box.setContentsMargins(18,16,18,16)
            title = QLabel(name)
            title.setStyleSheet("font-size:18px; font-weight:900; color:#f3f2ff;")
            sub = QLabel(category)
            sub.setStyleSheet("font-size:11px; color:#a995ff; font-weight:700;")
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color:#a2a7c0; font-size:12px;")
            button = QPushButton(button_text)
            button.setObjectName("primary")
            button.clicked.connect(lambda checked=False, target=url: QDesktopServices.openUrl(QUrl(target)))
            box.addWidget(title)
            box.addWidget(sub)
            box.addWidget(desc, 1)
            box.addWidget(button)
            grid.addWidget(card, i // 2, i % 2)
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)
        return page

    def build_consoles(self):
        page=QWidget(); v=QVBoxLayout(page)
        intro=QLabel("Catalogue élargi des consoles et systèmes historiques. Leur présence ici ne signifie pas que l’émulation est déjà disponible : chaque système devra être validé, avec un statut de compatibilité et un émulateur adapté.")
        intro.setWordWrap(True); intro.setStyleSheet("color:#a4a9c2; padding:5px;")
        v.addWidget(intro)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); inner=QWidget(); grid=QGridLayout(inner); grid.setAlignment(Qt.AlignTop)
        row=0
        for maker, systems in CONSOLES.items():
            box=self.panel(); lay=QVBoxLayout(box)
            name=QLabel(maker.upper()); name.setStyleSheet("font-weight:900; color:#b7a5ff; letter-spacing:2px;")
            lay.addWidget(name)
            for system in systems:
                line=QHBoxLayout(); lab=QLabel(system); lab.setStyleSheet("font-size:13px;")
                status=QLabel("Catalogue • compatibilité à valider"); status.setStyleSheet("color:#858ba9; font-size:11px;")
                line.addWidget(lab); line.addStretch(); line.addWidget(status); lay.addLayout(line)
            grid.addWidget(box,row//2,row%2); row+=1
        scroll.setWidget(inner); v.addWidget(scroll,1)
        return page

    def simple_page(self, title, text):
        p=QWidget(); v=QVBoxLayout(p); box=self.panel(); b=QVBoxLayout(box)
        t=QLabel(title); t.setStyleSheet("font-size:24px; font-weight:800;")
        d=QLabel(text); d.setWordWrap(True); d.setStyleSheet("color:#a2a7c0;")
        b.addWidget(t); b.addWidget(d); b.addStretch(); v.addWidget(box); v.addStretch(); return p

    def build_favorites(self):
        return self.simple_page("Vos favoris", "Les jeux marqués comme favoris seront affichés ici. Retrouvez-les aussi dans votre bibliothèque.")

    def build_settings(self):
        p=QWidget(); v=QVBoxLayout(p); box=self.panel(); form=QFormLayout(box)
        note=QLabel("Associez un exécutable d'émulateur à une console. Les fichiers de jeux doivent provenir de sources que vous êtes autorisé à utiliser.")
        note.setWordWrap(True); note.setStyleSheet("color:#a3a8c1;")
        v.addWidget(note)
        self.emu_select=QComboBox(); self.emu_select.addItems([c for g in CONSOLES.values() for c in g])
        self.emu_path=QLineEdit(); self.emu_path.setReadOnly(True)
        browse=QPushButton("Parcourir…"); browse.clicked.connect(self.choose_emulator)
        row=QHBoxLayout(); row.addWidget(self.emu_path,1); row.addWidget(browse)
        form.addRow("Console",self.emu_select); form.addRow("Émulateur",row)
        save=QPushButton("Enregistrer l'association"); save.setObjectName("primary"); save.clicked.connect(self.save_selected_emulator)
        form.addRow("",save)
        v.addWidget(box); v.addStretch()
        self.emu_select.currentTextChanged.connect(self.update_emulator_field)
        return p

    def choose_emulator(self):
        f,_=QFileDialog.getOpenFileName(self,"Choisir l'émulateur","","Applications (*.exe);;Tous les fichiers (*)")
        if f: self.emu_path.setText(f)

    def update_emulator_field(self, console):
        self.emu_path.setText(self.emulator_paths.get(console,""))

    def save_selected_emulator(self):
        c=self.emu_select.currentText(); p=self.emu_path.text()
        if not p or not Path(p).exists():
            QMessageBox.warning(self,"Émulateur","Choisissez un exécutable existant."); return
        self.save_emulator(c,p); QMessageBox.information(self,"GAMESVERSE",f"Association enregistrée pour {c}.")

    def add_games(self):
        files,_=QFileDialog.getOpenFileNames(self,"Ajouter des jeux","","Fichiers de jeux (*.*)")
        if not files: return
        con=db()
        for path in files:
            dlg=AddGameDialog(self,path)
            if dlg.exec():
                try:
                    art=dlg.art.text().strip()
                    if art and Path(art).exists():
                        dest=ART_DIR/(str(abs(hash(path)))+Path(art).suffix.lower())
                        dest.write_bytes(Path(art).read_bytes()); art=str(dest)
                    con.execute("INSERT OR IGNORE INTO games(title,console,path,artwork,franchise,genre) VALUES(?,?,?,?,?,?)",
                                (dlg.title.text().strip() or Path(path).stem, dlg.console.currentText(), path, art,
                                 dlg.franchise.text().strip(), dlg.genre.currentText()))
                except Exception as e:
                    QMessageBox.warning(self,"Ajout impossible",str(e))
        con.commit(); con.close(); self.refresh_library(); self.refresh_home()

    def refresh_library(self, *_):
        if not hasattr(self,"library_grid"): return
        while self.library_grid.count():
            item=self.library_grid.takeAt(0); w=item.widget()
            if w: w.deleteLater()
        con=db()
        q="SELECT id,title,console,path,artwork,favorite FROM games WHERE 1=1"
        args=[]
        term=self.search.text().strip() if hasattr(self,"search") else ""
        if term: q+=" AND title LIKE ?"; args.append(f"%{term}%")
        filt=self.filter_console.currentText() if hasattr(self,"filter_console") else "Toutes les consoles"
        if filt!="Toutes les consoles": q+=" AND console=?"; args.append(filt)
        q+=" ORDER BY title COLLATE NOCASE"
        games=con.execute(q,args).fetchall(); con.close()
        for i,g in enumerate(games):
            card=GameCard(g,self.select_game)
            self.library_grid.addWidget(card,i//5,i%5)
        if not games:
            empty=QLabel("Aucun jeu pour le moment. Cliquez sur « Ajouter un jeu » pour importer vos fichiers.")
            empty.setStyleSheet("color:#8f95b3; padding:24px;"); self.library_grid.addWidget(empty,0,0)

    def refresh_home(self):
        if not hasattr(self,"home_recent"): return
        while self.home_recent.count():
            item=self.home_recent.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        con=db(); games=con.execute("SELECT id,title,console,path,artwork,favorite FROM games ORDER BY id DESC LIMIT 5").fetchall(); con.close()
        if not games:
            lab=QLabel("Votre bibliothèque est encore vide — ajoutez vos premiers jeux.")
            lab.setStyleSheet("color:#858ba9; padding:12px;"); self.home_recent.addWidget(lab); return
        for g in games:
            card=GameCard(g,self.go_library_select); self.home_recent.addWidget(card)

    def go_library_select(self, game):
        self.nav.setCurrentRow(1); self.select_game(game)

    def select_game(self, game):
        self.current_game=game
        self.detail_title.setText(game[1]); self.detail_sub.setText(f"{game[2]}  •  {Path(game[3]).name}")
        if game[4] and Path(game[4]).exists():
            pix=QPixmap(game[4]).scaled(92,120,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation); self.detail_art.setPixmap(pix)
            art_url = Path(game[4]).as_posix()
            self.hero_detail.setStyleSheet(f"QFrame#panel {{ border-image: url('{art_url}') 0 0 0 0 stretch stretch; border-radius:16px; }}")
            self.detail_title.setStyleSheet("font-size:20px; font-weight:900; background:rgba(8,10,20,190); padding:5px; border-radius:5px;")
            self.detail_sub.setStyleSheet("color:#ffffff; background:rgba(8,10,20,175); padding:4px; border-radius:5px;")
        else:
            self.detail_art.setPixmap(QPixmap()); self.detail_art.setText("GAMES\\nVERSE")
            self.hero_detail.setStyleSheet("QFrame#panel { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #21183d,stop:1 #111426); border:1px solid #242943; border-radius:16px; }")
            self.detail_title.setStyleSheet("font-size:20px; font-weight:800;")
            self.detail_sub.setStyleSheet("color:#a2a7c0;")
        for b in [self.play_btn,self.fav_btn,self.art_btn,self.del_btn]: b.setEnabled(True)
        self.fav_btn.setText("★ Favori" if game[5] else "☆ Favori")

    def launch_current(self):
        if not self.current_game: return
        game=self.current_game; emulator=self.emulator_paths.get(game[2])
        if not emulator or not Path(emulator).exists():
            QMessageBox.information(self,"Émulateur manquant",f"Aucun émulateur n'est associé à {game[2]}.\nConfigurez son exécutable dans Paramètres."); return
        try:
            subprocess.Popen([emulator,game[3]],cwd=str(Path(emulator).parent))
        except Exception as e: QMessageBox.critical(self,"Lancement impossible",str(e))

    def toggle_favorite(self):
        if not self.current_game: return
        con=db(); con.execute("UPDATE games SET favorite=1-favorite WHERE id=?",(self.current_game[0],)); con.commit(); con.close()
        self.refresh_library(); self.refresh_home()
        con=db(); self.current_game=con.execute("SELECT id,title,console,path,artwork,favorite FROM games WHERE id=?",(self.current_game[0],)).fetchone(); con.close()
        self.select_game(self.current_game)

    def change_art(self):
        if not self.current_game: return
        f,_=QFileDialog.getOpenFileName(self,"Choisir la jaquette","","Images (*.png *.jpg *.jpeg *.webp)")
        if not f: return
        dest=ART_DIR/(str(self.current_game[0])+Path(f).suffix.lower()); dest.write_bytes(Path(f).read_bytes())
        con=db(); con.execute("UPDATE games SET artwork=? WHERE id=?",(str(dest),self.current_game[0])); con.commit(); con.close()
        self.current_game=(*self.current_game[:4],str(dest),self.current_game[5]); self.select_game(self.current_game); self.refresh_library(); self.refresh_home()

    def remove_current(self):
        if not self.current_game: return
        answer=QMessageBox.question(self,"Retirer le jeu","Retirer ce jeu de GAMESVERSE ? Le fichier original ne sera pas supprimé.")
        if answer!=QMessageBox.Yes: return
        con=db(); con.execute("DELETE FROM games WHERE id=?",(self.current_game[0],)); con.commit(); con.close()
        self.current_game=None; self.refresh_library(); self.refresh_home()
        self.detail_title.setText("Votre prochaine aventure vous attend"); self.detail_sub.setText("Choisissez un jeu pour afficher ses détails.")
        self.detail_art.setPixmap(QPixmap()); self.detail_art.setText("Sélectionnez un jeu")
        for b in [self.play_btn,self.fav_btn,self.art_btn,self.del_btn]: b.setEnabled(False)

def main():
    app=QApplication(sys.argv); app.setStyleSheet(STYLE)
    app.setWindowIcon(QIcon(str(resource_path(Path("assets") / "gamesverse-logo.svg"))))
    window=GAMESVERSE(); window.show()
    sys.exit(app.exec())

if __name__=="__main__": main()
