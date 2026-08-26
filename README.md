# Change of Heart — Persona 5 Royal Save Editor for macOS

Un éditeur de sauvegardes Persona 5 Royal conçu pour fonctionner comme une
application macOS autonome sur les Mac Apple Silicon.

<p align="center">
  <img src="change_of_heart_logo.jpg" alt="Change of Heart" width="360">
</p>

<p align="center">
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20arm64-black?style=for-the-badge&logo=apple" alt="macOS Apple Silicon"></a>
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/Tests-173%20passing-brightgreen?style=for-the-badge" alt="173 tests passing"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License"></a>
</p>

## Version macOS

Cette version transforme l’éditeur Windows d’origine en véritable bundle
`Change of Heart.app` pour macOS :

- exécutable Mach-O natif `arm64` ;
- fenêtre macOS Cocoa utilisant WebKit ;
- moteur Python et dépendances entièrement intégrés dans l’application ;
- aucun besoin d’installer Python sur le Mac qui exécute le bundle ;
- détection automatique des sauvegardes Steam, CrossOver et Whisky ;
- serveur interne limité à `127.0.0.1` avec protection contre les requêtes
  provenant de sites externes.

Le moteur de manipulation des sauvegardes reste celui du projet original. Il
n’a pas été réécrit en Swift afin de conserver les tests et les protections qui
empêchent la corruption des fichiers.

## Compatibilité

| Environnement | État |
|---|---|
| Mac Apple Silicon | **Pris en charge et testé** |
| Architecture | `arm64` |
| macOS minimum déclaré | macOS 12 Monterey |
| Fenêtre native | Cocoa + WebKit |
| Mac Intel | Non testé, aucun bundle `x86_64` fourni actuellement |
| CrossOver | Détection automatique prise en charge |
| Whisky | Détection automatique prise en charge |
| Steam macOS | Recherche dans le dossier `userdata` prise en charge |

Les Mac Apple Silicon regroupent les machines équipées d’une puce Apple de la
famille M. Le bundle actuellement produit n’est pas universel : il ne contient
pas de tranche Intel `x86_64`.

## Construire l’application

### Prérequis

- un Mac Apple Silicon ;
- [Homebrew](https://brew.sh/) ;
- Python 3.14 installé avec Homebrew.

```bash
brew install python@3.14
```

### Build automatique

Clonez le dépôt puis lancez le script de construction :

```bash
git clone https://github.com/SltcYann/change-of-heart-mac.git
cd change-of-heart-mac
./Build_macOS.command
```

Le script :

1. crée un environnement isolé dans `.venv-macos` ;
2. installe PyWebView, PyObjC, PyInstaller et les dépendances cryptographiques ;
3. exécute la suite de tests ;
4. construit et signe localement le bundle macOS.

Résultat :

```text
dist/Change of Heart.app
```

Vous pouvez ensuite déplacer `Change of Heart.app` dans le dossier
`Applications`.

## Lancer l’application

Double-cliquez sur `Change of Heart.app`.

La version construite localement reçoit une signature macOS ad hoc. Elle est
valide pour une utilisation locale, mais elle n’est pas encore signée avec un
certificat Apple Developer ID ni notarisée par Apple.

Lors du premier lancement d’un bundle téléchargé, macOS peut afficher une
alerte Gatekeeper. Dans ce cas, utilisez **clic droit → Ouvrir**, puis confirmez
l’ouverture. Ne désactivez pas globalement les protections de macOS.

## Trouver les sauvegardes

L’application recherche automatiquement les sauvegardes Persona 5 Royal dans
les emplacements courants.

### CrossOver

```text
~/Library/Application Support/CrossOver/Bottles/*/drive_c/users/*/
AppData/Roaming/SEGA/P5R/Steam/*/savedata/
```

### Whisky

```text
~/Library/Containers/com.isaacmarovitz.Whisky/Bottles/*/drive_c/users/*/
AppData/Roaming/SEGA/P5R/Steam/*/savedata/
```

### Steam

```text
~/Library/Application Support/Steam/userdata/*/1687950/remote/
```

Si votre sauvegarde se trouve ailleurs, utilisez le bouton de sélection
manuelle dans l’interface.

## Fonctionnalités

### Informations générales

- modification du prénom, du nom et du nom des Phantom Thieves ;
- modification des yens ;
- lecture des informations de partie, du niveau et du temps de jeu ;
- prise en charge des sauvegardes PC/Steam Persona 5 Royal.

### Confidents et statistiques sociales

- modification des 23 Confidents ;
- conservation des points d’affinité déjà accumulés ;
- modification des cinq statistiques sociales ;
- gestion protégée des routes romance/amitié ;
- garde-fous contre les rangs incompatibles avec la progression de l’histoire.

### Personas et équipe

- édition des 12 emplacements de Personas de Joker ;
- niveaux, statistiques, compétences et traits ;
- synchronisation automatique niveau/EXP ;
- choix des évolutions de Personas des membres de l’équipe ;
- détection des personnages qui n’ont pas encore rejoint le groupe.

### Compendium

- édition individuelle des inscriptions ;
- déverrouillage complet conforme aux sauvegardes PC vérifiées ;
- synchronisation du masque principal et de sa copie miroir ;
- protection contre les entrées mortes ou incompatibles.

### Inventaire

- armes de mêlée et à distance ;
- protections et accessoires ;
- consommables et outils d’infiltration ;
- cartes de compétences ;
- trésors, matériaux et objets clés ;
- recherche globale, filtres, quantités et révision des changements avant
  écriture.

Les costumes restent volontairement en lecture seule tant que leur écriture
n’est pas suffisamment vérifiée par comparaison de sauvegardes.

## Sécurité des sauvegardes

Change of Heart modifie des données binaires chiffrées. Les protections
suivantes sont intégrées :

- sauvegarde ZIP automatique avant chaque écriture ;
- conservation d’une copie initiale immuable ;
- écriture synchronisée des zones principale et miroir ;
- recalcul des CRC et réapplication du chiffrement ;
- refus d’écrire si Persona 5 Royal est détecté en cours d’exécution ;
- avertissement lorsqu’une même sauvegarde est ouverte dans plusieurs fenêtres ;
- validation des quantités, niveaux, identifiants et structures connues.

Conservez malgré tout une copie externe de vos sauvegardes importantes et
désactivez temporairement la synchronisation Steam Cloud pendant une opération
sensible.

## Architecture

```text
Change of Heart.app (Mach-O arm64)
        │
        ├── Cocoa / WebKit — fenêtre macOS
        │
        ├── serveur HTTP local — 127.0.0.1, port éphémère
        │
        ├── interface HTML / CSS / JavaScript
        │
        └── moteur Python
              ├── lecture et écriture des structures P5R
              ├── AES-256-CBC
              ├── CRC32
              ├── backups
              └── contrôles d’intégrité
```

Le serveur n’écoute jamais sur le réseau local. Les fichiers de sauvegarde ne
sont envoyés vers aucun service distant.

## Développement

Installation manuelle :

```bash
/opt/homebrew/bin/python3 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r requirements-build.txt
.venv-macos/bin/python main.py
```

Tests :

```bash
.venv-macos/bin/python -m unittest discover -s tests
.venv-macos/bin/python scripts/check-invariants.py
npm run lint:context
```

Build PyInstaller direct :

```bash
DEVELOPER_DIR=/Library/Developer/CommandLineTools \
  .venv-macos/bin/python -m PyInstaller \
  P5R_Save_Editor.spec --noconfirm --clean --distpath dist
```

## Limites actuelles

- le bundle actuellement produit est Apple Silicon uniquement ;
- Intel `x86_64` et `universal2` ne sont pas encore testés ;
- la signature publique Developer ID et la notarisation Apple restent à faire ;
- l’éditeur cible le format de sauvegarde PC/Steam de Persona 5 Royal, pas les
  sauvegardes PlayStation ;
- certaines données d’histoire complexes restent volontairement non modifiables
  lorsqu’aucun mapping suffisamment sûr n’est disponible.

## Projet original et crédits

Le moteur de Change of Heart est issu du projet communautaire créé par
**j0nny DiGITAL**, avec des travaux de rétro-ingénierie et de validation menés
avec Hermes Agent et Antigravity. Cette variante ajoute le packaging, le moteur
de fenêtre et la détection de sauvegardes nécessaires à macOS.

Persona 5 Royal est une marque d’ATLUS et SEGA. Ce projet communautaire n’est ni
affilié à ATLUS/SEGA, ni approuvé par eux.

## Licence

Le projet est distribué sous licence [MIT](LICENSE).
