from pathlib import Path

LIBRARY_ROOT = Path(r"/mnt/hdmenezess42/TomeHold/")

IGNORAR_PASTAS = {
    "2bSorted",
    "Papers"
}

# True  = apenas mostra o que será feito
# False = realmente renomeia os arquivos
DRY_RUN = True


def nome_corrigido(nome: str) -> str:
    """Remove < e > do nome."""
    return nome.replace("<", "").replace(">", "")


def deve_ignorar(path: Path) -> bool:
    """Retorna True se o caminho estiver dentro de uma pasta ignorada."""
    return any(parente.name in IGNORAR_PASTAS for parente in path.parents)


def main():
    if not LIBRARY_ROOT.is_dir():
        print(f"Pasta não encontrada: {LIBRARY_ROOT}")
        return

    encontrados = 0
    renomeados = 0
    conflitos = 0
    erros = 0

    print(f"Pasta analisada: {LIBRARY_ROOT}")
    print(f"Modo simulação:  {'ATIVADO' if DRY_RUN else 'DESATIVADO'}")
    print("-" * 80)

    for path in LIBRARY_ROOT.rglob("*"):

        if deve_ignorar(path):
            continue

        if not path.is_file():
            continue

        if "<" not in path.name and ">" not in path.name:
            continue

        encontrados += 1

        corrigido = nome_corrigido(path.name)
        novo_path = path.parent / corrigido

        print(f"ERRADO:    {path.name}")
        print(f"CORRIGIDO: {corrigido}")
        print(f"CAMINHO:   {path.parent}")

        if novo_path == path:
            print("STATUS:    Nenhuma alteração necessária")
            print()
            continue

        if novo_path.exists():
            print("STATUS:    CONFLITO - o nome corrigido já existe")
            print(f"EXISTENTE: {novo_path}")
            conflitos += 1
            print()
            continue

        if DRY_RUN:
            print("STATUS:    SERIA RENOMEADO")
            print()
            continue

        try:
            path.rename(novo_path)
            print("STATUS:    RENOMEADO COM SUCESSO")
            renomeados += 1

        except OSError as e:
            print(f"STATUS:    ERRO AO RENOMEAR: {e}")
            erros += 1

        print()

    print("-" * 80)
    print("RESUMO")
    print("-" * 80)
    print(f"Arquivos encontrados: {encontrados}")
    print(f"Arquivos renomeados:  {renomeados}")
    print(f"Conflitos:            {conflitos}")
    print(f"Erros:                {erros}")

    if DRY_RUN:
        print()
        print("SIMULAÇÃO FINALIZADA.")
        print("Nenhum arquivo foi alterado.")
        print("Se os resultados estiverem corretos, altere:")
        print("    DRY_RUN = True")
        print("para:")
        print("    DRY_RUN = False")


if __name__ == "__main__":
    main()
