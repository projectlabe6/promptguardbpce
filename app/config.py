import json
from pathlib import Path
from typing import Any, Dict, List, cast

# Cache module-level : évite de relire le disque à chaque requête.
_SETTINGS_CACHE: Dict[str, Any] | None = None


def _settings_path() -> Path:
    # Remonte de app/config/ → app/ → settings.json, indépendamment du cwd.
    return Path(__file__).resolve().parent.parent / "settings.json"


def load_settings(force_reload: bool = False) -> Dict[str, Any]:
    # Retourne le cache sauf si force_reload=True (utilisé après update_weights).
    global _SETTINGS_CACHE
    if _SETTINGS_CACHE is not None and not force_reload:
        return _SETTINGS_CACHE

    path = _settings_path()
    if not path.exists():
        raise FileNotFoundError(f"settings.json introuvable : {path}")

    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("settings.json doit contenir un objet JSON à la racine")

    # cast() informe mypy du type — sans effet à l'exécution.
    _SETTINGS_CACHE = cast(Dict[str, Any], raw)
    return _SETTINGS_CACHE


def save_settings(settings: Dict[str, Any]) -> None:
    # Écrase settings.json sur disque — ensure_ascii=False préserve les accents.
    path = _settings_path()
    path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_rule_patterns() -> List[Dict[str, str]]:
    # rules.patterns : liste des regex configurables
    s = load_settings()
    return cast(List[Dict[str, str]], s.get("rules", {}).get("patterns", []))


def get_weights() -> Dict[str, float]:
    # risk.weights : poids par type d'entité, utilisés par le decision_engine.
    s = load_settings()
    return cast(Dict[str, float], s.get("risk", {}).get("weights", {}))


def get_thresholds() -> Dict[str, float]:
    # risk.thresholds : seuils ALLOW / MASK / BLOCK, défaut allow=0.20 mask=0.85.
    s = load_settings()
    return cast(
        Dict[str, float],
        s.get("risk", {}).get("thresholds", {"allow": 0.20, "mask": 0.85}),
    )


def get_placeholders() -> Dict[str, str]:
    # masking.placeholders : mapping type → placeholder ex. {"EMAIL": "[EMAIL]"}.
    s = load_settings()
    return cast(Dict[str, str], s.get("masking", {}).get("placeholders", {}))


def get_block_message() -> str:
    # masking.block_message : texte retourné à la place du contenu bloqué.
    s = load_settings()
    return str(s.get("masking", {}).get("block_message", "[BLOCKED]"))


def audit_enabled() -> bool:
    # audit.enabled : active la journalisation, True par défaut.
    s = load_settings()
    return bool(s.get("audit", {}).get("enabled", True))


def audit_file_path() -> str:
    # audit.file_path : chemin du fichier de log JSON.
    s = load_settings()
    return str(s.get("audit", {}).get("file_path", "logs/audit.log"))


def update_weights(weights: Dict[str, float]) -> None:
    # Fusionne les nouveaux poids, persiste sur disque, invalide le cache (US-11).
    s = load_settings()
    s.setdefault("risk", {}).setdefault("weights", {}).update(weights)
    save_settings(s)
    load_settings(force_reload=True)
