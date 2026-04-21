

# Conventions de développement

## Outils requis

| Outil | Version | Rôle |
|---|---|---|
| `pytest` | 8.3.2 | Framework de tests |
| `pytest-asyncio` | 0.24.0 | Support des tests async |
| `httpx` | 0.27.0 | Client HTTP pour les tests d'API |
| `mypy` | 1.11.2 | Vérification statique des types |
| `ruff` | 0.6.9 | Linting et formatage du code |
| `pre-commit` | 3.8.0 | Hooks automatiques avant chaque commit |

Installation :

```bash
pip install -r requirements-dev.txt
pre-commit install
```

---

## Formatage — ruff

Ruff formate et lint le code automatiquement.

**Règles actives :**
- `E` — erreurs de style PEP8
- `F` — erreurs logiques (imports inutilisés, variables non définies)
- `I` — ordre des imports (stdlib → third-party → local)

**Longueur de ligne max : 88 caractères**

Commandes :

```bash
ruff check app/          # détecte les problèmes
ruff check app/ --fix    # corrige automatiquement
ruff format app/         # formate le code
```

---

## Typage — mypy

Tout le code dans `app/` doit être typé. Mypy vérifie les types statiquement avant l'exécution.

**Règles actives :**
- `warn_return_any` — interdit les retours implicites `Any`
- `warn_unused_ignores` — interdit les `# type: ignore` inutiles
- `ignore_missing_imports` — ignore les libs sans stubs de types (ex: gliner)


## Pre-commit hooks

Les hooks s'exécutent automatiquement à chaque `git commit`.

**Hooks actifs :**

| Hook | Action |
|---|---|
| `ruff` | Lint + fix automatique |
| `ruff-format` | Formatage automatique |
| `mypy` | Vérification des types sur `app/` |
| `trailing-whitespace` | Supprime les espaces en fin de ligne |
| `end-of-file-fixer` | Ajoute une ligne vide en fin de fichier |
| `check-merge-conflict` | Bloque si un conflit git n'est pas résolu |
| `check-json` | Valide la syntaxe des fichiers JSON |
| `check-toml` | Valide la syntaxe des fichiers TOML |

Si un hook échoue, le commit est bloqué. Corrige le problème puis recommence.

---

## Branches et commits

**Stratégie de branches :**

```
main       ← production stable
develop    ← intégration
feature/   ← une branche par fonctionnalité
hotfix/    ← correction urgente sur main
```

**Convention de commit (Conventional Commits) :**

```
feat:     nouvelle fonctionnalité
fix:      correction de bug
chore:    tâche technique (config, deps, scaffold)
refactor: refactoring sans changement de comportement
test:     ajout ou modification de tests
docs:     documentation uniquement
```


---

## Politique de secrets

- Ne jamais commiter de credentials, tokens, clés API ou mots de passe
- Toute valeur sensible va dans `.env` (jamais dans le repo)
- `.env.example` est le seul fichier d'environnement commité — sans vraies valeurs
- En cas de commit accidentel d'un secret : changer la valeur immédiatement + contacter le tech lead
- Les modèles ML (dossier `models/`) ne sont pas versionnés (trop lourds + pas de credentials)
