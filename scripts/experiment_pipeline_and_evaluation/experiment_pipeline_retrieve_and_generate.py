import csv
import time
from scripts.experiment_pipeline_and_evaluation.main_agent import Agent

CSV_PATH = "datasets/questions_answers/QA.csv"

agent = Agent()

RATE_LIMIT_DELAY = 1.5  # seconds delay between requests to avoid rate limit errors

with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        question = row["Question"].strip()
        print(f"\n[{i+1}] Pertanyaan: {question}")
        try:
            answer, used_docs = agent.process(question)
            print("Jawaban:")
            print(answer)
            print("Dokumen yang digunakan:")
            for doc in used_docs:
                print(f"- {doc}")
        except Exception as e:
            print(f"❌ Error saat memproses: {e}")
        time.sleep(RATE_LIMIT_DELAY)  # delay to avoid hitting rate limits

print("\n✅ Semua pertanyaan telah diproses.")
# This script reads questions from a CSV file and processes them using an Agent instance.