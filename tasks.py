from dataclasses import dataclass
from typing import List
import random

@dataclass
class Task:
    id: str
    description: str
    expected_columns: List[str]
    validation_query: str
    difficulty: str

TASKS = [
    Task(
        id="task_01",
        description="Get the name and salary of all employees earning more than 50000",
        expected_columns=["name", "salary"],
        validation_query="SELECT name, salary FROM employees WHERE salary > 50000",
        difficulty="easy",
    ),
    Task(
        id="task_02",
        description="Get each employee's name along with their department name",
        expected_columns=["name", "department"],
        validation_query="SELECT e.name, d.name AS department FROM employees e JOIN departments d ON e.department = d.id",
        difficulty="medium",
    ),
    Task(
        id="task_03",
        description="Get the average salary per department with department name",
        expected_columns=["name", "avg_salary"],
        validation_query="SELECT d.name, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department = d.id GROUP BY d.id",
        difficulty="hard",
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