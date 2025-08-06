import os
import json
import csv
from collections import defaultdict
from tabulate import tabulate

BASE_DIR = os.path.dirname(__file__)
GAP_RESULTS_FILE = os.path.join(BASE_DIR, "..", "output", "gap_analysis_results.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "..", "output", "compliance_scores.json")
OUTPUT_CSV = os.path.join(BASE_DIR, "..", "output", "compliance_scores.csv")

# Scoring rules
SCORE_MAP = {"full": 1.0, "partial": 0.5, "none": 0.0, "unknown": 0.0}

# Grading scale
def grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    elif percentage >= 50: return "D"
    else: return "F"

def score_gap_results():
    with open(GAP_RESULTS_FILE, encoding="utf-8") as f:
        gap_results = json.load(f)

    summary = {
        "total_score": 0.0,
        "total_possible": 0,
        "overall_percentage": 0.0,
        "grade": "",
        "by_framework": defaultdict(lambda: {"score": 0.0, "count": 0}),
        "by_policy": {}
    }

    for policy_file, controls in gap_results.items():
        policy_score = 0.0
        for item in controls:
            score = SCORE_MAP.get(item["coverage"].lower(), 0.0)
            summary["total_score"] += score
            summary["total_possible"] += 1
            summary["by_framework"][item["source"]]["score"] += score
            summary["by_framework"][item["source"]]["count"] += 1
            policy_score += score

        total_controls = len(controls)
        pct = round((policy_score / total_controls) * 100, 2) if total_controls else 0.0
        summary["by_policy"][policy_file] = {
            "score": policy_score,
            "total_controls": total_controls,
            "percentage": pct,
            "grade": grade(pct)
        }

    summary["overall_percentage"] = round(
        (summary["total_score"] / summary["total_possible"]) * 100, 2
    ) if summary["total_possible"] > 0 else 0.0

    summary["grade"] = grade(summary["overall_percentage"])

    # Save JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save CSV
    with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Policy File", "Score", "Total Controls", "Percentage", "Grade"])
        for policy, data in summary["by_policy"].items():
            writer.writerow([
                policy, data["score"], data["total_controls"],
                data["percentage"], data["grade"]
            ])

    # Console Output
    print("\n✅ COMPLIANCE SCORING COMPLETE")
    print(f"Overall Score: {summary['total_score']} / {summary['total_possible']}")
    print(f"Overall Compliance: {summary['overall_percentage']}% ({summary['grade']})")

    print("\n📊 Score by Framework:")
    table = []
    for framework, data in summary["by_framework"].items():
        pct = (data["score"] / data["count"]) * 100 if data["count"] else 0.0
        table.append([
            framework, data["score"], data["count"],
            f"{pct:.2f}%", grade(pct)
        ])
    print(tabulate(table, headers=["Framework", "Score", "Controls", "Compliance %", "Grade"], tablefmt="fancy_grid"))

    print(f"\n📁 Results saved to:\n  - {OUTPUT_JSON}\n  - {OUTPUT_CSV}")

if __name__ == "__main__":
    score_gap_results()
