from openai import AzureOpenAI
import yaml
import os
import base64
import time
import json
import hashlib
from tqdm import tqdm  # Import tqdm for the progress bar

# Reading Config File
current_path = os.getcwd()
full_config_path = "config.yaml"
config_values = yaml.safe_load(open(full_config_path))

AZURE_OPENAI_ENDPOINT=config_values['AZURE_OPENAI_ENDPOINT']
AZURE_OPENAI_KEY=config_values['AZURE_OPENAI_API_KEY']
OPENAI_API_VERSION=config_values['OPENAI_API_VERSION']
DEPLOYMENT_NAME=config_values['DEPLOYMENT_NAME']

try:
    client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT, 
    api_key= AZURE_OPENAI_KEY,  
    api_version= OPENAI_API_VERSION
    )
except:
    print("Azure openai connection error.")

start_time = time.time()

def generate_questions_from_kb(user_input, extracted_contents, batch_size=10):
    all_questions = []
    remaining_difficulties = user_input["difficulty_levels"].copy()
    total_questions = sum(remaining_difficulties.values())
    message_history = []
    
    # Set to track unique questions
    unique_questions_set = set()

    # This list will hold all previous questions to help avoid duplication
    previous_questions = []

    # Create the tqdm progress bar
    progress_bar = tqdm(total=total_questions, desc="Generating Questions", dynamic_ncols=True)

    while total_questions > 0:
        current_batch_size = min(batch_size, total_questions)
        
        # Update user_input with remaining difficulties
        current_user_input = user_input.copy()
        current_user_input["difficulty_levels"] = remaining_difficulties

        file_prompt= f"""
        Generate {current_batch_size} unique question and answer pairs based on the user input.
        Make sure each question is unique and non-repetitive, both in terms of the question content and type.
        Strictly Avoid generating similar questions from previous questions.

        Avoid repeating any previous questions: {json.dumps(previous_questions, indent=2)}

        User Input: {json.dumps(current_user_input, indent=2)}

        Please ensure that all questions cover a broad range of subtopics and difficulties as described. Do not repeat previous questions.

        Extracted Contents: {extracted_contents}

        Use the user inputs and extracted contents to create questions that cover a broad range of subtopics and difficulties as described. Ensure the questions match the provided difficulty levels and formats, and cite the relevant paragraph/data from the Extracted contents.

        # Steps

        1. Understand Parameters:
          - Topic: The main subject area of the questions.
          - Subtopics: Specific areas under the main topic to focus on.
          - Total Number of Questions: Total count of questions to generate.
          - Difficulty Levels: Distribution of questions across difficulty levels (easy, medium, hard).
          - Types: Format of the questions (MCQ, Case Study, True or False, Fill Ups, Find the Code Output (Should have choices), Find the Error (Should have choices)).
          - Extracted Contents: The data from which to generate the questions.

        2. Generate Questions:
          - Distribute questions across subtopics.
          - Ensure the correct number of questions per difficulty level.
          - Format each question to match the specified type.
          - Utilize the extracted contents to create questions.
          - Add a citation for each question referencing the relevant paragraph/data from the extracted contents.
          - Strictly Avoid hallucination and ensure the generated questions are grounded in the provided information.

        3. Provide Answers:
          - For each question, generate a corresponding answer.
          - Ensure accuracy and alignment with the difficulty level and type.
          - Include the citation for the content source from extracted contents.

        # Output Format

        The output should be a JSON object containing the generated question and answer pairs. Each question should have a unique identifier, and the corresponding answer should be clearly linked, along with a citation.

        Output JSON Sample:
        {{
          "questions": [
            {{
              "id": 1,
              "topic": "Full Stack Development",
              "subtopic": "ReactJs",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is [MCQ Example Question]?",
              "choices": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "Option A",
              "citation": "[Citation for the extracted content]"
            }},
            {{
              "id": 2,
              "topic": "Full Stack Development",
              "subtopic": "Python",
              "difficulty": "hard",
              "type": "Case Study",
              "question": "Describe [Case Study Example Question]?",
              "choices": [],
              "answer": "Expected Answer of Case Study",
              "citation": "[Citation for the extracted content]"
            }}
            ... (additional questions follow the same structure)
          ]
        }}

        # Examples

        Output JSON:

        {{
          [
            {{
              "id": 1,
              "topic": "Mathematics",
              "subtopic": "Algebra",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is the value of x if 2x + 3 = 7?",
              "choices": ["1", "2", "3", "4"],
              "answer": "2",
              "citation": "The value of x in the equation 2x + 3 = 7 can be found by subtracting 3 from 7, resulting in 2x = 4, and then dividing by 2 to get x = 2."    }},
            {{
              "id": 2,
              "topic": "Mathematics",
              "subtopic": "Geometry",
              "difficulty": "easy",
              "type": "MCQ",
              "question": "What is the area of a triangle with base 4 and height 3?",
              "choices": ["6", "8", "10", "12"],
              "answer": "6",
              "citation": "[Citation for the extracted content]"
            }}
            ...(additional questions follow the same structure)
          ]
        }}

        # Notes

        - Ensure that all generated unique questions are relevant to the specified subtopics and difficulty levels  and are generated from the extracted contents.
        - For MCQs, provide a balanced set of distractors that are plausible and well thought out.
        - The total number of questions should precisely match the sum of questions across all specified difficulty levels.
        - Ensure the format adheres strictly to the type specified in the input.
        - Include citations for each question to reference the extracted content properly.
        - Strictly you should not hallucinate and provide questions that are not present in the extracted content.

        """

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
            {"role": "user", "content": file_prompt},
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
                
                for question in batch_questions:
                    question_text = question["question"]  # Hash only the 'question' field
                    question_hash = hashlib.md5(question_text.encode('utf-8')).hexdigest()

                    # If the question is not in the set (not a duplicate), add it to the set and proceed
                    if question_hash not in unique_questions_set:

                        if remaining_difficulties[question['difficulty']] > 0:
                            unique_questions_set.add(question_hash)
                            all_questions.append(question)
                            previous_questions.append(question['question'])

                            remaining_difficulties[question['difficulty']] -= 1
                            total_questions -= 1

                            # Update progress bar
                            progress_bar.update(1)

                            # # Write current questions to a temporary file for real-time checking
                            # with open('temp_questions.json', 'w') as temp_file:
                            #     json.dump({"questions": all_questions}, temp_file, indent=2)

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

    if len(unique_questions_set) != user_input["total_number_of_questions"]:
        error_message = f"Expected {user_input['total_number_of_questions']} unique questions, got {len(unique_questions_set)}"
        print(error_message)  # Raise an exception with a descriptive message

    # Check that the difficulty distribution matches
    final_difficulty_counts = {k: 0 for k in user_input["difficulty_levels"].keys()}
    for question in all_questions:
        final_difficulty_counts[question['difficulty']] += 1

    if final_difficulty_counts != user_input["difficulty_levels"]:
        error_message = f"Expected difficulty levels: {user_input['difficulty_levels']}, but got {final_difficulty_counts}"
        print(error_message) 

    # Recalculate IDs
    for i, question in enumerate(all_questions, 1):
        question['id'] = i

    return all_questions, final_difficulty_counts


user_input = {
  "topic": "Prequin Institutional Allocations",
  "subtopics": [
"Institutional investor asset allocation trends",
"Alternatives allocation growth",
"Endowment and foundation investment strategies",
"Insurance company portfolio allocations",
"Public and private pension fund investments",
"Superannuation fund asset allocation",
"Private equity allocation increases",
"Real estate investment trends",
"Infrastructure and private debt allocations",
"Hedge fund allocation changes",
"Impact of interest rates on pension funding status",
"Defined benefit vs defined contribution pension plans",
"Regulatory influences on institutional allocations",
"Cash and fixed income allocations",
"Portfolio diversification strategies"
],
  "total_number_of_questions":50 ,
  "difficulty_levels": {"easy": 25, "medium": 15, "hard": 10},
  "types": ["MCQ","Case Study","True or False","Fill Ups","Find the Code Output","Find the Error"],
}


extracted_contents = """
Institutional Allocation Study 2024 1
Institutional Allocation
Study 2024
Insights +
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 2
Key findings
Institutions increased their alternative 
allocations to a fifth of their portfolio
in 2023 
The weighted average for alternatives surged 
by 4.5 percentage points, up from 15.1% in 
2019 to nearly 20% (19.6%) in 2023. Individual 
alternative assets also experienced growth, 
with private equity comprising 6.9% of 
the total portfolio, real estate 3.1%, hedge 
funds 6.4%, and infrastructure 2.1%. The 
weighted average allocation for private debt 
remained relatively stable over the period, 
hovering at 0.9%.
Insurance allocations to alternatives are 
the smallest among all institutions 
Among all institutional investor segments, 
insurance companies have the smallest 
weighed average allocation to alternatives 
(5.8%). Real estate (3.3%) makes up 
the largest portion, more than double 
that of private equity (1.5%). On average, 
infrastructure (0.5%), private debt (0.3%), 
and hedge funds (0.2%) attract the 
smallest allocations.
Endowment and foundation allocations to 
alternatives dominated by private equity
Endowments allocate close to half of their 
total assets (46.5%) to alternatives, with 
private equity taking the lion’s share at 
23.8%. Hedge funds, which made up the 
largest allocation in 2019, now constitute 
14.8%. For foundations, both private equity 
and hedge funds attracted an equal 
alternative allocation of 27.7% in 2023. 
Notably, in 2019 foundations allocated less to 
private equity than they did to hedge funds.
Private pension allocations skew to 
real estate, while public pension funds 
are more inclined toward private 
equity with exposure to private debt 
and infrastructure
Alternatives make up nearly a fifth (19.1%) 
of aggregate private pension AUM, with 
real estate (7.4%) comprising the largest 
portion of investor portfolios. Conversely, 
nearly all public pension funds (92%) have 
exposure to alternatives, with a weighted 
average of 27.2%. Despite real estate being 
the most popular investment type for 
public plans (85.4%), just over half (54.3%) 
invest in private equity, which is larger than 
real estate in terms of weighted allocation. 
Notably, out of all investor groups, public 
funds have the greatest portion invested in 
nfrastructure (31.6%) and private debt (30%).
1 2
3 4
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 3
Global Institutional Allocation 
Study 2024 
How asset allocation has 
changed for institutional 
investors globally since 2019
Asset allocation data can provide an insight into how institutional investors 
are strategically positioning portfolios for the coming years. Of course, many 
institutions set strategic allocations during periodic reviews, but many investors 
also react to market conditions in the short-to-medium term and hold out-ofcycle reviews in the face of major regime change (e.g. the COVID-19 pandemic, the 
recent rise in interest rates). This study looks at how asset allocation has changed 
across a five-year period for institutional investors globally.
The overall mix of allocation will differ according to each individual 
institutional investor, but there are common threads such as source of funds (e.g. 
donations or government funding), presence, size and timing of liabilities (pension 
payments), investment horizon, regulatory/government mandates or limits, and 
location. Institutional investors as defined in this report include endowments, 
foundations, insurance companies, public sector pension funds, private sector 
pensions, sovereign wealth funds, and superannuation funds. 
For the institutional market as whole, average allocation to alternatives 
has increased from 18.4% to 20% over the last five years (Fig. 1.1). The number of 
investors that meet Preqin’s survey criteria has almost doubled in that time, from 
2,147 to 4,255 institutions, raising the total assets under management (AUM) from 
$13.5tn to $21.1tn. This obviously gives Preqin even more robust data across various 
investor types and geographical regions. For historical analysis, the full sample of 
data is used as it was not necessary to focus only on investors present in both 
sample periods (2019 and 2023) to gauge changes in asset allocation. The direction 
and magnitude of change toward asset allocation is very similar in this subgroup 
(data available in data pack). 
Within this shift to private assets, the commitment to private equity 
(including venture capital) has risen by 1.5 percentage points (ppts) to 5.4% of total 
allocation. Private debt and infrastructure achieved minimal gains – standing at 
0.8% each in 2023, while real estate fell slightly from 7.6% to 7.3% and hedge fund 
allocation was down 0.1ppt to 5.5%.
Weighted average allocation, which accounts for the total AUM of institutional 
investors and provides a more accurate representation of how total aggregate 
assets are flowing, points to an even greater growth in alternatives, jumping 
4.5ppts to 19.6%. Total allocation has risen in almost all asset classes, reaching 
6.9% for private equity, 3.1% for real estate, 6.4% for hedge funds, and 2.1% for 
infrastructure. The outlier is private debt, whose weighted allocation percentage 
has remained flat.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 4
The median institutional investment in alternatives
Not all institutions commit to every individual alternative asset class. Using data 
only from those that allocate to each particular asset class gives us the median 
allocation change over our five-year period. This median allocation (i.e., by only 
investors in a particular asset class) has risen broadly in line with the average 
overall allocation (i.e., by all investors), with alternatives’ median allocation up from 
Alternatives Equities
20.0%
38.2%
28.9%
9.3%
5.4%
7.3%
5.5%
3.5%
Total AUM:
$21.1tn
Investors: 4,255
0.8%
0.8%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
18.4%
8.1%
38.2%
32.2%
3.9%
7.6%
5.6%
3.1%
Total AUM:
$13.5tn
Investors: 2,147
0.6%
0.7%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
19.6%
7.5%
30.4%
39.5%
6.9% 3.1%
6.4%
2.8%
Total AUM:
$21.1tn
Investors: 4,255
0.9%
2.1%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
15.1%
5.4%
27.6%
49.5%
4.3%
2.7%
2.5% 6.0%
Total AUM:
$13.5tn
Investors: 2,147
0.9%
1.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 1.1: Global institutional allocation to alternatives grows to 20% of total portfolios
Asset allocation across time, 2019 and 2023
Simple average 2023 institutional asset allocation Weighted average 2023 institutional asset allocation
Simple average 2019 institutional asset allocation Weighted average 2019 institutional asset allocation
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 5
16.4% to 19.1% (Fig. 1.2). Private equity has seen the largest median jump from 4.5% 
of portfolios to 7.2%. In these same parameters, private debt and infrastructure 
now make up 2.3% and 3.3% of portfolios respectively, both up on 2019. Real 
estate has seen the most muted gain in allocation, while hedge funds have seen a 
1.1ppt increase.
Looking forward to future allocation
Survey data can help to suggest how allocations might change in the medium 
and long term. Preqin’s Investor Outlook1
 helps highlight the reasons investors are 
allocating to private assets in the first place but also provides a gauge for strategic 
asset allocation moving forward. In particular, as of November 2023, private equity, 
infrastructure, and private debt attracted the most net positive sentiment around 
increases in allocations (Fig. 1.3). Venture capital (VC) and natural resources told 
a more mixed story: a larger proportion of investors were looking to decrease 
allocations here, but overall investors were still planning net greater allocations. 
Hedge funds is the only asset class to have net negative sentiment around 
future allocations.
1 https://www.preqin.com/insights/research/investor-outlooks/investor-outlook-h1-2024
0
5
10
15
20
Alternatives Private equity Private debt Real estate Hedge funds Infrastructure
(%)
2019 2023
0%
20%
40%
60%
80%
100%
Private equity Venture capital Private debt Hedge funds Real estate Infrastructure Natural
resources
Proportion of investors
Increase allocation Maintain allocation Decrease allocation
Source: Preqin Pro
Source: Preqin H1 2024 Investor Outlook
*For more details on the Preqin sample data and filters, please download the data pack.
Fig. 1.2: The median institution is increasing allocations across individual private assets 
Median allocation among institutions in each private asset class, 2019 and 2023 
Fig. 1.3: LPs plan increases in allocation to private equity, private debt, and infrastructure
Investors' intentions for their alternatives asset allocations over the longer term
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 6
Why have alternatives generally become more attractive over the past few 
years – and why is there a continued expectation for growth? There are a few 
possible reasons:
• Hunt for higher risk-adjusted returns: Preqin’s quarterly index suggest that 
private equity and VC net of fees have outperformed public equities markets 
between 2008 and 2023. At the start of this period the financial crash showed 
the downside protection of private equity capital, but also kick-started a 
lengthy period of low interest rates that increased the use of leverage and 
expanded multiples. Projecting forward, long-term asset allocation will 
be shaped by how LPs believe GPs can handle a sustained higher interest 
environment and its potential impact on returns. For VC in particular, recent 
performance is likely impacting planned allocations - for the past 18 months 
the Preqin index has been falling and currently shows no sign of recovery. 
This partly explains LPs’ muted sentiment toward private equity. Hedge funds2
are also associated with high risk-adjusted returns but have suffered some 
heavy outflows over the medium term, while remaining a sizeable part of 
investor portfolios. Relative underperformance to public market indices across 
multiple hedge funds strategies has likely played a part in the expected fall in 
planned allocations.
• Diversification benefits: Low correlation to public markets and 60/40 
portfolios is a well-known benefit of private asset investments. Preqin’s 
analysis3
 suggests private equity and private debt offer the fewest 
diversification benefits, while VC offers a little more diversification for investor 
portfolios dominated by public assets. Real assets offer the most benefit, 
and include real estate and natural resources. However, the real asset for 
diversification is infrastructure, which has been the steady performer on an 
index level and less exposed to tail risk events when compared with real 
estate. 
• Inflation hedge: In a high-inflation environment, real assets are also expected 
to perform well, as income such as rents also tend to rise. However, use of 
leverage and valuations in a low-interest environment hurts the underlying 
asset values. Currently, real estate globally has relatively not performed well, 
with specific areas such as offices impacted negatively by structural change, 
for instance the move to hybrid working. Real estate has been a popular asset 
class in the past with institutional pension funds, but our survey suggests a 
fifth of investors will decrease their allocations here over the longer term. 
• Income generation:
4 Yield was highly sought after in a period of low interest 
rates, and private capital assets, such as real estate and infrastructure, were 
seen as the alternatives to generate higher returns. Traditional fixed income 
has provided higher yield of late, but private debt has done even better, 
especially as rates have risen over the past two years and offered double-digit 
return opportunity for debt funds. However, private debt’s long-term role in 
LP portfolios will likely be determined by its performance when rates fall, and 
how managers react to a large-scale credit event.
Despite the tailwinds for alternatives, one possible headwind for greater allocation 
is the denominator effect. This phenomenon describes how a fall in valuation 
of one part of a portfolio will decrease the whole portfolio value, and by effect, 
increase the allocation of other parts of the portfolio (i.e., alternatives) that have 
not experienced the same drop in valuation. This could lead to an over-allocation 
2 https://www.preqin.com/insights/research/research-notes/whats-driving-the-hedge-fundsexodus
3 https://www.preqin.com/insights/research/reports/preqins-state-of-the-market-h1-2024
4 https://www.preqin.com/insights/research/reports/strategy-in-focus-income-generation
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 7
where institutional investors may act to reduce exposure (e.g., pull back on forward 
commitments). However, if underperforming assets are quick to re-adjust (e.g., 
public equity markets), private capital allocation may unintentionally fall in the 
medium term due to shorter term reactionary measures. Moreover, LPs would be 
more cautious about investing to the edge of limit thresholds to avoid potentially 
costly remedial actions and prefer to have greater runway to cater for large public 
market swings, limiting allocation gains.
Overall, the trend in institutional asset allocation will also be a useful guide 
to potential high-net-worth investors’ asset mix. The following chapters examine 
the data to pinpoint emerging trends and assess how institutional investor 
allocations are changing.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 8
Endowments and foundations
Both endowments and 
foundations have significant 
exposure to alternatives 
assets with equity-like 
return profiles
Endowments and foundations have higher percentage allocations to alternatives 
than other institutional investors. They are quite similar but have a key difference 
in their underlying objective for investment: while endowments are tied to, and 
support the needs of, a specific institution, such as a hospital or a university, 
foundations are much broader in scope, supporting, say, a community. But they do 
both have longer-term investment horizons, have few restrictions and regulations 
around portfolio allocations and limits, and enjoy tax-exempt status in some 
jurisdictions. As such, they are significant investors in private capital, particularly 
in asset classes with historically higher return profiles, such as private equity 
(including venture capital) and hedge funds. They have considerably less significant 
exposure to public market income-focused assets.
Using our investor data from 2019 and 2023 and selecting only investors that 
appear in both periods, we can understand the historical trends underpinning how 
and where these investor groups’ allocations are changing. For current trends, the 
full sample of all relevant investor data was used to determine allocation trends.5
Historical trends: endowments replace public equity and hedge funds 
with private equity
For endowments, average asset allocation to alternatives has increased slightly 
over the period 2019 to 2023, from 29.4% to 31.2%. This boost has largely been 
allocation away from public equity. Interestingly, hedge funds exposure has 
reduced significantly, going from 15.9% to 12.5%, with private equity seemingly the 
main beneficiary here too. Granted, this could be a result of market movements 
and the rise or fall of specific asset classes, but significant shifts in commitment 
will be tied to wider changes to allocation targets.
When using weighted averages, endowments’ allocation to alternatives is 
even greater, rising by 2.5% from 2019 to make up 39.2% of total portfolio weighting 
in 2023. This is the largest allocation for any single investor group. Here too, this 
increase is the result of reduced equity portfolios, but also a reduction in fixedincome allocation. The results also confirm that a dip in allocation to hedge funds 
has benefited private equity, with the latter gaining most of hedge funds’ 4.2% 
reduction. Note that the weighted-average figure will be significantly impacted by 
the size of large US endowments.
5 This was unnecessary for the all investors analysis in section 1 as the sample size was 
sufficient not to be significantly impacted by the larger sample in 2023.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 9
Alternatives Equities
31.2%
39.6%
17.2%
7.2%
13.5%
4.2%
12.5%
4.8%
Total AUM:
$119bn
Investors: 137
0.5%
0.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
29.4%
42.5%
16.8%
7.0%
8.1%
15.9%
4.3% 4.4%
Total AUM:
$91bn
Investors: 132
0.6%
0.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
39.2%
33.2%
14.0%
6.9%
18.2%
5.8%
13.5%
6.6%
Total AUM:
$119bn
Investors: 137
1.2%
0.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
36.7%
36.5%
16.9%
5.1% 11.6%
17.7%
5.6%
4.8%
Total AUM:
$91bn
Investors: 132
1.4%
0.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 2.1: Endowments plough into private equity but cut hedge fund allocations 
Asset allocation across time for subsample, 2019 and 2023 
Simple average 2023 endowment allocation Weighted average 2023 endowment allocation 
Simple average 2019 endowment allocation Weighted average 2019 endowment allocation 
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 10
Today’s picture: Private equity dominates the alternative book for endowments
The full study sample of 403 endowments’ weighted-average allocation shows 
almost half (46.5%) of their $439bn AUM allocated to alternatives (Fig. 2.2). The 
top allocations are private equity (23.8%) and hedge funds (14.8%), followed by real 
estate (6.5%), private debt (0.6%), and infrastructure (0.4%).
Almost 90% of endowments have exposure to alternatives, second only to public 
equity (Fig. 2.3). More than two-thirds (67.5%) invest in private equity, 65.3% in 
hedge funds and 58.3% in real estate. This is considerably more than private debt 
(14.6%) and infrastructure (5.7%), with many investors allocating nothing at all to 
these classes. 
Source: Preqin
Fig. 2.2: Alternatives are nearly half the allocation of aggregate
endowment AUM
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
29.5%
11.7%
4.8%
7.0%
23.8%
0.6%
6.5%
14.8%
0.4%
46.5%
Total AUM:
$439bn
Investors: 403
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
0
20
40
60
80
100
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 2.3: Nearly 90% of endowments have allocation to alternatives
Portion of investors that have exposure to individual asset class, 2023 
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 11
Historical trends: larger foundations make alternative bets in private equity 
and hedge funds
Foundations' average allocation to alternatives is also up, from 21.2% in 2019 to 
23.9% in 2023 (Fig. 2.4). However, the same period has seen a fall in allocations to 
cash and other non-categorized investments, alongside a slight reduction in fixed 
income. Private equity has experienced a larger increase in its role in the average 
portfolio. Private debt is also creeping up slightly, while there has been a fall in 
hedge funds and real estate investment contribution.
The weighted average results differ significantly, with larger assets flowing 
and/or growing into alternatives. More than a third of portfolio (34.8%) assets 
are allocated here, up nearly 8% over the past five years. Allocations to public 
equity and the ‘other’ category have fallen relative to aggregate AUM and, as with 
endowments, private equity and hedge funds are the major beneficiaries of this 
shift. However, aggregate real estate contribution to the average portfolio fell in the 
five-year period, in line with the simple average results.
Alternatives Equities
23.9%
46.6%
16.3%
9.1%
9.0% 2.0%
5.5%
4.1%
Total AUM:
$285bn
Investors: 283
0.6%
0.5%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
21.2%
47.0%
16.7%
10.1%
5.6%
2.6%
4.9% 12.0%
Total AUM:
$206bn
Investors: 283
0.4%
0.4%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
34.8%
36.0%
14.6%
9.2%
15.9%
2.9%
15.0%
5.4%
Total AUM:
$285bn
Investors: 283
0.3%
0.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
27.0%
44.0%
14.3%
10.4%
10.6%
3.5%
12.1%
4.2%
Total AUM:
$206bn
Investors: 283
0.3%
0.4%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 2.4: Private equity grows for all foundations, but larger institutions also back hedge funds 
Asset allocation across time, 2019 and 2023
Simple average 2023 foundation allocation Weighted average 2023 foundation allocation 
Simple average 2019 foundation allocation Weighted average 2019 foundation allocation 
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 12
Today’s picture: private equity and hedge funds make up a quarter of 
foundation investors' AUM 
In the full sample (996 foundations globally, with $703bn AUM) weighted-average 
allocation results show alternatives make up 27.7% of total aggregate allocation 
(Fig. 2.5). Private equity (12.2%) and hedge funds (12.2%) add up to nearly a quarter 
of total AUM, with real estate allocated 2.5%, private debt 0.5% and infrastructure 
0.3%. Given foundations and endowments are very similar, it would not be a big 
jump to assume foundations are using endowments and their historical growth as 
a benchmark indicating their own way forward.
Source: Preqin
Fig. 2.5: Alternatives make up more than a quarter of aggregate
foundation AUM
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
42.9%
13.6%
3.4%
12.2%
12.2%
0.5%
2.5%
12.2%
0.3%
27.7%
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
Total AUM:
$705bn
Investors: 996
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 13
Almost three-quarters (74.7%) of foundations have exposure to alternatives, second 
only to public equity (Fig. 2.6). More than half invest in private equity (56.5%) and 
hedge funds (50.5%), with real estate not far behind (41.3%). Private debt (16.6%) 
and infrastructure (5.5%) are less attractive to foundations, with many investors 
allocating nothing to these classes. The potential for further growth in alternatives 
will likely involve the significant number of foundations that are yet to invest in any 
one particular asset.
0
20
40
60
80
100
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 2.6: Nearly 75% of foundations invest in alternatives
Portion of investors that have exposure to individual asset class, 2023 
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 14
Insurance companies
Insurers uncertain about 
alternatives in portfolios 
Insurance companies are unique investor institutions. By investing their customers’ 
premiums, their portfolio objectives are invariably linked to generating income and 
returns to finance those same policy-holders' claims – while simultaneously trying 
to earn additional cash flow and build up reserves.
However, the approach will vary according to their individual insurance 
specialty – liability structures differ depending on whether the category of 
insurance is life, health, property, or casualty. Moreover, regulation of the insurance 
industry, which has a significant focus on risk management, restricts its scope 
to invest (See Preqin’s report Fundraising from insurance companies: A guide 
to raising capital).6 For instance, solvency capital requirements (SCR) under the 
EU’s Solvency II directive require insurers to hold capital to cover potential losses 
in portfolios, and this capital will differ depending on the asset class invested. 
Inevitably, this will impact insurance companies’ asset allocations.
This need for insurers to match portfolios against liabilities has skewed 
historical allocations heavily toward fixed income. However, the low-yield 
environment of the 2010s has more recently persuaded investors away from 
primarily fixed-income investment and led them to consider equities and 
alternatives as a way to both diversify the risk and potentially generate greater 
returns. More recently, higher interest rates have caused long-duration liabilities 
to decline, thereby improving insurers’ capital position. On the other hand, non-life 
insurers have to contend with higher-than-expected claim values because of an 
inflationary environment that could cut into reserves – while also benefiting less 
from the higher interest rates.7
As in previous chapters of this report, current insurance company data 
is used to determine current trends in allocation, while a sub-sample of those 
investors with data from both 2019 and 2023 is used to highlight historical 
trends and changes.
Historical trends: alternative allocations for insurers fall slightly
Insurance companies’ average allocation to alternatives has fallen from 5.9% in 
2019 to 5.7% in 2023 (Fig. 3.1). However, most other asset classes have also seen a 
reduction, with the public equity proportion of insurer portfolios taking the greatest 
hit at 3.1%. Insurers appear to be moving into cash or cash-like instruments, 
whose average allocations nearly doubled from 4.7% to 10%. Higher interest rates 
for cash investments is a likely cause of this shift, alongside the liquidity benefits 
and favorable SCR treatment. By comparison, allocation changes to underlying 
alternative assets were minimal, with no class seeing a difference greater than 
0.3%. Within this were fractional declines in private equity and real estate, and 
equally fractional gains in private debt, infrastructure, and hedge funds.
6 https://www.preqin.com/insights/research/reports/fundraising-from-insurance-companies-aguide-to-raising-capital
7 International Association of Insurance Supervisors estimate the market to be $40tn at the end 
of 2023. https://www.iaisweb.org/uploads/2023/12/Global-Insurance-Market-Report-2023.pdf
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 15
When using weighted averages, the fall in alternatives allocation is more 
pronounced, from 7.5% to 5.8% of the portfolio. Unlike the average portfolio, total 
aggregate capital is increasing in fixed income, reaching nearly three-quarters 
of entire portfolios in 2023 (74.6%). Cash is also up from 3.9% to 5.5%, which is 
similar to the average figure but less pronounced. Within alternatives, allocations 
fell for all classes, except infrastructure. Private debt was the biggest faller, 
from 1.5% to 0.2%.
Alternatives Equities
5.7%
9.7%
63.5%
11.1%
0.8% 3.3%
0.8%
10.0%
Total AUM:
$2.1tn
Investors: 61
0.3%
0.4%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
5.9%
12.8%
64.3%
12.3%
1.1%
3.5% 0.6%
4.7%
Total AUM:
$1.9tn
Investors: 61
0.2% 0.4%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
5.8%
4.9%
74.6%
9.1%
1.4% 3.1%
0.7%
5.5%
Total AUM:
$2.1tn
Investors: 61
0.2%
0.1%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
7.5%
6.2%
73.2%
9.2%
1.8% 3.4%
0.6%
3.9%
Total AUM:
$1.9tn
Investors: 61
1.5%
0.2%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 3.1: Aggregate allocations to alternatives fall for insurers 
Asset allocation across time for subsample, 2019 and 2023 
Simple average 2023 insurance allocation Weighted average 2023 insurance allocation
Simple average 2019 insurance allocation Weighted average 2019 insurance allocation
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 16
Today’s picture: real estate is the largest alternative investment in 
insurer portfolios
For an up-to-date snapshot of allocation, the full study sample shows the 
weighted average allocations of 176 insurance companies, with a total $4.7tn AUM 
(Fig. 3.2). This is approximately 12% of the aggregate insurance market data total 
assets.2 It is no surprise that fixed income dominates, at 70.2% of total portfolios. 
This reflects the ability to duration-match liabilities, as well as favorable capital 
charge treatments under regulatory requirements such as Solvency II.
Alternatives make up 5.8% of total aggregate allocation, with real estate 
(3.3%) the largest portion of investor portfolios. The next biggest is private equity 
(1.5%), followed by infrastructure (0.5%), private debt (0.3%), and hedge funds 
(0.2%). The higher allocation to ‘Other’ at 13% highlights assets that do not fit into 
the larger categories or were reported as ‘Other’ from the source material and can 
range from derivatives to undefined mutual funds.
Source: Preqin
Fig. 3.2: Alternatives remain a small portion of insurers’ portfolios 
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
7.2%
70.2%
3.7%
13.0%
1.5%
0.3%
3.3%
0.2%
5.8% 0.5%
Total AUM:
$4.7tn
Investors: 176
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
A large share (73%) of insurers allocate to alternatives as whole (Fig. 3.3), but 
this is significantly tilted toward real estate exposure (65.3%). This is supported 
by more favorable capital charges. For example, under the Solvency II Directive, 
property has a lower associated charge of 25% (value of regulatory capital 
required as a percentage of the real estate portfolio) when compared with other 
alternatives. This charge is even lower for real estate debt, especially senior debt 
backed by collateral.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 17
The number of insurance companies investing in the other alternatives drops 
heavily after that with just over a quarter (27.3%) allocating to private equity, which 
does have a significant SCR under Solvency II of 49% (vs. 39% for developedmarket equities). Less than a fifth of firms invest in the remaining categories, 
including private debt (16.5%), infrastructure (13.6%) and hedge funds (11.4%). Going 
forward, these numbers are unlikely to change significantly in this environment of 
high interest rates and capital costs associated with illiquid instruments. 
0
20
40
60
80
100
120
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 3.3: Insurers heavily favor real estate in alternatives portfolio 
Portion of insurers that have exposure to specific asset classes, 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 18
Pension funds
Higher rates may slow 
the rise of alternatives for 
private pensions that are 
now fully funded
Pension funds are the largest group of institutional investors by number in 
Preqin’s database and can be split into many different categories. The three major 
types as defined by Preqin are private pension funds, public pension funds, and 
superannuation funds.
The first two categories are distinguished by the organization that has 
responsibility over the pension fund and where the liability lies – that is, a 
private company or governmental or state-affiliated institution. The third 
category, superannuation, is a group of funds largely based in Australia and is an 
investment vehicle, rather than the distribution vehicle that pays out funds in 
retirement. The size of the pension market is significant, making up $51tn in assets 
just in the OECD.8
Pension funds must follow regulatory guidelines according to their 
jurisdiction, and these can include rules around allocation and transparency. 
There are two types of public and private pensions: defined contribution (DC) 
and defined benefit (DB) pensions. These differ in terms of funding and liability 
structure, and therefore influence the overall strategic asset allocation.
For defined contribution plans, employees and employers both contribute 
to the fund, but the employee has control over which pension plan strategy to 
invest in and takes on the investment risk because the pension pays out based 
on contributions. This balance of risk influences the asset allocation of portfolios. 
In general, pension plans have been influenced by governments to invest in or 
increase allocations to private assets. The UK’s Long-Term Asset Fund and the EU’s 
European Long-Term Investment Funds 2.0 are fund structures that will support 
DC pension investment into alternatives. In terms of active allocation, in the UK, 
the Mansion House Compact9 commits schemes to allocating 5% of their default 
funds to unlisted equities by 2030.
For DB plans, contributions are made by both the employer and employee, 
but the employer takes on the investment risk by agreeing to pay defined benefits 
when an employee retires, and so has the responsibility to manage those assets. 
This responsibility can be outsourced to investment managers or trustees to 
ensure plans are fully funded (where the value of assets equals or exceeds 
liabilities). Management of liabilities has given rise to asset liability management 
(ALM) strategies, where assets are selected to match the cash flows with 
expected liabilities and are focused on duration matching. Therefore, interest rates 
play a critical role because lower rates increase the value of liabilities and vice 
versa. Allocation is also influenced by the maturity of the plan, for example, the 
average duration of liabilities might be below a benchmark. The more mature a 
scheme, the more emphasis is placed on cash flow, a phase known as de-risking. 
Allocations can change dramatically to match cash flows more closely and this 
means a reduction in growth assets.
8 https://www.oecd.org/daf/fin/private-pensions/globalpensionstatistics.htm
9 https://www.gov.uk/government/collections/mansion-house-2023
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 19
The primary indicator used to gauge the health of a DB plan is its funded status. 
A plan is deemed fully funded when the current value of its assets equals or 
exceeds its liabilities, and unfunded if it does not. The rising interest rates over the 
past two years partly explain the rebound in fund status in DB plans (Fig. 4.1). The 
funded status can also influence decision-making around asset allocation. This 
was the case when pension plans were unfunded for multiple years, prompting 
an increase in liability driven investing because of its more dynamic management 
of interest rate risk and inflation risk through hedging. Use of leverage has also 
become more common as underfunded pension plans increased their allocation 
toward growth assets to help reduce deficits over time. This included allocation 
toward alternative assets, especially high-return-oriented assets. The following 
60%
70%
80%
90%
100%
110%
120%
130%
140%
2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023
Aggregate funded status
US Fortune 1000 UK DB pensions
Source: WTW's Fortune 1000 pension funded status analysis, January 2024; The Pension Protection Fund's (PPF) Purple Book 2023
Fig. 4.1: DB plans are fully funded and could give rise to de-risking – a headwind for alternatives
Aggregate pension plan funding levels, 2007 to 2023
analysis of the three main pension fund categories includes data from all relevant 
pension funds in 2023 to determine the current allocation trends. The historical 
allocation trends include a subset of this data where both 2019 and 2023 data is 
available for each institution to highlight how allocation trends have changed.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 20
Historical trends: alternative allocations grows for private pension funds 
For private pension funds, average asset allocation to alternatives has increased 
from 14.7% to 17.4% (Fig. 4.2) between 2019 and 2023. A large portion of that 
increase has come from a reduction in public equities, which has boosted 
allocation to all alternative asset classes. Private equity has seen the largest 
increase, up by 1ppt to 2.8% of the portfolio. However, other asset classes have 
also grown, with real estate a sizable 7.4% of the average portfolio and hedge funds 
5.6%. Infrastructure grew to 0.9% and private debt to 0.7%. When using weighted 
averages, the increase in private pension fund total allocation to alternatives is 
more significant, rising more than 5ppts to 20.4% of the weighted portfolio. In the 
aggregate, both fixed income and public equities shed weighting for the gain in 
alternatives. Private equity attracted the largest increase (2.6ppts), to reach 5.8%, 
with real estate up 1.8ppts to 8.5% (making it the largest single alternative) and 
hedge funds up 0.4ppt to 4.1%. 
Alternatives Equities
17.4%
8.3%
28.0% 43.4%
2.8%
7.4%
5.6%
2.9%
Total AUM:
$1.59tn
Investors: 596
0.7%
0.9%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
14.7%
31.6%
42.2%
9.6%
1.8%
6.9%
5.2% 1.9%
Total AUM:
$1.58tn
Investors: 596
0.7%
0.5%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
20.4%
25.1% 44.1%
8.1%
5.8%
8.5%
4.1%
2.3%
Total AUM:
$1.59tn
Investors: 596
0.7%
1.0%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
15.3%
29.4%
45.6%
7.6%
3.2%
6.7%
3.7% 2.2%
Total AUM:
$1.58tn
Investors: 596
0.8%
0.8%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 4.2: Aggregate allocations to alternatives rise for private pension plans
Asset allocation across time for subsample, 2019 and 2023 
Simple average 2023 public pension allocation Weighted average 2023 public pension allocation
Simple average 2019 public pension allocation Weighted average 2019 public pension allocation
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 21
Today’s picture: real estate remains the largest alternative in private 
pension portfolios 
In the current 2023 allocation data, the full study sample shows the weighted 
average allocations of 1,785 private pension plans, representing $3.8tn in aggregate 
AUM (Fig. 4.3). The largest allocation is to fixed income investments (42.7%) that are 
well suited to income generation and cash flow matching within ALM strategies. 
However, a significant portion of allocation is invested elsewhere. Equity is strongly 
represented, which is a reflection of the increase in allocation of assets that are 
growth oriented rather than pure income generation. 
Alternatives make up nearly a fifth (19.1%) of aggregate private pension AUM, 
with real estate the largest portion of investor portfolios at 7.8%. This is likely 
because of real estate’s attractiveness for income generation and inflation hedging. 
The next largest class is private equity (5.6%), followed by hedge funds (4.2%). 
Infrastructure and private debt play a much more minor role but do amount, 
respectively, to $32bn and $25bn in absolute terms for the given sample. 
Source: Preqin
Fig. 4.3: Real estate is largest alternative asset class in private pension 
portfolios 
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
26.5%
42.7%
3.5%
8.0%
5.6%
0.7%
7.8%
4.2%
0.8%
19.1%
Total AUM:
$3.8tn
Investors:
1,785
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
Most private pension funds (86%) have exposure to alternative asset classes 
(Fig. 4.4) with real estate the most popular, attracting two-thirds of investors 
(67.7%). More than half of private plans with allocations have committed to 
hedge funds, and 44% are in private equity, ahead of private debt (23.4%) and 
infrastructure (19.7%). 
Looking forward, the funded status of DB private plans will likely impact 
future growth in alternatives. There will be some natural limits due to the desire to 
maintain liability matching, and because the cost of leverage has increased. Cash 
management and the institution’s ability to manage liquidity will also become an 
increasing focus. However, DC schemes’ allocation to alternatives, while currently 
low, will likely rise if boosted by government initiatives. A sustained higher interest 
rate environment may slow the rise in alternatives as plans are now fully funded, 
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 22
although there may be more opportunities once rates fall. Relative expectation of 
public equity will also be a consideration along with private equity (including VC) 
and hedge funds. However, pensions in the private space are smaller than public 
plans and de-risking through annuities is a more likely path that could limit the 
overall aggregate allocation to alternatives. 
Historical trends: nearly 7% of growth in alternatives allocation for total 
public pension assets
Public pension funds’ average asset allocation to alternatives increased from 18.7% 
to 23.2% (Fig. 4.5) between 2019 and 2023. This growth in alternatives and the 
absolute allocation are both higher than in private pension funds, which is partly 
explained by the fact that private pensions are more likely to be DC than DB.
The increase in public plans’ allocation to alternatives has come from a 
reduction in public equities and fixed income, which benefited all individual 
alternative asset classes except hedge funds. Private equity attracted the largest 
increase, up by 1.8% to become 5.2% of the portfolio, while private debt increased 
to 1.4% and infrastructure to 2.3%. Real estate also attracted gains to remain a 
sizable portion of the average portfolio at 10.2%.
When using weighted averages, the increase in private pension fund total 
allocation to alternatives is more significant, up by 6.8ppts to 27.8% of the 
weighted portfolio. Overall, fixed income, public equities and ‘other’ shed weighting 
for the gain in alternatives. The largest increase went to private equity, up 3.5ppts 
to 9.2%, while real estate remains the largest single alternative at 10.1%, up 1.8ppts. 
Infrastructure grew 1.1ppts to lift it to 3% of the average total portfolio, and private 
debt attracted minimal gains to comprise 1.7% of the total subsample. Hedge funds 
was the only alternative class to fall, down by 0.2ppt to comprise 3.2% of the 
total portfolio. 
0
20
40
60
80
100
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 4.4: More than half of private pension plans have allocations to hedge funds
Portion of private pensions investors with exposure to individual asset classes, 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 23
Alternatives Equities
23.2%
47.2%
23.8%
3.7% 5.2%
10.2%
3.9%
2.0%
Total AUM:
$2.4tn
Investors: 337
1.4%
2.3%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
18.7%
49.2%
26.9%
3.5%
3.4%
9.3%
3.9%
1.6%
Total AUM:
$2.1tn
Investors: 337
1.7%
3.0%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
27.8%
38.9%
28.8%
2.6% 9.2%
10.1%
3.2%
1.9%
Total AUM:
$2.4tn
Investors: 337
1.7%
3.0%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Alternatives Equities
21.0%
41.2%
28.8%
4.5%
5.7%
8.2%
3.4%
1.6%
Total AUM:
$2.1tn
Investors: 337
1.5%
1.9%
Fixed income Cash
Other Private equity Private debt Real estate
Hedge funds Infrastructure
Fig. 4.5: Alternatives make up over a quarter of total public pension assets 
Asset allocation across time for subsample, 2019 and 2023 
Simple average 2023 public pension allocation Weighted average 2023 public pension allocation
Simple average 2019 public pension allocation Weighted average 2019 public pension allocation
*For more details on the Preqin sample data and filters, please download the data pack. Source: Preqin Pro
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 24
Today’s picture: private equity the largest alternative in total public 
plan portfolios 
In the current 2023 allocation data, the full study sample shows the weighted 
average allocations of 831 public pension plans with a combined $8.3tn in AUM 
(Fig. 4.6). The largest allocation is to equities at 35%, followed by fixed income 
at 32.3%. Alternatives make up more than a quarter (27.2%) of aggregate public 
pension AUM, with private equity (10.1%) the largest single alternative asset, instead 
of real estate (8.6%). This differs when compared with the average weighted data 
for 2023 in Fig. 4.5, where real estate is larger than private equity allocation. This 
is not surprising due the larger sample size in Fig. 4.6 and also the strong growth 
in private equity allocation in the historical analysis. A similar or stronger historical 
trend toward private equity would likely be exhibited in the full sample as well if 
data was available. 
Hedge funds (4.2%) and infrastructure (3.2%) are the next biggest alternative 
allocations. Private debt is the smallest at 1.7%. Despite this low percentage, the 
private debt allocation from public pension funds is in fact the largest percentage 
allocation to the asset class for any institutional investor group in absolute terms, 
equating to $137bn for the public pension plans sample. 
Source: Preqin
Fig. 4.6: Private equity the largest alternative asset in public
pension portfolios
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
35.0%
32.3%
1.5%
3.6%
10.1%
1.7%
8.6% 2.9%
3.8%
27.2%
Total AUM:
$8.3tn
Investors:
831
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
Nearly all public pension funds (92%) have exposure to alternative asset classes 
(Fig. 4.7) with the most popular being real estate, where 85.4% of investors have 
exposure. The income generation and inflation hedge elements of real estate make 
it a popular investment strategy. Just over half (54.3%) of public pension funds 
invest in private equity, which is relatively low compared with real estate given the 
size of the private equity allocation. This implies that those who do invest in private 
equity allocate significantly more than they do to real estate. Hedge funds (37.7%) 
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 25
are not as popular with public plans as they are with private pension plans, but 
both private debt (30%) and infrastructure (31.6%) have a greater exposure than any 
of the other featured investor groups.
The trend for DB public plans will likely tend to mirror private plans in their 
growing allocation to alternatives, albeit with some natural limits due to a desire 
to maintain liability matching. Meanwhile the cost of leverage has also increased. 
However, it is likely they face less pressure to de-risk portfolios with government 
institutions backing such plans. Management of illiquidity within private equity 
(venture capital) will also be a factor in how the allocation will grow in comparison 
with public equity. 
0
20
40
60
80
100
120
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 4.7: Nearly all public pensions invest in alternatives
Portion of public pensions investors with exposure to individual asset classes, 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
Today’s picture: real asset allocation is highest with superannuation funds 
As superannuation schemes are based mainly in Australia, our sample is inevitably 
smaller, with only 2023 data considered for analysis. The full study sample is made 
up of 49 superannuation schemes globally, representing $626bn in aggregate 
AUM (Fig. 4.8).10 The largest allocation is to equities at 45.3%, although alternatives 
make up more than a quarter (26.9%) of aggregate superannuation AUM, which is 
a similar size allocation to that made by public pension schemes. However, fixed 
income allocation (13.8%) is significantly lower and cash equivalents is higher 
(12.3%) compared with the same group. 
10 Superannuation Funds of Australia estimate the total superannuation assets in the country to 
be AUD 3.7tn (approx. $2.5tn).
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 26
Real assets are a significant standout at 14.8% of the entire group portfolio, with 
real estate (7.5%) just pipping infrastructure (7.3%) as the top asset. The latter is a 
particularly attractive class in Australia, where the government offers taxation and 
other benefits for superannuation funds to invest. Private equity (5.9%) and hedge 
funds (5.2%) both also have significant allocations, with private debt the smallest 
class at 1.1%. 
Source: Preqin
Fig. 4.8: Real assets dominate alternative asset allocation for 
superannuation scheme portfolios
Weighted average asset allocation in 2023 
*For more details on the Preqin sample data and filters, please download the data pack.
45.3%
13.8%
12.3%
1.5%
5.9%
1.1%
7.5%
5.2%
26.9% 7.3%
Total AUM:
$626bn
Investors:
49
Alternatives Equities Fixed income
Cash Other Private equity
Private debt Real estate Hedge funds
Infrastructure
Nearly all superannuation funds (93.9%) have exposure to alternative asset classes 
(Fig. 4.9). Every alternative investor also has exposure to real estate (93.9%). The 
income generation and inflation hedge elements of real estate make it a popular 
investment strategy for superannuation funds. Notably, these funds also have the 
highest portion of institutions investing in infrastructure (77.6%).
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 27
The drop-off after that is significant when comparing the proportion of firms 
committing to higher absolute return type investments, with almost a third of 
schemes (32.7%) investing in private equity and even fewer in hedge funds (28.6%). 
Real assets appear to be the core focus of this investor type, although a fifth 
(20.4%) of superannuation schemes also invest in private debt.
0
20
40
60
80
100
120
Equities
Fixed income
Cash
Other
Alternatives
Private equity
Private debt
Real estate
Hedge funds
Infrastructure
(%)
Source: Preqin Pro
Fig. 4.9: Nearly all superannuation funds invest in real assets 
Portion of superannuation with exposure to individual asset classes, 2023
*For more details on the Preqin sample data and filters, please download the data pack.
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
Institutional Allocation Study 2024 28
Empowering the global
alternatives community with 
essential data and insights.
preqin.com
info@preqin.com
Related content
All rights reserved. The entire contents of Institutional Allocation Study 2024 are the Copyright of Preqin Ltd. No part of this publication or any 
information contained in it may be copied, transmitted by any electronic means, or stored in any electronic or other data storage medium, or printed 
or published in any document, report, or publication, unless expressly agreed with Preqin Ltd. The information presented in Institutional Allocation 
Study 2024 is for information purposes only and does not constitute and should not be construed as a solicitation or other offer, or recommendation 
to acquire or dispose of any investment or to engage in any other transaction, or as advice of any nature whatsoever. If the reader seeks advice rather 
than information then it should seek an independent financial advisor and hereby agrees that it will not hold Preqin Ltd. responsible in law or equity for 
any decisions of whatever nature the reader makes or refrains from making following its use of Institutional Allocation Study 2024. While reasonable 
efforts have been made to obtain information from sources that are believed to be accurate, and to confirm the accuracy of such information wherever 
possible, Preqin Ltd. does not make any representation or warranty that the information or opinions contained in Institutional Allocation Study 2024 are 
accurate, reliable, up to date, or complete. Although every reasonable effort has been made to ensure the accuracy of this publication, Preqin Ltd. does 
not accept any responsibility for any errors or omissions within Institutional Allocation Study 2024 or for any expense or other loss alleged to have arisen 
in any way with a reader’s use of this publication.
Asset Allocation: Cash Flow Management: Slowing Distributions 1
Asset Allocation:
Cash Flow Management:
Slowing Distributions
Insights + Asset Allocation: Outlook 2024 1
Insights+
Asset Allocation:
Unsmoothing private
capital returns
Fundraising from insurance companies: A guide to raising capital 1
Insights+
Fundraising from insurance 
companies: A guide to 
raising capital
Cash Flow Management: 
Slowing Distributions
Read now
Asset Allocation: 
Unsmoothing Private 
Capital Returns
Read now
Fundraising from 
insurance companies: A 
guide to raising capital
Read now
User License for Eric Warters
Carlyle Group [Eric.Warters@carlyle.com]
"""

# # Use the function
# start_time = time.time()

# all_generated_questions, final_difficulty_counts = generate_questions_from_kb(client, user_input, extracted_contents)

# # Calculate and print the response time
# end_time = time.time()
# response_time = end_time - start_time
# print(f"Total Response Time: {response_time:.2f} seconds")

# # Combine all questions into a single JSON object
# final_output = {"questions": all_generated_questions}

# # Write the content to a file
# with open(f'{user_input["topic"]}.json', 'w') as file:
#     json.dump(final_output, file, indent=2)

# print(f"Generated {len(all_generated_questions)} questions. Content has been written to 'response_content_1.json'")

# # Print final difficulty distribution
# print(f"Final difficulty distribution: {final_difficulty_counts}")
