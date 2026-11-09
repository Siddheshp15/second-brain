from rag.answer import ask

questions = [
    "How is the job priority score calculated?",
    "What percentage of jobs request 1 GPU?",
    "What is the capital of France?",  # NOT in the paper
]

for q in questions:
    result = ask(q)
    print("\n" + "=" * 60)
    print("Q:", q)
    print("A:", result["answer"])
    for s in result["sources"]:
        print(f"   source: {s['file']}, page {s['page']}")