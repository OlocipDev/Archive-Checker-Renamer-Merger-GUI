import sys
import os
import re
import zipfile
import patoolib

# --- GESTION DES CHEMINS TEMPORAIRES SI COMPILÉ EN .EXE ---
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    os.environ["PATH"] += os.pathsep + BUNDLE_DIR
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- IMPORTATION SÉCURISÉE DE SEND2TRASH ---
try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QMessageBox, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

APP_VERSION = "2.4"

IMAGE_EXTS = ('.jpg', '.jpeg', '.jpe', '.jfif', '.png', '.webp', '.bmp', '.gif', '.tif', '.tiff', '.avif')
ARCHIVE_EXTS = ('.zip', '.cbz', '.rar', '.cbr', '.7z', '.tar', '.gz')

# --- Dictionnaire de traductions FR / EN ---
TRANSLATIONS = {
    "FR": {
        "title": f"Vérificateur, Renommeur & Fusionneur d'Archives v{APP_VERSION}",
        "btn_select": "📁 Sélectionner",
        "btn_refresh": "🔄 Actualiser",
        "btn_stop": "⏹️ Arrêter",
        "btn_toggle_all_check": "☑️ Tout cocher",
        "btn_toggle_all_uncheck": "🔳 Tout décocher",
        "btn_rename": "🏷️ Formater en 0001",
        "btn_prefix": "🏷️ Appliquer préfixe",
        "btn_create_cbz": "📦 Créer CBZ",
        "btn_merge": "⚡ Fusionner",
        "btn_delete": "🗑️ Corbeille",
        "lbl_dest": "📂 Destination (Fusion) :",
        "txt_dest_placeholder": "Par défaut : même dossier que l'importation...",
        "btn_browse_dest": "Parcourir...",
        "lbl_prefix": "🏷️ Préfixe (nom des archives + fichiers internes) :",
        "txt_prefix_placeholder": "Préfixe détecté automatiquement, modifiable...",
        "lbl_status_ready": "Prêt",
        "lbl_filter": "🔍 Filtrer :",
        "txt_filter_placeholder": "Filtrer la liste...",
        "col_select": "Sélection",
        "col_parent": "Dossier parent",
        "col_archive": "Nom de l'Archive",
        "col_format": "Format 0000",
        "col_status": "Statut",
        "col_files": "Fichiers",
        "col_range": "Séquence",
        "col_bin": "Fichiers .BIN",
        "lbl_details_title": "Détails & Informations :",
        "lbl_source_folder": "📂 Dossier source : ",
        "lbl_no_folder": "Aucun dossier sélectionné (Glissez-déposez un dossier ici)",
        "yes": "OUI ✅",
        "no": "NON ❌",
        "msg_no_selection": "Veuillez cocher au moins une archive.",
        "msg_merge_min": "Veuillez cocher au moins deux archives à fusionner.",
        "msg_no_folder_to_refresh": "Veuillez d'abord sélectionner un dossier à analyser.",
        "msg_invalid_folder": "Veuillez glisser-déposer un **dossier**.",
        "msg_prefix_empty": "Veuillez saisir un préfixe dans la case dédiée.",
        "msg_no_image_selection": "Veuillez cocher au moins une image à convertir en CBZ.",
        "confirm_rename_title": "Confirmer le renommage",
        "confirm_rename_body": "Voulez-vous réécrire la numérotation en 4 chiffres pour les {count} archive(s) sélectionnée(s) ?",
        "confirm_prefix_title": "Confirmer l'application du préfixe",
        "confirm_prefix_body": "Appliquer le préfixe « {prefix} » au nom des archives ET à leurs fichiers internes pour les {count} archive(s) listée(s) ?",
        "confirm_create_title": "Créer les archives CBZ",
        "confirm_create_body": "Créer {count} archive(s) .cbz à partir des images cochées (regroupées par dossier) ?\nPréfixe utilisé : « {prefix} »\n\nLe nom du CBZ sera le préfixe (le n° du dossier sera ajouté en cas de doublon).",
        "confirm_delete_title": "⚠️ Déplacer vers la corbeille",
        "confirm_delete_body": "Voulez-vous envoyer {count} fichier(s) sélectionné(s) vers la corbeille ?",
        "guardrail_title": "Garde-fou : Format non respecté",
        "guardrail_body": "Impossible de fusionner !\n\n{count} archive(s) sélectionnée(s) ne respectent pas le format à 4 chiffres (Format 0000) :\n{list}\n\nVeuillez d'abord utiliser le bouton '🏷️ Formater en 0001' sur votre sélection.",
        "status_processing": "Traitement [{current}/{total}] : {file}",
        "status_done": "Analyse terminée !",
        "status_rename_done": "Renommage terminé !",
        "status_prefix_done": "Préfixe appliqué !",
        "status_create_done": "Création des CBZ terminée !",
        "status_merge_done": "Fusion terminée !",
        "status_delete_done": "Envoi à la corbeille effectué !",
        "status_stopped": "Arrêt en cours...",
        "status_image": "IMAGE",
        "status_outlier": "HORS SÉQUENCE",
        "about_title": f"À propos & Guide - v{APP_VERSION}",
        "about_btn": f"ℹ️ v{APP_VERSION}",
        "about_content": (
            "📖 GUIDE D'UTILISATION (TUTORIEL PERMANENT)\n"
            "==================================================\n\n"
            "1. SÉLECTION ET ANALYSE :\n"
            " • Cliquez sur '📁 Sélectionner' ou faites un Glisser-Déposer d'un dossier d'archives.\n"
            " • L'application analyse récursivement les sous-dossiers (.cbz, .zip, .rar, .7z).\n"
            " • Le scanner vérifie l'absence de fichiers indésirables (.bin) et affiche leur nombre exact.\n\n"
            "2. FORMATAGE EN 0001 (SÉLECTION) :\n"
            " • Cochez les archives à corriger, puis cliquez sur '🏷️ Formater en 0001'.\n"
            " • L'application renomme les fichiers internes et le nom d'archive sur 4 chiffres (ex: 1 -> 0001, 3.5 -> 0003.5).\n\n"
            "3. FUSION SÉCURISÉE EN CBZ :\n"
            " • Cochez au moins 2 archives formatées en 'Format 0000' et cliquez sur '⚡ Fusionner'.\n"
            " • Les images sont extraites, réordonnées séquentiellement et regroupées dans une archive CBZ unique.\n"
            " • Le nom du CBZ est généré automatiquement : 'DOSSIER - XXXX to XXXX.cbz'.\n\n"
            "4. CRÉER DES CBZ À PARTIR D'IMAGES (🖼️) :\n"
            " • Chaque fichier image libre (.jpg, .png...) apparaît sur sa propre ligne, avec sa case à cocher.\n"
            " • Les images dont le nom ne suit pas la séquence du dossier (ex: logo) sont surlignées en rouge (⚠️ HORS SÉQUENCE).\n"
            " • Cochez les images à inclure, puis cliquez sur '📦 Créer CBZ'. Les images cochées sont regroupées par dossier.\n"
            " • Chaque dossier devient un .cbz créé à côté du dossier (dans son dossier parent).\n"
            " • Les images internes sont renommées en préfixe + numérotation 0001, 0002... dans l'ordre naturel.\n"
            " • Préfixe par défaut = nom du dossier déposé/ouvert (modifiable : n° de chapitre/tome).\n\n"
            "5. PRÉFIXE AUTOMATIQUE (NOM + FICHIERS INTERNES) :\n"
            " • La case 'Préfixe' reprend par défaut le nom du dossier déposé / ouvert par l'utilisateur.\n"
            " • La case est modifiable : saisissez le nom de votre choix puis cliquez sur '🏷️ Appliquer préfixe'.\n"
            " • Le préfixe s'applique à TOUTES les archives listées, à leur nom ET à leurs fichiers internes.\n\n"
            "6. OUTILS D'INTERFACE ET GESTION :\n"
            " • 🔄 Actualiser : Rescanne instantanément le dossier source pour prendre en compte les ajouts/modifications.\n"
            " • 🗑️ Corbeille : Envoie les archives cochées directement dans la Corbeille de votre OS.\n"
            " • Tri Dynamique : Cliquez sur les en-têtes de colonnes du tableau pour trier les données.\n"
            " • Shift + Clic : Cochez une case puis faites Shift+Clic sur une autre pour sélectionner la plage entière.\n\n"
            "--------------------------------------------------\n"
            "📌 NOTE DE VERSION v2.4 :\n"
            " - NOUVEAU : les fichiers images libres (.jpg, .png...) sont listés ligne par ligne avec une case à cocher.\n"
            " - NOUVEAU : bouton '📦 Créer CBZ' -> chaque dossier d'images cochées devient un .cbz (images internes renumérotées préfixe + 0001, 0002...).\n"
            " - NOUVEAU : détection des fichiers hors séquence (ex: logo) -> surlignés en rouge avec '⚠️ HORS SÉQUENCE'.\n"
            " - NOUVEAU : case Préfixe -> reprend le nom du dossier déposé/ouvert, modifiable, appliqué aux noms d'archives ET aux fichiers internes.\n"
            " - Sélection par plage des cases à cocher (Shift + Clic).\n"
            " - Tri naturel (1, 2... 10 au lieu de 1, 10, 2) et filtrage en temps réel.\n"
            " - Envoi sécurisé des fichiers vers la corbeille de l'OS.\n"
        )
    },
    "EN": {
        "title": f"Archive Checker, Renamer & Merger v{APP_VERSION}",
        "btn_select": "📁 Select",
        "btn_refresh": "🔄 Refresh",
        "btn_stop": "⏹️ Stop",
        "btn_toggle_all_check": "☑️ Check All",
        "btn_toggle_all_uncheck": "🔳 Uncheck All",
        "btn_rename": "🏷️ Format 0001",
        "btn_prefix": "🏷️ Apply Prefix",
        "btn_create_cbz": "📦 Create CBZ",
        "btn_merge": "⚡ Merge",
        "btn_delete": "🗑️ Trash",
        "lbl_dest": "📂 Destination (Merge):",
        "txt_dest_placeholder": "Default: same folder as imported...",
        "btn_browse_dest": "Browse...",
        "lbl_prefix": "🏷️ Prefix (archive names + internal files):",
        "txt_prefix_placeholder": "Prefix auto-detected, editable...",
        "lbl_status_ready": "Ready",
        "lbl_filter": "🔍 Filter:",
        "txt_filter_placeholder": "Filter list...",
        "col_select": "Selection",
        "col_parent": "Parent Folder",
        "col_archive": "Archive Name",
        "col_format": "0000 Format",
        "col_status": "Status",
        "col_files": "Files",
        "col_range": "Sequence",
        "col_bin": ".BIN Files",
        "lbl_details_title": "Details & Information:",
        "lbl_source_folder": "📂 Source Folder: ",
        "lbl_no_folder": "No folder selected (Drag and drop a folder here)",
        "yes": "YES ✅",
        "no": "NO ❌",
        "msg_no_selection": "Please check at least one archive.",
        "msg_merge_min": "Please check at least two archives to merge.",
        "msg_no_folder_to_refresh": "Please select a folder to analyze first.",
        "msg_invalid_folder": "Please drag and drop a **folder**.",
        "msg_prefix_empty": "Please type a prefix in the dedicated box.",
        "msg_no_image_selection": "Please check at least one image to convert to CBZ.",
        "confirm_rename_title": "Confirm Renaming",
        "confirm_rename_body": "Do you want to rewrite 4-digit numbering for the {count} selected archive(s)?",
        "confirm_prefix_title": "Confirm Prefix Application",
        "confirm_prefix_body": "Apply the prefix \"{prefix}\" to the archive names AND their internal files for the {count} listed archive(s)?",
        "confirm_create_title": "Create CBZ archives",
        "confirm_create_body": "Create {count} .cbz archive(s) from the checked images (grouped by folder)?\nPrefix used: \"{prefix}\"\n\nThe CBZ name will be the prefix (the folder number is appended on name clash).",
        "confirm_delete_title": "⚠️ Move to Trash",
        "confirm_delete_body": "Do you want to send {count} selected file(s) to the Recycle Bin?",
        "guardrail_title": "Guardrail: Format not respected",
        "guardrail_body": "Cannot merge!\n\n{count} selected archive(s) do not follow the 4-digit format (0000 Format):\n{list}\n\nPlease use the '🏷️ Format to 0001' button on your selection first.",
        "status_processing": "Processing [{current}/{total}]: {file}",
        "status_done": "Analysis finished!",
        "status_rename_done": "Renaming finished!",
        "status_prefix_done": "Prefix applied!",
        "status_create_done": "CBZ creation finished!",
        "status_merge_done": "Merging finished!",
        "status_delete_done": "Moved to Recycle Bin successfully!",
        "status_stopped": "Stopping in progress...",
        "status_image": "IMAGE",
        "status_outlier": "OUT OF SEQUENCE",
        "about_title": f"About & User Guide - v{APP_VERSION}",
        "about_btn": f"ℹ️ v{APP_VERSION}",
        "about_content": (
            "📖 USER GUIDE (PERMANENT TUTORIAL)\n"
            "==================================================\n\n"
            "1. SELECTION & ANALYSIS:\n"
            " • Click '📁 Select' or Drag and Drop an archive folder.\n"
            " • The application recursively scans subfolders (.cbz, .zip, .rar, .7z).\n"
            " • The analyzer checks for corrupt/unwanted files (.bin) and displays their exact count.\n\n"
            "2. FORMAT TO 0001 (SELECTION):\n"
            " • Check archives to fix, then click '🏷️ Format 0001'.\n"
            " • Renames internal files and archive names to 4 digits (e.g. 1 -> 0001, 3.5 -> 0003.5).\n\n"
            "3. SAFE CBZ MERGING:\n"
            " • Check at least 2 archives matching '0000 Format' and click '⚡ Merge'.\n"
            " • Images are extracted, sequentially reordered, and packaged into a single CBZ archive.\n"
            " • Automatic CBZ naming: 'FOLDER - XXXX to XXXX.cbz'.\n\n"
            "4. CREATE CBZ FROM IMAGES (🖼️):\n"
            " • Each loose image file (.jpg, .png...) appears on its own row with a checkbox.\n"
            " • Images whose name does not follow the folder sequence (e.g. a logo) are highlighted in red (⚠️ OUT OF SEQUENCE).\n"
            " • Check the images to include, then click '📦 Create CBZ'. Checked images are grouped by folder.\n"
            " • Each folder becomes a .cbz created next to the folder (in its parent folder).\n"
            " • Internal images are renamed to prefix + 0001, 0002... numbering in natural order.\n"
            " • Default prefix = name of the dropped/opened folder (editable: chapter/tome number).\n\n"
            "5. AUTOMATIC PREFIX (NAME + INTERNAL FILES):\n"
            " • The 'Prefix' box defaults to the name of the folder dropped / opened by the user.\n"
            " • The box is editable: type the name you want, then click '🏷️ Apply Prefix'.\n"
            " • The prefix is applied to ALL listed archives, to both their name AND their internal files.\n\n"
            "6. INTERFACE TOOLS & MANAGEMENT:\n"
            " • 🔄 Refresh: Instantly rescans active folder for added or modified archives.\n"
            " • 🗑️ Trash: Sends checked archives directly to system Recycle Bin.\n"
            " • Dynamic Sorting: Click table headers to sort rows interactively.\n"
            " • Shift + Click: Click a checkbox, then Shift+Click another to select the entire range.\n\n"
            "--------------------------------------------------\n"
            "📌 RELEASE NOTES v2.4:\n"
            " - NEW: loose image files (.jpg, .png...) are listed row by row with a checkbox.\n"
            " - NEW: '📦 Create CBZ' button -> each folder of checked images becomes a .cbz (internal images renamed prefix + 0001, 0002...).\n"
            " - NEW: out-of-sequence files detection (e.g. a logo) -> highlighted in red as '⚠️ OUT OF SEQUENCE'.\n"
            " - NEW: Prefix box -> defaults to the dropped/opened folder name, editable, applied to archive names AND internal files.\n"
            " - Range selection of checkboxes (Shift + Click).\n"
            " - Natural sort (1, 2... 10 instead of 1, 10, 2) and live filtering.\n"
            " - Safe sending of files to the OS Recycle Bin.\n"
        )
    }
}


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


def safe_move_to_trash(file_path):
    """ Nettoie le chemin Windows et envoie à la corbeille de façon sécurisée. """
    clean_path = os.path.abspath(os.path.normpath(file_path))
    if clean_path.startswith("\\\\?\\"):
        clean_path = clean_path[4:]

    if HAS_SEND2TRASH:
        try:
            send2trash(clean_path)
            return
        except Exception:
            pass

    os.remove(clean_path)


class NaturalSortTableWidgetItem(QTableWidgetItem):
    """ Item personnalisé pour un tri naturel (reconnaît les nombres). """
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            return natural_sort_key(self.text()) < natural_sort_key(other.text())
        return super().__lt__(other)


def format_number_with_decimals(name):
    pattern = r'(\d+)(([._\,]\d+)?)(?=[^\d]*$)'
    match = re.search(pattern, name)
    if not match:
        return name

    start, end = match.span()
    int_part = match.group(1)
    dec_part = match.group(2) if match.group(2) else ""
    return name[:start] + f"{int(int_part):04d}{dec_part}" + name[end:]


def format_chapter_number(filename):
    base_name = os.path.splitext(filename)[0]
    pattern = r'(\d+)(([._\,]\d+)?)(?=[^\d]*$)'
    match = re.search(pattern, base_name)
    if match:
        return f"{int(match.group(1)):04d}" + (match.group(2) if match.group(2) else "")
    return "0000"


def is_formatted_4_digits(filename):
    base_name = os.path.splitext(filename)[0]
    matches = list(re.finditer(r'(\d+)(([._\,]\d+)?)', base_name))
    if not matches:
        return True
    return len(matches[-1].group(1)) >= 4


# --- DÉTECTION INTELLIGENTE DU PRÉFIXE (FICHIER / DOSSIER / DOSSIER PARENT) ---
_GENERIC_FOLDER_TOKENS = re.compile(
    r'^(chap|chaps|chapter|chapters|chapitre|chapitres|ch|scans?|raws?|pages?|imgs?|images?|cd\d*|disc\d*|partie|part)$',
    re.IGNORECASE
)


def _is_generic_folder_name(name):
    """ Considère un nom de dossier comme générique (chapitres, scans, nombres...). """
    n = (name or "").strip().lower()
    if not n:
        return True
    if re.fullmatch(r'[\W_]+', n):
        return True
    if re.fullmatch(r'\d+([._,\-]\d+)*', n):
        return True
    tokens = [tok for tok in re.split(r'[\s._,\-]+', n) if tok]
    if not tokens:
        return True
    return all(re.fullmatch(r'\d+', tok) or _GENERIC_FOLDER_TOKENS.match(tok) for tok in tokens)


def _prefix_from_filename(filename):
    """ Extrait le texte précédant la numérotation finale (ex: 'One Piece Tome 12 - 0001' -> 'One Piece Tome 12'). """
    base = os.path.splitext(os.path.basename(filename))[0]
    stripped = re.sub(r'[\s._,\-]*\d+([._,\-]\d+)?\s*$', '', base)
    return stripped.strip(' -_.')


def detect_prefix(archive_path, root_folder):
    """ Déduit le préfixe : dossier immédiat, sinon dossier parent non générique, sinon nom de fichier. """
    parent = os.path.dirname(os.path.abspath(archive_path))
    root = os.path.abspath(root_folder)

    candidates = []
    cur = parent
    while True:
        candidates.append(os.path.basename(cur))
        if os.path.normcase(cur) == os.path.normcase(root):
            break
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt

    for name in candidates:
        if not _is_generic_folder_name(name):
            return name

    return _prefix_from_filename(archive_path)


def _extract_core_token(base_name):
    """ Renvoie le dernier nombre (avec décimales éventuelles) du nom, ou None. """
    matches = list(re.finditer(r'\d+([._\,]\d+)?', base_name))
    if not matches:
        return None
    return matches[-1].group(0)


def apply_prefix_to_name(base_name, prefix):
    """ Renomme la base en '<préfixe> <numéro>' en conservant le numéro (opération idempotente). """
    p = (prefix or "").strip()
    if not p:
        return base_name
    core = _extract_core_token(base_name)
    if core is None:
        return f"{p} {base_name}"
    return f"{p} {core}"


def suggest_global_prefix(results, root_folder):
    """ Préfixe par défaut = nom du dossier déposé / ouvert par l'utilisateur. """
    if root_folder:
        return os.path.basename(root_folder.rstrip("\\/"))
    return ""


def _trailing_number(text):
    m = re.findall(r'\d+', text)
    return m[-1] if m else ""


def list_images(folder):
    """ Liste les fichiers images (non cachés) directement dans un dossier. """
    try:
        return [f for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))
                and not f.startswith('.')
                and f.lower().endswith(IMAGE_EXTS)]
    except OSError:
        return []


class AboutDialog(QDialog):
    def __init__(self, parent=None, lang="FR"):
        super().__init__(parent)
        self.lang = lang
        t = TRANSLATIONS[self.lang]
        self.setWindowTitle(t["about_title"])
        self.resize(620, 500)

        layout = QVBoxLayout(self)
        lbl_title = QLabel(f"{t['title']}")
        lbl_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        txt_info = QTextEdit()
        txt_info.setReadOnly(True)
        txt_info.setText(t["about_content"])
        layout.addWidget(txt_info)

        btn_close = QPushButton("OK")
        btn_close.setFixedHeight(35)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class ArchiveWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    result_found = pyqtSignal(dict)
    finished_processing = pyqtSignal()

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        archive_files = []
        image_map = {}

        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(ARCHIVE_EXTS):
                    archive_files.append(os.path.join(root, file))
            imgs = [f for f in files if f.lower().endswith(IMAGE_EXTS) and not f.startswith('.')]
            if imgs:
                image_map[root] = sorted(imgs, key=natural_sort_key)

        archive_files.sort(key=natural_sort_key)
        total_files = len(archive_files) + sum(len(v) for v in image_map.values())
        index = 0

        for archive_path in archive_files:
            if not self.is_running:
                break
            index += 1
            self.progress_updated.emit(index, total_files, os.path.basename(archive_path))
            self.result_found.emit(self.analyze_archive(archive_path))

        for folder_path in sorted(image_map, key=natural_sort_key):
            if not self.is_running:
                break
            imgs = image_map[folder_path]
            outliers = self._find_outliers(imgs)
            for name in imgs:
                if not self.is_running:
                    break
                index += 1
                self.progress_updated.emit(index, total_files, name)
                self.result_found.emit(self.analyze_image_file(folder_path, name, len(imgs), name in outliers))

        self.finished_processing.emit()

    def _find_outliers(self, imgs):
        """ Détecte les fichiers hors séquence (sans numéro ou en dehors de la séquence principale). """
        nums = []
        for name in imgs:
            base = os.path.splitext(name)[0]
            match = re.findall(r'\d+', base)
            nums.append(int(match[-1]) if match else None)

        numbered = sorted({n for n in nums if n is not None})
        if not numbered:
            return set()

        # Plus longue suite contiguë = séquence principale
        runs = []
        start = prev = numbered[0]
        for value in numbered[1:]:
            if value == prev + 1:
                prev = value
            else:
                runs.append((start, prev))
                start = prev = value
        runs.append((start, prev))
        lo, hi = max(runs, key=lambda r: r[1] - r[0])

        outliers = set()
        for name, n in zip(imgs, nums):
            if n is None or n < lo or n > hi:
                outliers.add(name)
        return outliers

    def stop(self):
        self.is_running = False

    def analyze_archive(self, archive_path):
        filename = os.path.basename(archive_path)
        parent_dir_full = os.path.dirname(archive_path)
        try:
            rel_parent_dir = os.path.relpath(parent_dir_full, self.folder_path)
            parent_folder_display = "." if rel_parent_dir == "." else rel_parent_dir
        except ValueError:
            parent_folder_display = parent_dir_full

        status = "OK"
        details = []
        has_bin = False
        bin_count = 0
        missing_numbers = []
        file_count = 0
        min_num, max_num = None, None
        is_4_digits = is_formatted_4_digits(filename)
        detected_prefix = detect_prefix(archive_path, self.folder_path)

        try:
            files = []
            if archive_path.lower().endswith(('.zip', '.cbz')):
                with zipfile.ZipFile(archive_path, 'r') as z:
                    files = z.namelist()
            else:
                files = [item[0] for item in patoolib.list_archive(archive_path, verbosity=-1)]

            files = [f for f in files if not f.endswith('/') and not f.endswith('\\')]
            file_count = len(files)

            bin_files = [f for f in files if f.lower().endswith('.bin')]
            bin_count = len(bin_files)
            if bin_count > 0:
                has_bin = True
                details.append(f"❌ {bin_count} .BIN file(s) found : {', '.join(bin_files)}")

            numbers = []
            for f in files:
                base_f = os.path.basename(f)
                if base_f.startswith('.'):
                    continue
                match = re.findall(r'\d+', base_f)
                if match:
                    numbers.append((int(match[-1]), base_f))

            if numbers:
                numbers.sort(key=lambda x: x[0])
                extracted_nums = [n[0] for n in numbers]
                min_num, max_num = extracted_nums[0], extracted_nums[-1]
                expected_set = set(range(min_num, max_num + 1))
                missing_numbers = sorted(list(expected_set - set(extracted_nums)))

                if missing_numbers:
                    details.append(f"❌ Incomplete sequence ({min_num} ➔ {max_num}). Missing: {missing_numbers}")
                else:
                    details.append(f"✅ Complete sequence ({min_num} ➔ {max_num})")
            else:
                details.append("⚠️ No numbered files found.")

            if has_bin and missing_numbers:
                status = "CRITICAL (BIN + Seq)"
            elif has_bin:
                status = "ERROR (.BIN inside)"
            elif missing_numbers:
                status = f"INCOMPLETE (-{len(missing_numbers)} num)"
            elif not numbers:
                status = "WARNING (Unnumbered)"

        except Exception as e:
            status = "READ ERROR"
            details.append(f"❌ Read error: {str(e)}")

        return {
            "path": archive_path,
            "kind": "archive",
            "parent_folder": parent_folder_display,
            "filename": filename,
            "prefix": detected_prefix,
            "status": status,
            "file_count": file_count,
            "has_bin": has_bin,
            "bin_count": bin_count,
            "is_4_digits": is_4_digits,
            "missing_numbers": missing_numbers,
            "range": f"{min_num} - {max_num}" if min_num is not None else "N/A",
            "details": "\n".join(details)
        }

    def analyze_image_file(self, folder_path, name, folder_count, is_outlier):
        clean_folder = folder_path.rstrip("\\/")
        folder_label = os.path.basename(clean_folder) or clean_folder
        try:
            rel_parent_dir = os.path.relpath(folder_path, self.folder_path)
            parent_folder_display = "." if rel_parent_dir == "." else rel_parent_dir
        except ValueError:
            parent_folder_display = folder_path

        base = os.path.splitext(name)[0]
        match = re.findall(r'\d+', base)
        num = match[-1] if match else None

        details = [f"🖼️ Image from folder '{folder_label}' ({folder_count} image(s))."]
        if is_outlier:
            details.append("⚠️ Out of sequence: name has no number or does not fit the main page range (possible logo/extra).")
        else:
            details.append("✅ Name fits the folder sequence.")

        return {
            "path": os.path.join(folder_path, name),
            "kind": "image_file",
            "folder": folder_path,
            "parent_folder": parent_folder_display,
            "filename": name,
            "prefix": folder_label,
            "status": "OUTLIER" if is_outlier else "IMAGE",
            "file_count": folder_count,
            "has_bin": False,
            "bin_count": 0,
            "is_4_digits": bool(num and len(num) >= 4),
            "is_outlier": is_outlier,
            "number": num,
            "missing_numbers": [],
            "range": num if num else "N/A",
            "details": "\n".join(details)
        }


class RenameWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_rename = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, selected_archives):
        super().__init__()
        self.selected_archives = selected_archives

    def run(self):
        total = len(self.selected_archives)
        processed = 0

        try:
            for idx, archive_path in enumerate(self.selected_archives):
                self.progress_updated.emit(idx + 1, total, os.path.basename(archive_path))

                dir_name, full_filename = os.path.split(archive_path)
                name_part, ext_part = os.path.splitext(full_filename)

                new_name_part = format_number_with_decimals(name_part)
                target_archive_path = os.path.join(dir_name, new_name_part + ext_part)

                if archive_path.lower().endswith(('.zip', '.cbz')):
                    temp_path = archive_path + ".tmp"
                    with zipfile.ZipFile(archive_path, 'r') as in_zip:
                        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                            for item in in_zip.namelist():
                                data = in_zip.read(item)
                                if item.endswith('/') or item.endswith('\\'):
                                    out_zip.writestr(item, data)
                                    continue

                                folder_part, filename = os.path.split(item)
                                if filename.startswith('.'):
                                    out_zip.writestr(item, data)
                                    continue

                                base_name, file_ext = os.path.splitext(filename)
                                formatted_base = format_number_with_decimals(base_name)
                                new_filename = formatted_base + file_ext

                                new_item_path = os.path.join(folder_part, new_filename).replace('\\', '/') if folder_part else new_filename
                                out_zip.writestr(new_item_path, data)

                    safe_move_to_trash(archive_path)
                    os.rename(temp_path, target_archive_path)
                else:
                    if archive_path != target_archive_path:
                        os.rename(archive_path, target_archive_path)

                processed += 1

            self.finished_rename.emit(processed)
        except Exception as e:
            self.error_occurred.emit(str(e))


class PrefixWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_prefix = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, selected_archives):
        super().__init__()
        self.selected_archives = selected_archives

    def run(self):
        total = len(self.selected_archives)
        processed = 0

        try:
            for idx, item in enumerate(self.selected_archives):
                archive_path = item["path"]
                prefix = (item.get("prefix") or "").strip()
                if not prefix:
                    continue

                self.progress_updated.emit(idx + 1, total, os.path.basename(archive_path))

                dir_name, full_filename = os.path.split(archive_path)
                name_part, ext_part = os.path.splitext(full_filename)

                new_name_part = apply_prefix_to_name(name_part, prefix)
                target_archive_path = os.path.join(dir_name, new_name_part + ext_part)

                if archive_path.lower().endswith(('.zip', '.cbz')):
                    temp_path = archive_path + ".tmp"
                    with zipfile.ZipFile(archive_path, 'r') as in_zip:
                        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                            for entry in in_zip.namelist():
                                data = in_zip.read(entry)
                                if entry.endswith('/') or entry.endswith('\\'):
                                    out_zip.writestr(entry, data)
                                    continue

                                folder_part, filename = os.path.split(entry)
                                if filename.startswith('.'):
                                    out_zip.writestr(entry, data)
                                    continue

                                base_name, file_ext = os.path.splitext(filename)
                                formatted_base = apply_prefix_to_name(base_name, prefix)
                                new_filename = formatted_base + file_ext

                                new_item_path = os.path.join(folder_part, new_filename).replace('\\', '/') if folder_part else new_filename
                                out_zip.writestr(new_item_path, data)

                    safe_move_to_trash(archive_path)
                    os.rename(temp_path, target_archive_path)
                else:
                    if archive_path != target_archive_path:
                        os.rename(archive_path, target_archive_path)

                processed += 1

            self.finished_prefix.emit(processed)
        except Exception as e:
            self.error_occurred.emit(str(e))


class CreateCbzWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_create = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, jobs):
        super().__init__()
        self.jobs = jobs

    def run(self):
        total = len(self.jobs)
        done = 0

        try:
            for idx, job in enumerate(self.jobs):
                folder = job["folder"]
                output_path = job["output_path"]
                prefix = (job.get("prefix") or "").strip()
                self.progress_updated.emit(idx + 1, total, os.path.basename(folder.rstrip("\\/")))

                imgs = job.get("images")
                if imgs is None:
                    imgs = list_images(folder)
                imgs = sorted(imgs, key=natural_sort_key)

                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                    for i, img in enumerate(imgs, 1):
                        ext = os.path.splitext(img)[1]
                        arcname = f"{prefix} {i:04d}{ext}" if prefix else f"{i:04d}{ext}"
                        out_zip.write(os.path.join(folder, img), arcname)

                done += 1

            self.finished_create.emit(done)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MergeWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished_merge = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, selected_archives, output_path):
        super().__init__()
        self.selected_archives = selected_archives
        self.output_path = output_path

    def run(self):
        current_index = 1
        total_archives = len(self.selected_archives)

        try:
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for idx, archive_path in enumerate(self.selected_archives):
                    self.progress_updated.emit(idx + 1, total_archives, os.path.basename(archive_path))

                    if archive_path.lower().endswith(('.zip', '.cbz')):
                        with zipfile.ZipFile(archive_path, 'r') as in_zip:
                            items = [f for f in in_zip.namelist() if not f.endswith('/') and not f.endswith('\\')]

                            def extract_num(fname):
                                m = re.findall(r'\d+', os.path.basename(fname))
                                return int(m[-1]) if m else None

                            items_numbered = [i for i in items if extract_num(i) is not None]
                            items_unnumbered = [i for i in items if extract_num(i) is None]

                            items_numbered.sort(key=extract_num)

                            for item in items_numbered:
                                filename = os.path.basename(item)
                                if filename.startswith('.'):
                                    continue
                                ext = os.path.splitext(filename)[1]
                                out_zip.writestr(f"{current_index:04d}{ext}", in_zip.read(item))
                                current_index += 1

                            for item in items_unnumbered:
                                filename = os.path.basename(item)
                                if not filename.startswith('.'):
                                    out_zip.writestr(filename, in_zip.read(item))

            self.finished_merge.emit(self.output_path)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ArchiveCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "FR"
        self.resize(880, 750)
        self.worker = None
        self.merge_worker = None
        self.rename_worker = None
        self.prefix_worker = None
        self.create_worker = None
        self.results_data = []
        self.all_checked = False
        self.current_folder = ""
        self.custom_destination_locked = False
        self.custom_prefix_locked = False
        self.last_checked_row = None

        self.setAcceptDrops(True)
        self.init_ui()
        self.update_language_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Top Controls
        top_layout = QHBoxLayout()
        self.btn_select = QPushButton()
        self.btn_select.setFixedHeight(36)
        self.btn_select.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_select.clicked.connect(self.select_folder)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_refresh.clicked.connect(self.refresh_folder)

        self.btn_stop = QPushButton()
        self.btn_stop.setFixedHeight(36)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_analysis)

        self.btn_toggle_all = QPushButton()
        self.btn_toggle_all.setFixedHeight(36)
        self.btn_toggle_all.setFont(QFont("Arial", 9))
        self.btn_toggle_all.clicked.connect(self.toggle_all_checkboxes)

        self.btn_rename = QPushButton()
        self.btn_rename.setFixedHeight(36)
        self.btn_rename.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_rename.setStyleSheet("background-color: #1565c0; color: white;")
        self.btn_rename.clicked.connect(self.rename_selected)

        self.btn_prefix = QPushButton()
        self.btn_prefix.setFixedHeight(36)
        self.btn_prefix.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_prefix.setStyleSheet("background-color: #ef6c00; color: white;")
        self.btn_prefix.clicked.connect(self.apply_prefix_selected)

        self.btn_create_cbz = QPushButton()
        self.btn_create_cbz.setFixedHeight(36)
        self.btn_create_cbz.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_create_cbz.setStyleSheet("background-color: #00838f; color: white;")
        self.btn_create_cbz.clicked.connect(self.create_cbz_selected)

        self.btn_merge = QPushButton()
        self.btn_merge.setFixedHeight(36)
        self.btn_merge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_merge.setStyleSheet("background-color: #2e7d32; color: white;")
        self.btn_merge.clicked.connect(self.merge_selected)

        self.btn_delete = QPushButton()
        self.btn_delete.setFixedHeight(36)
        self.btn_delete.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.btn_delete.setStyleSheet("background-color: #c62828; color: white;")
        self.btn_delete.clicked.connect(self.delete_selected)

        top_layout.addWidget(self.btn_select)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_stop)
        top_layout.addWidget(self.btn_toggle_all)
        top_layout.addWidget(self.btn_rename)
        top_layout.addWidget(self.btn_prefix)
        top_layout.addWidget(self.btn_create_cbz)
        top_layout.addWidget(self.btn_merge)
        top_layout.addWidget(self.btn_delete)
        main_layout.addLayout(top_layout)

        # Destination
        dest_layout = QHBoxLayout()
        self.lbl_dest = QLabel()
        self.lbl_dest.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.txt_destination = QLineEdit()
        self.btn_browse_dest = QPushButton()
        self.btn_browse_dest.clicked.connect(self.browse_destination)

        dest_layout.addWidget(self.lbl_dest)
        dest_layout.addWidget(self.txt_destination, 1)
        dest_layout.addWidget(self.btn_browse_dest)
        main_layout.addLayout(dest_layout)

        # Préfixe global (nom de l'archive + fichiers internes)
        prefix_layout = QHBoxLayout()
        self.lbl_prefix = QLabel()
        self.lbl_prefix.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.txt_prefix = QLineEdit()
        self.txt_prefix.setStyleSheet("background-color: #e3f2fd;")
        self.txt_prefix.textEdited.connect(self.on_prefix_edited)
        prefix_layout.addWidget(self.lbl_prefix)
        prefix_layout.addWidget(self.txt_prefix, 1)
        main_layout.addLayout(prefix_layout)

        # Progress
        progress_layout = QVBoxLayout()
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #444; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.lbl_status)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        # Filter
        filter_layout = QHBoxLayout()
        self.lbl_filter = QLabel()
        self.lbl_filter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.txt_filter = QLineEdit()
        self.txt_filter.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.lbl_filter)
        filter_layout.addWidget(self.txt_filter)
        main_layout.addLayout(filter_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 200)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.show_details)
        self.table.itemClicked.connect(self.handle_table_item_clicked)
        splitter.addWidget(self.table)

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 5, 0, 0)

        self.lbl_source_folder_info = QLabel()
        self.lbl_source_folder_info.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.lbl_source_folder_info.setStyleSheet("color: #1565c0; margin-bottom: 2px;")

        self.lbl_details_title = QLabel()
        self.lbl_details_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setFont(QFont("Monospace", 9))

        bottom_bar_layout = QHBoxLayout()
        self.btn_about = QPushButton()
        self.btn_about.setFixedHeight(30)
        self.btn_about.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.btn_about.setStyleSheet("background-color: #424242; color: white;")
        self.btn_about.clicked.connect(self.show_about_dialog)

        self.btn_lang = QPushButton("🌐 FR")
        self.btn_lang.setFixedHeight(30)
        self.btn_lang.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.btn_lang.setStyleSheet("background-color: #6a1b9a; color: white;")
        self.btn_lang.clicked.connect(self.toggle_language)

        bottom_bar_layout.addWidget(self.lbl_details_title, 1)
        bottom_bar_layout.addWidget(self.btn_about)
        bottom_bar_layout.addWidget(self.btn_lang)

        details_layout.addWidget(self.lbl_source_folder_info)
        details_layout.addLayout(bottom_bar_layout)
        details_layout.addWidget(self.txt_details)
        splitter.addWidget(details_widget)

        splitter.setSizes([450, 180])
        main_layout.addWidget(splitter)

    def handle_table_item_clicked(self, item):
        """ Gère la sélection par plage (Shift + Clic) sur les cases à cocher. """
        if item.column() != 0:
            return

        current_row = item.row()
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.KeyboardModifier.ShiftModifier and self.last_checked_row is not None:
            target_state = item.checkState()
            start_row = min(self.last_checked_row, current_row)
            end_row = max(self.last_checked_row, current_row)

            for row in range(start_row, end_row + 1):
                if not self.table.isRowHidden(row):
                    chk = self.table.item(row, 0)
                    if chk:
                        chk.setCheckState(target_state)

        self.last_checked_row = current_row

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "FR" else "FR"
        self.btn_lang.setText(f"🌐 {self.current_lang}")
        self.update_language_ui()

    def update_language_ui(self):
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(t["title"])
        self.btn_select.setText(t["btn_select"])
        self.btn_refresh.setText(t["btn_refresh"])
        self.btn_stop.setText(t["btn_stop"])
        self.btn_toggle_all.setText(t["btn_toggle_all_uncheck"] if self.all_checked else t["btn_toggle_all_check"])
        self.btn_rename.setText(t["btn_rename"])
        self.btn_prefix.setText(t["btn_prefix"])
        self.btn_create_cbz.setText(t["btn_create_cbz"])
        self.btn_merge.setText(t["btn_merge"])
        self.btn_delete.setText(t["btn_delete"])
        self.btn_about.setText(t["about_btn"])

        self.lbl_dest.setText(t["lbl_dest"])
        self.txt_destination.setPlaceholderText(t["txt_dest_placeholder"])
        self.btn_browse_dest.setText(t["btn_browse_dest"])
        self.lbl_prefix.setText(t["lbl_prefix"])
        self.txt_prefix.setPlaceholderText(t["txt_prefix_placeholder"])
        self.lbl_status.setText(t["lbl_status_ready"])
        self.lbl_filter.setText(t["lbl_filter"])
        self.txt_filter.setPlaceholderText(t["txt_filter_placeholder"])

        self.table.setHorizontalHeaderLabels([
            t["col_select"], t["col_parent"], t["col_archive"], t["col_format"],
            t["col_status"], t["col_files"], t["col_range"], t["col_bin"]
        ])
        self.lbl_details_title.setText(t["lbl_details_title"])

        if self.current_folder:
            self.lbl_source_folder_info.setText(f"{t['lbl_source_folder']}{self.current_folder}")
        else:
            self.lbl_source_folder_info.setText(t['lbl_no_folder'])

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                res = next((r for r in self.results_data if r["path"] == file_path), None)
                if res:
                    item_fmt = self.table.item(row, 3)
                    item_bin = self.table.item(row, 7)
                    if item_fmt:
                        item_fmt.setText(t["yes"] if res["is_4_digits"] else t["no"])
                    if item_bin:
                        bin_text = f"{t['yes']} ({res['bin_count']})" if res["has_bin"] else t["no"]
                        item_bin.setText(bin_text)
                    if res.get("kind") == "image_file":
                        item_status = self.table.item(row, 4)
                        if item_status:
                            item_status.setText(t["status_outlier"] if res.get("is_outlier") else t["status_image"])

    def show_about_dialog(self):
        dialog = AboutDialog(self, self.current_lang)
        dialog.exec()

    def browse_destination(self):
        dir_path = QFileDialog.getExistingDirectory(self, TRANSLATIONS[self.current_lang]["lbl_dest"])
        if dir_path:
            self.txt_destination.setText(dir_path)
            self.custom_destination_locked = True

    def set_root_folder(self, folder):
        self.current_folder = folder
        self.custom_prefix_locked = False
        t = TRANSLATIONS[self.current_lang]
        self.lbl_source_folder_info.setText(f"{t['lbl_source_folder']}{folder}")
        if not self.custom_destination_locked:
            self.txt_destination.setText(folder)
        self.start_analysis(folder)

    def refresh_folder(self):
        t = TRANSLATIONS[self.current_lang]
        if self.current_folder and os.path.exists(self.current_folder):
            self.start_analysis(self.current_folder)
        else:
            QMessageBox.information(self, "Info", t["msg_no_folder_to_refresh"])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.set_root_folder(path)
            else:
                QMessageBox.warning(self, "Error", TRANSLATIONS[self.current_lang]["msg_invalid_folder"])

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.set_root_folder(folder)

    def delete_selected(self):
        t = TRANSLATIONS[self.current_lang]
        items_to_delete = []

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    items_to_delete.append(file_path)

        if not items_to_delete:
            QMessageBox.warning(self, "Warning", t["msg_no_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_delete_title"],
            t["confirm_delete_body"].format(count=len(items_to_delete)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.table.setSortingEnabled(False)
        deleted_count = 0
        errors = []

        for row in range(self.table.rowCount() - 1, -1, -1):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                try:
                    if file_path and os.path.exists(file_path):
                        safe_move_to_trash(file_path)

                    self.results_data = [r for r in self.results_data if r["path"] != file_path]
                    self.table.removeRow(row)
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")

        self.table.setSortingEnabled(True)

        if errors:
            QMessageBox.critical(self, "Error", "Erreur lors de la suppression :\n" + "\n".join(errors))
        else:
            self.lbl_status.setText(t["status_delete_done"])
            QMessageBox.information(self, "OK", f"{deleted_count} fichier(s) traité(s).")

    def rename_selected(self):
        t = TRANSLATIONS[self.current_lang]
        selected_paths = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                res = next((r for r in self.results_data if r["path"] == file_path), None)
                if file_path and res and res.get("kind") == "archive":
                    selected_paths.append(file_path)

        if not selected_paths:
            QMessageBox.warning(self, "Warning", t["msg_no_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_rename_title"],
            t["confirm_rename_body"].format(count=len(selected_paths)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_prefix.setEnabled(False)
        self.btn_create_cbz.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.rename_worker = RenameWorker(selected_paths)
        self.rename_worker.progress_updated.connect(self.update_progress)
        self.rename_worker.finished_rename.connect(self.rename_finished)
        self.rename_worker.error_occurred.connect(self.rename_error)
        self.rename_worker.start()

    def rename_finished(self, count):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_rename_done"])
        QMessageBox.information(self, "OK", f"{count} archive(s) OK.")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def rename_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def toggle_all_checkboxes(self):
        t = TRANSLATIONS[self.current_lang]
        self.all_checked = not self.all_checked
        target_state = Qt.CheckState.Checked if self.all_checked else Qt.CheckState.Unchecked

        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    item.setCheckState(target_state)

        self.btn_toggle_all.setText(t["btn_toggle_all_uncheck"] if self.all_checked else t["btn_toggle_all_check"])

    def start_analysis(self, folder):
        t = TRANSLATIONS[self.current_lang]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.results_data.clear()
        self.txt_details.clear()
        self.txt_filter.clear()
        self.all_checked = False
        self.last_checked_row = None
        self.btn_toggle_all.setText(t["btn_toggle_all_check"])
        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.worker = ArchiveWorker(folder)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.result_found.connect(self.add_result)
        self.worker.finished_processing.connect(self.analysis_finished)
        self.worker.start()

    def stop_analysis(self):
        if self.worker:
            self.worker.stop()
        self.lbl_status.setText(TRANSLATIONS[self.current_lang]["status_stopped"])

    def update_progress(self, current, total, filename):
        t = TRANSLATIONS[self.current_lang]
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.lbl_status.setText(t["status_processing"].format(current=current, total=total, file=filename))

    def add_result(self, res):
        t = TRANSLATIONS[self.current_lang]
        self.results_data.append(res)
        row = self.table.rowCount()
        self.table.insertRow(row)

        chk_item = QTableWidgetItem()
        chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk_item.setCheckState(Qt.CheckState.Unchecked)
        chk_item.setData(Qt.ItemDataRole.UserRole, res["path"])

        item_folder = NaturalSortTableWidgetItem(res["parent_folder"])
        kind = res.get("kind")
        is_outlier = bool(res.get("is_outlier"))
        if kind == "image_file":
            name_text = f"⚠️ {res['filename']}" if is_outlier else res["filename"]
        else:
            name_text = res["filename"]
        item_name = NaturalSortTableWidgetItem(name_text)
        item_fmt = QTableWidgetItem(t["yes"] if res["is_4_digits"] else t["no"])
        if kind == "image_file":
            status_text = t["status_outlier"] if is_outlier else t["status_image"]
        else:
            status_text = res["status"]
        item_status = QTableWidgetItem(status_text)
        item_count = NaturalSortTableWidgetItem(f"{res['file_count']}")
        item_range = QTableWidgetItem(res["range"])

        bin_text = f"{t['yes']} ({res['bin_count']})" if res["has_bin"] else t["no"]
        item_bin = QTableWidgetItem(bin_text)

        if kind == "image_file" and is_outlier:
            item_name.setBackground(QColor("#ffebee"))
            item_name.setForeground(QColor("#b71c1c"))
            item_status.setBackground(QColor("#ffcdd2"))
            item_status.setForeground(QColor("#b71c1c"))
        elif kind == "image_file":
            item_status.setBackground(QColor("#b3e5fc"))
            item_status.setForeground(QColor("#01579b"))
        elif "CRITICAL" in res["status"] or "CRITIQUE" in res["status"] or "ERROR" in res["status"] or "ERREUR" in res["status"]:
            item_status.setBackground(QColor("#ffcdd2"))
            item_status.setForeground(QColor("#b71c1c"))
        elif "INCOMPLETE" in res["status"] or "INCOMPLET" in res["status"]:
            item_status.setBackground(QColor("#ffe0b2"))
            item_status.setForeground(QColor("#e65100"))
        elif "WARNING" in res["status"] or "AVERTISSEMENT" in res["status"]:
            item_status.setBackground(QColor("#fff9c4"))
            item_status.setForeground(QColor("#f57f17"))
        else:
            item_status.setBackground(QColor("#c8e6c9"))
            item_status.setForeground(QColor("#1b5e20"))

        self.table.setItem(row, 0, chk_item)
        self.table.setItem(row, 1, item_folder)
        self.table.setItem(row, 2, item_name)
        self.table.setItem(row, 3, item_fmt)
        self.table.setItem(row, 4, item_status)
        self.table.setItem(row, 5, item_count)
        self.table.setItem(row, 6, item_range)
        self.table.setItem(row, 7, item_bin)

    def filter_table(self):
        query = self.txt_filter.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(1, self.table.columnCount()):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def show_details(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        chk_item = self.table.item(row, 0)
        if not chk_item:
            return

        file_path = chk_item.data(Qt.ItemDataRole.UserRole)
        res = next((r for r in self.results_data if r["path"] == file_path), None)

        if res:
            text = f"Folder : {res['parent_folder']}\n"
            text += f"Path : {res['path']}\n"
            text += f"Prefix : {res.get('prefix', '')}\n"
            text += f"Format 0000 : {'Yes' if res['is_4_digits'] else 'No'}\n"
            text += f"Files : {res['file_count']}\n"
            text += f"Status : {res['status']}\n"
            text += "=" * 60 + "\n"
            text += res['details']

            self.txt_details.setText(text)

    def on_prefix_edited(self, text):
        self.custom_prefix_locked = True

    def apply_prefix_selected(self):
        t = TRANSLATIONS[self.current_lang]
        prefix = self.txt_prefix.text().strip()

        if not prefix:
            QMessageBox.warning(self, "Warning", t["msg_prefix_empty"])
            return

        targets = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            chk_item = self.table.item(row, 0)
            if not chk_item:
                continue
            file_path = chk_item.data(Qt.ItemDataRole.UserRole)
            res = next((r for r in self.results_data if r["path"] == file_path), None)
            if res and res.get("kind") == "archive":
                targets.append(res)

        if not targets:
            QMessageBox.warning(self, "Warning", t["msg_no_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_prefix_title"],
            t["confirm_prefix_body"].format(count=len(targets), prefix=prefix),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_prefix.setEnabled(False)
        self.btn_create_cbz.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        items = [{"path": r["path"], "prefix": prefix} for r in targets]
        self.prefix_worker = PrefixWorker(items)
        self.prefix_worker.progress_updated.connect(self.update_progress)
        self.prefix_worker.finished_prefix.connect(self.prefix_finished)
        self.prefix_worker.error_occurred.connect(self.prefix_error)
        self.prefix_worker.start()

    def prefix_finished(self, count):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_prefix_done"])
        QMessageBox.information(self, "OK", f"{count} archive(s) OK.")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def prefix_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def create_cbz_selected(self):
        t = TRANSLATIONS[self.current_lang]
        prefix = self.txt_prefix.text().strip()

        folders = {}
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            chk_item = self.table.item(row, 0)
            if not chk_item or chk_item.checkState() != Qt.CheckState.Checked:
                continue
            file_path = chk_item.data(Qt.ItemDataRole.UserRole)
            res = next((r for r in self.results_data if r["path"] == file_path), None)
            if res and res.get("kind") == "image_file":
                folders.setdefault(res["folder"], []).append(res["filename"])

        if not folders:
            QMessageBox.warning(self, "Warning", t["msg_no_image_selection"])
            return

        reply = QMessageBox.question(
            self, t["confirm_create_title"],
            t["confirm_create_body"].format(count=len(folders), prefix=prefix or "-"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        used = set()
        jobs = []
        for folder in sorted(folders, key=natural_sort_key):
            clean_folder = folder.rstrip("\\/")
            parent = os.path.dirname(clean_folder)
            base = prefix or os.path.basename(clean_folder)
            candidate = base
            attempt = 0
            while candidate.lower() in used or os.path.exists(os.path.join(parent, candidate + ".cbz")):
                attempt += 1
                num = _trailing_number(os.path.basename(clean_folder))
                candidate = f"{base} {num}" if (attempt == 1 and num) else f"{base} {attempt}"
            used.add(candidate.lower())
            jobs.append({
                "folder": clean_folder,
                "output_path": os.path.join(parent, candidate + ".cbz"),
                "prefix": prefix,
                "images": folders[folder],
            })

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_prefix.setEnabled(False)
        self.btn_create_cbz.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.create_worker = CreateCbzWorker(jobs)
        self.create_worker.progress_updated.connect(self.update_progress)
        self.create_worker.finished_create.connect(self.create_cbz_finished)
        self.create_worker.error_occurred.connect(self.create_cbz_error)
        self.create_worker.start()

    def create_cbz_finished(self, count):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_create_done"])
        QMessageBox.information(self, "OK", f"{count} .cbz OK.")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def create_cbz_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def merge_selected(self):
        t = TRANSLATIONS[self.current_lang]
        selected_items = []

        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
                file_path = chk_item.data(Qt.ItemDataRole.UserRole)
                res = next((r for r in self.results_data if r["path"] == file_path), None)
                if res and res.get("kind") == "archive":
                    selected_items.append(res)

        if len(selected_items) < 2:
            QMessageBox.warning(self, "Warning", t["msg_merge_min"])
            return

        non_formatted = [item["filename"] for item in selected_items if not item["is_4_digits"]]
        if non_formatted:
            fmt_list = "\n".join([f"- {name}" for name in non_formatted[:5]]) + ("\n..." if len(non_formatted) > 5 else "")
            QMessageBox.critical(self, t["guardrail_title"], t["guardrail_body"].format(count=len(non_formatted), list=fmt_list))
            return

        selected_paths = [item["path"] for item in selected_items]
        first_num = format_chapter_number(selected_items[0]["filename"])
        last_num = format_chapter_number(selected_items[-1]["filename"])

        folder_base_name = os.path.basename(self.current_folder) if self.current_folder else "Archive_fusion"
        output_filename = f"{folder_base_name} - {first_num} to {last_num}.cbz"

        dest_dir = self.txt_destination.text().strip()
        if not dest_dir or not os.path.isdir(dest_dir):
            dest_dir = self.current_folder if self.current_folder else os.getcwd()

        output_path = os.path.join(dest_dir, output_filename)

        self.btn_select.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_prefix.setEnabled(False)
        self.btn_create_cbz.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.merge_worker = MergeWorker(selected_paths, output_path)
        self.merge_worker.progress_updated.connect(self.update_progress)
        self.merge_worker.finished_merge.connect(self.merge_finished)
        self.merge_worker.error_occurred.connect(self.merge_error)
        self.merge_worker.start()

    def merge_finished(self, out_path):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_status.setText(t["status_merge_done"])
        QMessageBox.information(self, "OK", f"CBZ OK:\n{out_path}")
        if self.current_folder:
            self.start_analysis(self.current_folder)

    def merge_error(self, err):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_prefix.setEnabled(True)
        self.btn_create_cbz.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_delete.setEnabled(True)
        QMessageBox.critical(self, "Error", err)

    def analysis_finished(self):
        self.btn_select.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.table.setSortingEnabled(True)
        self.lbl_status.setText(TRANSLATIONS[self.current_lang]["status_done"])
        if not self.custom_prefix_locked:
            self.txt_prefix.setText(suggest_global_prefix(self.results_data, self.current_folder))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArchiveCheckerApp()
    window.show()
    sys.exit(app.exec())