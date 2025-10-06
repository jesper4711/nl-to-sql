# Case Instructions — NL → SQL on a Sales Database

Welcome! This case evaluates how you can leverage LLMs to convert **natural language business questions** into **correct SQL** using today’s LLMs or agents.

We care about **correctness, clarity, and engineering choices**. We expect the coding to take 1-3 hours. IMPORTANT: be prepared to describe your approach and discuss topics like Python coding choices, how you would handle SQL correctness, validation, deployment in the cloud etc.

Tips:
- Use JSON to return the responses from the LLM
- Tell the LLM to use Sqlite SQL. Dates can be tricky to get right.
- It is ok if it doesn't handle all questions. The important thing is that the code is well structured and that you can discuss your work and given topics.

---

## 1) Repository Deliverables

- **README**: how to install & run.
- **CLI tool**: `python app.py "business question"` → prints SQL (and optionally executes it against sales.db).

---

## 2) Data & Schema

Install requirements and generate a sales.db file by running

```bash
pip install -r requirements.txt
python generate_db.py
```

### Tables

**Customers**
- `customer_id` (TEXT, UUID, PK)  
- `name` (TEXT)  
- `region` (TEXT)

**Products**
- `product_id` (TEXT, UUID, PK)  
- `name` (TEXT)  
- `category` (TEXT)  
- `price` (REAL)

**Orders**
- `order_id` (TEXT, UUID, PK)  
- `customer_id` (TEXT, FK)  
- `order_date` (TEXT, ISO YYYY-MM-DD)  
- `total_amount` (REAL)

**Order_Items**
- `order_id` (TEXT, FK)  
- `product_id` (TEXT, FK)  
- `quantity` (INTEGER)  
- `revenue` (REAL)

Indices exist on common join/filter columns.

---

## 3) Your Task

Build a small system that:
1. **Parses** a natural-language question.
2. **Produces SQL** that answers the question for this schema.
3. (Optional) **Executes SQL against `sales.db`** and prints a compact result.

---

## 4) Running Examples

```bash
# Generate SQL only
python app.py "Which product category generated the most revenue in Q2 2024?"

# Generate and execute (optional)
python app.py --execute "List the top 5 customers by total spend in the last year"
```

---

## 5) Example Questions

- Which product category generated the most revenue in **Q2 2024**?  
- List the **top 5 customers** by total spend in the **last 365 days**.  
- Show **month-over-month order growth** for the **Electronics** category.  
- Which **region** had the **lowest average order value** in **2024**?  
- Find all customers who bought a **Laptop** but never a **Smartphone**.  
- Among customers in **Nordics: Sweden**, which categories grew the fastest **MoM** in **2025**?

---

## 6) Model Options

You may pick any of the following (or others):
- **APIs**: GPT-4.1, Claude 4.5 Sonnet, Gemini 2.5 Pro/Flash, etc
- **Local**: LLaMA 3.1 8B etc.

### Suggested building blocks
- **Schema-aware prompts**: supply table/column names and brief descriptions.
- **Retrieval**: store schema as retrievable chunks; feed relevant bits to the model.

---

## 7) Evaluation & Monitoring

We’ll discuss how you thought about:
- **Correctness**: How do you ensure the SQL really answers the question?
- **Robustness**: Handling ambiguous queries; graceful failure with clarifying guidance.
- **Scalability**: Extending to new tables, synonyms, time filters, and larger data.

---

## 8) Suggested Project Structure

```
.
├─ app.py                 # CLI entrypoint
├─ models/                # LLM wrapper
├─ prompts/               # prompt templates
├─ sales.db               # generated 
├─ generate_db.py         # dataset generator (optional)
├─ README.md              # setup & run
```

---

## 9) Getting Started Quickly

**Python**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # if used
export OPENAI_API_KEY=...
python app.py --help
```

**SQLite**
```bash
python -c 'import sqlite3; import pandas as pd; conn=sqlite3.connect("sales.db"); print(pd.read_sql_query("SELECT COUNT(*) AS n FROM Orders", conn))'
```

---

## 10) What We’ll Ask You About

- Why this model/agent design?  
- How you evaluate correctness & avoid hallucinations.  
- How you’d extend to bigger/changed schemas.  
- Trade-offs: latency, cost, reliability, local vs API, few-shot vs tools. 
- How would you think about tests? 
- If you had another day: what would you improve?
- How would you deploy it on the cloud?

Good luck — and have fun!