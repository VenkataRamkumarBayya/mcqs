from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_models import (
    load_question_generator,
    load_answer_extractor,
    generate_mcq
)
import re
import json
import random

app = Flask(__name__)
CORS(app)

# Load models once at startup
print("(Gear) Initializing models...")
question_model = load_question_generator()
answer_model = load_answer_extractor()
print("(Checkmark) All models loaded.")

@app.route('/generate', methods=['POST'])
def generate_mcqs():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Only .txt files are supported'}), 400

    raw_text = file.read().decode('utf-8')
    print("(Document) Text received.")

    num_questions = request.form.get('num_questions', type=int)
    effective_num = num_questions if num_questions and num_questions > 0 else 5

    # Split into sentences/paragraphs
    sentences = re.split(r'[.?!]\s*', raw_text)
    sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 500]
    
    # Ensure we have enough sentences to choose from
    if len(sentences) < effective_num:
        print(f"(Warning) Warning: Not enough sentences ({len(sentences)}) to generate {effective_num} questions. Will generate as many as possible.")
    
    random.shuffle(sentences)

    mcqs = []
    used_contexts = set()
    generated_questions = set()
    excluded_questions = []

    for context in sentences:
        if len(mcqs) >= effective_num:
            break

        # Skip context if it has been used
        if context in used_contexts:
            continue
        
        used_contexts.add(context)

        mcq = generate_mcq(question_model, answer_model, context)
        
        if mcq:
            question_text = mcq['question'].strip()
            
            # Skip if question is empty or already generated
            if not question_text or question_text in generated_questions or question_text in excluded_questions:
                print(f"(Refresh) Duplicate, empty, or excluded question generated, skipping.")
                continue

            print(f"(Brain) Generated MCQ {len(mcqs) + 1}/{effective_num}")
            mcqs.append(mcq)
            generated_questions.add(question_text)
        else:
            print(f"(X Mark) Failed to generate a valid MCQ from context: '{context[:50]}...' ")

    if len(mcqs) < effective_num:
        print(f"(Warning) Warning: Could only generate {len(mcqs)} out of {effective_num} requested questions.")

    final_mcqs = []
    for i, mcq in enumerate(mcqs):
        mcq_with_number = {
            'question_number': i + 1,
            'question': mcq['question'],
            'options': mcq['options'],
            'answer': mcq['answer']
        }
        final_mcqs.append(mcq_with_number)

    print(f"\n(Checkmark) Generated {len(final_mcqs)} MCQs.")
    return jsonify(final_mcqs)

@app.route('/generate_quiz_mcqs', methods=['POST'])
def generate_quiz_mcqs():
    data = request.get_json()
    raw_text = data.get('raw_text')
    num_questions = int(data.get('num_questions', 5))
    excluded_questions = data.get('excluded_questions', [])

    

    effective_num = num_questions if num_questions and num_questions > 0 else 5

    sentences = re.split(r'[.?!]\s*', raw_text)
    sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 500]
    
    if len(sentences) < effective_num:
        print(f"(Warning) Warning: Not enough sentences ({len(sentences)}) to generate {effective_num} questions. Will generate as many as possible.")
    
    random.shuffle(sentences)

    mcqs = []
    used_contexts = set()
    generated_questions = set()

    for context in sentences:
        if len(mcqs) >= effective_num:
            break

        if context in used_contexts:
            continue
        
        used_contexts.add(context)

        mcq = generate_mcq(question_model, answer_model, context)
        
        if mcq:
            question_text = mcq['question'].strip()
            
            if not question_text or question_text in generated_questions or question_text in excluded_questions:
                print(f"(Refresh) Duplicate, empty, or excluded question generated, skipping.")
                continue

            print(f"(Brain) Generated MCQ {len(mcqs) + 1}/{effective_num}")
            mcqs.append(mcq)
            generated_questions.add(question_text)
        else:
            print(f"(X Mark) Failed to generate a valid MCQ from context: '{context[:50]}...' ")

    if len(mcqs) < effective_num:
        print(f"(Warning) Warning: Could only generate {len(mcqs)} out of {effective_num} requested questions.")

    final_mcqs = []
    for i, mcq in enumerate(mcqs):
        mcq_with_number = {
            'question_number': i + 1,
            'question': mcq['question'],
            'options': mcq['options'],
            'answer': mcq['answer']
        }
        final_mcqs.append(mcq_with_number)

    print(f"\n(Checkmark) Generated {len(final_mcqs)} MCQs for quiz.")
    return jsonify(final_mcqs)

if __name__ == '__main__':
    print("(Rocket) Running on http://127.0.0.1:5000")
    app.run(debug=True)
