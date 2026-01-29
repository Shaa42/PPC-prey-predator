# PPC-prey-predator

Projet Python - Simulation Proie-Prédateur

Ce projet implémente une simulation simple d'un écosystème proie-prédateur en utilisant Python. Chaque agents (proie ou prédateur) sont des processus indépendant qui interagissent avec l'environnement qui agit comme serveur et mémoire partagée.

## Pré-requis
- Python 3.10+

### Installation
```sh
git clone https://github.com/Shaa42/PPC-prey-predator.git
cd PPC-prey-predator
```

Création d'un environnement virtuel (optionnel) :
```sh
python -m venv venv
source venv/bin/activate    # Sur Linux/Mac
venv\Scripts\activate       # Sur Windows
```

Lancement du projet :
```sh
python main.py
```

## Architecture

```
.
├── color.py            # Affiche avec des couleurs dans le terminal
├── constants.py        # Constantes utilisées dans le projet
├── display.py          # Affichage de l'état de l'environnement
├── environment.py      # Gestion de l'environnement (serveur)
├── main.py             # Point d'entrée du programme et gestion des processus
├── predator.py         # Comportement des prédateurs
├── prey.py             # Comportement des proies
├── README.md
```

## Auteurs
Projet réalisé par :
- VIGOUREUX Ryan
- MATSUMOTO Taïga
