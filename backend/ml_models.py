from transformers import pipeline
import nltk
import random
import re
from difflib import get_close_matches
from sentence_transformers import SentenceTransformer, util

# Load SentenceTransformer once globally
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load question generation model
def load_question_generator():
    print("📘 Loading question generator: mrm8488/t5-base-finetuned-question-generation-ap")
    return pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

# Load answer extraction model
def load_answer_extractor():
    print("📘 Loading answer extractor: deepset/roberta-base-squad2")
    return pipeline("question-answering", model="deepset/roberta-base-squad2")

# Normalize text for deduplication (lowercase, strip articles, remove punctuation)
def normalize_option(text):
    text = text.lower().strip()
    text = re.sub(r'\b(a|an|the)\b', '', text)
    text = re.sub(r'[^a-z0-9 ]+', '', text)
    return text.strip()

# Generate distractors using semantic similarity only
def generate_distractors(answer, context, max_distractors=3):
    distractors = set()
    normalized_set = set()

    candidate_pool = list(set(
        w for w in re.findall(r'\b[a-zA-Z]{4,}\b', context)
        if normalize_option(w) != normalize_option(answer)
    ))

    if candidate_pool:
        answer_emb = embed_model.encode(answer, convert_to_tensor=True)
        candidate_embs = embed_model.encode(candidate_pool, convert_to_tensor=True)
        cosine_scores = util.cos_sim(answer_emb, candidate_embs)[0]
        scored = sorted(zip(candidate_pool, cosine_scores.tolist()), key=lambda x: x[1], reverse=True)

        for word, score in scored:
            norm = normalize_option(word)
            if norm != normalize_option(answer) and norm not in normalized_set:
                distractors.add(word)
                normalized_set.add(norm)
            if len(distractors) >= max_distractors:
                break

    return list(distractors)[:max_distractors]

# Mask answer in context to avoid leakage
def mask_answer_in_context(context, answer):
    if answer.lower() in context.lower():
        return re.sub(re.escape(answer), "this concept", context, flags=re.IGNORECASE)
    else:
        words = context.split()
        match = get_close_matches(answer, words, n=1)
        if match:
            return re.sub(re.escape(match[0]), "this concept", context, flags=re.IGNORECASE)
    return context

# Generate MCQ
def generate_mcq(question_model, answer_model, context: str):
    try:
        if len(context.strip().split()) < 5 or context.lower().startswith("chapter"):
            print("⛔ Skipping: invalid or short context")
            return None

        qa_result = answer_model(question="What is the key concept?", context=context)
        answer = qa_result.get('answer', '').strip()
        print(f"🔍 Extracted answer: {answer}")

        # Add filters for answer quality
        if not answer or len(answer.split()) > 5 or len(answer) < 3:
            print(f"⛔ Skipping: Invalid answer extracted: '{answer}'")
            return None

        prompt_answer = " ".join(answer.split()[:10]) + "..." if len(answer.split()) > 12 else answer
        masked_context = mask_answer_in_context(context, prompt_answer)
        qg_prompt = f"answer: {prompt_answer}  context: {masked_context}"
        raw_question = question_model(qg_prompt, max_new_tokens=64)[0]['generated_text']

        question = re.sub(r'^(question|answer)[\s:]*', '', raw_question.strip(), flags=re.IGNORECASE)
        question = question.replace(prompt_answer, "").strip()
        question = re.sub(r'[^a-zA-Z0-9 ,?]+', '', question).strip()
        if not question.endswith("?"):
            question += "?"
        print(f"❓ Generated question: {question}")

        # ⛔ Filter malformed or irrelevant questions - GENERALIZED
        q_text = question.strip()
        q_lower = q_text.lower()

        # Generic question filter
        generic_endings = ["known as?", "called?", "named?"]
        if any(q_lower.endswith(ending) for ending in generic_endings) and len(q_lower.split()) < 7:
            print(f"⛔ Skipping: Overly generic question: \"{q_text}\"")
            return None

        # List of common bad question starters
        BAD_STARTERS = [
            'what is the term for', 'what do you call', 'what forms when', 
            'what does a', 'what is a', 'are all', 'what is the name of the'
        ]

        # List of words that indicate an incomplete question if at the end
        BAD_ENDINGS = [
            'a', 'an', 'the', 'of', 'for', 'in', 'on', 'at', 'with', 'by', 'to', 'or', 'and', 'but'
        ]
        
        # List of grammatically incorrect or nonsensical phrases to filter out
        BAD_PHRASES = [
            'or than', 'a this concept', 'of what concept', 'basic this concept',
            'is the most of what', 'give rise to basic', 'of the concept', 'where what happens'
        ]

        if any(phrase in q_lower for phrase in BAD_PHRASES):
            print(f"⛔ Skipping: Question contains a nonsensical phrase: \"{q_text}\"")
            return None

        # Check for bad starters
        if any(q_lower.startswith(starter) for starter in BAD_STARTERS):
            print(f"⛔ Skipping: Question starts with a generic pattern: \"{q_text}\"")
            return None

        # Check for bad endings (word before the '?')
        words = q_text.rstrip('?').split()
        if words and words[-1].lower() in BAD_ENDINGS:
            print(f"⛔ Skipping: Question ends with a preposition/article/conjunction: \"{q_text}\"")
            return None

        # Other general checks
        if (
            q_text.startswith("?") or
            q_text.count("?") > 1 or
            len(words) < 4
        ):
            print(f"⛔ Skipping: Malformed or too short question: \"{q_text}\"")
            return None

        # Filters
        if question.lower().startswith(answer.lower()) or \
           (answer.lower() in question.lower() and question.lower().count(answer.lower()) > 1) or \
           question.lower() in ["true?", "false?", "none?", "yes?", "no?"]:
            print("⛔ Skipping: Invalid question.")
            return None

        # Options
        distractors = generate_distractors(answer, context)
        distractors = [d for d in distractors if normalize_option(d) != normalize_option(answer)]

        if len(distractors) < 3:
            print("⚠️ Not enough quality distractors. Skipping.")
            return None

        all_options = list(dict.fromkeys([answer] + distractors))[:4]

        # Deduplicate semantically
        norm_seen = set()
        final_options = []
        for opt in all_options:
            norm = normalize_option(opt)
            if norm not in norm_seen:
                final_options.append(opt)
                norm_seen.add(norm)
            if len(final_options) == 4:
                break

        if len(final_options) < 4:
            print("⚠️ Less than 4 distinct options after normalization. Skipping.")
            return None

        random.shuffle(final_options)
        correct_key = next((k for k, v in zip("ABCD", final_options) if normalize_option(v) == normalize_option(answer)), "A")

        score = 10
        if len(question.split()) < 5: score -= 2
        if question.lower().count(answer.lower()) > 1: score -= 2

        return {
            "question": question,
            "options": dict(zip("ABCD", final_options)),
            "answer": correct_key,
            "forced": False,
            "score": max(score, 0)
        }

    except Exception as e:
        print(f"❌ Error generating MCQ: {e}")
        return None