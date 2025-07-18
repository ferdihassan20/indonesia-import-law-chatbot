
import logging
from typing import List, Dict, Optional
from scripts.embedding_and_indexing.embed_decomposed import DecomposedEmbedder
from scripts.embedding_and_indexing.retrieval_pipeline import RetrievalPipeline
from models.llm_runtime import LLMRuntime
from utils.prompt.response_refinement_prompt import RESPONSE_REFINEMENT_PROMPT
from utils.prompt.input_decomposition_prompt import INPUT_DECOMPOSER_PROMPT

class Agent:
    def __init__(self,
                 embedding_model_name: str = "sentence-transformers/LaBSE",
                 cache_threshold: float = 0.7,
                 top_k: int = 3):
        self.logger = logging.getLogger("Agent")
        self.embedder = DecomposedEmbedder(model_name=embedding_model_name)
        self.pipeline = RetrievalPipeline(embedding_model_name=embedding_model_name)
        self.llm = LLMRuntime()
        self.cache_threshold = cache_threshold
        self.top_k = top_k
        self.dialogue_history = []

    def refine_query(self, query: str) -> str:
        """
        Menggunakan LLM untuk memperjelas dan memecah pertanyaan pengguna.
        Output bisa berupa beberapa sub-pertanyaan.
        """
        prompt = INPUT_DECOMPOSER_PROMPT.format(user_input=query)
        self.logger.debug(f"Refinement prompt:\n{prompt}")
        
        refined_output = self.llm.generate(prompt)
        
        self.logger.debug(f"Refined output:\n{refined_output}")
        return refined_output.strip()

    def manage_dialogue(self, user_input: str) -> None:
        """
        Manage multi-turn dialogue by storing history.
        """
        self.dialogue_history.append(user_input)
        self.logger.debug(f"Dialogue history updated: {self.dialogue_history}")

    def confidence_score(self, response: Optional[str]) -> float:
        """
        Assess confidence in the response.
        Placeholder: returns 1.0 if response exists, else 0.0
        """
        score = 1.0 if response else 0.0
        self.logger.debug(f"Confidence score: {score} for response: {response}")
        return score

    def aggregate_results(self, results: Dict[str, Dict]) -> (str, list):
        """
        Aggregate multiple results into a coherent summary and collect used document IDs.
        Returns a tuple of (aggregated_text, list_of_doc_ids).
        """
        aggregated = ""
        used_doc_ids = []
        for question, result in results.items():
            aggregated += f"Question: {question}\n"
            if result["source"] == "cache":
                aggregated += f"Cached Response: {result['response']}\n"
                # Assuming cached response metadata is not available, so no doc ids here
            else:
                aggregated += "Retrieved Results:\n"
                for res in result["results"][:3]:
                    meta = res["metadata"]
                    doc_id = meta.get('filename', None)
                    if doc_id and doc_id not in used_doc_ids:
                        used_doc_ids.append(doc_id)
                    aggregated += f" - {meta.get('judul', '')} Pasal {meta.get('pasal', '')}: {meta.get('isi', '')}\n"
            aggregated += "\n"
        self.logger.debug("Aggregated results prepared with used document IDs.")
        return aggregated, used_doc_ids

    def dynamic_prompt(self, user_question: str, aggregated_results: str) -> str:
        """
        Construct a dynamic prompt for the LLM based on user question and aggregated results using RESPONSE_REFINEMENT_PROMPT.
        """
        prompt = RESPONSE_REFINEMENT_PROMPT.format(user_question=user_question, retrieval_results=aggregated_results)
        self.logger.debug(f"Dynamic prompt type: {type(prompt)}")
        self.logger.debug(f"Dynamic prompt content: {repr(prompt)}")
        self.logger.debug("Dynamic prompt constructed using RESPONSE_REFINEMENT_PROMPT.")
        return prompt

    def process(self, user_input: str) -> (str, list):
        """
        Full agent pipeline:
        - Decompose input
        - Embed and retrieve with cache check
        - Aggregate results and collect used documents
        - Generate LLM response
        Returns a tuple of (llm_response_text, list_of_used_doc_ids)
        """
        self.logger.info(f"Processing user input: {user_input}")

        # Manage dialogue history
        self.manage_dialogue(user_input)

        # Decompose input
        decomposed_str = self.embedder.embedder.embedder.generate_decomposition(user_input) if hasattr(self.embedder.embedder, 'generate_decomposition') else None
        if not decomposed_str:
            # fallback to simple decomposition using existing method
            decomposed_str = self.embedder.embedder.embedder.decompose(user_input) if hasattr(self.embedder.embedder, 'decompose') else user_input

        # For now, use the input directly if decomposition not available
        decomposed_str = decomposed_str or user_input

        # Refine queries (optional)
        refined_decomposed = self.refine_query(decomposed_str)
        self.logger.debug(f"Refined decomposed input: {refined_decomposed}")

        # Query retrieval pipeline
        results = self.pipeline.query(refined_decomposed, cache_threshold=self.cache_threshold, top_k=self.top_k)

        # Aggregate results and get used documents
        aggregated_results, used_doc_ids = self.aggregate_results(results)

        # Ensure aggregated_results is string
        if not isinstance(aggregated_results, str):
            aggregated_results = str(aggregated_results)

        # Construct prompt and get LLM response
        prompt = self.dynamic_prompt(user_input, aggregated_results)
        if not isinstance(prompt, str):
            prompt = str(prompt)

        # Debug log prompt type
        self.logger.debug(f"Prompt type before LLM generate: {type(prompt)}")

        llm_response = self.llm.generate(prompt)

        # Post-process LLM response to extract only the final answer and doc IDs
        # Assuming the output format is:
        # ANSWER: ...
        # DOC IDS: ...
        answer = ""
        doc_ids = []
        lines = llm_response.splitlines()
        for line in lines:
            if line.strip().upper().startswith("ANSWER:"):
                answer = line[len("ANSWER:"):].strip()
            elif line.strip().upper().startswith("DOC IDS:"):
                doc_ids_str = line[len("DOC IDS:"):].strip()
                # Parse doc IDs assuming comma or space separated
                doc_ids = [doc_id.strip() for doc_id in doc_ids_str.replace(",", " ").split()]
        if not answer:
            # fallback to full response if parsing fails
            answer = llm_response

        # Log and return cleaned response and used documents
        self.logger.info("LLM response generated and post-processed.")
        return answer, doc_ids


# if __name__ == "__main__":

if __name__ == "__main__":
    import argparse
    import csv
    import logging

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Path ke file CSV untuk batch testing (dengan kolom 'Question')")
    args = parser.parse_args()

    agent = Agent()

    if args.csv:
        # === MODE BATCH DARI CSV ===
        input_csv = args.csv
        output_csv = input_csv.replace(".csv", "_output.csv")

        results = []

        with open(input_csv, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader):
                question = row.get("Question", "").strip()
                if not question:
                    continue
                print(f"\n[{i+1}] Pertanyaan: {question}")
                try:
                    answer, used_docs = agent.process(question)
                    print(f"Jawaban: {answer}")
                    print(f"Dokumen: {used_docs}")
                    results.append({
                        "Question": question,
                        "Answer": answer,
                        "Used_Documents": ", ".join(used_docs)
                    })
                except Exception as e:
                    print(f"❌ Error: {e}")
                    results.append({
                        "Question": question,
                        "Answer": f"[ERROR] {e}",
                        "Used_Documents": ""
                    })

        with open(output_csv, "w", newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["Question", "Answer", "Used_Documents"])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Semua pertanyaan selesai diproses. Hasil disimpan di: {output_csv}")

    else:
        # === MODE INTERAKTIF ===
        while True:
            try:
                user_question = input("Masukkan pertanyaan Anda (ketik 'exit' untuk keluar): ").strip()
                if user_question.lower() == 'exit':
                    print("Keluar dari program.")
                    break
                response, used_docs = agent.process(user_question)
                print("\nJawaban:")
                print(response)
                print("\nDokumen yang digunakan:")
                for doc in used_docs:
                    print(f"- {doc}")
                print("\n" + "-"*40 + "\n")
            except KeyboardInterrupt:
                print("\nKeluar dari program.")
                break

    import logging
    logging.basicConfig(level=logging.WARNING)

    agent = Agent()
    while True:
        try:
            user_question = input("Masukkan pertanyaan Anda (ketik 'exit' untuk keluar): ").strip()
            if user_question.lower() == 'exit':
                print("Keluar dari program.")
                break
            response, used_docs = agent.process(user_question)
            print("\nJawaban:")
            print(response)
            print("\nDokumen yang digunakan:")
            for doc in used_docs:
                print(f"- {doc}")
            print("\n" + "-"*40 + "\n")
        except KeyboardInterrupt:
            print("\nKeluar dari program.")
            break
