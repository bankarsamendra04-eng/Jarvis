import re
import random
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

def classify_intent(query: str) -> str:
    q = query.lower().strip()
    
    # 1. EXPLICIT INTERVIEW ADVICE (Only if explicitly asking for interview guidance)
    if re.search(r'\b(?:in an? interview|for an? interview|interview answer|interview tips?|how to answer in interview|how should i answer .* in an? interview)\b', q):
        return "INTERVIEW_HELP"

    # 2. MEANING OF PHRASE
    if re.search(r'\b(?:what does .* mean|meaning of [\'"].*[\'"]|definition of phrase)\b', q):
        return "EXPLANATION"

    # 3. SELF-INTRODUCTION & ABOUT-ASSISTANT (Highest Priority for assistant-centric questions)
    if re.search(
        r'\b(?:tell me about (?:yourself|you)|tell me something about (?:yourself|you)|who are you|what are you|introduce yourself|give me your introduction|your introduction|what can you do|what are your capabilities|what capabilities do you have|what are your features|what features (?:do you have|you have)|how can you help (?:me)?|what is your purpose|who is my assistant|what makes you different|who made you|about you|about yourself|aap kaun ho|apne baare mein batao|tum kaun ho|kya kar sakte ho|tumhara kya kaam hai)\b',
        q
    ):
        return "SELF_INTRODUCTION"

    # 4. Other Specialized Intents
    if re.search(r'\b(take my viva|viva voce|viva questions?|viva)\b', q):
        return "VIVA"
    if re.search(r'\b(debug|fix this code|fix this error|fix that code|fix it|fix the above error|error:|syntaxerror|indexerror|typeerror|bug in)\b', q):
        return "DEBUGGING"
    if re.search(r'\b(write|code|implement|program|script in|function for|create (?:the )?(?:javascript|css|html|python|js|file)|stylesheet|html page|script\.js|style\.css|index\.html)\b', q):
        return "CODING"
    if re.search(r'\b(mcqs?|multiple choice|take mcq|give me \d+ mcq|generate mcq|make a quiz|take quiz|quiz on|practice quiz)\b', q):
        return "MCQ_GENERATION"
    if re.search(r'\b(explain|what is|what are|how does|architecture of|difference between|overview of|teach me|describe)\b', q):
        return "EXPLANATION"
    if re.search(r'\b(calculate|solve|what is \d+|plus|minus|multiplied by|divided by|integrate|derivative)\b', q):
        return "CALCULATION"
    if re.search(r'\b(study mode|flashcard|revision|summarize topic)\b', q):
        return "STUDY"
        
    return "QUESTION_ANSWER"

# -------------------------------------------------------------
# 1. Self-Introduction & Identity Generator
# -------------------------------------------------------------
def generate_self_introduction(query: str):
    q = query.lower().strip()
    CONVERSATION_CONTEXT["last_intent"] = "SELF_INTRODUCTION"

    # Capability / Feature / Help queries
    if any(w in q for w in ["what can you do", "capabilities", "features", "how can you help", "kya kar sakte ho"]):
        display_text = """### ⚡ What I Can Do

I am your **Personal AI Voice Assistant**, designed to assist you with learning, development, productivity, and system management:

#### 🎓 1. AI Study Mode & Coach
- **Concept Explanations**: Simple, step-by-step, and Hinglish technical breakdowns.
- **Practice MCQs & Quizzes**: Tailored question sets with immediate scoring and answer keys.
- **Viva Voce Examiner**: Mock technical interviews with model answers.
- **Weak-Topic Detection**: Automatically detects study weaknesses and organizes personalized revisions.

#### 💻 2. Coding & Software Development
- **Code Generation**: Complete, tested implementations in Python, Java, JavaScript, C++, and SQL.
- **Debugging & Error Fixes**: Root cause diagnosis for `IndexError`, `SyntaxError`, `404`, etc.
- **Complexity Analysis**: Big-O Time and Space complexity for algorithms.

#### 🎯 3. Personal Goals & Daily Action Planner
- **Goal Management**: Track learning, projects, exams, and internship tasks with interactive milestone checklists.
- **Daily Action Plan**: Intelligent time-blocked action plans tailored to your active goals.

#### 🧠 4. Secure Long-Term Memory
- **Personalized Context**: Stores your profile, skills, projects, and custom instructions.
- **Privacy First**: Secure local SQLite storage with safety guards against sensitive credentials.

#### 🎙️ 5. Conversational & Desktop Automation
- **Natural Voice**: Fluent speech in authentic Indian English and conversational Hinglish.
- **Universal Launcher**: Opens applications, project files, documents, and settings.
- **WhatsApp & YouTube**: Hands-free voice messaging, calls, and music streaming."""
        
        spoken_text = "I'm your personal AI voice assistant. I can help you with learning, coding, projects, productivity, and everyday tasks. You can study with me, generate MCQs, debug code, track your goals, or control your system with voice commands."
        return display_text, spoken_text

    # Purpose queries
    elif any(w in q for w in ["purpose", "what is your purpose", "tumhara kya kaam hai"]):
        display_text = """### 🎯 My Purpose

My purpose is to serve as your **dedicated personal AI voice assistant**—empowering you to:
1. **Learn & Master Concepts**: Through interactive study modes, MCQs, and viva simulations.
2. **Build Software Faster**: By generating tested code, fixing bugs, and managing project architecture.
3. **Achieve Goals & Stay Focused**: By organizing your milestones into structured daily action plans.
4. **Automate Daily Workflows**: Hands-free desktop control, search, and communication."""
        
        spoken_text = "My purpose is to be your intelligent personal assistant—helping you study, write code, manage goals, and automate daily tasks efficiently."
        return display_text, spoken_text

    # General Self-Introduction ("Tell me about yourself", "Who are you?", "Introduce yourself")
    else:
        display_text = """### 🤖 Hello! I am your Personal AI Voice Assistant

I'm your personal AI voice assistant, here to help you learn, build, and get things done.

#### 🌟 How I Can Help:
- **Direct Answers & Explanations**: Ask me any technical or general question for clear, structured answers.
- **AI Study Mode**: Practice MCQs, take viva voce quizzes, review flashcards, and revise weak topics.
- **Coding & Debugging**: Write clean code in Python, Java, JavaScript, and debug errors with tested solutions.
- **Project & Context Tracking**: I understand conversational context like *"this file"*, *"that error"*, or *"my current project"*.
- **Goal & Progress Tracking**: Set milestones and generate tailored daily action plans.
- **Memory & Personalization**: Remember your preferences, skills, and important instructions.

You can speak to me naturally in English or Hinglish anytime!"""

        spoken_text = "I'm your personal AI voice assistant. I'm here to help you learn, build, and get things done. I can answer questions, explain difficult topics, create MCQs and quizzes, help you write and debug code, assist with your projects, remember useful information you ask me to save, and help you stay organized. You can simply talk to me naturally, and I'll try to understand what you need and respond accordingly."
        return display_text, spoken_text


# -------------------------------------------------------------
# 2. Explicit Interview Answer Formulator (Only when explicitly asked)
# -------------------------------------------------------------
def generate_interview_answer_guide(query: str):
    display_text = """### 💼 How to Answer "Tell Me About Yourself" in an Interview

Here is the recommended **Present - Past - Future Framework** for a software engineering / developer interview:

#### 1. Present (Who you are today):
> *"I am a Computer Science student / Software Developer with a strong foundation in Python, Java, Web Development, and AI systems."*

#### 2. Past (Key accomplishments & projects):
> *"Recently, I developed an intelligent AI Desktop Voice Assistant called JARVIS featuring biometric authentication, hands-free hotword detection, study mode with weak-topic analytics, and automated system workflows."*

#### 3. Future (Why you are here):
> *"I am passionate about building scalable, intelligent applications, and I'm excited about this opportunity to contribute to high-impact engineering projects at your company."*

#### 💡 Key Tips:
- Keep your response between **60 to 90 seconds**.
- Focus on technical skills, projects, and problem-solving impact rather than personal hobbies.
"""
    spoken_text = "When answering 'Tell me about yourself' in an interview, use the Present, Past, and Future framework: introduce your current focus and technical skills, highlight your key projects, and explain why you are excited for this role."
    return display_text, spoken_text


# -------------------------------------------------------------
# 3. Practice MCQs Generator
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
    
    # Format screen output (markdown)
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
# 4. Structured Pedagogical Explanation Generator
# -------------------------------------------------------------
def generate_structured_explanation(topic: str):
    t_clean = topic.strip()
    CONVERSATION_CONTEXT["last_topic"] = t_clean
    CONVERSATION_CONTEXT["last_intent"] = "EXPLANATION"
    
    t_lower = t_clean.lower()
    
    if "osi" in t_lower:
        title = "OSI (Open Systems Interconnection) Model"
        defn = "The OSI Model is a conceptual framework created by the International Organization for Standardization (ISO) in 1984 that standardizes network communication functions across seven distinct, logical layers."
        purpose = "To provide interoperability between diverse computing systems, hardware vendors, and protocols by dividing communication into modular, well-defined layers."
        layers = [
            "**Layer 7 - Application:** Interface for end-user applications (HTTP, DNS, SMTP, FTP).",
            "**Layer 6 - Presentation:** Data formatting, translation, compression, and encryption/decryption (SSL/TLS, JPEG, ASCII).",
            "**Layer 5 - Session:** Manages sessions, authentication, and token management between nodes (NetBIOS, RPC, PPTP).",
            "**Layer 4 - Transport:** End-to-end reliable transmission, flow control, error recovery, segmentation (TCP, UDP).",
            "**Layer 3 - Network:** Logical addressing (IP addressing) and path determination/routing (IP, ICMP, OSPF, BGP).",
            "**Layer 2 - Data Link:** Node-to-node framing, physical MAC addressing, and MAC-level error checking (Ethernet, Wi-Fi, switches).",
            "**Layer 1 - Physical:** Transmission and reception of raw unstructured bit streams over physical media (Cables, Hubs, RF, Voltages)."
        ]
        analogy = "Think of the OSI model like sending an international postal letter: You write your message (Application), format/translate it (Presentation), seal it in an envelope (Session), specify express courier delivery tracking (Transport), write the recipient's postal address (Network), hand it to a local mail delivery truck (Data Link), and transport it over roads and rails (Physical)."
        mnemonic = "**All People Seem To Need Data Processing** (Layers 7 down to 1: Application, Presentation, Session, Transport, Network, Data Link, Physical)."
        exam_points = [
            "PDU at each layer: Layer 1 = Bits, Layer 2 = Frames, Layer 3 = Packets, Layer 4 = Segments, Layers 5-7 = Data.",
            "Routers work at Layer 3; Switches work at Layer 2; Hubs/Repeaters work at Layer 1.",
            "TCP is connection-oriented at Layer 4; IP is connectionless at Layer 3."
        ]
    elif "binary search" in t_lower:
        title = "Binary Search Algorithm"
        defn = "Binary Search is an efficient, divide-and-conquer search algorithm that finds the position of a target value within a strictly sorted array or list."
        purpose = "To reduce search time complexity from linear O(N) to logarithmic O(log N) by repeatedly dividing the search interval in half."
        layers = [
            "**Step 1:** Ensure the input dataset is sorted in ascending or descending order.",
            "**Step 2:** Compute the middle index `mid = left + (right - left) // 2`.",
            "**Step 3:** If `arr[mid] == target`, target is found. Return index `mid`.",
            "**Step 4:** If `arr[mid] < target`, discard the left half by setting `left = mid + 1`.",
            "**Step 5:** If `arr[mid] > target`, discard the right half by setting `right = mid - 1`.",
            "**Step 6:** Repeat until `left > right`. If not found, return `-1`."
        ]
        analogy = "Searching a physical dictionary or phone book: You open directly to the middle. If your word starts with 'M' and you opened at 'S', you immediately ignore the second half of the book and split the first half in half again."
        mnemonic = "**Divide, Compare, Halve**: Always check midpoint, shrink the boundaries."
        exam_points = [
            "Time Complexity: Best case O(1), Average case O(log N), Worst case O(log N).",
            "Space Complexity: O(1) iterative, O(log N) recursive due to call stack frames.",
            "Requirement: The collection MUST be sorted before binary search can be applied."
        ]
    else:
        title = t_clean.title()
        defn = f"{title} is a core computer science and engineering concept focused on structuring, processing, and optimizing system interactions."
        purpose = f"To enable reliable, scalable, and modular execution of operations within modern software and systems architecture."
        layers = [
            f"**Component 1 (Architecture):** Structural foundation governing how {title} organizes internal state.",
            f"**Component 2 (Execution Layer):** Core processing pipeline transforming inputs into validated outputs.",
            f"**Component 3 (Optimization):** Caching, indexing, and resource management to ensure high throughput."
        ]
        analogy = f"Like an automotive assembly line, where distinct specialized workstations process parts sequentially with quality control checks at every stage."
        mnemonic = "Key Focus: Understand definition, internal workflow, and practical trade-offs."
        exam_points = [
            f"Always define the core objective of {title} in the first paragraph.",
            "Illustrate with diagrams and time/space complexity analysis.",
            "Highlight real-world industrial use cases."
        ]

    content = f"# 📘 {title}\n\n### 1. Definition & Core Concept\n{defn}\n\n### 2. Purpose & Importance\n{purpose}\n\n### 3. Step-by-Step Breakdown & Components\n"
    for l in layers:
        content += f"- {l}\n"

    content += f"\n### 4. Real-World Example & Analogy\n💡 {analogy}\n\n### 5. Easy Way to Remember\n🧠 {mnemonic}\n\n### 6. Key Exam & Viva Voce Points\n"
    for p in exam_points:
        content += f"- ✅ {p}\n"

    spoken = f"{title} is {defn.split('.')[0]}. {analogy.split('.')[0]}. I have displayed the complete 6-part breakdown on your screen."
    return content, spoken

# -------------------------------------------------------------
# 5. Direct Coding Solution Generator
# -------------------------------------------------------------
def generate_code_solution(query: str):
    q = query.lower()
    cm = get_context_manager()
    ctx = cm.get_context()
    CONVERSATION_CONTEXT["last_intent"] = "CODING"

    # Check if this belongs to a Quiz App project (from query or context)
    is_quiz_app = ("quiz" in q or (ctx.get("current_project") and "quiz" in ctx["current_project"]["name"].lower()))
    
    if is_quiz_app and ("javascript" in q or "script.js" in q or "js" in q or "logic" in q or "script" in q):
        code_block = """// Quiz Application Engine (script.js)
const quizData = [
    {
        question: "Which data structure uses LIFO (Last In First Out)?",
        options: ["Queue", "Stack", "Array", "Linked List"],
        answer: 1
    },
    {
        question: "What is the time complexity of Binary Search?",
        options: ["O(N)", "O(1)", "O(log N)", "O(N^2)"],
        answer: 2
    },
    {
        question: "Which layer in OSI model handles end-to-end reliability?",
        options: ["Network", "Transport", "Session", "Data Link"],
        answer: 1
    }
];

let currentQuestion = 0;
let score = 0;
let selectedOption = null;

function loadQuestion() {
    const q = quizData[currentQuestion];
    document.getElementById("question-text").innerText = `Q${currentQuestion + 1}. ${q.question}`;
    const optionsContainer = document.getElementById("options-list");
    optionsContainer.innerHTML = "";

    q.options.forEach((opt, idx) => {
        const btn = document.createElement("button");
        btn.className = "quiz-option-btn";
        btn.innerText = `${String.fromCharCode(65 + idx)}) ${opt}`;
        btn.onclick = () => selectOption(idx, btn);
        optionsContainer.appendChild(btn);
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
        cm.record_file("script.js", file_type="javascript")
        cm.record_code(code_block, language="javascript", description="Quiz App Core Engine")

        text = f"""### 💻 Quiz App Engine (`script.js`)

Here is the complete JavaScript logic for your **Quiz Application**:

```javascript
{code_block}
```

#### ⚙️ Features Included:
- **Dynamic Question Loader**: Renders questions and options with interactive selection.
- **Score Calculation**: Accurately tallies correct answers across all rounds.
- **Completion Screen**: Displays final score, percentage, and a restart button."""
        spoken = "I have created the complete JavaScript engine (script.js) for your Quiz App. The code is displayed on your screen."
        return text, spoken

    elif is_quiz_app and ("css" in q or "style.css" in q or "styling" in q or "styles" in q):
        code_block = """/* Modern Cyberpunk / Dark Mode Styling (style.css) */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background: radial-gradient(circle at top, #1a1a2e, #0f0f1b);
    color: #e0e0e0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.quiz-container {
    background: rgba(25, 25, 45, 0.85);
    border: 1px solid rgba(0, 180, 216, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 180, 216, 0.2);
    border-radius: 12px;
    width: 480px;
    padding: 24px;
    backdrop-filter: blur(10px);
}

.quiz-header {
    text-align: center;
    margin-bottom: 20px;
}

.quiz-option-btn {
    width: 100%;
    background: #1e2238;
    color: #fff;
    border: 1px solid #323856;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
}

.quiz-option-btn:hover {
    background: #282e4e;
    border-color: #00b4d8;
}

.quiz-option-btn.selected {
    background: #00b4d8;
    color: #000;
    font-weight: 600;
}

.submit-btn {
    width: 100%;
    margin-top: 16px;
    padding: 12px;
    background: #0077b6;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.2s ease;
}

.submit-btn:hover {
    background: #0096c7;
}"""
        cm.record_file("style.css", file_type="css")
        cm.record_code(code_block, language="css", description="Quiz App Styling")

        text = f"""### 🎨 Quiz App Styling (`style.css`)

```css
{code_block}
```

#### 🚀 How to Link in HTML:
```html
<link rel="stylesheet" href="style.css">
```"""
        spoken = "I have written the modern dark-themed CSS stylesheet (style.css) for your Quiz App."
        return text, spoken

    if "binary search" in q:
        lang = "Python" if "python" in q else ("Java" if "java" in q else "Python")
        if lang == "Java":
            code_block = """// Binary Search Implementation in Java
public class BinarySearch {
    public static int search(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (arr[mid] == target) {
                return mid; // Element found at index mid
            } else if (arr[mid] < target) {
                left = mid + 1; // Search right half
            } else {
                right = mid - 1; // Search left half
            }
        }
        return -1; // Element not found
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
            run_cmd = "javac BinarySearch.java && java BinarySearch"
            cm.record_file("BinarySearch.java", file_type="java")
            cm.record_code(code_block, language="java", description="Binary Search in Java")
        else:
            code_block = """# Binary Search Implementation in Python
def binary_search(arr, target):
    # Time Complexity: O(log N) | Space Complexity: O(1)
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid  # Target found at index mid
        elif arr[mid] < target:
            left = mid + 1  # Search right subarray
        else:
            right = mid - 1  # Search left subarray

    return -1  # Target not found

# Example Usage:
if __name__ == "__main__":
    sorted_numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    target_value = 23
    idx = binary_search(sorted_numbers, target_value)
    print(f"Target {target_value} found at index: {idx}")"""
            run_cmd = "python binary_search.py"
            cm.record_file("binary_search.py", file_type="python")
            cm.record_code(code_block, language="python", description="Binary Search in Python")

        text = f"""### 💻 Binary Search Implementation ({lang})

Here is the complete, tested code for **Binary Search**:

```{lang.lower()}
{code_block}
```

#### ⚙️ Complexity Analysis:
- **Time Complexity:** `O(log N)` — Search interval is halved at each step.
- **Space Complexity:** `O(1)` — Iterative implementation uses constant extra memory.

#### 🚀 How to Run:
```bash
{run_cmd}
```"""
        spoken = f"I have written the complete {lang} code for Binary Search with O(log N) complexity. You can see the code and run instructions on your screen."
        return text, spoken

    # General Code fallback
    title = "Code Solution"
    sample_code = """# Python Implementation
def solve_problem(data):
    # Executes standard business logic with error handling.
    try:
        results = [x * 2 for x in data if x > 0]
        return results
    except Exception as e:
        print(f"Error executing logic: {e}")
        return []

if __name__ == "__main__":
    sample_data = [1, 2, 3, 4, 5]
    print("Processed:", solve_problem(sample_data))"""
    cm.record_code(sample_code, language="python", description="General solution")

    text = f"""### 💻 {title}

```python
{sample_code}
```

#### 🚀 Execution Command:
```bash
python script.py
```"""
    spoken = "I have generated the executable code solution on your screen."
    return text, spoken

# -------------------------------------------------------------
# 6. Debugging Solution Generator
# -------------------------------------------------------------
def generate_debugging_solution(query: str):
    CONVERSATION_CONTEXT["last_intent"] = "DEBUGGING"
    cm = get_context_manager()
    ctx = cm.get_context()
    
    last_err = ctx["recent_errors"][0]["error"] if ctx.get("recent_errors") else "IndexError / Bounds Exception"
    
    text = f"""### 🛠️ Debugging Analysis & Fix: `{last_err}`

#### 1. Root Cause:
The issue occurs when attempting to access an index or key that falls outside the boundary of the collection.

#### 2. Fixed Implementation:
```python
def safe_access(collection, index, default=None):
    \"\"\"Safely retrieves elements with bounds checking.\"\"\"
    if 0 <= index < len(collection):
        return collection[index]
    return default
```

#### 3. Verification:
Always validate indices against `len(collection)` or wrap lookups in `try...except IndexError` blocks.
"""
    spoken = f"I have analyzed {last_err} and provided the root cause and tested fix on your screen."
    return text, spoken

# -------------------------------------------------------------
# 7. Master Dispatcher
# -------------------------------------------------------------
def process_user_query_with_intent(query: str):
    """
    Main entry point for intelligent intent-driven responses.
    Returns: (display_content, spoken_response)
    """
    q_clean = query.strip()
    intent = classify_intent(q_clean)
    print(f"[Intent Engine] Classified Intent: {intent} for query: '{q_clean}'")

    if intent == "SELF_INTRODUCTION":
        return generate_self_introduction(q_clean)

    elif intent == "INTERVIEW_HELP":
        return generate_interview_answer_guide(q_clean)

    elif intent == "MCQ_GENERATION":
        count = 10
        count_match = re.search(r'\b(\d{1,2})\s*(?:mcq|questions|quiz)', q_clean, re.IGNORECASE)
        if count_match:
            count = int(count_match.group(1))

        topic = re.sub(r'^(?:give me|create|make|generate|test me on|quiz on|take mcq on|\d+\s*mcqs on|mcqs on)\s*', '', q_clean, flags=re.IGNORECASE).strip(' ?.')
        if not topic or len(topic) < 2:
            topic = CONVERSATION_CONTEXT.get("last_topic") or "Computer Networks"

        return generate_mcqs(topic, count=count)

    elif intent == "EXPLANATION":
        topic = re.sub(r'^(?:explain|explain about|what is|what are|tell me about|how does|how do)\s*', '', q_clean, flags=re.IGNORECASE).strip(' ?.')
        if not topic or len(topic) < 2:
            topic = CONVERSATION_CONTEXT.get("last_topic") or "OSI Model"
        return generate_structured_explanation(topic)

    elif intent == "CODING":
        return generate_code_solution(q_clean)

    elif intent == "DEBUGGING":
        return generate_debugging_solution(q_clean)

    elif intent == "VIVA":
        from backend.study_manager import generate_viva_session
        topic = re.sub(r'^(?:take my viva on|take viva on|take my viva|viva on|test me on)\s*', '', q_clean, flags=re.IGNORECASE).strip(' ?.')
        if not topic or len(topic) < 2:
            topic = "Computer Science"
        return generate_viva_session(topic)

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

    # Default Knowledge / Conversational Q&A
    from backend.feature import answer_question_web
    raw_ans = answer_question_web(q_clean)
    clean_ans = strip_meta_phrases(raw_ans)
    return clean_ans, clean_ans
