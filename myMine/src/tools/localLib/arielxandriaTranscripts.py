"""
Catalog books into the local library
"""

import re
import shutil
import sys
from pathlib import Path

import questionary
from questionary import Style
from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

LIBRARY_ROOT = Path("library/path")

TO_BE_SORTED = "2bSorted"
BACK = "__BACK__"
NEW = "__NEW__"
SAVE_HERE = "__SAVE__"
QUIT = "__QUIT__"
SKIP = "__SKIP__"

console = Console()

M1 = "#415A77"
M2 = "#6C7A89"
N1 = "#E6D5B8"
N2 = "#CFC8B5"
W1 = "#FF6A00"
W2 = "#F05A22"
H1 = "#00D2C3"
H2 = "#48C4F8"

CUSTOM_STYLE = Style(
    [
        ("qmark", f"fg:{H2} bold"),
        ("question", f"fg:{N1} bold"),
        ("answer", f"fg:{H1} bold"),
        ("pointer", f"fg:{W1} bold"),
        ("highlighted", f"fg:{W1} bold"),
        ("selected", f"fg:{H1}"),
        ("separator", f"fg:{M2}"),
        ("instruction", f"fg:{M2}"),
    ]
)


FIELD_SEP = re.compile(r"\s+[-\u2013\u2014]\s+")


EXPECTED_LABELS = ["mainTopic", "subTopic", "título", "autor", "ano", "idioma"]


def parse_filename(filename: str):
    """Extrai title, author, year, lang e ext do nome original do arquivo.

    Espera o padrão:
        <mainTopic> - <subTopic> - <title> - <authorLastName> - <year> - [<lang>].ext

    Retorna (info_dict, parts, ext). `info_dict` é None se não achou pelo
    menos 6 campos — nesse caso `parts` traz os campos brutos encontrados,
    pra montar a tela de diagnóstico.
    """
    stem, ext = Path(filename).stem, Path(filename).suffix
    parts = [p.strip() for p in FIELD_SEP.split(stem)]

    if len(parts) < 6:
        return None, parts, ext

    lang = parts[-1]
    year = parts[-2]
    author = parts[-3]
    title = " - ".join(parts[2:-3])

    info = {
        "title": title,
        "author": author,
        "year": year,
        "lang": lang,
        "ext": ext,
    }
    return info, parts, ext


def build_new_filename(main_topic: str, sub_topic: str, info: dict) -> str:
    return (
        f"{main_topic} - {sub_topic} - {info['title']} - "
        f"{info['author']} - {info['year']} - {info['lang']}{info['ext']}"
    )


def list_dirs(path: Path):
    return sorted(
        [p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )


def list_files(path: Path):
    return sorted(
        [p for p in path.iterdir() if p.is_file() and not p.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )


def ask_new_folder_name() -> str:
    while True:
        name = questionary.text("Nome da nova pasta:", style=CUSTOM_STYLE).ask()
        if name is None:
            return None
        name = name.strip()
        if name:
            return name
        console.print(f"[{W1}]O nome não pode ser vazio.[/{W1}]")


def choose_top_level(root: Path, label: str):
    """Escolhe/cria uma pasta de primeiro nível dentro de `root` (mainTopic)."""
    while True:
        dirs = [d for d in list_dirs(root) if d.name != TO_BE_SORTED]
        choices = [questionary.Choice(f"📁 {d.name}", value=d) for d in dirs]
        choices.append(questionary.Choice("➕ Criar nova pasta...", value=NEW))
        choices.append(questionary.Choice("🚪 Sair do programa", value=QUIT))

        answer = questionary.select(
            f"Selecione o {label}:", choices=choices, style=CUSTOM_STYLE
        ).ask()

        if answer is None or answer == QUIT:
            return QUIT

        if answer == NEW:
            name = ask_new_folder_name()
            if name is None:
                continue
            new_path = root / name
            new_path.mkdir(exist_ok=True)
            console.print(f"[{H1}]✓ Pasta criada:[/{H1}] {new_path}")
            return new_path

        return answer


def choose_sub_level(parent: Path, label: str):
    """Escolhe/cria uma subpasta dentro de `parent` (subTopic)."""
    while True:
        dirs = list_dirs(parent)
        choices = [questionary.Choice(f"📁 {d.name}", value=d) for d in dirs]
        choices.append(questionary.Choice("➕ Criar nova subpasta...", value=NEW))
        choices.append(questionary.Choice("⬅️  Voltar", value=BACK))

        answer = questionary.select(
            f"Selecione o {label} (dentro de '{parent.name}'):",
            choices=choices,
            style=CUSTOM_STYLE,
        ).ask()

        if answer is None or answer == BACK:
            return BACK

        if answer == NEW:
            name = ask_new_folder_name()
            if name is None:
                continue
            new_path = parent / name
            new_path.mkdir(exist_ok=True)
            console.print(f"[{H1}]✓ Pasta criada:[/{H1}] {new_path}")
            return new_path

        return answer


def descend_or_save(start_path: Path) -> Path:
    """A partir de subTopic, deixa navegar em subpastas mais profundas
    até o usuário decidir salvar o livro em algum ponto."""
    current = start_path
    while True:
        subdirs = list_dirs(current)

        choices = [
            questionary.Choice(
                f"💾 Salvar o livro aqui ({current.name})", value=SAVE_HERE
            )
        ]
        for d in subdirs:
            choices.append(questionary.Choice(f"📁 Entrar em: {d.name}", value=d))
        choices.append(questionary.Choice("➕ Criar nova subpasta e entrar", value=NEW))
        if current != start_path:
            choices.append(questionary.Choice("⬆️  Subir um nível", value=BACK))

        answer = questionary.select(
            f"O que fazer em '{current}'?", choices=choices, style=CUSTOM_STYLE
        ).ask()

        if answer is None or answer == SAVE_HERE:
            return current

        if answer == NEW:
            name = ask_new_folder_name()
            if name is None:
                continue
            new_path = current / name
            new_path.mkdir(exist_ok=True)
            console.print(f"[{H1}]✓ Pasta criada:[/{H1}] {new_path}")
            current = new_path
            continue

        if answer == BACK:
            current = current.parent
            continue

        current = answer


def show_book_panel(index: int, total: int, filename: str, info: dict):
    table = Table(show_header=False, box=box.SIMPLE, pad_edge=False)
    table.add_column(style=f"bold {H2}")
    table.add_column()

    table.add_row("Título", info["title"])
    table.add_row("Autor", info["author"])
    table.add_row("Ano", info["year"])
    table.add_row("Idioma", escape(info["lang"]))
    table.add_row("Extensão", info["ext"])

    console.print(
        Panel(
            table,
            title=f"📖 Livro {index}/{total}  —  {filename}",
            border_style=M1,
            box=box.ROUNDED,
        )
    )


def show_parse_error_panel(
    book_path: Path, parts: list, ext: str, index: int, total: int
):
    table = Table(show_header=False, box=box.SIMPLE, pad_edge=False)
    table.add_column(style=f"bold {H2}")
    table.add_column()

    table.add_row("Nome completo", escape(book_path.name))
    table.add_row("Extensão detectada", escape(ext) if ext else "(nenhuma)")
    table.add_row("Campos encontrados", str(len(parts)))
    table.add_row("", "")

    for i, part in enumerate(parts):
        label = EXPECTED_LABELS[i] if i < len(EXPECTED_LABELS) else f"extra [{i}]"
        value = escape(part) if part else f"[{W2}](vazio)[/{W2}]"
        table.add_row(f"[{i}] {label}", value)

    if len(parts) < 6:
        faltando = ", ".join(EXPECTED_LABELS[len(parts) :])
        table.add_row(f"[{W1}]Faltando[/{W1}]", faltando)

    console.print(
        Panel(
            table,
            title=f"⚠️  Nome fora do padrão — Livro {index}/{total}",
            border_style=W2,
            box=box.ROUNDED,
        )
    )
    console.print(
        f'[{M2}]Esperado (separado por " - "): '
        f"mainTopic - subTopic - título - autor - ano - [idioma]  (mínimo 6 campos)[/{M2}]\n"
    )


def handle_parse_error(book_path: Path, parts: list, ext: str, index: int, total: int):
    """Tela dedicada quando o nome não bate o padrão. Retorna
    ('skipped'|'quit'|'continue'|'reparsed_ok', book_path_atualizado)."""
    while True:
        console.clear()
        show_parse_error_panel(book_path, parts, ext, index, total)

        action = questionary.select(
            "O que deseja fazer?",
            choices=[
                questionary.Choice("✏️  Renomear o arquivo agora", value="rename"),
                questionary.Choice(
                    "➡️  Continuar mesmo assim (informar campos manualmente)",
                    value="continue",
                ),
                questionary.Choice("⏭  Pular por agora", value=SKIP),
                questionary.Choice("🚪 Sair do programa", value=QUIT),
            ],
            style=CUSTOM_STYLE,
        ).ask()

        if action is None or action == QUIT:
            return "quit", book_path
        if action == SKIP:
            return "skipped", book_path
        if action == "continue":
            return "continue", book_path

        # action == "rename"
        new_name = questionary.text(
            "Novo nome completo do arquivo (com extensão):",
            default=book_path.name,
            style=CUSTOM_STYLE,
        ).ask()
        if not new_name or new_name == book_path.name:
            continue

        new_path = book_path.with_name(new_name)
        if new_path.exists():
            console.print(
                f"[{W1}]Já existe um arquivo com esse nome nesta pasta.[/{W1}]"
            )
            questionary.text("Pressione Enter para voltar...", style=CUSTOM_STYLE).ask()
            continue

        book_path.rename(new_path)
        book_path = new_path
        info, parts, ext = parse_filename(book_path.name)
        if info is not None:
            return "reparsed_ok", book_path


def manual_filename(main_topic: str, sub_topic: str, original: Path) -> str:
    suggestion = f"{main_topic} - {sub_topic} - {original.stem}"
    console.print(
        f"[{W2}]Não consegui separar título/autor/ano/idioma automaticamente.[/{W2}]"
    )
    name = questionary.text(
        "Digite o nome final do arquivo (sem extensão):",
        default=suggestion,
        style=CUSTOM_STYLE,
    ).ask()
    if name is None:
        name = suggestion
    return name + original.suffix


def resolve_collision(dest: Path) -> Path:
    if not dest.exists():
        return dest

    console.print(
        f"[{W2}]⚠ Já existe um arquivo com esse nome em destino:[/{W2}] {dest}"
    )
    choice = questionary.select(
        "O que fazer?",
        choices=[
            questionary.Choice(
                "Renomear automaticamente (adicionar sufixo)", value="rename"
            ),
            questionary.Choice("Sobrescrever o arquivo existente", value="overwrite"),
            questionary.Choice("Pular este livro", value="skip"),
        ],
        style=CUSTOM_STYLE,
    ).ask()

    if choice == "overwrite" or choice is None:
        return dest
    if choice == "skip":
        return None

    counter = 2
    stem, ext = dest.stem, dest.suffix
    new_dest = dest
    while new_dest.exists():
        new_dest = dest.with_name(f"{stem} ({counter}){ext}")
        counter += 1
    return new_dest


def classify_flow(root: Path, book_path: Path, info: dict, index: int, total: int):
    """Fluxo de escolha de mainTopic/subTopic/subpastas e gravação final.
    Retorna (status, path) onde status é 'moved', 'skipped' ou 'quit'."""
    main_dir = choose_top_level(root, "mainTopic")
    if main_dir == QUIT:
        return "quit", book_path

    sub_dir = choose_sub_level(main_dir, "subTopic")
    if sub_dir == BACK:
        return process_book(root, book_path, index, total)

    main_topic_name = main_dir.name
    sub_topic_name = sub_dir.name

    final_dir = descend_or_save(sub_dir)

    if info:
        new_name = build_new_filename(main_topic_name, sub_topic_name, info)
    else:
        new_name = manual_filename(main_topic_name, sub_topic_name, book_path)

    dest = final_dir / new_name
    dest = resolve_collision(dest)
    if dest is None:
        return "skipped", book_path

    shutil.move(str(book_path), str(dest))
    console.print(f"[bold {H1}]✓ Movido para:[/bold {H1}] {dest}\n")
    return "moved", dest


def process_book(root: Path, book_path: Path, index: int, total: int):
    """Retorna (status, path) onde status é 'moved', 'skipped' ou 'quit'."""
    info, parts, ext = parse_filename(book_path.name)

    if info is None:
        outcome, book_path = handle_parse_error(book_path, parts, ext, index, total)
        if outcome in ("skipped", "quit"):
            return outcome, book_path
        if outcome == "continue":
            return classify_flow(root, book_path, None, index, total)
        info, parts, ext = parse_filename(book_path.name)

    show_book_panel(index, total, book_path.name, info)

    action = questionary.select(
        "O que deseja fazer com este livro?",
        choices=[
            questionary.Choice("➡️  Classificar este livro", value="classify"),
            questionary.Choice("⏭  Pular por agora", value=SKIP),
            questionary.Choice("🚪 Sair do programa", value=QUIT),
        ],
        style=CUSTOM_STYLE,
    ).ask()

    if action is None or action == QUIT:
        return "quit", book_path
    if action == SKIP:
        return "skipped", book_path

    return classify_flow(root, book_path, info, index, total)


def main():
    root = LIBRARY_ROOT
    to_sort = root / TO_BE_SORTED

    console.print(
        Panel.fit(
            f"[bold {H2}]📚 Organizador de Biblioteca Pessoal[/bold {H2}]",
            border_style=H2,
            box=box.DOUBLE,
        )
    )

    if not to_sort.is_dir():
        console.print(f"[{W1}]Pasta não encontrada:[/{W1}] {to_sort}")
        sys.exit(1)

    stats = {"moved": 0}
    skipped_names = set()

    while True:
        console.clear()
        all_files = list_files(to_sort)
        pending = [f for f in all_files if f.name not in skipped_names]

        if not pending:
            if skipped_names:
                revisit = questionary.confirm(
                    f"A fila principal acabou. Restam {len(skipped_names)} livro(s) "
                    "pulado(s). Deseja revisá-los agora?",
                    default=True,
                    style=CUSTOM_STYLE,
                ).ask()
                if revisit:
                    skipped_names.clear()
                    continue
                console.print(
                    f"[{W2}]Encerrando com {len(skipped_names)} livro(s) ainda em "
                    f"2bSorted (pulados).[/{W2}]"
                )
                break

            console.print(
                Panel(
                    f"[bold {H1}]🎉 Tudo organizado! A pasta 2bSorted está vazia.[/bold {H1}]",
                    border_style=H1,
                )
            )
            break

        book = pending[0]
        total_remaining = len(pending)
        result, current_path = process_book(root, book, index=1, total=total_remaining)

        if result == "moved":
            stats["moved"] += 1
            skipped_names.discard(book.name)
        elif result == "skipped":
            skipped_names.add(current_path.name)
        elif result == "quit":
            break

    console.print(
        Panel(
            f"Movidos: [{H1}]{stats['moved']}[/{H1}]    "
            f"Ainda pulados: [{W2}]{len(skipped_names)}[/{W2}]",
            title="Resumo",
            border_style=M1,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(f"\n[{W2}]Encerrado pelo usuário.[/{W2}]")
        sys.exit(0)
