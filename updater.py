import requests
import os
import zipfile
import io
import json

# Repositorio GitHub (reemplaza si cambias de repo)
REPO_URL = "https://api.github.com/repos/mrgonzalo/perplexity/releases/latest"
LOCAL_VERSION_FILE = "config/version.json"

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0.0"
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except:
        return "0.0.0"

def save_local_version(version):
    os.makedirs(os.path.dirname(LOCAL_VERSION_FILE), exist_ok=True)
    with open(LOCAL_VERSION_FILE, "w") as f:
        json.dump({"version": version}, f, indent=2)

def version_mayor(v1, v2):
    return [int(x) for x in v1.split(".")] > [int(x) for x in v2.split(".")]

def check_for_update():
    print("🔎 Buscando actualización...")
    try:
        response = requests.get(REPO_URL, timeout=10)
        response.raise_for_status()
        release = response.json()

        latest_version = release["tag_name"].lstrip("v")
        local_version = get_local_version()

        if version_mayor(latest_version, local_version):
            print(f"⬆️ Actualización disponible: {latest_version} (local: {local_version})")
            zip_url = release["zipball_url"]
            apply_update(zip_url, latest_version)
        else:
            print("✅ Ya estás en la última versión.")
    except Exception as e:
        print(f"❌ Error al buscar actualización: {e}")

def apply_update(zip_url, version):
    print("📥 Descargando y aplicando actualización...")
    try:
        response = requests.get(zip_url, timeout=30)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for member in z.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue
                with z.open(member) as source, open(filename, "wb") as target:
                    target.write(source.read())
        save_local_version(version)
        print("✅ Actualización completada.")
    except Exception as e:
        print(f"❌ Falló la actualización: {e}")

if __name__ == "__main__":
    check_for_update()
