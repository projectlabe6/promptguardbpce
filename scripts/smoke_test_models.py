from gliner import GLiNER

print("Chargement du modèle médical...")
model = GLiNER.from_pretrained(
    "models/camembert-bio-gliner-v0.1",
    local_files_only=True,
)

print("Test de prédiction...")
entities = model.predict_entities(
    "Le patient Jean Dupont souffre de diabète.",
    ["Patient", "Maladie"],
    threshold=0.5,
)

print(f"Entités détectées : {entities}")
print("Smoke test OK.")
