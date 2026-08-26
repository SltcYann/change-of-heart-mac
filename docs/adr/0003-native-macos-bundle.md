# ADR 0003 — Bundle macOS natif avec Cocoa/WebKit

- Statut : **Accepté** — 2026-08-26
- Parties prenantes : utilisateur macOS, mainteneur de Change of Heart.
- Minimum releasable maintenant : une application `.app` Apple Silicon autonome,
  sans Python installé chez l'utilisateur, qui conserve le moteur de sauvegarde
  déjà testé et ouvre l'interface dans une fenêtre Cocoa/WebKit.
- Données de jeu : aucun offset, segment ou stride `ITEM.TBL` n'est modifié par
  cette décision ; les invariants existants restent inchangés.

## Options considérées

1. **Bundle PyInstaller + PyWebView Cocoa/WebKit (retenu).** Produit un exécutable
   Mach-O dans un bundle macOS standard, réutilise le backend et les tests actuels,
   et remplace le moteur WebView2 propre à Windows par le WebKit fourni par macOS.
2. **Coque SwiftUI qui lance le backend Python embarqué.** Offre davantage de code
   AppKit/SwiftUI, mais ajoute deux cycles de vie et une passerelle IPC sans supprimer
   Python du paquet.
3. **Réécriture complète en Swift.** C'est le résultat le plus strictement natif,
   mais il faudrait reporter puis revalider toute la cryptographie, les offsets et
   les 174 garde-fous avant de pouvoir livrer une première version fiable.

## Décision

Livrer l'option 1 comme première version macOS. Le bundle utilise Cocoa/WebKit,
embarque Python et toutes ses dépendances, choisit automatiquement le backend GUI
selon la plateforme et garde le navigateur comme solution de secours.

Le build cible l'architecture du Python qui le produit (`arm64` sur Apple Silicon,
`x86_64` sur Mac Intel). Un build `universal2` pourra être ajouté plus tard avec une
distribution Python et des roues tierces elles-mêmes universelles.

## Conséquences et validation

- `P5R_Save_Editor.spec` produit `Change of Heart.app` sur macOS et conserve le
  `.exe` actuel sur Windows.
- Les dépendances CLR restent exclusivement Windows ; PyObjC/WebKit est installé
  exclusivement sur macOS.
- Le script `Build_macOS.command` crée un environnement isolé, lance les tests puis
  fabrique le bundle.
- Gate : tests unitaires, vérification des invariants, lancement du Mach-O contenu
  dans le bundle et réponse HTTP de `/api/build`.

