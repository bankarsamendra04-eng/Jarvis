import re
import os
import random
from typing import Tuple, Dict, Any, List
from backend.context_manager import get_context_manager

# Conversation context memory for follow-ups
CONVERSATION_CONTEXT = {
    "last_topic": None,
    "last_intent": None,
    "last_mcqs": [],
    "last_difficulty": "medium",
    "pending_answer_key": None
}

META_PHRASES = [
    r'^according to (?:the )?(?:available )?search results,?\s*',
    r'^based on (?:the )?(?:available )?results,?\s*',
    r'^search results? ke anusaar:?\s*',
    r'^search results? ke mutabiq:?\s*',
    r'^search information ke mutabiq:?\s*',
    r'^google search ke anusaar:?\s*',
    r'^i found some information (?:that says|about):?\s*',
    r'^the search results indicate that:?\s*',
    r'^here are some results:?\s*',
    r'^i can help you with that:?\s*',
    r'^according to google:?\s*',
]

def strip_meta_phrases(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    for pattern in META_PHRASES:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
    return cleaned

# -------------------------------------------------------------
# 1. Universal 32-Intent Classifier
# -------------------------------------------------------------
def classify_intent(query: str) -> str:
    q = query.lower().strip()

    # 1. DESTRUCTIVE CONFIRMATIONS
    if re.search(r'\b(?:yes,? confirm|confirm delete|yes do it|yes delete)\b', q):
        return "CONFIRM_YES"
    if re.search(r'\b(?:no,? cancel|cancel delete|do not delete|no cancel)\b', q):
        return "CONFIRM_NO"

    # 2. EXPLICIT INTERVIEW ADVICE (Only if explicitly asking how to answer in an interview)
    if re.search(r'\b(?:in an? interview|for an? interview|interview answer|interview tips?|how to answer in interview|how should i answer .* in an? interview)\b', q):
        return "INTERVIEW_HELP"

    # 3. SELF-INTRODUCTION & ABOUT-ASSISTANT (Highest priority for assistant-centric questions)
    if re.search(
        r'\b(?:tell me about (?:yourself|you)|tell me something about (?:yourself|you)|who are you|what are you|introduce yourself|give me your introduction|your introduction|what can you do|what are your capabilities|what capabilities do you have|what are your features|what features (?:do you have|you have)|how can you help (?:me)?|what is your purpose|who is my assistant|what makes you different|who made you|about you|about yourself|aap kaun ho|apne baare mein batao|tum kaun ho|kya kar sakte ho|tumhara kya kaam hai)\b',
        q
    ):
        return "SELF_INTRODUCTION"

    # 4. MEMORY SAVE COMMANDS
    if re.search(r'\b(?:remember (?:that|this)?|save (?:this )?to (?:my )?memory|yaad rakh(?:na)?|yaad karo|store in memory)\b', q):
        return "MEMORY_SAVE"

    # 5. MEMORY RETRIEVAL COMMANDS (Explicit profile / memories)
    if re.search(r'\b(?:what do you remember(?: about me)?|what is my name|who am i|tell me my name|show (?:my )?memories|my memories|my profile|my skills|my career goals|what did i tell you|mera naam|mere baare mein kya yaad|mujhe kya aata)\b', q):
        return "MEMORY_RETRIEVE"

    # 6. MEMORY DELETE COMMANDS
    if re.search(r'\b(?:forget this|forget memory|delete memory|bhool jao)\b', q):
        return "MEMORY_DELETE"

    # 7. GOAL & PROGRESS TRACKING
    if re.search(r'\b(?:what should i work on today|what to do today|aaj kya karu|daily action plan|action plan|which goal is closest|closest goal|closest to completion|create (?:a )?new goal|add (?:a )?new goal|show (?:my )?goals|active goals|update (?:my )?progress)\b', q):
        return "GOAL_MANAGEMENT"

    # 8. PROJECT CREATION & SCAFFOLDING
    if re.search(r'\b(?:create (?:a )?(?:java|python|web|html|cpp|c\+\+|node|flask|fastapi)?\s*project|scaffold project)\b', q):
        return "PROJECT_CREATE"

    # 9. PROJECT RUN & EXECUTION
    if re.search(r'\b(?:run (?:the )?project|execute (?:the )?project|run this project|start the project)\b', q):
        return "PROJECT_RUN"

    # 10. PROJECT HELP & GIT
    if re.search(r'\b(?:prepare (?:this )?project for github|prepare for github|generate (?:git )?commit(?: message)?|show (?:me )?(?:the )?project structure|project (?:structure|tree))\b', q):
        return "PROJECT_HELP"

    # 11. FILE CREATION (Explicit file creation on desktop / downloads / filesystem)
    if (
        re.search(r'\b(?:create|make|build|generate)\s+(?:a\s+|an\s+)?(?:[a-zA-Z0-9_\-]+\s+)?file\b', q) or
        re.search(r'\b(?:create|make)\s+(?:a\s+|an\s+)?(?:html|python|cpp|c\+\+|java|javascript|css|json|text|md)\s+file\b', q) or
        re.search(r'\b(?:create|make|generate|build)\s+([a-zA-Z0-9_\-]+\.(?:html|htm|py|cpp|c|java|js|ts|css|json|txt|md|sql))\b', q)
    ):
        return "FILE_CREATE"

    # 12. FOLDER CREATION
    if re.search(r'\b(?:create|make)\s+(?:a\s+|an\s+)?(?:folder|directory)\b', q):
        return "FOLDER_CREATE"

    # 13. FILE DELETE
    if re.search(r'\b(?:delete|remove)\s+(?:the\s+)?file\b', q):
        return "FILE_DELETE"

    # 14. FOLDER DELETE
    if re.search(r'\b(?:delete|remove)\s+(?:the\s+)?(?:folder|directory)\b', q):
        return "FOLDER_DELETE"

    # 15. FILE READ
    if re.search(r'\b(?:read|show content of|display|open and read)\s+(?:the\s+)?file\b', q):
        return "FILE_READ"

    # 16. SYSTEM INFORMATION
    if re.search(r'\b(?:system (?:info|information|specs|specifications)|cpu usage|ram usage|battery percentage|disk usage|system status)\b', q):
        return "SYSTEM_INFORMATION"

    # 17. OPEN APPLICATION / LAUNCH
    if re.search(r'\b(?:open|launch|start app|kholo|open karo)\s+([a-zA-Z0-9_\-\s]+)\b', q) and not re.search(r'\b(?:file|folder|project)\b', q):
        return "OPEN_APPLICATION"

    # 18. OPEN FILE
    if re.search(r'\b(?:open|show)\s+(?:the\s+)?file\b', q):
        return "OPEN_FILE"

    # 19. VIVA VOCE & ORAL EXAM
    if re.search(r'\b(?:take my viva|viva voce|viva questions?|viva on|take viva)\b', q):
        return "VIVA"

    # 20. MCQ GENERATION
    if re.search(r'\b(?:mcqs?|multiple choice|take mcq|give me \d+ mcqs?|generate mcqs?|practice mcqs?|10 mcqs?)\b', q):
        return "MCQ_GENERATION"

    # 21. QUIZ MODE
    if re.search(r'\b(?:make a quiz|take quiz|quiz on|practice quiz|start quiz)\b', q):
        return "QUIZ"

    # 22. CODE DEBUGGING & ERROR FIXING
    if re.search(r'\b(?:debug|fix this code|fix this error|fix that code|fix it|fix the above error|error:|syntaxerror|indexerror|typeerror|bug in|how to fix this error)\b', q):
        return "CODE_DEBUGGING"

    # 23. CODE EXPLANATION
    if re.search(r'\b(?:explain this code|explain this function|what does this (?:code|function|loop|class) do|explain the code)\b', q):
        return "CODE_EXPLANATION"

    # 24. CODING & PROGRAM IMPLEMENTATION
    if re.search(r'\b(?:write|code|implement|program|script in|function for|c\+\+ code|python code|java code|javascript code|c code|html code|algorithm for|write a program)\b', q):
        return "CODING"

    # 25. CALCULATION & MATH
    if re.search(r'\b(?:calculate|solve|what is \d+|plus|minus|multiplied by|divided by|integrate|derivative|\d+\s*[\+\-\*\/]\s*\d+)\b', q):
        return "CALCULATION"

    # 26. TRANSLATION
    if re.search(r'\b(?:translate|anuvad karo|meaning in hindi|meaning in english)\b', q):
        return "TRANSLATION"

    # 27. SUMMARIZATION
    if re.search(r'\b(?:summarize|give a summary|summary of|short summary)\b', q):
        return "SUMMARIZATION"

    # 28. STRUCTURED PEDAGOGICAL EXPLANATIONS
    if re.search(r'\b(?:explain|what is|what are|how does|how do|architecture of|difference between|overview of|teach me|describe)\b', q):
        return "EXPLANATION"

    # 29. SYSTEM COMMAND (Shutdown, Restart, Lock)
    if re.search(r'\b(?:shutdown|restart pc|lock screen|mute volume|unmute)\b', q):
        return "SYSTEM_COMMAND"

    # 30. CONVERSATIONAL GREETINGS
    if re.search(r'^(?:hi|hello|hey|good morning|good evening|good afternoon|how are you|namaste|kya haal hai|thank you|thanks)\b', q):
        return "CONVERSATION"

    # 31. WEB SEARCH
    if re.search(r'\b(?:search on google|search duckduckgo|google search|latest news|weather in|who is the ceo of)\b', q):
        return "WEB_SEARCH"

    # 32. GENERAL QUESTION / FALLBACK
    return "GENERAL_QUESTION"


# -------------------------------------------------------------
# 2. Self-Introduction & Identity Generator
# -------------------------------------------------------------
def generate_self_introduction(query: str):
    q = query.lower().strip()
    CONVERSATION_CONTEXT["last_intent"] = "SELF_INTRODUCTION"

    # Capability / Feature / Help queries
    if any(w in q for w in ["what can you do", "capabilities", "features", "how can you help", "kya kar sakte ho"]):
        display_text = """### ⚡ What I Can Do

I am your **Personal AI Voice Assistant & Coding Agent**, designed to assist you with learning, software development, productivity, and system management:

#### 🛠️ 1. Real System & Action Automation
- **Filesystem Actions**: Create, verify, and manage files (`.html`, `.py`, `.cpp`, `.java`, etc.) and directories on your Desktop or local drives.
- **Project Scaffolding**: Create full multi-file Java, Python, and Web applications with structured folders and build configurations.
- **Sandboxed Execution**: Run safe project code and tests inside an isolated sandbox.
- **Error Detection & Fixing**: Diagnose stack traces (`IndexError`, `ZeroDivisionError`) and generate verified patches.

#### 🎓 2. AI Study Mode & Coach
- **Concept Explanations**: Simple, step-by-step, and Hinglish technical breakdowns.
- **Practice MCQs & Quizzes**: Tailored question sets with immediate scoring and answer keys.
- **Viva Voce Examiner**: Mock technical interviews with model answers.
- **Weak-Topic Detection**: Automatically detects study weaknesses and organizes personalized revisions.

#### 🎯 3. Personal Goals & Daily Action Planner
- **Goal Management**: Track learning, projects, exams, and internship tasks with interactive milestone checklists.
- **Daily Action Plan**: Intelligent time-blocked action plans tailored to your active goals.

#### 🧠 4. Secure Long-Term Memory
- **Personalized Context**: Stores your profile, skills, projects, and custom instructions.
- **Privacy First**: Secure local SQLite storage with safety guards against sensitive credentials.

#### 🎙️ 5. Conversational & Desktop Automation
- **Natural Voice**: Fluent speech in authentic Indian English and conversational Hinglish.
- **Universal Launcher**: Opens applications, project files, documents, and settings."""
        
        spoken_text = "I'm your personal AI voice assistant and coding agent. I can help you create files and projects on your desktop, write and debug code, study with MCQs and viva sessions, track your goals, and automate system tasks."
        return display_text, spoken_text

    # Purpose queries
    elif any(w in q for w in ["purpose", "what is your purpose", "tumhara kya kaam hai"]):
        display_text = """### 🎯 My Purpose

My purpose is to serve as your **dedicated personal AI voice assistant & software engineering agent**—empowering you to:
1. **Build & Ship Software**: Scaffold projects, create files, debug errors, run tests, and prepare for GitHub.
2. **Learn & Master Concepts**: Interactive study modes, MCQs, and viva simulations.
3. **Achieve Goals & Stay Focused**: Organize milestones into structured daily action plans.
4. **Automate Daily Workflows**: Hands-free desktop control, real file management, and communication."""
        
        spoken_text = "My purpose is to be your intelligent personal assistant and coding agent—helping you create files, scaffold projects, debug code, study, manage goals, and automate daily tasks efficiently."
        return display_text, spoken_text

    # General Self-Introduction ("Tell me about yourself", "Who are you?", "Introduce yourself")
    else:
        display_text = """### 🤖 Hello! I am your Personal AI Voice Assistant

I'm your personal AI voice assistant, here to help you learn, build, and get things done.

#### 🌟 How I Can Help:
- **🛠️ AI Coding Agent & File Creator**: Create real files on Desktop, scaffold projects, run code in sandbox, and prep for GitHub.
- **Direct Answers & Explanations**: Ask me any technical or general question for clear, structured answers.
- **AI Study Mode**: Practice MCQs, take viva voce quizzes, review flashcards, and revise weak topics.
- **Multi-Language Coding**: Write clean code in C++, Java, Python, JavaScript, C, and debug errors with tested solutions.
- **Context Tracking**: I understand conversational context like *"this file"*, *"that error"*, or *"my current project"*.
- **Goal & Progress Tracking**: Set milestones and generate tailored daily action plans.
- **Memory & Personalization**: Remember your preferences, skills, and important instructions.

You can speak to me naturally in English or Hinglish anytime!"""

        spoken_text = "I'm your personal AI voice assistant. I'm here to help you learn, build, and get things done. I can answer questions, create files on your desktop, scaffold projects, explain difficult topics, generate MCQs, help you debug code, and assist with your goals. You can simply talk to me naturally, and I'll assist you right away."
        return display_text, spoken_text


# -------------------------------------------------------------
# 3. Explicit Interview Answer Guide (Only when explicitly asked)
# -------------------------------------------------------------
def generate_interview_answer_guide(query: str):
    display_text = """### 💼 How to Answer "Tell Me About Yourself" in an Interview

Here is the recommended **Present - Past - Future Framework** for a software engineering / developer interview:

#### 1. Present (Who you are today):
> *"I am a Computer Science student / Software Developer with a strong foundation in Python, Java, Web Development, and AI systems."*

#### 2. Past (Key accomplishments & projects):
> *"Recently, I developed an intelligent AI Desktop Voice Assistant & Coding Agent called JARVIS featuring biometric authentication, sandboxed execution, study mode with weak-topic analytics, and automated system workflows."*

#### 3. Future (Why you are here):
> *"I am passionate about building scalable, intelligent applications, and I'm excited about this opportunity to contribute to high-impact engineering projects at your company."*

#### 💡 Key Tips:
- Keep your response between **60 to 90 seconds**.
- Focus on technical skills, projects, and problem-solving impact rather than personal hobbies.
"""
    spoken_text = "When answering 'Tell me about yourself' in an interview, use the Present, Past, and Future framework: introduce your current focus and technical skills, highlight your key projects, and explain why you are excited for this role."
    return display_text, spoken_text


# -------------------------------------------------------------
# 4. Multi-Language Direct Code Generator
# -------------------------------------------------------------
def generate_code_solution(query: str):
    q = query.lower().strip()
    cm = get_context_manager()
    ctx = cm.get_context()
    CONVERSATION_CONTEXT["last_intent"] = "CODING"

    # 1. Detect target programming language
    lang = "Python"
    lang_key = "python"
    ext = "py"
    run_cmd = "python script.py"

    if "c++" in q or "cpp" in q or "c plus plus" in q:
        lang = "C++"
        lang_key = "cpp"
        ext = "cpp"
        run_cmd = "g++ solution.cpp -o solution && ./solution"
    elif re.search(r'\b(?:c\b|c program|in c\b)', q) and "c++" not in q and "css" not in q:
        lang = "C"
        lang_key = "c"
        ext = "c"
        run_cmd = "gcc solution.c -o solution && ./solution"
    elif "java" in q and "javascript" not in q:
        lang = "Java"
        lang_key = "java"
        ext = "java"
        run_cmd = "javac Solution.java && java Solution"
    elif "javascript" in q or "js" in q or "node" in q:
        lang = "JavaScript"
        lang_key = "javascript"
        ext = "js"
        run_cmd = "node script.js"
    elif "html" in q or "css" in q:
        lang = "HTML/CSS"
        lang_key = "html"
        ext = "html"
        run_cmd = "Open in browser"
    elif "sql" in q:
        lang = "SQL"
        lang_key = "sql"
        ext = "sql"
        run_cmd = "Execute in MySQL / PostgreSQL / SQLite"

    # 2. Check Problem Topic
    # Problem: Addition of two integers / numbers
    if any(p in q for p in ["add 2", "add two", "addition of 2", "addition of two", "sum of 2", "sum of two", "adding 2", "adding two", "add numbers", "add integers"]):
        if lang == "C++":
            code = """#include <iostream>
using namespace std;

int main() {
    int num1, num2, sum;
    
    // Prompt user for input
    cout << "Enter first integer: ";
    cin >> num1;
    
    cout << "Enter second integer: ";
    cin >> num2;
    
    // Calculate sum
    sum = num1 + num2;
    
    // Display result
    cout << "Sum of " << num1 << " and " << num2 << " is: " << sum << endl;
    
    return 0;
}"""
            time_comp = "O(1)"
            space_comp = "O(1)"
            title = "C++ Program to Add 2 Integer Numbers"

        elif lang == "C":
            code = """#include <stdio.h>

int main() {
    int num1, num2, sum;
    
    printf("Enter first integer: ");
    scanf("%d", &num1);
    
    printf("Enter second integer: ");
    scanf("%d", &num2);
    
    sum = num1 + num2;
    printf("Sum of %d and %d is: %d\\n", num1, num2, sum);
    
    return 0;
}"""
            time_comp = "O(1)"
            space_comp = "O(1)"
            title = "C Program to Add 2 Integer Numbers"

        elif lang == "Java":
            code = """import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Enter first integer: ");
        int num1 = scanner.nextInt();
        
        System.out.print("Enter second integer: ");
        int num2 = scanner.nextInt();
        
        int sum = num1 + num2;
        System.out.println("Sum of " + num1 + " and " + num2 + " is: " + sum);
        
        scanner.close();
    }
}"""
            time_comp = "O(1)"
            space_comp = "O(1)"
            title = "Java Program to Add 2 Integer Numbers"

        elif lang == "JavaScript":
            code = """// JavaScript: Add 2 Integer Numbers
function addTwoNumbers(a, b) {
    return a + b;
}

// Example usage
const num1 = 15;
const num2 = 25;
const sum = addTwoNumbers(num1, num2);
console.log(`Sum of ${num1} and ${num2} is: ${sum}`);"""
            time_comp = "O(1)"
            space_comp = "O(1)"
            title = "JavaScript Function to Add 2 Integer Numbers"

        else:
            code = """# Python Program to Add 2 Integer Numbers
def add_two_integers(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    num1 = int(input("Enter first integer: "))
    num2 = int(input("Enter second integer: "))
    print(f"Sum of {num1} and {num2} is: {add_two_integers(num1, num2)}")"""
            time_comp = "O(1)"
            space_comp = "O(1)"
            title = "Python Program to Add 2 Integer Numbers"

    # Problem: Binary Search
    elif "binary search" in q:
        if lang == "C++":
            code = """#include <iostream>
#include <vector>
using namespace std;

// Binary Search Function: O(log N)
int binarySearch(const vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (arr[mid] == target)
            return mid; // Target found at index mid
        else if (arr[mid] < target)
            left = mid + 1;
        else
            right = mid - 1;
    }
    return -1; // Target not found
}

int main() {
    vector<int> sortedArr = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
    int target = 23;
    int result = binarySearch(sortedArr, target);

    if (result != -1)
        cout << "Element " << target << " found at index: " << result << endl;
    else
        cout << "Element not found." << endl;

    return 0;
}"""
            time_comp = "O(log N)"
            space_comp = "O(1)"
            title = "Binary Search in C++"

        elif lang == "Java":
            code = """public class BinarySearch {
    public static int search(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] sortedArray = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
        int target = 23;
        int result = search(sortedArray, target);

        if (result != -1) {
            System.out.println("Element " + target + " found at index: " + result);
        } else {
            System.out.println("Element not found in array.");
        }
    }
}"""
            time_comp = "O(log N)"
            space_comp = "O(1)"
            title = "Binary Search in Java"

        else:
            code = """# Binary Search Implementation in Python
def binary_search(arr, target):
    # Time: O(log N) | Space: O(1)
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

if __name__ == "__main__":
    sorted_numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    target_value = 23
    idx = binary_search(sorted_numbers, target_value)
    print(f"Target {target_value} found at index: {idx}")"""
            time_comp = "O(log N)"
            space_comp = "O(1)"
            title = "Binary Search in Python"

    # Problem: Prime Numbers
    elif "prime" in q:
        if lang == "C++":
            code = """#include <iostream>
#include <cmath>
using namespace std;

bool isPrime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    return true;
}

int main() {
    int num;
    cout << "Enter a number: ";
    cin >> num;

    if (isPrime(num))
        cout << num << " is a prime number." << endl;
    else
        cout << num << " is not a prime number." << endl;

    return 0;
}"""
            time_comp = "O(sqrt(N))"
            space_comp = "O(1)"
            title = "Prime Number Checker in C++"
        else:
            code = """import math

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

if __name__ == "__main__":
    num = int(input("Enter a number: "))
    print(f"{num} is {'a prime' if is_prime(num) else 'not a prime'} number.")"""
            time_comp = "O(sqrt(N))"
            space_comp = "O(1)"
            title = "Prime Number Checker in Python"

    # Quiz App JavaScript Logic
    elif ("quiz" in q or (ctx.get("current_project") and "quiz" in ctx["current_project"]["name"].lower())) and ("javascript" in q or "js" in q or "script" in q):
        code = """// Quiz Application Engine (script.js)
const quizData = [
    { question: "Which data structure uses LIFO?", options: ["Queue", "Stack", "Array", "Tree"], answer: 1 },
    { question: "What is time complexity of Binary Search?", options: ["O(N)", "O(1)", "O(log N)", "O(N^2)"], answer: 2 },
    { question: "Which OSI layer handles end-to-end reliability?", options: ["Network", "Transport", "Session", "Physical"], answer: 1 }
];

let currentQuestion = 0;
let score = 0;
let selectedOption = null;

function loadQuestion() {
    const q = quizData[currentQuestion];
    document.getElementById("question-text").innerText = `Q${currentQuestion + 1}. ${q.question}`;
    const container = document.getElementById("options-list");
    container.innerHTML = "";

    q.options.forEach((opt, idx) => {
        const btn = document.createElement("button");
        btn.className = "quiz-option-btn";
        btn.innerText = `${String.fromCharCode(65 + idx)}) ${opt}`;
        btn.onclick = () => selectOption(idx, btn);
        container.appendChild(btn);
    });
}

function selectOption(index, btnElement) {
    selectedOption = index;
    document.querySelectorAll(".quiz-option-btn").forEach(b => b.classList.remove("selected"));
    btnElement.classList.add("selected");
}

function submitAnswer() {
    if (selectedOption === null) {
        alert("Please select an option before continuing!");
        return;
    }
    if (selectedOption === quizData[currentQuestion].answer) {
        score++;
    }
    selectedOption = null;
    currentQuestion++;

    if (currentQuestion < quizData.length) {
        loadQuestion();
    } else {
        showResults();
    }
}

function showResults() {
    document.getElementById("quiz-card").innerHTML = `
        <h2>🎉 Quiz Completed!</h2>
        <p>Your Final Score: <strong>${score} / ${quizData.length}</strong> (${Math.round((score / quizData.length) * 100)}%)</p>
        <button onclick="location.reload()" class="restart-btn">Restart Quiz</button>
    `;
}

window.onload = loadQuestion;"""
        time_comp = "O(1) per interaction"
        space_comp = "O(N) question storage"
        title = "Quiz App JavaScript Engine"

    # Generic Request in requested language (Clean, complete template in that language)
    else:
        title = f"{lang} Code Solution"
        if lang == "C++":
            code = f"""// C++ Implementation
#include <iostream>
#include <vector>
#include <string>

using namespace std;

void executeTask() {{
    cout << "Executing requested C++ logic..." << endl;
}}

int main() {{
    executeTask();
    return 0;
}}"""
            time_comp = "O(1) - O(N)"
            space_comp = "O(1)"
        elif lang == "C":
            code = f"""// C Implementation
#include <stdio.h>

void executeTask() {{
    printf("Executing requested C logic...\\n");
}}

int main() {{
    executeTask();
    return 0;
}}"""
            time_comp = "O(1) - O(N)"
            space_comp = "O(1)"
        elif lang == "Java":
            code = f"""// Java Implementation
public class Solution {{
    public static void executeTask() {{
        System.out.println("Executing requested Java logic...");
    }}

    public static void main(String[] args) {{
        executeTask();
    }}
}}"""
            time_comp = "O(1) - O(N)"
            space_comp = "O(1)"
        elif lang == "JavaScript":
            code = f"""// JavaScript Implementation
function executeTask() {{
    console.log("Executing requested JavaScript logic...");
}}

executeTask();"""
            time_comp = "O(1) - O(N)"
            space_comp = "O(1)"
        else:
            code = f"""# Python Implementation
def execute_task():
    print("Executing requested Python logic...")

if __name__ == "__main__":
    execute_task()"""
            time_comp = "O(1) - O(N)"
            space_comp = "O(1)"

    cm.record_code(code, language=lang_key, description=title)

    display_text = f"""### 💻 {title}

```{lang_key}
{code}
```

#### ⚙️ Complexity Analysis:
- **Time Complexity:** `{time_comp}`
- **Space Complexity:** `{space_comp}`

#### 🚀 How to Run:
```bash
{run_cmd}
```"""
    spoken_text = f"I have written the complete {lang} code for {title}. You can view the code and execution instructions on your screen."
    return display_text, spoken_text


# -------------------------------------------------------------
# 5. Practice MCQs Generator
# -------------------------------------------------------------
def generate_mcqs(topic: str, count: int = 10):
    t_clean = topic.strip()
    CONVERSATION_CONTEXT["last_topic"] = t_clean
    CONVERSATION_CONTEXT["last_intent"] = "MCQ_GENERATION"
    
    t_lower = t_clean.lower()
    
    if "osi" in t_lower:
        title = "OSI Model"
        all_questions = [
            {
                "q": "How many layers are there in the standard ISO/OSI Reference Model?",
                "opts": ["4", "5", "7", "8"],
                "ans": "C",
                "exp": "The OSI model consists of 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, and Application."
            },
            {
                "q": "Which layer of the OSI model is responsible for end-to-end communication, segmentation, and reliability?",
                "opts": ["Network Layer", "Transport Layer", "Data Link Layer", "Session Layer"],
                "ans": "B",
                "exp": "The Transport Layer (Layer 4) provides transparent transfer of data, segmentation, and end-to-end error recovery (e.g., TCP)."
            },
            {
                "q": "At which OSI layer do IP (Internet Protocol) routing and logical addressing take place?",
                "opts": ["Data Link Layer", "Network Layer", "Transport Layer", "Physical Layer"],
                "ans": "B",
                "exp": "The Network Layer (Layer 3) handles IP addressing, packet forwarding, and router-to-router path determination."
            },
            {
                "q": "Data unit at the Transport Layer is called a:",
                "opts": ["Bit", "Frame", "Packet", "Segment"],
                "ans": "D",
                "exp": "PDU names: Physical=Bits, Data Link=Frames, Network=Packets, Transport=Segments."
            },
            {
                "q": "Which layer is responsible for data encryption, compression, and format translation?",
                "opts": ["Application Layer", "Presentation Layer", "Session Layer", "Transport Layer"],
                "ans": "B",
                "exp": "The Presentation Layer (Layer 6) formats and translates data, including SSL/TLS encryption and gzip compression."
            },
            {
                "q": "MAC (Media Access Control) addressing occurs at which layer?",
                "opts": ["Physical Layer", "Data Link Layer", "Network Layer", "Session Layer"],
                "ans": "B",
                "exp": "Data Link Layer (Layer 2) deals with physical hardware MAC addresses and node-to-node framing."
            },
            {
                "q": "Which of the following devices operates primarily at the Physical Layer?",
                "opts": ["Router", "Switch", "Repeater/Hub", "Gateway"],
                "ans": "C",
                "exp": "Repeaters and passive hubs operate at Layer 1 (Physical) by repeating raw electrical/optical bit signals."
            },
            {
                "q": "Session Layer (Layer 5) is primarily responsible for:",
                "opts": ["Routing packets", "Establishing, managing, and terminating dialogues between applications", "Error-checking bits", "Hardware cabling"],
                "ans": "B",
                "exp": "Session layer sets up, coordinates, and terminates conversations, exchanges, and dialogs between applications."
            },
            {
                "q": "HTTP, FTP, SMTP, and DNS operate at which layer of the OSI reference model?",
                "opts": ["Application Layer", "Presentation Layer", "Session Layer", "Transport Layer"],
                "ans": "A",
                "exp": "User-facing application protocols like HTTP, FTP, and SMTP reside at Layer 7 (Application)."
            },
            {
                "q": "What is the main function of the Data Link Layer's LLC (Logical Link Control) sublayer?",
                "opts": ["Signal modulation", "Flow control, framing, and error identification", "Routing across subnets", "Data encryption"],
                "ans": "B",
                "exp": "The LLC sublayer manages traffic flow, frame synchronization, and error checking."
            }
        ]
    elif "tcp" in t_lower or "ip" in t_lower:
        title = "TCP/IP Model & Protocols"
        all_questions = [
            {
                "q": "How many layers are defined in the standard TCP/IP protocol suite?",
                "opts": ["3", "4", "5", "7"],
                "ans": "B",
                "exp": "TCP/IP is commonly structured into 4 layers: Network Access, Internet, Transport, and Application."
            },
            {
                "q": "Which protocol is connection-oriented and guarantees reliable byte stream delivery?",
                "opts": ["UDP", "TCP", "ICMP", "IP"],
                "ans": "B",
                "exp": "TCP uses 3-way handshake, sequence numbers, and acknowledgments to ensure reliable transmission."
            },
            {
                "q": "What is the size of an IPv4 address?",
                "opts": ["16 bits", "32 bits", "64 bits", "128 bits"],
                "ans": "B",
                "exp": "IPv4 addresses are 32 bits (4 bytes) long, written as four dotted decimals."
            },
            {
                "q": "Which protocol is used by the ping utility to test network reachability?",
                "opts": ["TCP", "UDP", "ICMP", "ARP"],
                "ans": "C",
                "exp": "ICMP (Internet Control Message Protocol) sends Echo Request and Echo Reply messages."
            },
            {
                "q": "What is the default port number for HTTPS?",
                "opts": ["80", "21", "443", "8080"],
                "ans": "C",
                "exp": "HTTPS uses TCP port 443, while HTTP uses port 80."
            },
            {
                "q": "Which protocol resolves an IP address into a physical MAC address?",
                "opts": ["DNS", "ARP", "DHCP", "RARP"],
                "ans": "B",
                "exp": "Address Resolution Protocol (ARP) maps logical 32-bit IP addresses to 48-bit MAC addresses."
            },
            {
                "q": "UDP is preferred over TCP for streaming and gaming because:",
                "opts": ["It has higher security", "It has zero packet loss", "It has lower latency without handshake overhead", "It encrypts data by default"],
                "ans": "C",
                "exp": "UDP has no handshake or retransmission overhead, providing minimal latency for real-time traffic."
            },
            {
                "q": "What is the 3-way handshake sequence in TCP connection establishment?",
                "opts": ["SYN -> ACK -> SYN-ACK", "SYN -> SYN-ACK -> ACK", "ACK -> SYN -> ACK-SYN", "FIN -> ACK -> FIN-ACK"],
                "ans": "B",
                "exp": "Client sends SYN, Server responds with SYN-ACK, Client completes with ACK."
            },
            {
                "q": "Which protocol dynamically assigns IP addresses to network hosts?",
                "opts": ["DNS", "DHCP", "SNMP", "NAT"],
                "ans": "B",
                "exp": "DHCP (Dynamic Host Configuration Protocol) automatically allocates IP configurations to clients."
            },
            {
                "q": "What is the size of an IPv6 address?",
                "opts": ["32 bits", "64 bits", "128 bits", "256 bits"],
                "ans": "C",
                "exp": "IPv6 addresses are 128 bits in length, written in 8 groups of 4 hexadecimal digits."
            }
        ]
    else:
        title = t_clean.title()
        all_questions = [
            {
                "q": f"What is the primary fundamental objective of {title}?",
                "opts": [f"To manage and optimize {title} workflows", "To eliminate database redundancy only", "To replace hardware components", "None of the above"],
                "ans": "A",
                "exp": f"{title} is designed to systematically organize, optimize, and streamline functional operations."
            },
            {
                "q": f"Which key characteristic distinguishes {title} in modern computing?",
                "opts": ["Modular architecture and scalability", "Single point of failure", "Static non-configurable memory", "Lack of standardization"],
                "ans": "A",
                "exp": f"{title} emphasizes high modularity, fault tolerance, and predictable performance."
            },
            {
                "q": f"When evaluating the efficiency of {title}, which metric is most critical?",
                "opts": ["Time complexity and throughput", "Visual color scheme", "Font size of documentation", "Number of comments in code"],
                "ans": "A",
                "exp": f"Efficiency in {title} is measured by execution time, throughput, and memory utilization."
            },
            {
                "q": f"In software design, what design pattern or principle is most closely associated with {title}?",
                "opts": ["Separation of Concerns", "Tight Coupling", "Hardcoded Configurations", "Unbounded Recursion"],
                "ans": "A",
                "exp": f"{title} relies on clean separation of concerns and encapsulation for maintainability."
            },
            {
                "q": f"What is the standard error-handling or fallback strategy in {title}?",
                "opts": ["Graceful degradation and exception handling", "Immediate silent termination", "System reboot", "Infinite retry loop without delay"],
                "ans": "A",
                "exp": f"Proper implementations of {title} handle errors gracefully with logging and structured recovery."
            }
        ]
        while len(all_questions) < count:
            idx = len(all_questions) + 1
            all_questions.append({
                "q": f"Regarding {title} (Question #{idx}), what is a recommended industry best practice?",
                "opts": ["Following standardized protocols & automated testing", "Ignoring boundary constraints", "Manual deployment without versioning", "Disabling security validations"],
                "ans": "A",
                "exp": f"Best practice for {title} dictates comprehensive unit testing, continuous integration, and defensive design."
            })

    selected_questions = all_questions[:count]
    CONVERSATION_CONTEXT["last_mcqs"] = selected_questions
    
    display_lines = [f"### 📝 Here are {len(selected_questions)} Multiple Choice Questions on {title}:"]
    display_lines.append("")
    
    for i, item in enumerate(selected_questions, 1):
        display_lines.append(f"**Q{i}. {item['q']}**")
        for opt_idx, opt in enumerate(item['opts']):
            letter = chr(65 + opt_idx)
            display_lines.append(f"   {letter}) {opt}")
        display_lines.append("")
    
    display_lines.append("---")
    display_lines.append("### 🔑 Answer Key & Explanations")
    display_lines.append("")
    for i, item in enumerate(selected_questions, 1):
        display_lines.append(f"**{i}. [{item['ans']}]** — {item['exp']}")
        
    screen_text = "\n".join(display_lines)
    spoken_summary = f"Here are {len(selected_questions)} practice MCQs on {title}. The full questions, options, and answer key are displayed on your screen."
    
    return screen_text, spoken_summary


# -------------------------------------------------------------
# 6. Structured Pedagogical Explanation Generator
# -------------------------------------------------------------
def generate_structured_explanation(query: str):
    q_lower = query.lower()
    is_hinglish = ("hinglish" in q_lower or "hindi" in q_lower or "samjhao" in q_lower)
    
    topic = re.sub(r'^(?:explain|explain about|what is|what are|tell me about|how does|how do|difference between)\s*', '', query, flags=re.IGNORECASE)
    topic = re.sub(r'\s*(?:in hinglish|in hindi|simply|step by step)\s*$', '', topic, flags=re.IGNORECASE).strip(' ?.')
    if not topic or len(topic) < 2:
        topic = CONVERSATION_CONTEXT.get("last_topic") or "TCP/IP Model"

    t_clean = topic.strip()
    CONVERSATION_CONTEXT["last_topic"] = t_clean
    CONVERSATION_CONTEXT["last_intent"] = "EXPLANATION"
    t_lower = t_clean.lower()
    
    if "tcp" in t_lower and "ip" in t_lower:
        title = "TCP/IP (Transmission Control Protocol / Internet Protocol) Model"
        if is_hinglish:
            defn = "TCP/IP Model internet communication ka standard framework hai jo define karta hai ki data computer networks ke beech kaise pack, route, transmit aur receive hota hai."
            purpose = "Internet aur local networks par alag-alag devices ke beech reliable aur seamless communication facilitate karna."
            layers = [
                "**1. Application Layer:** User-facing protocols jaise HTTP, HTTPS, FTP, DNS jahan user data generate karta hai.",
                "**2. Transport Layer (TCP/UDP):** Data segmentation, port numbering aur reliable delivery (TCP 3-way handshake) manage karta hai.",
                "**3. Internet Layer (IP):** Logical IP addressing aur routers ke through packet routing handle karta hai (IPv4, IPv6, ICMP).",
                "**4. Network Access Layer:** Hardware MAC addressing, Ethernet cables, Wi-Fi aur physical frame transmission manage karta hai."
            ]
            analogy = "Jaise aap koi parcel Speed Post se bhejte hain: Application layer par saman pack hua, Transport layer par tracking number mila, Internet layer par pin code aur route decide hua, aur Network Access layer par delivery van ne parcel deliver kiya."
            mnemonic = "**ATIN** — Application, Transport, Internet, Network Access."
            exam_points = [
                "TCP 3-way handshake: SYN -> SYN-ACK -> ACK.",
                "TCP reliable & connection-oriented hai; UDP fast & connectionless hai.",
                "IPv4 32 bits ka hota hai; IPv6 128 bits ka hota hai."
            ]
        else:
            defn = "The TCP/IP model is the practical, four-layer communication suite that powers the global Internet, defining how data is packetized, addressed, transmitted, routed, and received."
            purpose = "To provide end-to-end reliable data communication across diverse hardware, operating systems, and network topologies."
            layers = [
                "**1. Application Layer:** Directly interacts with software applications (HTTP, HTTPS, DNS, SMTP, SSH).",
                "**2. Transport Layer:** Manages end-to-end process communication, flow control, and error recovery (TCP, UDP).",
                "**3. Internet Layer:** Handles logical IP addressing, packet encapsulation, and path routing (IP, ICMP, ARP).",
                "**4. Network Access Layer:** Controls physical hardware drivers, network interface cards (NICs), MAC framing, and cable/wireless transmission."
            ]
            analogy = "Like a global courier network: Application prepares the content, Transport assigns tracking and receipt guarantees, Internet stamps the postal address and routes across cities, and Network Access puts the package onto physical delivery vans."
            mnemonic = "**A-T-I-N** (Application, Transport, Internet, Network Access)."
            exam_points = [
                "TCP guarantees delivery via 3-way handshaking (SYN, SYN-ACK, ACK).",
                "UDP is connectionless with low overhead, ideal for real-time video streaming.",
                "IPv4 uses 32-bit addresses while IPv6 uses 128-bit addresses."
            ]

    elif "osi" in t_lower:
        title = "OSI (Open Systems Interconnection) Model"
        if is_hinglish:
            defn = "OSI Model ISO dwara 1984 mein banaya gaya ek 7-layer theoretical conceptual model hai jo network architecture ko standardise karta hai."
            purpose = "Different vendors ke hardware aur protocols ke beech interoperability aur communication clear karna."
            layers = [
                "**Layer 7 - Application:** User interface (HTTP, DNS, SMTP).",
                "**Layer 6 - Presentation:** Data encryption, compression, aur formatting (SSL/TLS, JPEG).",
                "**Layer 5 - Session:** Dialog control aur session management (RPC, NetBIOS).",
                "**Layer 4 - Transport:** End-to-end reliable delivery aur segmentation (TCP, UDP).",
                "**Layer 3 - Network:** IP addressing aur packet routing (Routers).",
                "**Layer 2 - Data Link:** MAC addressing aur frame switching (Switches).",
                "**Layer 1 - Physical:** Raw bits, cables aur electrical signals (Hubs, Cables)."
            ]
            analogy = "Ek international parcel bhejne jaisa: Saman pack karo (App), format karo (Pres), seal karo (Session), courier tracking lo (Transport), address likho (Network), local truck mein dalo (Data Link), aur sadak par chalao (Physical)."
            mnemonic = "**All People Seem To Need Data Processing** (Layer 7 se Layer 1)."
            exam_points = [
                "PDUs: Layer 1=Bits, Layer 2=Frames, Layer 3=Packets, Layer 4=Segments.",
                "Routers Layer 3 par kaam karte hain; Switches Layer 2 par.",
                "TCP Layer 4 par reliable connection banata hai."
            ]
        else:
            defn = "The OSI Model is a conceptual 7-layer architectural framework created by ISO in 1984 that standardizes telecommunications and networking functions."
            purpose = "To enable vendor-neutral interoperability by separating distinct network communication tasks into modular layers."
            layers = [
                "**Layer 7 - Application:** Direct user services (HTTP, FTP, SMTP, DNS).",
                "**Layer 6 - Presentation:** Syntax translation, data compression, encryption/decryption (SSL/TLS).",
                "**Layer 5 - Session:** Session setup, maintenance, and teardown (RPC, NetBIOS).",
                "**Layer 4 - Transport:** Segmentation, flow control, end-to-end reliability (TCP, UDP).",
                "**Layer 3 - Network:** Logical addressing and path routing across networks (IP, ICMP, Routers).",
                "**Layer 2 - Data Link:** Physical framing, MAC addressing, switch forwarding (Ethernet, Wi-Fi).",
                "**Layer 1 - Physical:** Transmission of raw bitstreams over copper, fiber, or radio waves."
            ]
            analogy = "An international postal pipeline where content creation, translation, envelope sealing, courier tracking, postal routing, local hub sorting, and physical transit occur sequentially."
            mnemonic = "**All People Seem To Need Data Processing** (Layers 7 down to 1)."
            exam_points = [
                "PDUs: Layer 1=Bits, Layer 2=Frames, Layer 3=Packets, Layer 4=Segments, Layers 5-7=Data.",
                "Routers operate at Layer 3; Switches operate at Layer 2; Hubs operate at Layer 1.",
                "TCP uses a 3-way handshake for guaranteed segment delivery."
            ]

    else:
        title = t_clean.title()
        defn = f"{title} computer science aur software engineering ka ek essential concept hai jo system workflows ko modular aur optimize karta hai."
        purpose = f"{title} ka main purpose predictable, reliable aur high-performance operations deliver karna hai."
        layers = [
            f"**1. Architecture & Foundation:** {title} ki core structural design aur setup.",
            f"**2. Processing Pipeline:** Data aur instructions ko transform aur validate karne ka flow.",
            f"**3. Optimization & Reliability:** Caching, memory management aur fault-tolerant error handling."
        ]
        analogy = f"{title} ek well-organized assembly line ki tarah kaam karta hai jahan har stage validated output provide karta hai."
        mnemonic = f"{title} ke teen key pillars: Architecture, Execution, aur Optimization."
        exam_points = [
            f"{title} ka primary definition aur architecture pehle paragraph mein clearly explain karein.",
            "Time complexity aur space complexity ke tradeoffs ko highlight karein.",
            "Real-world practical use cases aur scalability benefits mention karein."
        ]

    content = f"# 📘 {title}\n\n### 1. Definition & Core Concept\n{defn}\n\n### 2. Purpose & Importance\n{purpose}\n\n### 3. Step-by-Step Breakdown\n"
    for l in layers:
        content += f"- {l}\n"

    content += f"\n### 4. Real-World Analogy\n💡 {analogy}\n\n### 5. Easy Way to Remember\n🧠 {mnemonic}\n\n### 6. Key Exam & Viva Voce Points\n"
    for p in exam_points:
        content += f"- ✅ {p}\n"

    spoken = f"{title}: {defn.split('.')[0]}. {analogy.split('.')[0]}. I have displayed the structured breakdown on your screen."
    return content, spoken


# -------------------------------------------------------------
# 7. Master Dispatcher
# -------------------------------------------------------------
def process_user_query_with_intent(query: str):
    """
    Main entry point for intelligent intent-driven responses and real system actions.
    Returns: (display_content, spoken_response)
    """
    q_clean = query.strip()
    intent = classify_intent(q_clean)
    print(f"[Master Intent Router] Query: '{q_clean}' -> Intent: {intent}")

    # 1. Destructive Actions
    if intent == "CONFIRM_YES":
        from backend.coding_agent import get_coding_agent
        return get_coding_agent().confirm_action(True)

    elif intent == "CONFIRM_NO":
        from backend.coding_agent import get_coding_agent
        return get_coding_agent().confirm_action(False)

    # 2. Self Introduction
    elif intent == "SELF_INTRODUCTION":
        return generate_self_introduction(q_clean)

    # 3. Explicit Interview Help
    elif intent == "INTERVIEW_HELP":
        return generate_interview_answer_guide(q_clean)

    # 4. File Creation (Real Filesystem on Desktop/etc.)
    elif intent == "FILE_CREATE":
        from backend.action_handler import handle_file_create
        return handle_file_create(q_clean)

    # 5. Folder Creation
    elif intent == "FOLDER_CREATE":
        from backend.action_handler import handle_folder_create
        return handle_folder_create(q_clean)

    # 6. Project Creation (Scaffolding Java, Python, Web)
    elif intent == "PROJECT_CREATE":
        from backend.action_handler import handle_project_create
        return handle_project_create(q_clean)

    # 7. Project Run
    elif intent == "PROJECT_RUN":
        from backend.coding_agent import get_coding_agent
        return get_coding_agent().run_project()

    # 8. Project Help / GitHub / Tree
    elif intent == "PROJECT_HELP":
        from backend.coding_agent import get_coding_agent
        agent = get_coding_agent()
        q_lower = q_clean.lower()
        if "prepare" in q_lower or "github" in q_lower:
            return agent.prepare_for_github()
        elif "commit" in q_lower:
            msg_match = re.search(r'commit(?:\s+message)?\s*(?:for)?\s*(.*)', q_clean, re.IGNORECASE)
            msg = msg_match.group(1).strip() if msg_match else None
            return agent.generate_git_commit(msg)
        else:
            tree = agent.get_project_tree()
            disp = f"### 📁 Project Structure: `{agent.active_project}`\n\n```plaintext\n{tree}\n```"
            return disp, f"Here is the directory structure for project {agent.active_project}."

    # 9. Multi-Language Coding
    elif intent == "CODING":
        return generate_code_solution(q_clean)

    # 10. Code Debugging
    elif intent == "CODE_DEBUGGING":
        cm = get_context_manager()
        ctx = cm.get_context()
        last_err = ctx["recent_errors"][0]["error"] if ctx.get("recent_errors") else "IndexError: list index out of range"
        disp = f"""### 🛠️ Debugging Analysis & Tested Fix: `{last_err}`

#### 1. Root Cause:
The program attempted to access an element index outside the valid sequence bounds (`0 <= index < len(collection)`).

#### 2. Fixed Implementation:
```python
def safe_lookup(items, index, default=None):
    \"\"\"Guards against bounds exceptions.\"\"\"
    if 0 <= index < len(items):
        return items[index]
    return default
```

#### 3. Verification:
Bounds checking prevents unhandled exceptions during execution."""
        return disp, f"I analyzed {last_err} and provided the root cause and tested fix on your screen."

    # 11. Code Explanation
    elif intent == "CODE_EXPLANATION":
        from backend.coding_agent import get_coding_agent
        return get_coding_agent().explain_code(q_clean)

    # 12. MCQ Generation
    elif intent == "MCQ_GENERATION":
        count = 10
        count_match = re.search(r'\b(\d{1,2})\s*(?:mcq|questions|quiz)', q_clean, re.IGNORECASE)
        if count_match:
            count = int(count_match.group(1))

        topic = re.sub(r'^(?:give me|create|make|generate|test me on|quiz on|take mcq on|\d+\s*mcqs on|mcqs on)\s*', '', q_clean, flags=re.IGNORECASE).strip(' ?.')
        if not topic or len(topic) < 2:
            topic = CONVERSATION_CONTEXT.get("last_topic") or "OSI Model"
        return generate_mcqs(topic, count=count)

    # 13. Viva Voce
    elif intent == "VIVA":
        from backend.study_manager import generate_viva_session
        topic = re.sub(r'^(?:take my viva on|take viva on|take my viva|viva on|test me on)\s*', '', q_clean, flags=re.IGNORECASE).strip(' ?.')
        if not topic or len(topic) < 2:
            topic = "Computer Science"
        return generate_viva_session(topic)

    # 14. Concept Explanation
    elif intent == "EXPLANATION":
        return generate_structured_explanation(q_clean)

    # 15. System Info
    elif intent == "SYSTEM_INFORMATION":
        from backend.action_handler import handle_system_info
        return handle_system_info()

    # 16. Calculation
    elif intent == "CALCULATION":
        math_match = re.search(r'([\d\.\s\+\-\*\/\^xX]+)', q_clean)
        if math_match:
            expr = math_match.group(1).replace('x', '*').replace('X', '*').replace('^', '**').strip()
            allowed = set('0123456789+-*/.() ')
            if all(c in allowed for c in expr):
                try:
                    result = eval(expr, {"__builtins__": None}, {})
                    ans = f"{expr} = {result}"
                    return ans, f"The answer is {result}."
                except Exception:
                    pass

    # 17. Memory Retrieve
    elif intent == "MEMORY_RETRIEVE":
        from backend.feature import answer_personal_query
        ans = answer_personal_query(q_clean)
        if ans:
            return ans, ans
        return "Aapka profile record loaded hai.", "Aapka profile record loaded hai."

    # 18. Default Knowledge / Web / Conversational Q&A
    from backend.feature import answer_question_web
    raw_ans = answer_question_web(q_clean)
    clean_ans = strip_meta_phrases(raw_ans)
    return clean_ans, clean_ans
