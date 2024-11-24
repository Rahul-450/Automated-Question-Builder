import os
from openai import AzureOpenAI
import yaml
import json

# Reading Config File
current_path = os.getcwd()
full_config_path = "config.yaml"
config_values = yaml.safe_load(open(full_config_path))

AZURE_OPENAI_ENDPOINT = config_values['AZURE_OPENAI_ENDPOINT']
AZURE_OPENAI_KEY = config_values['AZURE_OPENAI_API_KEY']
OPENAI_API_VERSION = config_values['OPENAI_API_VERSION']
DEPLOYMENT_NAME=config_values['DEPLOYMENT_NAME']

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)


user_request={
    "Primary_Focus": "Full Stack Web Development",
    "Skill_Level": "intermediate",
    "Learning_Style": "project-based",
    "Areas of improvement": "I want to improve my skills in Python and frontend",
    "learning goals": "To build dynamic web applications and enhance backend and frontend integration"
}

learning_resources=[
    {
      "id": 1,
      "File_Name": "Full Stack Development",
      "Topics_Covered": [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "SQL"
      ]
    },
    {
      "id": 2,
      "File_Name": "Backend Development",
      "Topics_Covered": [
        "Java",
        "Spring Boot",
        "REST APIs",
        "SQL Server"
      ]
    },
    {
      "id": 3,
      "File_Name": "Frontend Development",
      "Topics_Covered": [
        "ReactJS",
        "Angular",
        "Vue.js"
      ]
    },
    {
      "id": 4,
      "File_Name": "Database Management",
      "Topics_Covered": [
        "MySQL",
        "PostgreSQL",
        "MongoDB"
      ]
    },
    {
      "id": 5,
      "File_Name": "DevOps",
      "Topics_Covered": [
        "Docker",
        "Kubernetes",
        "Jenkins",
        "CI/CD"
      ]
    },
    {
      "id": 6,
      "File_Name": "Cloud Computing",
      "Topics_Covered": [
        "AWS",
        "Azure",
        "Google Cloud Platform"
      ]
    },
    {
      "id": 7,
      "File_Name": "Agile Methodologies",
      "Topics_Covered": [
        "Scrum",
        "Kanban",
        "Agile Principles"
      ]
    },
    {
      "id": 8,
      "File_Name": "Version Control",
      "Topics_Covered": [
        "Git",
        "GitHub",
        "Bitbucket"
      ]
    },
    {
      "id": 9,
      "File_Name": "Software Testing",
      "Topics_Covered": [
        "Unit Testing",
        "Integration Testing",
        "Selenium"
      ]
    },
    {
      "id": 10,
      "File_Name": "Microservices Architecture",
      "Topics_Covered": [
        "Design Patterns",
        "RESTful Services",
        "API Gateway"
      ]
    },
    {
      "id": 11,
      "File_Name": "Continuous Integration",
      "Topics_Covered": [
        "Jenkins",
        "Travis CI",
        "GitLab CI"
      ]
    },
    {
      "id": 12,
      "File_Name": "Mobile App Development",
      "Topics_Covered": [
        "Flutter",
        "React Native",
        "iOS Development"
      ]
    },
    {
      "id": 13,
      "File_Name": "Security Best Practices",
      "Topics_Covered": [
        "OWASP",
        "Data Encryption",
        "Network Security"
      ]
    },
    {
      "id": 14,
      "File_Name": "API Development",
      "Topics_Covered": [
        "REST",
        "GraphQL",
        "API Documentation"
      ]
    },
    {
      "id": 15,
      "File_Name": "Business Communication",
      "Topics_Covered": [
        "Technical Writing",
        "Client Interaction",
        "Presentation Skills"
      ]
    },
    {
      "id": 16,
      "File_Name": "Project Management Tools",
      "Topics_Covered": [
        "JIRA",
        "Trello",
        "Asana"
      ]
    },
    {
      "id": 17,
      "File_Name": "Data Structures and Algorithms",
      "Topics_Covered": [
        "Sorting Algorithms",
        "Data Structures",
        "Problem Solving"
      ]
    },
    {
      "id": 18,
      "File_Name": "Networking Basics",
      "Topics_Covered": [
        "TCP/IP",
        "DNS",
        "HTTP/HTTPS"
      ]
    },
    {
      "id": 19,
      "File_Name": "Performance Optimization",
      "Topics_Covered": [
        "Code Optimization",
        "Database Tuning",
        "Load Balancing"
      ]
    },
    {
      "id": 20,
      "File_Name": "Software Design Principles",
      "Topics_Covered": [
        "SOLID",
        "Design Patterns",
        "UML"
      ]
    },
    {
      "id": 21,
      "File_Name": "Full Stack Development",
      "Topics_Covered": [
        "Node.js",
        "Express.js",
        "Bootstrap",
        "GraphQL",
        "NoSQL"
      ]
    },
    {
      "id": 22,
      "File_Name": "Backend Development",
      "Topics_Covered": [
        "Node.js",
        "Express",
        "MongoDB",
        "GraphQL"
      ]
    },
    {
      "id": 23,
      "File_Name": "Frontend Development",
      "Topics_Covered": [
        "Sass",
        "TypeScript",
        "Webpack"
      ]
    },
    {
      "id": 24,
      "File_Name": "Database Management",
      "Topics_Covered": [
        "Oracle",
        "SQL Tuning",
        "Database Security"
      ]
    },
    {
      "id": 25,
      "File_Name": "DevOps",
      "Topics_Covered": [
        "Ansible",
        "Terraform",
        "Monitoring Tools"
      ]
    },
    {
      "id": 26,
      "File_Name": "Cloud Computing",
      "Topics_Covered": [
        "Serverless Architecture",
        "Cloud Security",
        "DevOps in Cloud"
      ]
    },
    {
      "id": 27,
      "File_Name": "Agile Methodologies",
      "Topics_Covered": [
        "Lean",
        "Extreme Programming",
        "Agile Coaching"
      ]
    },
    {
      "id": 28,
      "File_Name": "Version Control",
      "Topics_Covered": [
        "SVN",
        "Mercurial",
        "Branching Strategies"
      ]
    },
    {
      "id": 29,
      "File_Name": "Software Testing",
      "Topics_Covered": [
        "Test Automation",
        "Performance Testing",
        "Load Testing"
      ]
    },
    {
      "id": 30,
      "File_Name": "Microservices Architecture",
      "Topics_Covered": [
        "Service Mesh",
        "Event-Driven Architecture",
        "Micro Frontends"
      ]
    },
    {
      "id": 31,
      "File_Name": "Continuous Integration",
      "Topics_Covered": [
        "CircleCI",
        "Azure DevOps",
        "Continuous Deployment"
      ]
    },
    {
      "id": 32,
      "File_Name": "Mobile App Development",
      "Topics_Covered": [
        "Kotlin",
        "Swift",
        "Cross-Platform Development"
      ]
    },
    {
      "id": 33,
      "File_Name": "Security Best Practices",
      "Topics_Covered": [
        "Penetration Testing",
        "Security Audits",
        "Identity Management"
      ]
    },
    {
      "id": 34,
      "File_Name": "API Development",
      "Topics_Covered": [
        "Swagger",
        "Postman",
        "API Security"
      ]
    },
    {
      "id": 35,
      "File_Name": "Business Communication",
      "Topics_Covered": [
        "Negotiation Skills",
        "Interpersonal Skills",
        "Leadership Communication"
      ]
    },
    {
      "id": 36,
      "File_Name": "Project Management Tools",
      "Topics_Covered": [
        "MS Project",
        "Basecamp",
        "Monday.com"
      ]
    },
    {
      "id": 37,
      "File_Name": "Data Structures and Algorithms",
      "Topics_Covered": [
        "Dynamic Programming",
        "Graph Algorithms",
        "Complexity Analysis"
      ]
    },
    {
      "id": 38,
      "File_Name": "Networking Basics",
      "Topics_Covered": [
        "Network Protocols",
        "Firewall Configuration",
        "VPN"
      ]
    },
    {
      "id": 39,
      "File_Name": "Performance Optimization",
      "Topics_Covered": [
        "Profiling Tools",
        "Caching Strategies",
        "Concurrency"
      ]
    },
    {
      "id": 40,
      "Topic": "Software Design Principles",
      "Topics_Covered": [
        "Clean Code",
        "Refactoring",
        "Design Thinking"
      ]
    }
  ]

# question_banks=[
#     {
#         "File_Name": "Full_stack_development.json",
#         "Topics_Covered": ["HTML", "CSS", "JavaScript", "Python", "Node.js", "React"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Python.json",
#         "Topics_Covered": ["Variables", "Data Types", "Control Structures", "Functions", "Modules"],
#         "Difficulty": "beginner"
#     },
#     {
#         "File_Name": "python_100.json",
#         "Topics_Covered": ["Advanced Functions", "Decorators", "Generators", "File Handling", "Error Handling"],
#         "Difficulty": "advanced"
#     },
#     {
#         "File_Name": "advanced_coding.json",
#         "Topics_Covered": ["Algorithms", "Data Structures", "Design Patterns", "Optimization Techniques"],
#         "Difficulty": "expert"
#     },
#     {
#         "File_Name": "AI.json",
#         "Topics_Covered": ["Machine Learning", "Deep Learning", "Neural Networks", "Natural Language Processing"],
#         "Difficulty": "advanced"
#     },
#     {
#         "File_Name": "Frontend_development.json",
#         "Topics_Covered": ["HTML", "CSS", "JavaScript", "React", "Vue.js"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Backend_development.json",
#         "Topics_Covered": ["Java", "Spring Boot", "REST APIs", "SQL Server"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Database_management.json",
#         "Topics_Covered": ["MySQL", "PostgreSQL", "MongoDB"],
#         "Difficulty": "beginner"
#     },
#     {
#         "File_Name": "DevOps.json",
#         "Topics_Covered": ["Docker", "Kubernetes", "Jenkins", "CI/CD"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Cloud_computing.json",
#         "Topics_Covered": ["AWS", "Azure", "Google Cloud Platform"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Agile_methodologies.json",
#         "Topics_Covered": ["Scrum", "Kanban", "Agile Principles"],
#         "Difficulty": "beginner"
#     },
#     {
#         "File_Name": "Version_control.json",
#         "Topics_Covered": ["Git", "GitHub", "Bitbucket"],
#         "Difficulty": "beginner"
#     },
#     {
#         "File_Name": "Software_testing.json",
#         "Topics_Covered": ["Unit Testing", "Integration Testing", "Selenium"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Microservices_architecture.json",
#         "Topics_Covered": ["Design Patterns", "RESTful Services", "API Gateway"],
#         "Difficulty": "advanced"
#     },
#     {
#         "File_Name": "Continuous_integration.json",
#         "Topics_Covered": ["Jenkins", "Travis CI", "GitLab CI"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Mobile_app_development.json",
#         "Topics_Covered": ["Flutter", "React Native", "iOS Development"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Security_best_practices.json",
#         "Topics_Covered": ["OWASP", "Data Encryption", "Network Security"],
#         "Difficulty": "advanced"
#     },
#     {
#         "File_Name": "API_development.json",
#         "Topics_Covered": ["REST", "GraphQL", "API Documentation"],
#         "Difficulty": "intermediate"
#     },
#     {
#         "File_Name": "Business_communication.json",
#         "Topics_Covered": ["Technical Writing", "Client Interaction", "Presentation Skills"],
#         "Difficulty": "beginner"
#     },
#     {
#         "File_Name": "Project_management_tools.json",
#         "Topics_Covered": ["JIRA", "Trello", "Asana"],
#         "Difficulty": "beginner"
#     }
# ]

def generate_learning_plan(user_request,learning_resources,question_banks):
        
        # Generate a learning plan based on user input
        prompt=f"""
        Generate a personalized, comprehensive learning plan in JSON format based on the user's request, available learning resources, and question banks. The plan should be tailored to the user's specific needs and goals, ensuring a holistic approach to learning.

        User's Request : {user_request}

        Learning Resources : {learning_resources}

        Question Banks : {question_banks}


        # Steps

        1. Analyze the user's request to identify:
            a. Primary technology focus
            b. Specific learning goals
            c. Current skill level (beginner, intermediate, advanced)
            d. Preferred learning style (e.g., hands-on, theoretical, project-based)
            e. Specific areas for improvement
            f. Learning goals

        2. Map user learning goals to relevant topics in the provided resources:
            a. Identify core concepts and skills required
            b. Prioritize topics based on user's current skill level and goals
            c. Ensure a balanced coverage of both backend and frontend technologies

        3. Select and curate learning resources:
            a. Choose resources that align with the user's skill level and learning style
            b. Ensure a mix of theoretical content and practical exercises
            c. Include resources for both backend and frontend integration

        4. Incorporate appropriate question banks:
            a. Select question banks that reinforce key concepts
            b. Ensure coverage of all relevant topics
            c. Include a mix of difficulty levels to support progressive learning

        5. Create a structured learning timeline:
            a. Organize resources in a logical, progressive order
            b. Estimate time requirements for each resource
            c. Include milestones and checkpoints for self-assessment

        6. Provide AI-generated recommendations to enhance the learning experience:
            a. Suggest coding projects that integrate multiple concepts
            b. Recommend additional practice exercises or coding challenges
            c. Propose strategies for effective learning and retention
            d. Suggest relevant communities or forums for support and networking

        7. Structure the plan in a clear, detailed JSON format as specified

        # Output Format

        The learning plan should be structured in the following JSON format:

        {{
            "User_Profile": {{
                "Primary_Focus": "[primary_technology]",
                "Skill_Level": "[beginner/intermediate/advanced]",
                "Learning_Style": "[preferred_learning_style]",
                "Areas_of_improvement": ["[topic1]", "[topic2]", ...],
                "Learning_goals": ["[goal1]", "[goal2]", ...]
            }},
            "Learning_Plan": [
                {{
                    "id": [resource_id],
                    "File_Name": "[resource_topic]",
                    "Topics_Covered": ["[relevant_sub_topic1]", "[relevant_sub_topic2]"],
                    "Estimated_Time": "[estimated_time_in_hours] hrs",
                    "Difficulty": "[beginner/intermediate/advanced]"
                }},
                ...
            ],
            "Question_Banks": [
                {{
                    "File_Name": "[question_bank_file]",
                    "Topics_Covered": ["[topic1]", "[topic2]"],
                    "Difficulty": "[beginner/intermediate/advanced]"
                }},
                ...
            ],
            "Timeline": [
                {{
                    "Week": [week_number],
                    "Focus": "[weekly_focus]",
                    "Milestone": "[weekly_milestone]"
                }},
                ...
            ],
            "Recommendations": [
                {{
                    "Type": "[project/exercise/strategy]",
                    "Description": "[detailed_recommendation]",
                    "Benefits": ["[benefit1]", "[benefit2]"]
                }},
                ...
            ]
        }}


        # Example JSON Output


        {{
            "User_Profile": {{
                "Primary_Focus": "Full Stack Development",
                "Skill_Level": "intermediate",
                "Learning_Style": "project-based",
                "Areas of improvement": "I want to improve my skills in Python and JavaScript",
                "learning goals": "To build dynamic web applications and enhance backend and frontend integration"
            }},
            "Learning_Plan": [
                {{
                    "id": 1,
                    "File_Name": "Advanced JavaScript",
                    "Topics_Covered": ["Closures", "Promises", "Async/Await"],
                    "Estimated_Time": "4 hrs",
                    "Difficulty": "intermediate"
                }},
                {{
                    "id": 2,
                    "Topic": "Python Backend Development",
                    "Topics_Covered": ["FastAPI", "SQLAlchemy", "Authentication"],
                    "Estimated_Time": "6 hrs",
                    "Difficulty": "intermediate"
                }}
            ],
            "Question_Banks": [
                {{
                    "File_Name": "advanced_javascript.json",
                    "Topics_Covered": ["Closures", "Promises", "Async/Await"],
                    "Difficulty": "intermediate"
                }},
                {{
                    "File_Name": "python_backend.json",
                    "Topics_Covered": ["FastAPI", "SQLAlchemy", "Authentication"],
                    "Difficulty": "intermediate"
                }}
            ],
            "Timeline": [
                {{
                    "Week": 1,
                    "Focus": "Advanced JavaScript Concepts",
                    "Milestone": "Complete JavaScript refresher and advanced topics"
                }},
                {{
                    "Week": 2,
                    "Focus": "Python Backend Development",
                    "Milestone": "Build a simple API with FastAPI and SQLAlchemy"
                }}
            ],
            "Recommendations": [
                {{
                    "Type": "project",
                    "Description": "Develop a full-stack task management application using React for frontend and FastAPI for backend",
                    "Benefits": ["Practical application of learned concepts", "Integration of frontend and backend skills"]
                }},
                {{
                    "Type": "strategy",
                    "Description": "Participate in coding challenges on platforms like LeetCode or HackerRank to reinforce problem-solving skills",
                    "Benefits": ["Improved algorithmic thinking", "Preparation for technical interviews"]
                }}
            ]
        }}


        # Notes

        - Tailor the learning plan to the user's specific needs, goals, and current skill level.
        - Ensure a balanced approach covering both theoretical knowledge and practical application.
        - Include resources that support both backend and frontend development for a comprehensive full-stack learning experience.
        - Provide clear milestones and checkpoints to help the user track their progress.
        - Offer diverse learning materials to cater to different learning styles and preferences.
        - Suggest relevant projects and exercises that integrate multiple concepts for practical application.
        - Include recommendations for ongoing learning and skill development beyond the initial plan.

        """
        try:
                response = client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=[
                            {
                                "role": "system",
                                "content": "You are a personalized learning plan generator",
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                    response_format = {"type": "json_object"}
                )

                try:
                        response_json = json.loads(response.choices[0].message.content)
                        return response_json
                
                except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        print("Raw content:", response.choices[0].message.content)
                        return ""

        except Exception as e:
            print(f"Error in API call: {e}")
            return ""
        

print(str(generate_learning_plan(user_request,learning_resources,question_banks)))
                
                        
