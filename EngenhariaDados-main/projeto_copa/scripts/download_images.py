import os
import sys
import time
import random
import pandas as pd
import requests
from urllib.parse import urlparse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
]

def baixar_imagem(url, caminho_arquivo):
    tentativas = 5

    for tentativa in range(tentativas):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS)
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                stream=True
            )

            # Sucesso
            if response.status_code == 200:
                with open(caminho_arquivo, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                return True

            # Rate limit
            elif response.status_code == 429:
                espera = (tentativa + 1) * 10
                print(f"HTTP 429, aguardando {espera}s...")
                time.sleep(espera)

            else:
                print(f"Erro HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(5)

    return False

def baixar_imagens(csv_path, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)

    df = pd.read_csv(csv_path)

    if "foto_url" not in df.columns:
        print("Coluna 'foto_url' não encontrada.")
        return

    total = len(df)

    for i, url in enumerate(df["foto_url"]):
        if pd.isna(url):
            continue

        url = str(url).strip()

        parsed = urlparse(url)
        extensao = os.path.splitext(parsed.path)[1]

        if extensao == "":
            extensao = ".jpg"

        nome_arquivo = f"imagem_{i+1}{extensao}"
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

        print(f"[{i+1}/{total}] Baixando...")

        sucesso = baixar_imagem(url, caminho_arquivo)

        if sucesso:
            print(f"OK: {nome_arquivo}")
        else:
            print(f"Falhou: {url}")

        # Pausa aleatória entre downloads
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso:")
        print("python baixar_imagens.py arquivo.csv pasta_destino")
        sys.exit(1)

    csv_path = sys.argv[1]
    pasta_destino = sys.argv[2]

    baixar_imagens(csv_path, pasta_destino)