from datetime import datetime, timezone
from app.database import SessionLocal, engine, Base
from app.models import Card

Base.metadata.create_all(bind=engine)
db = SessionLocal()

questions = [
    {
        "category": "Operating Systems",
        "question": "What is the difference between a process and a thread?",
        "answer": "A process has an independent virtual address space, memory, and file handles. Threads within the same process share that memory space (heap, code, global data) but retain their own program counter, registers, and call stack.",
        "hint": "Think about memory isolation vs shared execution context."
    },
    {
        "category": "Operating Systems",
        "question": "What is thrashing in virtual memory?",
        "answer": "Thrashing occurs when the operating system spends more time swapping pages into and out of secondary storage than executing actual instructions, typically caused by insufficient physical RAM to hold the active working set of processes.",
        "hint": "High page-fault frequency leads to degraded CPU utilization."
    },
    {
        "category": "Data Structures",
        "question": "Explain the time complexity of searching, inserting, and deleting in a Red-Black Tree.",
        "answer": "All three operations run in O(log N) worst-case time because the tree maintains a self-balancing invariant where the longest path from root to leaf is no more than twice the shortest path.",
        "hint": "Self-balancing binary search tree invariants."
    },
    {
        "category": "Data Structures",
        "question": "What is the amortized cost of inserting an element into a dynamic array?",
        "answer": "O(1) amortized. Resizing (doubling capacity) takes O(N) operations, but happens exponentially less frequently, meaning N insertions cost roughly 3N operations total.",
        "hint": "Analyze aggregate cost over a sequence of geometric resizes."
    },
    {
        "category": "Concurrency",
        "question": "What are the four necessary conditions for a deadlock to occur (Coffman conditions)?",
        "answer": "1. Mutual Exclusion (non-shareable resources)\n2. Hold and Wait (processes hold resources while awaiting others)\n3. No Preemption (resources cannot be forcibly reclaimed)\n4. Circular Wait (a closed chain of processes waiting on each other)",
        "hint": "Remember the acronym or the Coffman conditions list."
    },
    {
        "category": "Concurrency",
        "question": "What is the difference between a Mutex and a Semaphore?",
        "answer": "A mutex is an ownership-based locking mechanism allowing only one thread to access a critical section. A semaphore is a signaling mechanism backed by an integer counter, allowing up to N threads access concurrently.",
        "hint": "Ownership lock vs signaling counter."
    },
    {
        "category": "Computer Architecture",
        "question": "What causes a pipeline stall (bubble) in modern CPUs?",
        "answer": "Hazards: Structural hazards (hardware resource conflicts), Data hazards (instruction depends on result of a prior uncompleted instruction), or Control hazards (branch/jump instructions altering the instruction pipeline).",
        "hint": "Structural, Data, and Control hazards."
    },
    {
        "category": "Computer Architecture",
        "question": "What is the difference between spatial and temporal cache locality?",
        "answer": "Temporal locality means data accessed recently is likely to be accessed again soon (e.g., loop variables). Spatial locality means memory locations close to recently accessed data are likely to be accessed soon (e.g., iterating through a contiguous array).",
        "hint": "Time-based reuse vs proximity in address space."
    },
    {
        "category": "System Design",
        "question": "Explain the trade-offs described by the CAP Theorem.",
        "answer": "In any asynchronous network prone to network Partitions (P), a distributed data store must choose between Consistency (all nodes return the latest write simultaneously) and Availability (every non-failing node returns a response, possibly stale). You cannot guarantee both during a partition.",
        "hint": "Network partitions are unavoidable; pick C or A during a split."
    },
    {
        "category": "Algorithms",
        "question": "Why is Quicksort generally preferred over Mergesort for in-memory array sorting despite having a worst-case O(N^2) complexity?",
        "answer": "Quicksort has high cache efficiency due to sequential localized access, sorts in-place (O(log N) auxiliary space), and has small constant factors. Randomized pivot selection makes O(N^2) exceptionally rare in practice.",
        "hint": "Cache locality and auxiliary space overhead."
    }
]

added_count = 0
for q in questions:
    existing = db.query(Card).filter(Card.question == q["question"]).first()
    if not existing:
        card = Card(
            category=q["category"],
            question=q["question"],
            answer=q["answer"],
            hint=q["hint"],
            next_review_date=datetime.now(timezone.utc)
        )
        db.add(card)
        added_count += 1

db.commit()
db.close()
print(f"Database seeded successfully: {added_count} new cards added.")
