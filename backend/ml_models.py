# # ml_models.py

# from transformers import pipeline
# import nltk
# import random
# import re
# from nltk.corpus import wordnet as wn

# # One-time download
# nltk.download('wordnet')
# nltk.download('omw-1.4')

# # Load question generation model
# def load_question_generator():
#     print("📘 Loading question generator: iarfmoose/t5-base-question-generator")
#     return pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")

# # Load answer extractor
# def load_answer_extractor():
#     print("📘 Loading answer extractor: distilbert-base-cased-distilled-squad")
#     return pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# # Generate distractors from WordNet + fallback
# def generate_distractors(answer, context, max_distractors=3):
#     distractors = set()

#     for syn in wn.synsets(answer):
#         for lemma in syn.lemmas():
#             word = lemma.name().replace("_", " ")
#             if word.lower() != answer.lower() and word.lower() not in context.lower() and len(word.split()) <= 3:
#                 distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break
#         if len(distractors) >= max_distractors:
#             break

#     # Fallback
#     if len(distractors) < max_distractors:
#         keywords = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', context)
#                     if w.lower() != answer.lower() and w.lower() not in context.lower()]
#         random.shuffle(keywords)
#         for word in keywords:
#             distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break

#     return list(distractors)[:max_distractors]

# # Generate a full MCQ
# def generate_mcq(question_model, answer_model, context: str):
#     try:
#         if len(context.strip().split()) < 5 or context.lower().startswith("chapter"):
#             return None

#         # Step 1: Extract answer
#         qa_result = answer_model(question="What is the key concept?", context=context)
#         answer = qa_result.get('answer', '').strip()

#         if not answer or len(answer.split()) > 10 or answer.lower() in ["true", "false", "yes", "no", "none"]:
#             return None

#         # Step 2: Generate question
#         qg_prompt = f"context: {context} answer: {answer}"
#         qg_prompt = f"generate a question from the following context: {context} and the answer is: {answer}"
#         raw_question = question_model(qg_prompt, max_new_tokens=128)[0]['generated_text']

#         # ✅ Clean the question text properly
#         question = re.sub(r'(question\s*:?|answer\s*:?)+', '', raw_question, flags=re.IGNORECASE).strip()
#         question = question.capitalize()
#         if not question.endswith("?"):
#             question += "?"

#         if not question or len(question.split()) < 4:
#             return None

#         # Step 3: Generate distractors
#         distractors = generate_distractors(answer, context)
#         if not distractors or answer in distractors:
#             return None

#         options = list(dict.fromkeys([answer] + distractors))[:4]
#         if len(options) < 4:
#             return None

#         random.shuffle(options)
#         correct_key = next((k for k, v in zip("ABCD", options) if v == answer), None)

#         return {
#             "question": question,
#             "options": dict(zip("ABCD", options)),
#             "answer": correct_key
#         }

#     except Exception as e:
#         print(f"❌ Failed to generate MCQ: {e}")
#         return None

## return pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")
## return pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# from transformers import pipeline
# import nltk
# import random
# import re
# from nltk.corpus import wordnet as wn
# from difflib import get_close_matches

# # Download required NLTK data
# nltk.download('wordnet')
# nltk.download('omw-1.4')

# # Load question generator
# def load_question_generator():
#     print("📘 Loading question generator: mrm8488/t5-base-finetuned-question-generation-ap")
#     return pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

# # Load answer extractor
# def load_answer_extractor():
#     print("📘 Loading answer extractor: deepset/roberta-base-squad2")
#     return pipeline("question-answering", model="deepset/roberta-base-squad2")

# # Generate distractor options
# def generate_distractors(answer, context, max_distractors=3):
#     distractors = set()
#     for syn in wn.synsets(answer):
#         for lemma in syn.lemmas():
#             word = lemma.name().replace("_", " ")
#             if word.lower() != answer.lower() and word.lower() not in context.lower():
#                 distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break
#         if len(distractors) >= max_distractors:
#             break

#     if len(distractors) < max_distractors:
#         keywords = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', context)
#                     if w.lower() != answer.lower()]
#         random.shuffle(keywords)
#         for word in keywords:
#             distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break

#     return list(distractors)

# # Mask the answer in the context to avoid question leakage
# def mask_answer_in_context(context, answer):
#     if answer.lower() in context.lower():
#         return re.sub(re.escape(answer), "this concept", context, flags=re.IGNORECASE)
#     else:
#         words = context.split()
#         match = get_close_matches(answer, words, n=1)
#         if match:
#             return re.sub(re.escape(match[0]), "this concept", context, flags=re.IGNORECASE)
#     return context

# # Generate a multiple choice question
# def generate_mcq(question_model, answer_model, context: str):
#     try:
#         if len(context.strip().split()) < 5 or context.lower().startswith("chapter"):
#             print("⛔ Skipping: invalid or short context")
#             return None

#         qa_result = answer_model(question="What is the key concept?", context=context)
#         answer = qa_result.get('answer', '').strip()
#         print(f"🔍 Extracted answer: {answer}")

#         if not answer:
#             print("⛔ No answer extracted")
#             return None

#         if len(answer.split()) > 12:
#             print(f"⚠️ Truncating long answer for question generation: {answer}")
#             prompt_answer = " ".join(answer.split()[:10]) + "..."
#         else:
#             prompt_answer = answer

#         # Use proper prompt format for the model
#         masked_context = mask_answer_in_context(context, prompt_answer)
#         qg_prompt = f"answer: {prompt_answer}  context: {masked_context}"
#         raw_question = question_model(qg_prompt, max_new_tokens=64)[0]['generated_text']
#         #question = re.sub(r'^(question\\s*:?|answer\\s*:?)\\s*', '', raw_question.strip(), flags=re.IGNORECASE)
#         question = re.sub(r'^(question|answer)[\s:]*', '', raw_question.strip(), flags=re.IGNORECASE)


#         question = question.replace(prompt_answer, "").strip()
#         question = re.sub(r'[^a-zA-Z0-9 ,?]+', '', question).strip()
#         if not question.endswith("?"):
#             question += "?"
#         print(f"❓ Generated question: {question}")

#         if question.lower().startswith(answer.lower()):
#             print("⛔ Skipping: question starts with answer.")
#             return None

#         if answer.lower() in question.lower() and question.lower().count(answer.lower()) > 1:
#             print("⛔ Skipping: answer repeated in question.")
#             return None

#         if question.lower() in ["true?", "false?", "none?", "yes?", "no?"]:
#             print("⛔ Skipping: Hallucinated generic question.")
#             return None

#         # Generate options
#         distractors = generate_distractors(answer, context)
#         distractors = [d for d in distractors if d.lower() != answer.lower()]
#         forced = False

#         while len(distractors) < 3:
#             distractors.append("Unknown")
#             forced = True

#         options = list(dict.fromkeys([answer] + distractors))[:4]
#         while len(options) < 4:
#             options.append("Unknown")
#             forced = True

#         random.shuffle(options)
#         correct_key = next((k for k, v in zip("ABCD", options) if v == answer), "A")

#         # Score logic
#         score = 10
#         if "Unknown" in options:
#             score -= 2
#         if forced:
#             score -= 2
#         if len(question.split()) < 5:
#             score -= 2
#         if question.lower().count(answer.lower()) > 1:
#             score -= 2

#         return {
#             "question": question,
#             "options": dict(zip("ABCD", options)),
#             "answer": correct_key,
#             "forced": forced,
#             "score": max(score, 0)
#         }

#     except Exception as e:
#         print(f"❌ Error generating MCQ: {e}")
#         return None


# from transformers import pipeline
# import nltk
# import random
# import re
# from nltk.corpus import wordnet as wn
# from difflib import get_close_matches
# from sentence_transformers import SentenceTransformer, util

# # Download required NLTK data
# nltk.download('wordnet')
# nltk.download('omw-1.4')

# # Load SentenceTransformer once globally
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Load question generation model
# def load_question_generator():
#     print("📘 Loading question generator: mrm8488/t5-base-finetuned-question-generation-ap")
#     return pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

# # Load answer extraction model
# def load_answer_extractor():
#     print("📘 Loading answer extractor: deepset/roberta-base-squad2")
#     return pipeline("question-answering", model="deepset/roberta-base-squad2")

# # Generate distractors using WordNet + semantic fallback
# def generate_distractors(answer, context, max_distractors=3):
#     distractors = set()

#     # Try WordNet
#     for syn in wn.synsets(answer):
#         for lemma in syn.lemmas():
#             word = lemma.name().replace("_", " ")
#             if word.lower() != answer.lower() and word.lower() not in context.lower():
#                 distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break
#         if len(distractors) >= max_distractors:
#             break

#     # Semantic fallback
#     if len(distractors) < max_distractors:
#         candidate_pool = list(set(
#             w for w in re.findall(r'\b[a-zA-Z]{4,}\b', context)
#             if w.lower() != answer.lower() and w.lower() not in distractors
#         ))

#         if candidate_pool:
#             answer_emb = embed_model.encode(answer, convert_to_tensor=True)
#             candidate_embs = embed_model.encode(candidate_pool, convert_to_tensor=True)
#             cosine_scores = util.cos_sim(answer_emb, candidate_embs)[0]
#             scored = sorted(zip(candidate_pool, cosine_scores.tolist()), key=lambda x: x[1], reverse=True)

#             for word, score in scored:
#                 if word.lower() != answer.lower() and word.lower() not in distractors:
#                     distractors.add(word)
#                 if len(distractors) >= max_distractors:
#                     break

#     return list(distractors)[:max_distractors]

# # Mask answer in context to avoid leakage
# def mask_answer_in_context(context, answer):
#     if answer.lower() in context.lower():
#         return re.sub(re.escape(answer), "this concept", context, flags=re.IGNORECASE)
#     else:
#         words = context.split()
#         match = get_close_matches(answer, words, n=1)
#         if match:
#             return re.sub(re.escape(match[0]), "this concept", context, flags=re.IGNORECASE)
#     return context

# # Generate MCQ
# def generate_mcq(question_model, answer_model, context: str):
#     try:
#         if len(context.strip().split()) < 5 or context.lower().startswith("chapter"):
#             print("⛔ Skipping: invalid or short context")
#             return None

#         qa_result = answer_model(question="What is the key concept?", context=context)
#         answer = qa_result.get('answer', '').strip()
#         print(f"🔍 Extracted answer: {answer}")

#         if not answer:
#             print("⛔ No answer extracted")
#             return None

#         prompt_answer = " ".join(answer.split()[:10]) + "..." if len(answer.split()) > 12 else answer
#         masked_context = mask_answer_in_context(context, prompt_answer)
#         qg_prompt = f"answer: {prompt_answer}  context: {masked_context}"
#         raw_question = question_model(qg_prompt, max_new_tokens=64)[0]['generated_text']

#         question = re.sub(r'^(question|answer)[\s:]*', '', raw_question.strip(), flags=re.IGNORECASE)
#         question = question.replace(prompt_answer, "").strip()
#         question = re.sub(r'[^a-zA-Z0-9 ,?]+', '', question).strip()
#         if not question.endswith("?"):
#             question += "?"
#         print(f"❓ Generated question: {question}")

#         # Filters
#         if question.lower().startswith(answer.lower()) or \
#            answer.lower() in question.lower() and question.lower().count(answer.lower()) > 1 or \
#            question.lower() in ["true?", "false?", "none?", "yes?", "no?"]:
#             print("⛔ Skipping: Invalid question.")
#             return None

#         # Options
#         distractors = generate_distractors(answer, context)
#         distractors = [d for d in distractors if d.lower() != answer.lower()]
#         forced = False
#         while len(distractors) < 3:
#             distractors.append("Unknown")
#             forced = True

#         options = list(dict.fromkeys([answer] + distractors))[:4]
#         while len(options) < 4:
#             options.append("Unknown")
#             forced = True

#         random.shuffle(options)
#         correct_key = next((k for k, v in zip("ABCD", options) if v == answer), "A")

#         score = 10
#         if "Unknown" in options: score -= 2
#         if forced: score -= 2
#         if len(question.split()) < 5: score -= 2
#         if question.lower().count(answer.lower()) > 1: score -= 2

#         return {
#             "question": question,
#             "options": dict(zip("ABCD", options)),
#             "answer": correct_key,
#             "forced": forced,
#             "score": max(score, 0)
#         }

#     except Exception as e:
#         print(f"❌ Error generating MCQ: {e}")
#         return None

# from transformers import pipeline
# import nltk
# import random
# import re
# from nltk.corpus import wordnet as wn
# from difflib import get_close_matches
# from sentence_transformers import SentenceTransformer, util

# # Download required NLTK data
# nltk.download('wordnet')
# nltk.download('omw-1.4')

# # Load SentenceTransformer once globally
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Load question generation model
# def load_question_generator():
#     print("📘 Loading question generator: mrm8488/t5-base-finetuned-question-generation-ap")
#     return pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")

# # Load answer extraction model
# def load_answer_extractor():
#     print("📘 Loading answer extractor: deepset/roberta-base-squad2")
#     return pipeline("question-answering", model="deepset/roberta-base-squad2")

# # Generate distractors using WordNet + semantic fallback
# def generate_distractors(answer, context, max_distractors=3):
#     distractors = set()

#     # Try WordNet
#     for syn in wn.synsets(answer):
#         for lemma in syn.lemmas():
#             word = lemma.name().replace("_", " ")
#             if word.lower() != answer.lower() and word.lower() not in context.lower():
#                 distractors.add(word)
#             if len(distractors) >= max_distractors:
#                 break
#         if len(distractors) >= max_distractors:
#             break

#     # Semantic fallback
#     if len(distractors) < max_distractors:
#         candidate_pool = list(set(
#             w for w in re.findall(r'\b[a-zA-Z]{4,}\b', context)
#             if w.lower() != answer.lower() and w.lower() not in distractors
#         ))

#         if candidate_pool:
#             answer_emb = embed_model.encode(answer, convert_to_tensor=True)
#             candidate_embs = embed_model.encode(candidate_pool, convert_to_tensor=True)
#             cosine_scores = util.cos_sim(answer_emb, candidate_embs)[0]
#             scored = sorted(zip(candidate_pool, cosine_scores.tolist()), key=lambda x: x[1], reverse=True)

#             for word, score in scored:
#                 if word.lower() != answer.lower() and word.lower() not in distractors:
#                     distractors.add(word)
#                 if len(distractors) >= max_distractors:
#                     break

#     return list(distractors)[:max_distractors]

# # Mask answer in context to avoid leakage
# def mask_answer_in_context(context, answer):
#     if answer.lower() in context.lower():
#         return re.sub(re.escape(answer), "this concept", context, flags=re.IGNORECASE)
#     else:
#         words = context.split()
#         match = get_close_matches(answer, words, n=1)
#         if match:
#             return re.sub(re.escape(match[0]), "this concept", context, flags=re.IGNORECASE)
#     return context

# # Generate MCQ
# def generate_mcq(question_model, answer_model, context: str):
#     try:
#         if len(context.strip().split()) < 5 or context.lower().startswith("chapter"):
#             print("⛔ Skipping: invalid or short context")
#             return None

#         qa_result = answer_model(question="What is the key concept?", context=context)
#         answer = qa_result.get('answer', '').strip()
#         print(f"🔍 Extracted answer: {answer}")

#         if not answer:
#             print("⛔ No answer extracted")
#             return None

#         prompt_answer = " ".join(answer.split()[:10]) + "..." if len(answer.split()) > 12 else answer
#         masked_context = mask_answer_in_context(context, prompt_answer)
#         qg_prompt = f"answer: {prompt_answer}  context: {masked_context}"
#         raw_question = question_model(qg_prompt, max_new_tokens=64)[0]['generated_text']

#         question = re.sub(r'^(question|answer)[\s:]*', '', raw_question.strip(), flags=re.IGNORECASE)
#         question = question.replace(prompt_answer, "").strip()
#         question = re.sub(r'[^a-zA-Z0-9 ,?]+', '', question).strip()
#         if not question.endswith("?"):
#             question += "?"
#         print(f"❓ Generated question: {question}")

#         # ⛔ Filter malformed or irrelevant questions
#         if (
#             re.match(r'(?i)^what is the term for\s*\??$', question.strip()) or
#             question.strip().startswith("?") or
#             question.count("?") > 1 or
#             len(question.strip().split()) < 3
#         ):
#             print("⛔ Skipping: Malformed or irrelevant question.")
#             return None

#         # Filters
#         if question.lower().startswith(answer.lower()) or \
#            (answer.lower() in question.lower() and question.lower().count(answer.lower()) > 1) or \
#            question.lower() in ["true?", "false?", "none?", "yes?", "no?"]:
#             print("⛔ Skipping: Invalid question.")
#             return None

#         # Options
#         distractors = generate_distractors(answer, context)
#         distractors = [d for d in distractors if d.lower() != answer.lower()]

#         if len(distractors) < 3:
#             print("⚠️ Not enough quality distractors. Skipping.")
#             return None

#         options = list(dict.fromkeys([answer] + distractors))[:4]
#         if len(options) < 4:
#             print("⚠️ Less than 4 options even after filtering. Skipping.")
#             return None

#         random.shuffle(options)
#         correct_key = next((k for k, v in zip("ABCD", options) if v == answer), "A")

#         score = 10
#         if len(question.split()) < 5: score -= 2
#         if question.lower().count(answer.lower()) > 1: score -= 2

#         return {
#             "question": question,
#             "options": dict(zip("ABCD", options)),
#             "answer": correct_key,
#             "forced": False,
#             "score": max(score, 0)
#         }

#     except Exception as e:
#         print(f"❌ Error generating MCQ: {e}")
#         return None

### removed wordNet
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

        if not answer:
            print("⛔ No answer extracted")
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

        # ⛔ Filter malformed or irrelevant questions
        if (
            re.match(r'(?i)^what is the term for\s*\??$', question.strip()) or
            question.strip().startswith("?") or
            question.count("?") > 1 or
            len(question.strip().split()) < 3
        ):
            print("⛔ Skipping: Malformed or irrelevant question.")
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

# ✅ ADDITIONAL FUNCTION TO GENERATE A RANDOM MCQ FROM CONTEXT LIST
def generate_random_mcq(question_model, answer_model, context_list: list):
    if not context_list:
        print("❌ Context list is empty.")
        return None

    for _ in range(len(context_list)):
        context = random.choice(context_list)
        mcq = generate_mcq(question_model, answer_model, context)
        if mcq:
            return mcq
    print("❌ No valid MCQ generated from any context.")
    return None
