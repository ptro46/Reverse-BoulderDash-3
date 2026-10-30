# Boulder Dash III — Amstrad CPC → Rust / Mac

Première version jouable native, réalisée à partir du disque `BoulderDash3.dsk` fourni. Le projet utilise Rust et Macroquad. Le jeu embarque ses ressources : aucun émulateur, ROM CPC ni fichier externe n'est nécessaire pour lancer l'application compilée.

## Jouer sur Mac

Ouvrir `build/Boulder Dash III.app`, ou décompresser l'archive Mac puis ouvrir l'application. La version livrée est compilée pour **Mac Apple Silicon (arm64), macOS 11 ou ultérieur**. Elle utilise Metal et une signature locale ad hoc, sans notarisation Apple.

- Entrée ou Espace sur l'écran original : accéder au choix des grottes.
- Menu : gauche/droite pour choisir une grotte, haut/bas pour la difficulté, Entrée pour démarrer. Les boutons sont aussi cliquables.
- Flèches, WASD ou ZQSD : déplacement.
- Majuscule + direction : creuser ou ramasser sans avancer.
- Espace : pause/reprise ; Tabulation : vue d'ensemble ou caméra rapprochée.
- R : recommencer ; Entrée après un succès ou une mort : continuer.
- Échap : retour au menu ; Échap au menu : quitter.
- M : couper/remettre le son ; F : plein écran.

Collecter le nombre demandé de diamants puis rejoindre la sortie. Les graphismes de ce volet ont un thème spatial : les diamants et rochers utilisent leurs représentations du disque. Les 16 grottes A–P et 4 intermèdes sont accessibles, chacun sur 5 difficultés. L'ordre de progression intercale un intermède après chaque groupe de quatre grottes.

## Ressources extraites

`Extracted/` contient les quatre fichiers AMSDOS, leurs fichiers avec en-tête, l'image mémoire initiale et l'image relogée. Le disque original est conservé sans modification. Son SHA-256 est :

`4b6b863a9fab9a924809b7cb799b416ca82293db734a70e0fbbf8433433f3622`

- `assets/sprites.png` : atlas de 64 tuiles et 17 poses du personnage, avec une ligne de palette par grotte (20 lignes).
- `assets/graphics-bank.bin` et `.png` : banque graphique, animations et caractères de la mémoire CPC, plage `0x2c00..0x5daf`.
- `assets/caves.bin` : 100 cartes de 40 × 22 cases ; `caves.json` : objectifs, temps, valeurs et palettes ; `caves-contact.png` : planche des 20 cartes en difficulté 1.
- `assets/loading.png` et `loading-screen.bin` : écran original de présentation, décompressé depuis `DASHIII.ECR`. Palette issue de `DASHIII.PAR`, mode CPC 0. Le décodeur consomme exactement les 6 993 octets du fichier.
- `assets/title.wav` : séquence musicale de 40,96 secondes ; `step`, `dig`, `diamond`, `rock`, `death`, `amoeba` : six effets WAV de 1,2 seconde.
- Les fichiers `*.ay.json` conservent les états des 16 registres AY à 50 Hz ; `audio-manifest.json` décrit la méthode. Les WAV sont des rendus numériques de ces états, pas des enregistrements audio stockés dans le DSK.
- `assets/manifest.json` et `Extracted/manifest.json` : provenance et empreintes des fichiers.
- `Notes/linear.asm` : désassemblage linéaire de référence ; il inclut aussi des données et ne constitue pas une analyse complète de chaque instruction.

L'extraction exécute hors ligne les routines Z80 originales pour reconstruire les cartes, palettes et séquences AY. La mémoire graphique et les cartes viennent de **ce disque III**. Les outils d'extraction et la base du moteur Rust sont adaptés du projet Boulder Dash antérieur. La comparaison des fichiers confirme que le bloc de code relogé `0x0200..0x2bff` est identique, alors que plusieurs banques graphiques et les cartes changent. Les cartes extraites diffèrent de celles du premier volet sur 31 961 cases parmi les 88 000.

## Compiler

Avec un Rust récent prenant en charge l'édition 2024 :

```bash
cd /Users/ptro/Projets/BoulderDash3
cargo run --release --locked
./build-app.sh
```

`build-app.sh` crée et signe localement l'application Mac. Toutes les ressources sont embarquées par `include_bytes!` / `include_str!`.

Le code Rust/Macroquad permet de cibler d'autres machines avec `cargo build --release --locked` sur le système concerné. Les versions Windows, Linux et Mac Intel n'ont pas été compilées ni vérifiées ici. Les bibliothèques système audio et graphiques peuvent être nécessaires sur ces plateformes. Le script `.app` est spécifique à macOS.

## Reproduire l'extraction

Les ressources déjà fournies permettent de compiler sans Python. Pour régénérer l'ensemble depuis le DSK :

```bash
python3 -m venv .venv
.venv/bin/pip install -r Tools/requirements.txt
PYTHON=.venv/bin/python Tools/extract_all.sh
```

Le désassembleur est facultatif : `.venv/bin/python Tools/disassemble.py`.

## Validation et limites

Huit tests Rust couvrent les cartes, entrées/sorties en bordure, chutes de rochers, collecte sans mouvement, explosions, mur magique et simulations prolongées. `cargo clippy --locked -- -D warnings` passe. L'outil `Tools/validate_assets.py` vérifie les empreintes du disque et des fichiers, les 100 cartes, leurs entrées/sorties/bordures et les sept WAV non silencieux. Le lancement graphique Mac, la présentation originale, le menu et l'affichage d'une partie ont été vérifiés visuellement.

Cette version reste une **réimplémentation jouable**, avec une physique approchée. Les probabilités de poussée et de croissance, la vitesse, l'ordre des mises à jour, les scores et vies, et certains rythmes d'animation ne sont pas certifiés conformes au Z80. La campagne entière n'a pas été terminée manuellement. Le système de vies permet de reprendre une session après trois pertes ; il ne reproduit pas encore exactement les fins de partie et vies supplémentaires du CPC. Les noms des grottes sont des identifiants A–P, sans réutiliser les noms du premier volet.

Le rendu sonore utilise des ondes carrées et un bruit pseudo-aléatoire 17 bits : filtre analogique et enveloppe matérielle ne sont pas reproduits. Les effets de collecte et de mort sont isolés avec un état initial explicite ; l'amibe est déclenchée périodiquement dans le moteur natif. L'association des sons aux événements natifs et leur synchronisation restent approchées.

Les droits sur les éléments du jeu original restent à leurs ayants droit ; l'archive est préparée à partir du disque fourni pour cet usage local.
