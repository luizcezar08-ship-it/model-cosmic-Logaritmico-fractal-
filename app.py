"""
Sistema de Gerenciamento de Tarefas — app funcional em Python puro.

Funcionalidades:
  - Adicionar, listar, completar e remover tarefas
  - Filtrar por prioridade e status
  - Persistência em JSON
  - Interface de menu interativo no terminal
"""

import json
import os
import sys
from datetime import datetime
from typing import Callable, TypeVar

DATA_FILE = "tasks.json"

# ---------- Tipos e estrutura de dados ----------

Task = dict  # {id, title, priority, done, created_at}

A = TypeVar("A")
B = TypeVar("B")


# ---------- Funções puras ----------

def make_task(task_id: int, title: str, priority: str) -> Task:
    return {
        "id": task_id,
        "title": title,
        "priority": priority,
        "done": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def next_id(tasks: list[Task]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


def add_task(tasks: list[Task], title: str, priority: str) -> list[Task]:
    return tasks + [make_task(next_id(tasks), title, priority)]


def complete_task(tasks: list[Task], task_id: int) -> list[Task]:
    return [
        {**t, "done": True} if t["id"] == task_id else t
        for t in tasks
    ]


def remove_task(tasks: list[Task], task_id: int) -> list[Task]:
    return [t for t in tasks if t["id"] != task_id]


def filter_tasks(
    tasks: list[Task],
    *,
    priority: str | None = None,
    done: bool | None = None,
) -> list[Task]:
    result = tasks
    if priority is not None:
        result = [t for t in result if t["priority"] == priority]
    if done is not None:
        result = [t for t in result if t["done"] == done]
    return result


def find_task(tasks: list[Task], task_id: int) -> Task | None:
    return next((t for t in tasks if t["id"] == task_id), None)


# ---------- Persistência ----------

def load_tasks(path: str) -> list[Task]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: list[Task], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ---------- Formatação ----------

PRIORITY_LABEL = {"alta": "🔴 Alta", "media": "🟡 Média", "baixa": "🟢 Baixa"}
PRIORITY_ORDER = {"alta": 0, "media": 1, "baixa": 2}


def format_task(task: Task) -> str:
    status = "✔" if task["done"] else "○"
    prio = PRIORITY_LABEL.get(task["priority"], task["priority"])
    return f"  [{task['id']:>3}] {status}  {prio:<12}  {task['title']}  ({task['created_at']})"


def sorted_tasks(tasks: list[Task]) -> list[Task]:
    return sorted(tasks, key=lambda t: (t["done"], PRIORITY_ORDER.get(t["priority"], 9), t["id"]))


# ---------- UI helpers ----------

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def header(text: str) -> None:
    width = 60
    print("=" * width)
    print(text.center(width))
    print("=" * width)


def prompt(msg: str, default: str = "") -> str:
    value = input(f"  {msg}: ").strip()
    return value or default


def choose_priority() -> str:
    print("  Prioridade: [1] Alta  [2] Média  [3] Baixa")
    choice = prompt("Escolha (padrão: 2)")
    return {"1": "alta", "3": "baixa"}.get(choice, "media")


def pause() -> None:
    input("\n  Pressione Enter para continuar...")


# ---------- Ações do menu ----------

def action_list(tasks: list[Task]) -> list[Task]:
    clear()
    header("LISTA DE TAREFAS")

    print("\n  Filtrar por: [1] Todas  [2] Pendentes  [3] Concluídas  [4] Por prioridade")
    choice = prompt("Filtro (padrão: 1)")

    filtered: list[Task]
    if choice == "2":
        filtered = filter_tasks(tasks, done=False)
        label = "Pendentes"
    elif choice == "3":
        filtered = filter_tasks(tasks, done=True)
        label = "Concluídas"
    elif choice == "4":
        print("  Prioridade: [1] Alta  [2] Média  [3] Baixa")
        pmap = {"1": "alta", "2": "media", "3": "baixa"}
        prio = pmap.get(prompt("Escolha"), "alta")
        filtered = filter_tasks(tasks, priority=prio)
        label = PRIORITY_LABEL.get(prio, prio)
    else:
        filtered = tasks
        label = "Todas"

    print(f"\n  --- {label} ({len(filtered)}) ---\n")
    if not filtered:
        print("  Nenhuma tarefa encontrada.")
    else:
        for t in sorted_tasks(filtered):
            print(format_task(t))

    pause()
    return tasks


def action_add(tasks: list[Task]) -> list[Task]:
    clear()
    header("ADICIONAR TAREFA")
    title = prompt("Título da tarefa")
    if not title:
        print("\n  Título não pode ser vazio.")
        pause()
        return tasks
    priority = choose_priority()
    updated = add_task(tasks, title, priority)
    save_tasks(updated, DATA_FILE)
    print(f"\n  Tarefa '{title}' adicionada com sucesso!")
    pause()
    return updated


def action_complete(tasks: list[Task]) -> list[Task]:
    clear()
    header("COMPLETAR TAREFA")
    pending = filter_tasks(tasks, done=False)
    if not pending:
        print("\n  Não há tarefas pendentes.")
        pause()
        return tasks
    for t in sorted_tasks(pending):
        print(format_task(t))
    try:
        task_id = int(prompt("\n  ID da tarefa a completar"))
    except ValueError:
        print("\n  ID inválido.")
        pause()
        return tasks
    if find_task(tasks, task_id) is None:
        print("\n  Tarefa não encontrada.")
        pause()
        return tasks
    updated = complete_task(tasks, task_id)
    save_tasks(updated, DATA_FILE)
    print(f"\n  Tarefa #{task_id} marcada como concluída!")
    pause()
    return updated


def action_remove(tasks: list[Task]) -> list[Task]:
    clear()
    header("REMOVER TAREFA")
    if not tasks:
        print("\n  Nenhuma tarefa cadastrada.")
        pause()
        return tasks
    for t in sorted_tasks(tasks):
        print(format_task(t))
    try:
        task_id = int(prompt("\n  ID da tarefa a remover"))
    except ValueError:
        print("\n  ID inválido.")
        pause()
        return tasks
    task = find_task(tasks, task_id)
    if task is None:
        print("\n  Tarefa não encontrada.")
        pause()
        return tasks
    confirm = prompt(f"  Confirmar remoção de '{task['title']}'? (s/N)")
    if confirm.lower() != "s":
        print("\n  Operação cancelada.")
        pause()
        return tasks
    updated = remove_task(tasks, task_id)
    save_tasks(updated, DATA_FILE)
    print(f"\n  Tarefa #{task_id} removida.")
    pause()
    return updated


def action_stats(tasks: list[Task]) -> list[Task]:
    clear()
    header("ESTATÍSTICAS")
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    print(f"\n  Total de tarefas : {total}")
    print(f"  Concluídas       : {done}")
    print(f"  Pendentes        : {pending}")
    print()
    for prio, label in PRIORITY_LABEL.items():
        count = sum(1 for t in tasks if t["priority"] == prio and not t["done"])
        print(f"  {label:<15} pendentes: {count}")
    pause()
    return tasks


# ---------- Loop principal ----------

MENU: list[tuple[str, str, Callable[[list[Task]], list[Task]]]] = [
    ("1", "Listar tarefas", action_list),
    ("2", "Adicionar tarefa", action_add),
    ("3", "Completar tarefa", action_complete),
    ("4", "Remover tarefa", action_remove),
    ("5", "Estatísticas", action_stats),
    ("0", "Sair", None),  # type: ignore[arg-type]
]


def show_menu(tasks: list[Task]) -> None:
    clear()
    header("GERENCIADOR DE TAREFAS")
    pending = sum(1 for t in tasks if not t["done"])
    print(f"\n  {len(tasks)} tarefa(s) no total  |  {pending} pendente(s)\n")
    for key, label, _ in MENU:
        print(f"  [{key}] {label}")
    print()


def run() -> None:
    tasks = load_tasks(DATA_FILE)
    while True:
        show_menu(tasks)
        choice = prompt("Opção")
        for key, _, action in MENU:
            if choice == key:
                if action is None:
                    print("\n  Até logo!")
                    sys.exit(0)
                tasks = action(tasks)
                break
        else:
            print("\n  Opção inválida.")
            pause()


if __name__ == "__main__":
    run()
