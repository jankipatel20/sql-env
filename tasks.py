from dataclasses import dataclass, field
from typing import List, Callable, Any
import random

@dataclass
class Task:
    id: str
    description: str
    expected_columns: List[str]
    validation_query: str
    difficulty: str
    grader: Callable[[List[Any]], float] = None  # ← add this


def grader_salary_above_50000(rows: List[Any]) -> float:
    """All returned rows must have salary > 50000."""
    if not rows:
        return 0.0
    correct = all(row[1] > 50000 for row in rows)
    return 1.0 if correct else 0.0


def grader_employee_department_join(rows: List[Any]) -> float:
    """Must return rows with at least 2 columns (name + department)."""
    if not rows:
        return 0.0
    correct = all(len(row) >= 2 for row in rows)
    return 1.0 if correct else 0.0


def grader_avg_salary_per_department(rows: List[Any]) -> float:
    """Must return rows with department name and a numeric avg salary."""
    if not rows:
        return 0.0
    try:
        correct = all(isinstance(row[1], (int, float)) for row in rows)
        return 1.0 if correct else 0.0
    except (IndexError, TypeError):
        return 0.0


TASKS = [
    Task(
        id="task_01",
        description="Get the name and salary of all employees earning more than 50000",
        expected_columns=["name", "salary"],
        validation_query="SELECT name, salary FROM employees WHERE salary > 50000",
        difficulty="easy",
        grader=grader_salary_above_50000,
    ),
    Task(
        id="task_02",
        description="Get each employee's name along with their department name",
        expected_columns=["name", "department"],
        validation_query="SELECT e.name, d.name AS department FROM employees e JOIN departments d ON e.department = d.id",
        difficulty="medium",
        grader=grader_employee_department_join,
    ),
    Task(
        id="task_03",
        description="Get the average salary per department with department name",
        expected_columns=["name", "avg_salary"],
        validation_query="SELECT d.name, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department = d.id GROUP BY d.id",
        difficulty="hard",
        grader=grader_avg_salary_per_department,
    ),
]

def get_task(task_id: str) -> Task:
    for t in TASKS:
        if t.id == task_id:
            return t
    raise ValueError(f"Task {task_id} not found")

def get_random_task() -> Task:
    return random.choice(TASKS)

def get_task_by_difficulty(difficulty: str) -> Task:
    filtered = [t for t in TASKS if t.difficulty == difficulty]
    if not filtered:
        raise ValueError(f"No tasks found for difficulty: {difficulty}")
    return random.choice(filtered)