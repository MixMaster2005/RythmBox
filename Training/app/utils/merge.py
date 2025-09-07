import csv
import os

METADATA_CSV = "metadata.csv"
FEATURES_CSV = "audio_features.csv"
OUTPUT_CSV = "merged_data.csv"

def normalize_filename(path):
    # Extrait juste le nom de fichier sans dossier ni extension différente
    # ici on enlève le dossier et garde le nom sans dossier, avec extension
    return os.path.basename(path).lower()

def read_csv_to_dict(file_path, key_func):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            key = key_func(row['file'])
            data[key] = row
        return data

def merge_dicts(d1, d2):
    # Combine deux dicts, d1 prioritaire sur certaines clés, d2 apporte les features
    merged = d1.copy()
    for k,v in d2.items():
        if k not in merged:
            merged[k] = v
        else:
            # Ajouter les clés de d2 qui ne sont pas dans d1
            for key, val in v.items():
                if key != 'file' and key not in merged:
                    merged[key] = val
    return merged

def main():
    metadata = read_csv_to_dict(METADATA_CSV, normalize_filename)
    features = read_csv_to_dict(FEATURES_CSV, normalize_filename)

    # Champs CSV de sortie
    # On prend toutes les colonnes de metadata + celles des features sauf 'file'
    metadata_fields = list(next(iter(metadata.values())).keys())
    features_fields = list(next(iter(features.values())).keys())
    features_fields.remove('file')

    all_fields = metadata_fields + features_fields

    merged_rows = []

    for key in set(metadata.keys()) | set(features.keys()):
        meta_row = metadata.get(key, {})
        feat_row = features.get(key, {})

        # Fusion simple : priorité metadata + features ajoutées
        merged = meta_row.copy()
        for fkey in features_fields:
            merged[fkey] = feat_row.get(fkey, '')

        # Assurer la présence du champ 'file' (prendre metadata ou features)
        merged['file'] = meta_row.get('file') or feat_row.get('file') or key

        merged_rows.append(merged)

    # Sauvegarde du CSV fusionné
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"Fusion terminée. Résultat dans {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
