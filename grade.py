import json

with open("eval/results.json", encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    r["correct"] = (not r["refused"]) if r["answerable"] else r["refused"]

with open("eval/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

ans = [r for r in results if r["answerable"]]
print("Correct:", sum(r["correct"] for r in ans), "/", len(ans))