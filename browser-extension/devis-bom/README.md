# devis-bom — extension navigateur

Capture le prix affiché sur une page produit d'un magasin en ligne et l'associe à une ligne
du BOM géré par l'app `devis_bom` (voir `../../src/devis_bom`). Couvre BOM-UI-EXTENSION-001.

## Installation (mode développeur)

1. Démarrer l'API locale (depuis la racine du repo) :
   ```
   uv run uvicorn devis_bom.api.app:app --port 8001
   ```
2. Dans Chrome/Edge/Brave : `chrome://extensions` → activer le *mode développeur* → *Charger
   l'extension non empaquetée* → sélectionner ce dossier (`browser-extension/devis-bom`).
3. Ouvrir `http://localhost:8001` et ajouter au moins une ligne au BOM.

## Utilisation

1. Aller sur la fiche produit chez un distributeur (ex: Rexel, CGE Distribution, Bricozor,
   Manomano, Amazon...).
2. Cliquer sur l'icône de l'extension. Le prix est pré-rempli si détecté sur la page (sinon
   à saisir manuellement), ainsi que le magasin (nom de domaine, éditable).
3. Choisir la ligne du BOM correspondante et cliquer *Capturer*.

## Configuration

Le bouton *Options* du popup permet de changer l'URL de l'API (par défaut
`http://localhost:8001`), si l'app tourne sur un autre port ou une autre machine du réseau
local.

## Limites connues (V1)

- L'extraction automatique du prix repose sur des sélecteurs génériques (`[itemprop="price"]`,
  `.price`, motif `12,34 €`...) : elle échoue sur certains sites, d'où la saisie manuelle en
  secours.
- Pas de correspondance automatique référence → page produit : la ligne du BOM est choisie
  manuellement dans le popup.
