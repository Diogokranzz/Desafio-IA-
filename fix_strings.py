import os
import re


def corrigir_f_strings_em_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
        linhas = f.readlines()

    alterado = False
    novas_linhas = []

    for linha in linhas:
        nova_linha = linha

        # Corrige prints quebrados com "f no final errado
        nova_linha = re.sub(r'(f"[^"\n{]*\{[^}]+\})f\)', r'\1")', nova_linha)

        # Corrige strings sem fechar aspas
        if (
            nova_linha.strip().startswith("print(f")
            and nova_linha.strip().count('"') == 1
        ):
            nova_linha = nova_linha.rstrip() + '")\n'

        if nova_linha != linha:
            alterado = True
        novas_linhas.append(nova_linha)

    if alterado:
        print(f"[Corrigido] {caminho_arquivo}")
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.writelines(novas_linhas)


def encontrar_arquivos_python(raiz="."):
    arquivos = []
    for root, dirs, files in os.walk(raiz):
        for file in files:
            if file.endswith(".py"):
                arquivos.append(os.path.join(root, file))
    return arquivos


if __name__ == "__main__":
    arquivos_py = encontrar_arquivos_python()
    for arquivo in arquivos_py:
        corrigir_f_strings_em_arquivo(arquivo)

    print("\n✅ Correção automática finalizada. Agora execute:")
    print("   pre-commit run --all-files\n")
