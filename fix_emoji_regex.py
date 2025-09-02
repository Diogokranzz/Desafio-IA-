import os

# Bloco novo corretamente escapado (em texto puro)
NOVO_PADRAO = """emoji_pattern = re.compile(
    r"["
    r"\\U0001F600-\\U0001F64F"  # emoticons
    r"\\U0001F300-\\U0001F5FF"  # symbols & pictographs
    r"\\U0001F680-\\U0001F6FF"  # transport & map
    r"\\U0001F1E0-\\U0001F1FF"  # flags
    r"\\u2600-\\u26FF"          # misc
    r"\\u2700-\\u27BF"          # dingbats
    r"\\U000024C2-\\U0001F251"  # enclosed
    r"]+",
    flags=re.UNICODE,
)
"""


def corrigir_bloco_em_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()

        if "emoji_pattern = re.compile" in conteudo and (
            "\\U" in conteudo or "\\u" in conteudo or r"\U" in conteudo
        ):

            # Aplica substituição *cega* entre a linha que começa com "emoji_pattern = re.compile"
            # e a linha que contém "flags=re.UNICODE"
            linhas = conteudo.splitlines()
            inicio, fim = None, None

            for i, linha in enumerate(linhas):
                if "emoji_pattern = re.compile" in linha:
                    inicio = i
                if inicio is not None and "flags=re.UNICODE" in linha:
                    fim = i
                    break

            if inicio is not None and fim is not None:
                print(f"[Corrigido] {caminho}")
                novas_linhas = (
                    linhas[:inicio]
                    + [linha_nova for linha_nova in NOVO_PADRAO.splitlines()]
                    + linhas[fim + 1 :]
                )
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write("\n".join(novas_linhas) + "\n")
            else:
                print(f"[Ignorado] {caminho} (bloco incompleto)")
        else:
            print(f"[Ignorado] {caminho} (padrão não encontrado ou já corrigido)")
    except Exception as e:
        print(f"[Erro] {caminho}: {e}")


def procurar_e_corrigir():
    for dirpath, _, arquivos in os.walk("."):
        for arquivo in arquivos:
            if arquivo == "strip_comments_and_emojis.py":
                caminho = os.path.join(dirpath, arquivo)
                corrigir_bloco_em_arquivo(caminho)


if __name__ == "__main__":
    procurar_e_corrigir()
