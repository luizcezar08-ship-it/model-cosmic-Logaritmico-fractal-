"""Testes unitários para as funções puras de app.py."""

import unittest
from app import (
    add_task,
    complete_task,
    filter_tasks,
    find_task,
    make_task,
    next_id,
    remove_task,
)


class TestMakeTask(unittest.TestCase):
    def test_fields(self):
        t = make_task(1, "Estudar Python", "alta")
        self.assertEqual(t["id"], 1)
        self.assertEqual(t["title"], "Estudar Python")
        self.assertEqual(t["priority"], "alta")
        self.assertFalse(t["done"])
        self.assertIn("created_at", t)


class TestNextId(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(next_id([]), 1)

    def test_existing(self):
        tasks = [make_task(3, "A", "alta"), make_task(7, "B", "baixa")]
        self.assertEqual(next_id(tasks), 8)


class TestAddTask(unittest.TestCase):
    def test_immutable(self):
        original: list = []
        result = add_task(original, "Nova", "media")
        self.assertEqual(len(original), 0)
        self.assertEqual(len(result), 1)

    def test_increments_id(self):
        tasks = add_task([], "A", "alta")
        tasks = add_task(tasks, "B", "media")
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)


class TestCompleteTask(unittest.TestCase):
    def test_marks_done(self):
        tasks = add_task([], "Ler livro", "baixa")
        updated = complete_task(tasks, 1)
        self.assertTrue(updated[0]["done"])

    def test_no_side_effect(self):
        tasks = add_task([], "Ler livro", "baixa")
        complete_task(tasks, 1)
        self.assertFalse(tasks[0]["done"])

    def test_unknown_id(self):
        tasks = add_task([], "X", "media")
        updated = complete_task(tasks, 999)
        self.assertFalse(updated[0]["done"])


class TestRemoveTask(unittest.TestCase):
    def test_removes(self):
        tasks = add_task(add_task([], "A", "alta"), "B", "baixa")
        updated = remove_task(tasks, 1)
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0]["title"], "B")

    def test_unknown_id(self):
        tasks = add_task([], "A", "alta")
        updated = remove_task(tasks, 999)
        self.assertEqual(len(updated), 1)


class TestFilterTasks(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            make_task(1, "A", "alta"),
            make_task(2, "B", "media"),
            make_task(3, "C", "alta"),
        ]
        self.tasks[2] = {**self.tasks[2], "done": True}

    def test_filter_priority(self):
        result = filter_tasks(self.tasks, priority="alta")
        self.assertEqual(len(result), 2)

    def test_filter_done(self):
        result = filter_tasks(self.tasks, done=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 3)

    def test_filter_pending(self):
        result = filter_tasks(self.tasks, done=False)
        self.assertEqual(len(result), 2)

    def test_combined(self):
        result = filter_tasks(self.tasks, priority="alta", done=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)


class TestFindTask(unittest.TestCase):
    def test_found(self):
        tasks = add_task([], "Buscar", "media")
        self.assertIsNotNone(find_task(tasks, 1))

    def test_not_found(self):
        self.assertIsNone(find_task([], 42))


if __name__ == "__main__":
    unittest.main()
