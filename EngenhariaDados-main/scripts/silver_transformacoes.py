import os
import pandas as pd
import gcsfs

def processar_dados_gcs(bucket_name, chave_json, formato_entrada, caminho_particionado,
                        limpar_colunas, pasta_saida_local, grupos, particionado=False):
    # Autentica no GCS
    fs = gcsfs.GCSFileSystem(token=chave_json)

    # Lista arquivos no bucket
    if particionado:
        arquivos = fs.glob(f'{bucket_name}/{caminho_particionado}*.{formato_entrada}')
    else:
        arquivos = [f'{bucket_name}/{caminho_particionado}.{formato_entrada}']

    for caminho_completo in arquivos:
        print(f'Processando {caminho_completo}...')
        nome_base = os.path.splitext(os.path.basename(caminho_completo))[0]

        # Lê o Parquet diretamente do GCS
        with fs.open(caminho_completo, 'rb') as f:
            df = pd.read_parquet(f)

        # Remove colunas que o usuário quer limpar
        for col in limpar_colunas:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)

        # Para cada grupo de colunas, cria um arquivo separado
        for grupo, colunas in grupos.items():
            colunas_existentes = [col for col in colunas if col in df.columns]
            if not colunas_existentes:
                continue

            df_subset = df[colunas_existentes]

            caminho_saida = f"{bucket_name}/{pasta_saida_local}/{grupo}/{nome_base}_{grupo}.parquet"
            print(f'Salvando arquivo {caminho_saida}...')

            # Salva diretamente no GCS
            with fs.open(caminho_saida, 'wb') as f_out:
                df_subset.to_parquet(f_out, index=False)

    print("Processamento finalizado.")

if __name__ == "__main__":
    # Configurações
    bucket_name = 'ifnmg-enem'
    chave_json = 'chave/fine-slice-304523-378cca0bed61.json'

    # Parâmetros para dados particionados
    formato_entrada = 'parquet'
    caminho_particionado = 'bronze/parquet/MICRODADOS_ENEM_2023_chunk_'
    
    #******************Transformaçoes*********************************
    # Adicione suas transformacoes aqui
    remover_colunas = ['coluna1', 'coluna2', 'coluna3']

    # Definição dos grupos de dados
    # Exemplos possíveis
    grupos_dados = {
        "participante": [
            "NU_INSCRICAO", "NU_ANO", "TP_FAIXA_ETARIA", "TP_SEXO"
        ],
        "escola": [
            "NU_INSCRICAO", "CO_MUNICIPIO_ESC"
        ],
    }

    # Executa o processamento
    processar_dados_gcs(
        bucket_name=bucket_name,
        chave_json=chave_json,
        formato_entrada=formato_entrada,
        caminho_particionado=caminho_particionado,
        limpar_colunas=remover_colunas,
        pasta_saida_local='silver/parquet',
        grupos=grupos_dados,
        particionado=True
    )
