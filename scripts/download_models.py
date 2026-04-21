from huggingface_hub import snapshot_download

print("Téléchargement de camembert-bio-base...")
snapshot_download(
    repo_id="almanach/camembert-bio-base",
    local_dir="models/camembert-bio-base",
)

print("Téléchargement de camembert-bio-gliner-v0.1...")
snapshot_download(
    repo_id="urchade/gliner_multi-v2.1",
    local_dir="models/camembert-bio-gliner-v0.1",
)

print("Téléchargement de camembert-ner...")
snapshot_download(
    repo_id="Jean-Baptiste/camembert-ner",
    local_dir="models/camembert-ner",
)

print("Modèles téléchargés.")
