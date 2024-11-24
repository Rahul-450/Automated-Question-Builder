import json
import hashlib
from tqdm import tqdm
import time
from openai import AzureOpenAI
import yaml
import os


# Reading Config File
current_path = os.getcwd()
full_config_path = "config.yaml"
config_values = yaml.safe_load(open(full_config_path))

AZURE_OPENAI_ENDPOINT = config_values['AZURE_OPENAI_ENDPOINT']
AZURE_OPENAI_KEY = config_values['AZURE_OPENAI_API_KEY']
OPENAI_API_VERSION = config_values['OPENAI_API_VERSION']
DEPLOYMENT_NAME=config_values['DEPLOYMENT_NAME']

try:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=OPENAI_API_VERSION
    )
except:
    print("Azure OpenAI connection error.")

user_input = {
    "topic": "Full Stack Development",
    "subtopics": [
        "c", "Python", "c#", "HTML", "CSS",
    ],
    "total_number_of_questions": 52,
    "difficulty_levels": {"easy": 26, "medium": 22, "hard": 4},
    "types": ["MCQ", "Case Study", "True or False", "Fill Ups", "Find the Code Output", "Find the Error"],
}

# Load Question Bank from file
def load_question_bank(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {"questions": []}

# Save the Question Bank to file
def save_question_bank(file_path, question_bank):
    with open(file_path, 'w') as file:
        json.dump(question_bank, file, indent=2)

# Fetch questions from the question bank based on user input
def fetch_questions_from_bank(user_input, question_bank):
    fetched_questions = []
    remaining_difficulties = user_input["difficulty_levels"].copy()

    print("Fetching questions from the question bank...")

    # Loop through the question bank and match questions based on topic, subtopic, difficulty, and type
    for question in question_bank["questions"]:
        # Check if the question matches the subtopics, difficulty, and type from user input
        if (
            question["subtopic"] in user_input["subtopics"] and
            remaining_difficulties.get(question["difficulty"], 0) > 0 and
            question["type"] in user_input["types"]  # Ensure the question type matches the user's request
        ):
            fetched_questions.append(question)
            remaining_difficulties[question["difficulty"]] -= 1
            if remaining_difficulties[question["difficulty"]] == 0:
                del remaining_difficulties[question["difficulty"]]
            if sum(remaining_difficulties.values()) == 0:
                break

    print(f"Fetched {len(fetched_questions)} questions from the bank.")
    print(f"Remaining difficulties : {remaining_difficulties}")
    return fetched_questions, remaining_difficulties


# Generate questions and append to the bank
def generate_questions(user_input, question_bank, question_bank_path, choice, batch_size=10):
    all_questions = []
    remaining_difficulties = user_input["difficulty_levels"].copy()
    total_questions = sum(remaining_difficulties.values())
    message_history = []
    
    # Set to track unique questions
    unique_questions_set = set()
    previous_questions = []

    # Deduplicate the questions when adding to the bank
    existing_questions_set = set()
    max_existing_id = 0  # Variable to track the highest ID in the current bank

    # Find the maximum ID in the existing questions
    for question in question_bank["questions"]:
        question_text = question["question"]  # Hash only the 'question' field
        question_hash = hashlib.md5(question_text.encode('utf-8')).hexdigest()
        existing_questions_set.add(question_hash)
        max_existing_id = max(max_existing_id, question["id"])  # Track the highest ID

    print("Existing Question Bank Hashed successfully!")

    if choice == "smart_generation":
        # Fetch existing questions from the bank
        print("Attempting to fetch questions from the bank...")
        fetched_questions, remaining_difficulties = fetch_questions_from_bank(user_input, question_bank)
        
        all_questions.extend(fetched_questions)

        total_questions -= len(fetched_questions)  # Adjust the total question count
        for question in fetched_questions:
            previous_questions.append(question["question"])

        print(f"Remaining questions to generate: {total_questions}")
        if total_questions > 0:
            print(f"Generating {total_questions} additional questions...")
    else:
        print("Generating questions from scratch using AI ...")

    progress_bar = tqdm(total=total_questions, desc="Generating Questions", dynamic_ncols=True)

    while total_questions > 0:
        current_batch_size = min(batch_size, total_questions)
        
        current_user_input = user_input.copy()
        current_user_input["difficulty_levels"] = remaining_difficulties

        ai_prompt = f"""

        Generate {current_batch_size} unique question and answer pairs based on the user input.
        Make sure each question is unique and non-repetitive, both in terms of the question content and type.
        Strictly Avoid generating similar questions from previous questions.

        Avoid repeating any previous questions: {json.dumps(previous_questions, indent=2)}

        User Input: {json.dumps(current_user_input, indent=2)}

        Please ensure that all questions cover a broad range of subtopics and difficulties as described. Do not repeat previous questions.

        # Steps

        1. Understand Parameters:
            - Topic: The main subject area of the questions.
            - Subtopics: Specific areas under the main topic to focus on.
            - Total Number of Questions: Total count of questions to generate.
            - Difficulty Levels: Distribution of questions across difficulty levels (easy, medium, hard).
            - Types: Format of the questions (MCQ, Case Study, True or False, Fill Ups, Find the Code Output (Should have choices), Find the Error (Should have choices)).

        2. Generate Questions:
            - Distribute questions across subtopics.
            - Ensure the correct number of questions per difficulty level.
            - Format each question to match the specified type.
            - Do not generate any "Find the Code Output" type questions unless the topic or subtopics explicitly include programming languages or concepts.
            - If the topic and subtopics do not involve programming, exclude "Find the Code Output" from the question types.
        
        3. Provide Answers:
            - For each question, generate a corresponding answer.
            - Ensure accuracy and alignment with the difficulty level and type.

        # Output Format

        The output should be a JSON object containing the generated question and answer pairs. Each question should have a unique identifier, and the corresponding answer should be clearly linked.

        Output JSON Sample:
        {{
          "questions": [
            {{
              "id": 1,
              "topic": "Main Topic",
              "subtopic": "Subtopic Example",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is [MCQ Example Question]?",
              "choices": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "Option A"
            }},
            {{
              "id": 2,
              "topic": "Main Topic",
              "subtopic": "Subtopic Example",
              "difficulty": "Hard",
              "type": "Case Study",
              "question": "What is [Case Study Example Question]?",
              "choices": [],
              "answer": "Expected Answer of Case Study"
            }}
            ... (additional questions follow the same structure)
          ]
        }}

        # Examples

        Input JSON:

        {{
          "topic": "Mathematics",
          "subtopics": ["Algebra", "Geometry"],
          "total_number_of_questions": 5,
          "difficulty_levels": {{"easy": 2, "medium": 2, "hard": 1}},
          "types": ["MCQ"]
        }}

        Output JSON:

        {{
          "questions": [
            {{
              "id": 1,
              "topic": "Mathematics",
              "subtopic": "Algebra",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is the value of x if 2x + 3 = 7?",
              "choices": ["1", "2", "3", "4"],
              "answer": "2"
            }},
            {{
              "id": 2,
              "topic": "Mathematics",
              "subtopic": "Geometry",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is the area of a triangle with base 4 and height 3?",
              "choices": ["6", "8", "10", "12"],
              "answer": "6"
            }},
            ...(additional questions follow the same structure)
          ]
        }}

        # Notes

        - Ensure that all generated unique questions are relevant to the specified subtopics and difficulty levels.
        - For MCQs, provide a balanced set of distractors that are plausible and well thought out.
        - The total number of questions should precisely match the sum of questions across all specified difficulty levels.
        - Ensure the format adheres strictly to the type specified in the input.
        
        """ 

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            *message_history,
            {"role": "user", "content": ai_prompt},
        ]

        try:
            res = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4096
            )

            try:
                batch_questions = json.loads(res.choices[0].message.content)["questions"]
                print(f"Generated {len(batch_questions)} new questions.")
                
                for question in batch_questions:
                    question_text = question["question"]  # Hash only the 'question' field
                    question_hash = hashlib.md5(question_text.encode('utf-8')).hexdigest()

                    # If the question is not in the set (not a duplicate), add it to the set and proceed
                    if question_hash not in unique_questions_set and question_hash not in existing_questions_set:
                        
                        # Increment ID to ensure it's unique and continues from the highest existing ID
                        max_existing_id += 1
                        question["id"] = max_existing_id  # Assign a new ID to the question
                        question_bank["questions"].append(question)
                        existing_questions_set.add(question_hash)

                        if remaining_difficulties[question['difficulty']] > 0:
                            unique_questions_set.add(question_hash)
                            all_questions.append(question)
                            previous_questions.append(question['question'])

                            remaining_difficulties[question['difficulty']] -= 1
                            total_questions -= 1

                            # Update progress bar
                            progress_bar.update(1)
                        else:
                            print("Added a new question but it's not needed as there are no remaining difficulties for this question's level.")

                    else:
                        print(f"Duplicate question skipped: {question['question']}")

                # Add this batch to message history
                message_history.append({
                    "role": "assistant",
                    "content": json.dumps({"questions": batch_questions})
                })

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print("Raw content:", res.choices[0].message.content)

        except Exception as e:
            print(f"Error in API call: {e}")

        # Break the loop if we're not making progress
        if total_questions == 0:
            break

    # Check if we've met the required number of questions
    if len(unique_questions_set) != user_input["total_number_of_questions"]:
        error_message = f"Expected {user_input['total_number_of_questions']} unique questions, got {len(unique_questions_set)}"
        print(error_message)

    # Check that the difficulty distribution matches
    final_difficulty_counts = {k: 0 for k in user_input["difficulty_levels"].keys()}
    for question in all_questions:
        final_difficulty_counts[question['difficulty']] += 1

    if final_difficulty_counts != user_input["difficulty_levels"]:
        error_message = f"Expected difficulty levels: {user_input['difficulty_levels']}, but got {final_difficulty_counts}."
        print(error_message)



    # Save the updated question bank
    save_question_bank(question_bank_path, question_bank)

    # Recalculate IDs
    for i, question in enumerate(all_questions, 1):
        question['id'] = i

    return all_questions, unique_questions_set, final_difficulty_counts


# # Example usage
# question_bank_path = "C:\\Users\\2000108359\\Downloads\\Presedio_latest\\Presedio_latest\\question_bank.json"
# question_bank = load_question_bank(question_bank_path)
# # choice = "smart_generation"
# choice = "Advanced AI Generation"
# start_time = time.time()
# print("Starting question generation process...")
# all_generated_questions, unique_questions_set, final_difficulty_counts = generate_questions( user_input, question_bank, question_bank_path, choice)

# # Calculate and print the response time
# end_time = time.time()
# response_time = end_time - start_time
# print(f"Total Response Time: {response_time:.2f} seconds")

# # Combine all questions into a single JSON object
# final_output = {"questions": all_generated_questions}

# # Write the content to a file
# with open(f'{user_input["topic"]}.json', 'w') as file:
#     json.dump(final_output, file, indent=2)

# print(f"Generated {len(all_generated_questions)} questions. Content has been written to '{user_input["topic"]}.json'")

# # Print final difficulty distribution
# print(f"Final difficulty distribution: {final_difficulty_counts}")
