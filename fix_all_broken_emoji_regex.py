import os
import re

# Regex completa segura
regex_nova = '''re.compile(
    r"[\\U0001F600-\\U0001F64F"
    r"\\U0001F300-\\U0001F5FF"
    r"\\U0001F680-\\U0001F6FF"
    r"\\U0001F1E0-\\U0001F1FF]+",
    flags=re.UNICODE
)'''

# Verifica se o conteúdo parece conter regex fragmentada
def contem_regex_quebrada(texto):
    return (
        "U0001F600" in texto or
        "U0001F300" in texto or
        "U0001F680" in texto or
        "U0001F1E0" in texto
    ) and "re.compile" not in texto[: texto.find("U0001F")]

def corrigir_regex_emojis_em_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
        conteudo = f.read()

    if contem_regex_quebrada(conteudo):
        # Remove blocos quebrados da regex
        novo_conteudo = re.sub(
            r'r"\\U0001F600.*?(?=\n)', "", conteudo, flags=re.DOTALL
        )
        # Substitui pela nova regex limpa
        novo_conteudo = regex_nova + "\n" + novo_conteudo

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(novo_conteudo)

        print(f"[Corrigido] {caminho_arquivo}")
    else:
        print(f"[Ignorado]  {caminho_arquivo} (sem regex quebrada)")

# Caminho base
diretorio_base = "scripts"

for root, _, files in os.walk(diretorio_base):
    for nome_arquivo in files:
        if nome_arquivo == "strip_comments_and_emojis.py":
            caminho = os.path.join(root, nome_arquivo)
            corrigir_regex_emojis_em_arquivo(caminho)
