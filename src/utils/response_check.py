from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

moderator = pipeline("text-classification", model="unitary/toxic-bert")

client = OpenAI()
embeddings = OpenAIEmbeddings()


class ResponseCheck:
    
    @staticmethod
    def is_safe_text(text: str, threshold: float = 0.5) -> bool:
        results = moderator(text)
        for r in results:
            if r["label"].lower() == "toxic" and r["score"] >= threshold:
                return False
        return True

    @staticmethod
    def is_output_safe(text: str) -> bool:
        try:
            result = client.moderations.create(
                model="omni-moderation-latest",
                input=text,
            )
            return not result.results[0].flagged

        except Exception:
            return False

    @staticmethod
    def evidence_score(student_answer: str, passage: str) -> float:
        try:
            ans_vec = np.array(embeddings.embed_query(student_answer)).reshape(1, -1)
            pas_vec = np.array(embeddings.embed_query(passage)).reshape(1, -1)
            score = cosine_similarity(ans_vec, pas_vec)[0][0]
            return float(score)
        except Exception:
            return 0.0

    @staticmethod
    def find_best_supported_passage(student_answer: str, passages, threshold: float = 0.72):
        best_score = 0.0
        best_passage = None

        for doc in passages:
            score = ResponseCheck.evidence_score(student_answer, doc.page_content)
            if score > best_score:
                best_score = score
                best_passage = doc.page_content

        if best_score >= threshold:
            return best_passage, best_score
        else:
            return None, best_score

