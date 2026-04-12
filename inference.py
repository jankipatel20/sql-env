import os
import asyncio
from typing import List
from openai import OpenAI
from sql_env_environment import SqlEnvironment
from models import SqlAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct:free")
HF_TOKEN     = os.getenv("HF_TOKEN")
MAX_STEPS    = 10
SUCCESS_SCORE_THRESHOLD = 0.6

if not HF_TOKEN:
    raise ValueError("HF_TOKEN is required")

def log_start(model):
    print(f"[START] env=sql_env model={model}", flush=True)

def log_step(step, action, reward, done, error):
    err = error if error else "null"
    print(f"[STEP] step={step} action={repr(action)} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)

def log_end(success, steps, score, rewards):
    r_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={r_str}", flush=True)

def get_model_query(client, last_output: str, history: List[str]) -> SqlAction:
    history_str = "\n".join(history[-4:]) if history else "None"
    prompt = f"""You are an expert SQL developer working with a SQLite database.

The database has these tables:
- employees (id, name, department, salary)
- departments (id, name, budget)

LAST OUTPUT:
{last_output}

RECENT HISTORY:
{history_str}

Instructions:
- Write a single valid SQLite SQL query
- Reply with ONLY one line:
QUERY: <your sql here>
"""
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        text = completion.choices[0].message.content.strip()
        lines = {l.split(":")[0].strip(): ":".join(l.split(":")[1:]).strip()
                 for l in text.splitlines() if ":" in l}
        query = lines.get("QUERY", "SELECT * FROM employees")
        return SqlAction(query=query)
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return SqlAction(query="SELECT * FROM employees")

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = SqlEnvironment()

    rewards: List[float] = []
    history: List[str] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(model=MODEL_NAME)

    try:
        obs = env.reset()
        last_output = obs.echoed_message

        for step in range(1, MAX_STEPS + 1):
            action = get_model_query(client, last_output, history)
            obs = env.step(action)

            metadata = obs.metadata or {}
            reward = metadata.get("reward", 0.0)
            error = metadata.get("error", None)
            done = False  # extend with your own done condition

            rewards.append(reward)
            steps_taken = step
            last_output = obs.echoed_message
            history.append(f"Step {step}: {action.query[:80]} → reward {reward:.2f}")

            log_step(step=step, action=action.query[:100],
                     reward=reward, done=done, error=error)

            if done:
                break

        score = sum(rewards) / max(len(rewards), 1)
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())