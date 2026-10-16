# 📦 ArchiveCRM - Archive Checker, Renamer & Merger GUI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)]()

--------------------------------------------------------------------------------
[EN] ENGLISH
--------------------------------------------------------------------------------

Archive Checker, Renamer & Merger is a full-featured desktop tool developed in 
Python (PyQt6)[cite: 1]. It is designed to automate the analysis, normalization, 
renaming, and merging of image archives (.cbz, .zip, .rar, .7z), specifically 
optimized for managing batches of manga chapters and scans[cite: 1].

GENERAL PURPOSE & USE CASES
---------------------------
Import a full folder of archives, recursively scan all supported files, 
identify sequence anomalies or corrupt files, format numbering to 4 digits 
(0000), and combine multiple archives into a single organized CBZ file[cite: 1].

CORE FEATURES
-------------

1. Asynchronous Scanner & Analyzer (ArchiveWorker)
 - Recursive Scanning : Scans all subdirectories to detect .zip, .cbz, .rar, 
   .cbr, .7z, .tar, and .gz formats[cite: 1].
 - Unwanted File Detection (.bin) : Detects corrupt or stray .bin files and 
   displays the exact count in a dedicated column (.BIN Files)[cite: 1].
 - Numerical Sequence Check : Inspects internal filenames to determine the 
   start/end sequence, detects missing pages in the chain (e.g., jump from 04 
   to 06), and highlights incomplete sequences[cite: 1].
 - Status Calculation : Assigns a color-coded status to each archive (OK, 
   INCOMPLETE, ERROR (.BIN inside), CRITICAL, WARNING)[cite: 1].
 - Threaded Execution : Runs on a dedicated QThread using Qt signals to ensure 
   a smooth, non-blocking UI[cite: 1].

2. Numbering Formatter (RenameWorker)
 - Standard 4-Digit Padding : Rewrites internal file numbering and the archive 
   filename to 4 digits (e.g., 1 -> 0001, 3.5 -> 0003.5)[cite: 1].
 - Decimal Retention : Preserves point and comma notation for half-chapters 
   or sub-releases[cite: 1].
 - Safe In-Place Rewrite : Builds a clean temporary archive, sends the original 
   file safely to the OS Recycle Bin, and applies the new name[cite: 1].

3. CBZ Archive Merger (MergeWorker)
 - Sequential Reassembly : Extracts and dynamically reorders images across all 
   selected archives into a single .cbz file[cite: 1].
 - Continuous Indexing : Renames all extracted pages into a contiguous 4-digit 
   sequence (0001.jpg, 0002.jpg, etc.)[cite: 1].
 - Automated Output Naming : Formats the final file name using the pattern: 
   SOURCE_FOLDER - XXXX to XXXX.cbz[cite: 1].
 - Strict Guardrail : Prevents merging if one or more selected archives have not 
   yet been formatted to 4 digits (is_formatted_4_digits)[cite: 1].

4. File Safety & Trash Integration (safe_move_to_trash)
 - System Trash (send2trash) : Deletion and replacement actions use the 
   operating system Recycle Bin / Trash rather than permanent deletion 
   (os.remove), allowing safe recovery[cite: 1].

5. Loose Images & CBZ Creation (CreateCbzWorker)
 - Image Listing : Every loose image file (.jpg, .jpeg, .png, .webp, .bmp, 
   .gif, .tif, .tiff, .avif) is displayed row by row with its own checkbox, 
   ready to be selected[cite: 1].
 - Create CBZ : Pack every folder of checked images into a single .cbz, created 
   next to the source folder. Internal images are rewritten as a continuous 
   sequence prefixed with the chosen prefix (e.g. 0001.jpg, 0002.jpg)[cite: 1].
 - Out-of-Sequence Detection : Images whose name has no number or falls outside 
   the folder's main sequence (e.g. a stray logo) are highlighted in red as 
   "OUT OF SEQUENCE" so they can be excluded[cite: 1].

6. Automatic Prefix (detect_prefix / PrefixWorker)
 - Smart Detection : The prefix defaults to the name of the folder dropped / 
   opened by the user, and can be freely edited in the dedicated field[cite: 1].
 - Apply Prefix : Applies the prefix to the archive name AND its internal files, 
   with a non-destructive, idempotent rename[cite: 1].

UI & USABILITY HIGHLIGHTS (ArchiveCheckerApp)
--------------------------------------------
 - Drag & Drop : Directly drop folders onto the window to begin scanning[cite: 1].
 - Dual-Pane Layout (QSplitter) : Interactive top data table paired with a 
   bottom information/guide pane[cite: 1].
 - Natural Sorting & Filtering : Full natural sort across columns 
   (NaturalSortTableWidgetItem: 1, 2, ..., 10 instead of 1, 10, 2) and instant 
   live filtering[cite: 1].
 - Range Selection : Click a checkbox, then Shift+Click another to select the 
   whole range[cite: 1].
 - Live Language Switch (FR / EN) : Instant UI localization via the 
   TRANSLATIONS dictionary[cite: 1].
 - Standalone Build Support : Includes sys._MEIPASS path handling for smooth 
   PyInstaller packaging[cite: 1].

BUILD (WINDOWS .EXE)
--------------------
pyinstaller --noconsole --onefile --clean archive-checker-renamer-merger-gui.py



[FR] FRANCAIS
--------------------------------------------------------------------------------

L'application Archive Checker, Renamer & Merger est un outil desktop complet 
developpe sous Python (PyQt6). Elle est concue pour automatiser l'analyse, 
la normalisation, le renommage et la fusion d'archives d'images 
(.cbz, .zip, .rar, .7z), particulierement adaptees au traitement de lots de scans 
et de mangas[cite: 1].

ROLE GENERAL & CAS D'USAGE
--------------------------
L'application permet d'importer un dossier complet d'archives, de scanner 
recursivement l'ensemble des fichiers, d'identifier les anomalies de sequence 
ou la presence de fichiers parasites, de formater la numerotation sur 4 chiffres 
(0000) et d'assembler plusieurs chapitres/archives en un unique fichier CBZ 
securise[cite: 1].

FONCTIONNALITES PRINCIPALES
---------------------------

1. Scanner & Analyseur asynchrone (ArchiveWorker)
 - Scan recursif : Analyse tous les sous-dossiers pour detecter les formats 
   .zip, .cbz, .rar, .cbr, .7z, .tar, .gz[cite: 1].
 - Detection des fichiers parasites (.bin) : Identifie specifiquement les 
   fichiers .bin corrompus ou inutiles et affiche leur nombre exact dans une 
   colonne dediee (.BIN Files)[cite: 1].
 - Controle de sequence numerique : Inspecte les noms des fichiers internes 
   pour calculer le premier et le dernier numero, identifie les numeros 
   manquants dans la chaine (ex: saut du chapitre 04 au 06) et signale les 
   sequences incompletes[cite: 1].
 - Calcul du statut : Attribue un etat colore par archive (OK, INCOMPLETE, 
   ERROR (.BIN inside), CRITICAL, WARNING)[cite: 1].
 - Execution hors thread : Fonctionne sur un QThread dedie avec emission de 
   signaux pour ne jamais figer l'interface graphique[cite: 1].

2. Formateur de numerotation (RenameWorker)
 - Formatage standard a 4 chiffres : Reecrit la numerotation des fichiers 
   internes de l'archive ainsi que le nom de l'archive elle-meme sur 4 chiffres 
   (ex: 1 -> 0001, 3.5 -> 0003.5)[cite: 1].
 - Conservation des decimaux : Preserve la precision des demi-chapitres ou des 
   numerotations a virgule/point[cite: 1].
 - Mise a jour securisee : Reconstruit une archive temporaire, deplace la 
   version originale vers la corbeille systeme et applique le nouveau nom sans 
   risque de perte de donnees[cite: 1].

3. Fusionneur d'archives CBZ (MergeWorker)
 - Assemblage sequentiel : Extrait et reordonne dynamiquement toutes les images 
   de plusieurs archives selectionnees pour les regrouper dans un fichier .cbz 
   unique[cite: 1].
 - Renommage sequentiel global : Reindexe toutes les pages extraites sous une 
   suite continue a 4 chiffres (0001.jpg, 0002.jpg, etc.)[cite: 1].
 - Nomenclature automatique : Genere automatiquement le nom du fichier CBZ 
   final au format : DOSSIER_SOURCE - XXXX to XXXX.cbz[cite: 1].
 - Garde-fou strict : Bloque la fusion si une ou plusieurs archives de la 
   selection n'ont pas ete prealablement formatees au format 4 chiffres 
   (is_formatted_4_digits)[cite: 1].

4. Securite & Gestion des fichiers (safe_move_to_trash)
 - Corbeille OS (send2trash) : Les operations de suppression ou de remplacement 
   lors des renommages envoient les fichiers vers la corbeille de l'OS 
   (Windows/Linux) pour permettre une recuperation au lieu d'une suppression 
   definitive[cite: 1].

5. Images libres & Creation de CBZ (CreateCbzWorker)
 - Liste des images : Chaque fichier image libre (.jpg, .jpeg, .png, .webp, 
   .bmp, .gif, .tif, .tiff, .avif) est affiche ligne par ligne avec sa propre 
   case a cocher, pret a etre selectionne[cite: 1].
 - Creer CBZ : Regroupe chaque dossier d'images cochees dans un unique .cbz, 
   cree a cote du dossier source. Les images internes sont reecrites en suite 
   continue prefixee (ex: 0001.jpg, 0002.jpg)[cite: 1].
 - Detection hors sequence : Les images dont le nom n'a pas de numero ou sort de 
   la sequence principale du dossier (ex: un logo parasite) sont surlignees en 
   rouge "HORS SEQUENCE" afin de pouvoir les exclure[cite: 1].

6. Prefixe automatique (detect_prefix / PrefixWorker)
 - Detection intelligente : Le prefixe reprend par defaut le nom du dossier 
   depose / ouvert par l'utilisateur, et reste modifiable dans le champ dedie[cite: 1].
 - Appliquer prefixe : Applique le prefixe au nom de l'archive ET a ses fichiers 
   internes, via un renommage non destructif et idempotent[cite: 1].

ERGONOMIE & INTERFACE GRAPHIQUE (ArchiveCheckerApp)
--------------------------------------------------
 - Glisser-Deposer (Drag & Drop) : Support du depot direct de dossiers sur la 
   fenetre pour lancer le scanner[cite: 1].
 - Interface a panneaux (QSplitter) : Tableau dynamique au-dessus et zone de 
   detail/guide sous le tableau[cite: 1].
 - Tri naturel & Filtrage : Tri numerique et naturel reel sur toutes les 
   colonnes (NaturalSortTableWidgetItem : 1, 2, ..., 10 au lieu de 1, 10, 2) 
   et champ de recherche/filtrage en temps reel[cite: 1].
 - Selection par plage : Cochez une case puis Shift+Clic sur une autre pour 
   selectionner toute la plage[cite: 1].
 - Internationalisation dynamique (FR / EN) : Bascule instantanee de la 
   totalite des libelles et messages de l'interface via le dictionnaire 
   TRANSLATIONS[cite: 1].
 - Compatibilite executables autonomes : Integration de la gestion de chemin 
   sys._MEIPASS pour la compilation sans erreur sous PyInstaller[cite: 1].

COMPILATION (WINDOWS .EXE)
--------------------------
pyinstaller --noconsole --onefile --clean archive-checker-renamer-merger-gui.py

---

## 📜 License
Distribué sous la licence GNU General Public License v3.0 (GPLv3). Voir le fichier `LICENSE` pour plus d'informations.  
Distributed under the GNU General Public License v3.0 (GPLv3). See `LICENSE` for more information.