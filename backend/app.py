from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_models import (
    load_question_generator,
    load_answer_extractor,
    generate_mcq,
    generate_random_mcq
)
import re
import json

app = Flask(__name__)
CORS(app)

# Load models once at startup
print("⚙️ Initializing models...")
question_model = load_question_generator()
answer_model = load_answer_extractor()
print("✅ All models loaded.")

@app.route('/generate', methods=['POST'])
def generate_mcqs():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Only .txt files are supported'}), 400

    raw_text = file.read().decode('utf-8')
    print("📄 Text received.")

    num_questions = request.form.get('num_questions', type=int)
    effective_num = num_questions if num_questions and num_questions > 0 else 5

    # Split into sentences/paragraphs
    sentences = re.split(r'[.?!]\s*', raw_text)
    sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 500]
    selected = sentences[:effective_num * 3]  # More for randomness pool


    mcqs = []
    attempts = 0
    max_attempts = effective_num * 5  # Allow more attempts

    while len(mcqs) < effective_num and attempts < max_attempts:
        # Ensure there are sentences to process
        if not selected:
            print("⚠️ Not enough sentences to generate more MCQs.")
            break

        mcq = generate_random_mcq(question_model, answer_model, selected)
        if mcq:
            # Basic check for uniqueness
            if mcq not in mcqs:
                print(f"🧠 Generated MCQ {len(mcqs) + 1}/{effective_num}")
                mcqs.append(mcq)
            else:
                print("🔄 Duplicate MCQ generated, trying again.")
        else:
            print("❌ Failed to generate a valid MCQ in this attempt.")
        
        attempts += 1

    final_mcqs = []
    for i, mcq in enumerate(mcqs):
        mcq_with_number = {
            'question_number': i + 1,
            'question': mcq['question'],
            'options': mcq['options'],
            'answer': mcq['answer']
        }
        final_mcqs.append(mcq_with_number)

    print(f"\n✅ Generated {len(final_mcqs)} MCQs.")
    return jsonify(final_mcqs)

if __name__ == '__main__':
    print("🚀 Running on http://127.0.0.1:5000")
    app.run(debug=True)
