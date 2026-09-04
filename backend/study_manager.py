import os
import re
import json
import sqlite3
import datetime
import random
import eel
from backend.command import speak

DB_PATH = "jarvis.db"

# Global Study Mode State in Memory
STUDY_MODE_ACTIVE = False
ACTIVE_STUDY_SUBJECT = "Computer Networks"

# -------------------------------------------------------------
# SQLite Database Initialization
# -------------------------------------------------------------
def init_study_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Study Sessions
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(100) NOT NULL,
            topic VARCHAR(200) NULL,
            mode VARCHAR(50) DEFAULT 'General',
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME NULL,
            notes TEXT NULL
        )
    """)

    # 2. Quiz History & Performance Tracking
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(100) NOT NULL,
            topic VARCHAR(200) NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            pct INTEGER NOT NULL,
            incorrect_topics TEXT DEFAULT '[]',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Weak Topics Tracking Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS weak_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(100) NOT NULL,
            topic VARCHAR(200) NOT NULL,
            error_count INTEGER DEFAULT 1,
            last_tested DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'Needs Revision',
            UNIQUE(subject, topic)
        )
    """)

    # 4. Flashcard Mastery Tracking
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcard_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(100) NOT NULL,
            card_id VARCHAR(50) NOT NULL,
            mastered INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subject, card_id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------------------
# Built-in High-Yield Curriculum & Question Bank
# -------------------------------------------------------------
STUDY_CURRICULUM = {
    "Computer Networks": {
        "topics": ["OSI Model", "TCP vs UDP", "DNS & HTTP/HTTPS", "IP Addressing & Subnetting", "Routing Algorithms", "Congestion Control"],
        "concepts": {
            "OSI Model": {
                "simple": "OSI (Open Systems Interconnection) model ek 7-layer framework hai jo batata hai ki computer networks mein data ek device se doosre device tak kaise travel karta hai.",
                "step_by_step": [
                    "1. Physical Layer: Raw bits (0s and 1s) cables ya radio signals ke through transfer hote hain.",
                    "2. Data Link Layer: MAC address use karke error-free frame delivery karta hai (e.g., Ethernet, Switches).",
                    "3. Network Layer: Logical IP addressing and routing karta hai (e.g., Routers, IP packets).",
                    "4. Transport Layer: End-to-end connection, reliability aur flow control sambhalta hai (e.g., TCP, UDP, Ports).",
                    "5. Session Layer: Devices ke beech communication session establish, maintain aur terminate karta hai.",
                    "6. Presentation Layer: Data encryption, decryption, compression aur formatting karta hai (e.g., SSL/TLS, JPEG).",
                    "7. Application Layer: End-user applications ke sath interact karta hai (e.g., HTTP, FTP, SMTP, DNS)."
                ],
                "example": "Real-world analogy: Jaise ek letter post office se deliver hota hai — aap letter likhte hain (Application), envelope mein seal karte hain (Presentation), address likhte hain (Network), truck se transport hota hai (Transport), aur roads se physical delivery hoti hai (Physical layer).",
                "summary": "7 Layers: Physical, Data Link, Network, Transport, Session, Presentation, Application (Mnemonic: Please Do Not Throw Sausage Pizza Away)."
            },
            "TCP vs UDP": {
                "simple": "TCP connection-oriented protocol hai jo reliable delivery guarantee karta hai (with 3-way handshake). UDP connectionless protocol hai jo fast delivery karta hai bina delivery guarantee ke.",
                "step_by_step": [
                    "TCP (Transmission Control Protocol):",
                    "  - 3-Way Handshake: SYN -> SYN-ACK -> ACK connection establish karta hai.",
                    "  - Ordered packet delivery aur error retransmission deta hai.",
                    "  - Use cases: Web browsing (HTTP/HTTPS), File transfer (FTP), Emails (SMTP).",
                    "UDP (User Datagram Protocol):",
                    "  - Lightweight, low latency, no handshake, no retransmission.",
                    "  - Use cases: Live video streaming, Online multiplayer gaming, VoIP calls, DNS lookup."
                ],
                "example": "Real-world analogy: TCP is like a Registered Post jisme acknowledgment sign hota hai. UDP is like a YouTube live broadcast — agar ek frame miss ho jaye toh stream pause nahi hoti, aage chalti rehti hai.",
                "summary": "TCP = High Reliability, Slower. UDP = High Speed & Low Latency, Unreliable."
            },
            "DNS & HTTP/HTTPS": {
                "simple": "DNS (Domain Name System) internet ka phonebook hai jo human-readable domain names (google.com) ko machine IP addresses (142.250.190.46) mein convert karta hai. HTTPS HTTP ka encrypted and secure version hai jo SSL/TLS use karta hai.",
                "step_by_step": [
                    "1. Browser mein google.com enter karte hi browser DNS cache check karta hai.",
                    "2. Agar cache miss ho, DNS Resolver Recursive lookup karta hai (Root Server -> TLD Server (.com) -> Authoritative Nameserver).",
                    "3. IP address milne ke baad browser target server ke sath TCP handshake + TLS handshake karta hai.",
                    "4. HTTPS port 443 par data encrypt karke bhejta hai, jabki plain HTTP port 80 par unencrypted text bhejta hai."
                ],
                "example": "Real-world analogy: DNS is like truecaller ya contact book jahan aap 'Mom' search karte ho aur phone uska number dial karta hai. HTTPS is like talking in a secret code jo beech mein koi eavesdrop nahi kar sakta.",
                "summary": "DNS resolves domain to IP on Port 53. HTTPS encrypts web traffic using TLS/SSL on Port 443."
            }
        },
        "mcqs": [
            {
                "id": "cn_1",
                "topic": "OSI Model",
                "question": "Which layer of the OSI model is responsible for end-to-end error recovery and flow control?",
                "options": ["A) Network Layer", "B) Transport Layer", "C) Data Link Layer", "D) Session Layer"],
                "answer": "B",
                "explanation": "Transport Layer (Layer 4) handles end-to-end communication, segmentation, flow control, and error recovery (e.g., TCP)."
            },
            {
                "id": "cn_2",
                "topic": "TCP vs UDP",
                "question": "Which protocol uses a 3-way handshake (SYN, SYN-ACK, ACK) before transmitting data?",
                "options": ["A) UDP", "B) ICMP", "C) TCP", "D) ARP"],
                "answer": "C",
                "explanation": "TCP establishes a reliable connection using the 3-way handshake prior to sending data packets."
            },
            {
                "id": "cn_3",
                "topic": "DNS & HTTP/HTTPS",
                "question": "What is the standard port number used by HTTPS for secure encrypted communication?",
                "options": ["A) 80", "B) 21", "C) 53", "D) 443"],
                "answer": "D",
                "explanation": "HTTPS operates on port 443 using SSL/TLS, whereas unencrypted HTTP uses port 80 and DNS uses port 53."
            },
            {
                "id": "cn_4",
                "topic": "Routing Algorithms",
                "question": "Which routing algorithm is Dijkstra's Shortest Path algorithm used in?",
                "options": ["A) Distance Vector Routing", "B) Link State Routing (OSPF)", "C) Flooding", "D) Bellman-Ford Routing"],
                "answer": "B",
                "explanation": "Link State Routing protocols like OSPF calculate the shortest path tree using Dijkstra's algorithm."
            },
            {
                "id": "cn_5",
                "topic": "IP Addressing & Subnetting",
                "question": "How many usable host IP addresses are available in a /24 subnet (255.255.255.0)?",
                "options": ["A) 256", "B) 254", "C) 255", "D) 128"],
                "answer": "B",
                "explanation": "A /24 network has 2^8 = 256 total addresses, minus 2 (Network ID and Broadcast ID) = 254 usable hosts."
            }
        ],
        "viva": [
            {
                "id": "cn_v1",
                "topic": "TCP vs UDP",
                "question": "Why is UDP preferred over TCP for live video streaming and gaming?",
                "answer": "In live streaming and gaming, low latency is critical. Retransmitting lost packets (as in TCP) causes lag/buffering. UDP sends packets without connection overhead or retransmissions, keeping the stream real-time."
            },
            {
                "id": "cn_v2",
                "topic": "OSI Model",
                "question": "What is the difference between a Router and a Switch in terms of OSI layers?",
                "answer": "A Switch works at Layer 2 (Data Link Layer) and forwards frames based on MAC addresses. A Router works at Layer 3 (Network Layer) and routes packets across different networks using IP addresses."
            },
            {
                "id": "cn_v3",
                "topic": "DNS & HTTP/HTTPS",
                "question": "Explain what happens when you type 'https://google.com' in your browser.",
                "answer": "1. DNS resolves google.com to an IP. 2. TCP 3-way handshake established on port 443. 3. TLS cryptographic handshake exchanges certificates and session keys. 4. Browser sends HTTP GET request over encrypted tunnel. 5. Server responds with HTML/CSS payload."
            }
        ],
        "exam_questions": {
            "short": [
                {
                    "question": "Explain the difference between IPv4 and IPv6 (2 Marks).",
                    "answer": "IPv4 uses 32-bit addresses (~4.3 billion unique IPs) written in decimal (192.168.1.1). IPv6 uses 128-bit hexadecimal addresses (~3.4x10^38 IPs) providing virtually unlimited space and built-in IPsec security."
                },
                {
                    "question": "What is ARP (Address Resolution Protocol)? (2 Marks).",
                    "answer": "ARP translates a known logical Layer 3 IP address into a physical Layer 2 MAC address on a local network using broadcast requests and unicast replies."
                }
            ],
            "long": [
                {
                    "question": "Explain the TCP Congestion Control mechanism with Slow Start, Congestion Avoidance, and Fast Recovery. (5 Marks)",
                    "answer": "1. Slow Start: Congestion Window (cwnd) starts at 1 MSS and doubles every RTT (exponential growth) until Slow Start Threshold (ssthresh). 2. Congestion Avoidance: Once cwnd >= ssthresh, growth becomes linear (+1 MSS per RTT) to probe bandwidth safely. 3. Fast Retransmit & Recovery: On receiving 3 duplicate ACKs, TCP retransmits missing segment without waiting for timeout, sets ssthresh = cwnd / 2, and recovers cwnd smoothly."
                }
            ]
        },
        "flashcards": [
            {"id": "fc_cn1", "front": "OSI Layer 3", "back": "Network Layer: Handles IP addressing, packet forwarding, and routing protocols (Routers operate here)."},
            {"id": "fc_cn2", "front": "TCP Handshake", "back": "SYN -> SYN-ACK -> ACK establishing reliable synchronized communication channel."},
            {"id": "fc_cn3", "front": "Port Numbers: HTTP vs HTTPS vs DNS", "back": "HTTP: 80 | HTTPS: 443 | DNS: 53 | SSH: 22 | FTP: 20/21."},
            {"id": "fc_cn4", "front": "Subnet Mask /28", "back": "255.255.255.240 | Block size = 16 | Usable hosts = 14 (16 - 2)."}
        ]
    },

    "Operating Systems": {
        "topics": ["Process vs Thread", "CPU Scheduling", "Deadlocks & Banker's Algorithm", "Paging & Virtual Memory", "Semaphores & Mutex"],
        "concepts": {
            "Process vs Thread": {
                "simple": "Process ek executing program hai jiska apna isolated memory space (Code, Data, Heap, Stack) hota hai. Thread process ke andar ka lightweight unit hai jo parent process ka memory space share karta hai.",
                "step_by_step": [
                    "Process: Isolated memory, heavy context switching overhead, IPC (Inter-Process Communication) required for data sharing.",
                    "Thread: Shares heap & code with peer threads, lightweight context switching, private program counter and stack.",
                    "Multi-threading allows concurrent execution within the same application (e.g., browser tabs or worker background threads)."
                ],
                "example": "Real-world analogy: Ek Factory ek Process hai (apni boundary, resources). Factory ke andar kaam karne wale workers Threads hain jo same raw materials aur machines share karte hain.",
                "summary": "Process = Independent memory space (Heavyweight). Thread = Shared memory space within process (Lightweight)."
            },
            "Deadlocks & Banker's Algorithm": {
                "simple": "Deadlock ek aisi condition hai jahan 2 ya zyada processes ek doosre ke resources release hone ka wait karte hain aur koi bhi aage nahi badh pata (Infinite block).",
                "step_by_step": [
                    "Deadlock ki 4 Coffman Conditions:",
                    "  1. Mutual Exclusion: At least ek non-shareable resource hona chahiye.",
                    "  2. Hold and Wait: Process ek resource hold karke doosre ka wait kar raha ho.",
                    "  3. No Preemption: Resources forcibly cheene nahi ja sakte.",
                    "  4. Circular Wait: P1 waits for P2, P2 waits for P3, and Pn waits for P1.",
                    "Banker's Algorithm: Deadlock avoidance algorithm jo resource allocation se pehle Safe State check karta hai (Need <= Available)."
                ],
                "example": "Real-world analogy: Ek single-lane bridge par do gaadiyan aamne-saamne aa gayi hain aur dono peeche hatne ko taiyar nahi hain.",
                "summary": "Deadlock happens when Mutual Exclusion, Hold & Wait, No Preemption, and Circular Wait occur simultaneously."
            },
            "Paging & Virtual Memory": {
                "simple": "Virtual Memory OS ko allow karta hai physical RAM se bada program run karna by using hard disk space (Swap space). Paging memory management scheme hai jo logical memory ko fixed-size 'Pages' aur physical memory ko 'Frames' mein divide karti hai.",
                "step_by_step": [
                    "1. Logical Address CPU generate karta hai (Page Number + Offset).",
                    "2. Page Table Page Number ko Physical Frame Number se map karta hai.",
                    "3. TLB (Translation Lookaside Buffer) ek fast hardware cache hai jo Page Table lookups speed up karta hai.",
                    "4. Page Fault: Jab requested page RAM mein nahi milta, OS disk se page load karta hai."
                ],
                "example": "Real-world analogy: Kitab ka index page (Page Table) batata hai ki kaun sa chapter (Page) kaun se physical page number (Frame) par printed hai.",
                "summary": "Paging eliminates external fragmentation. Virtual Memory = RAM + Disk Paging file."
            }
        },
        "mcqs": [
            {
                "id": "os_1",
                "topic": "Deadlocks & Banker's Algorithm",
                "question": "Which of the following is NOT one of the four necessary Coffman conditions for a Deadlock?",
                "options": ["A) Mutual Exclusion", "B) Hold and Wait", "C) Preemption", "D) Circular Wait"],
                "answer": "C",
                "explanation": "The condition is 'No Preemption'. If preemption is allowed, deadlock cannot occur."
            },
            {
                "id": "os_2",
                "topic": "CPU Scheduling",
                "question": "Which CPU scheduling algorithm is non-preemptive and can cause the 'Convoy Effect'?",
                "options": ["A) Round Robin", "B) First-Come, First-Served (FCFS)", "C) Shortest Remaining Time First (SRTF)", "D) Priority Scheduling"],
                "answer": "B",
                "explanation": "FCFS suffers from the Convoy Effect when a CPU-intensive long process blocks short processes behind it."
            },
            {
                "id": "os_3",
                "topic": "Paging & Virtual Memory",
                "question": "What happens when a CPU references a page that is not currently loaded in physical RAM?",
                "options": ["A) Segmentation Fault", "B) Page Fault", "C) Thrashing", "D) Buffer Overflow"],
                "answer": "B",
                "explanation": "A Page Fault interrupt is generated, prompting the OS to fetch the page from secondary storage into RAM."
            },
            {
                "id": "os_4",
                "topic": "Semaphores & Mutex",
                "question": "What is the primary difference between a Binary Semaphore and a Mutex?",
                "options": ["A) A Mutex can be locked/unlocked by any thread", "B) A Mutex has ownership (only locking thread can unlock it)", "C) Semaphores cannot prevent race conditions", "D) They are completely identical"],
                "answer": "B",
                "explanation": "A Mutex provides strict ownership (only the thread that acquired the lock can release it), whereas a semaphore is a signaling mechanism."
            }
        ],
        "viva": [
            {
                "id": "os_v1",
                "topic": "Paging & Virtual Memory",
                "question": "What is Thrashing in Operating Systems, and how can it be resolved?",
                "answer": "Thrashing occurs when the OS spends more time swapping pages in and out of disk than executing instructions because physical memory is overloaded. It is resolved by reducing degree of multiprogramming or adding more RAM."
            },
            {
                "id": "os_v2",
                "topic": "Process vs Thread",
                "question": "Why is Context Switching between threads faster than between processes?",
                "answer": "Threads share the same virtual address space, page tables, and memory mappings. Switching threads only requires saving registers, PC, and stack pointer without invalidating TLB caches."
            }
        ],
        "exam_questions": {
            "short": [
                {
                    "question": "Differentiate between Preemptive and Non-Preemptive scheduling (2 Marks).",
                    "answer": "Preemptive scheduling allows the OS to forcibly interrupt a running process when a higher priority process arrives (e.g., Round Robin, SRTF). In Non-Preemptive, once a process gets the CPU, it holds it until termination or I/O (e.g., FCFS, SJF)."
                }
            ],
            "long": [
                {
                    "question": "Explain Banker's Algorithm with data structures (Allocation, Max, Available, Need) for deadlock avoidance. (5 Marks)",
                    "answer": "Banker's Algorithm tests for safety by simulating resource allocation for maximum declared claims. Data structures: 1. Available[m]: instances of each resource type. 2. Max[n][m]: maximum demand of each process. 3. Allocation[n][m]: current assigned resources. 4. Need[n][m] = Max - Allocation. If a sequence exists where every process's Need <= Work, the system is in a Safe State and deadlock is avoided."
                }
            ]
        },
        "flashcards": [
            {"id": "fc_os1", "front": "Deadlock 4 Conditions", "back": "1. Mutual Exclusion  2. Hold & Wait  3. No Preemption  4. Circular Wait"},
            {"id": "fc_os2", "front": "TLB (Translation Lookaside Buffer)", "back": "High-speed associative hardware cache for Page Table address lookups."},
            {"id": "fc_os3", "front": "Belady's Anomaly", "back": "Phenomenon where increasing page frames causes MORE page faults (occurs in FIFO page replacement)."},
            {"id": "fc_os4", "front": "Mutex vs Semaphore", "back": "Mutex = Locking mechanism with thread ownership. Semaphore = Signaling integer counter."}
        ]
    },

    "Database Management Systems": {
        "topics": ["ACID Properties", "Normalization (1NF to BCNF)", "SQL vs NoSQL", "Indexing & B-Trees", "Transactions & Concurrency Control"],
        "concepts": {
            "ACID Properties": {
                "simple": "ACID properties ensure karte hain ki database transactions reliable aur consistent rahein, chahe system crash ya errors kyun na ho.",
                "step_by_step": [
                    "A - Atomicity: 'All or Nothing' rule — transaction ya toh pura complete hoga ya poora rollback hoga.",
                    "C - Consistency: Database valid states mein rehta hai (all integrity constraints & foreign keys preserved).",
                    "I - Isolation: Concurrent transactions ek doosre ke intermediate states ko interfere nahi karte (Isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable).",
                    "D - Durability: Once committed, data crash hone ke baad bhi permanently save rehta hai (Write-Ahead Logging / WAL)."
                ],
                "example": "Real-world analogy: Bank transfer — Samendra ke account se Rs 1000 debit hue aur recipient ke account mein credit hone se pehle power cut ho gaya. Atomicity ensures Rs 1000 wapas refund ho jaye.",
                "summary": "Atomicity (Rollback), Consistency (Rules valid), Isolation (Concurrency safe), Durability (Persistent storage)."
            },
            "Normalization (1NF to BCNF)": {
                "simple": "Normalization relational database design technique hai jisme data redundancy (duplication) aur insertion/update/deletion anomalies ko eliminate kiya jata hai.",
                "step_by_step": [
                    "1NF: Atomic values (no multi-valued attributes / arrays in columns).",
                    "2NF: Must be in 1NF + No partial dependencies (non-prime attributes must depend on the WHOLE primary key).",
                    "3NF: Must be in 2NF + No transitive dependencies (A -> B, B -> C so A -> C removed into separate table).",
                    "BCNF (Boyce-Codd): Stricter 3NF where for every functional dependency X -> Y, X must be a Super Key."
                ],
                "example": "Real-world analogy: Ek phone contact list mein agar har call log ke sath pura address store karoge toh memory waste hogi aur address change hone par har row update karni padegi. Isko separate contact aur call tables mein divide karna Normalization hai.",
                "summary": "1NF = Atomic values, 2NF = Remove Partial Dependency, 3NF = Remove Transitive Dependency, BCNF = Determinant is Super Key."
            }
        },
        "mcqs": [
            {
                "id": "db_1",
                "topic": "ACID Properties",
                "question": "Which ACID property guarantees that committed transaction changes survive system crashes?",
                "options": ["A) Atomicity", "B) Consistency", "C) Isolation", "D) Durability"],
                "answer": "D",
                "explanation": "Durability guarantees that once a transaction commits, its updates are permanently recorded in non-volatile storage."
            },
            {
                "id": "db_2",
                "topic": "Normalization (1NF to BCNF)",
                "question": "A table is in 2NF if it is in 1NF and contains NO:",
                "options": ["A) Transitive Dependency", "B) Partial Functional Dependency", "C) Multi-valued Dependency", "D) Join Dependency"],
                "answer": "B",
                "explanation": "2NF requires eliminating partial dependencies on composite candidate keys."
            },
            {
                "id": "db_3",
                "topic": "Indexing & B-Trees",
                "question": "What is the primary data structure used by most relational databases for indexing table columns?",
                "options": ["A) Binary Search Tree", "B) B+ Tree", "C) Hash Table only", "D) Red-Black Tree"],
                "answer": "B",
                "explanation": "B+ Trees maintain balanced depth, optimize disk I/O, and allow efficient range scans because leaf nodes are linked."
            }
        ],
        "viva": [
            {
                "id": "db_v1",
                "topic": "Indexing & B-Trees",
                "question": "What is the difference between Clustered Index and Non-Clustered Index?",
                "answer": "Clustered Index physically reorders the actual rows on disk based on key (only 1 allowed per table). Non-Clustered Index is a separate pointer structure referencing row addresses (multiple allowed)."
            }
        ],
        "exam_questions": {
            "short": [
                {"question": "What is the difference between TRUNCATE and DELETE in SQL? (2 Marks)", "answer": "DELETE is a DML command that removes rows one by one, can have a WHERE clause, and generates undo logs (can be rolled back). TRUNCATE is a DDL command that deallocates table pages quickly, resets identity, and cannot have a WHERE clause."}
            ],
            "long": [
                {"question": "Explain Conflict Serializability and how Precedence Graphs (Serialization Graphs) are used to test it. (5 Marks)", "answer": "Two operations conflict if they belong to different transactions, access the same data item, and at least one is a Write. A schedule is Conflict Serializable if it is conflict equivalent to a serial schedule. We test this by building a Precedence Graph (Nodes = Transactions, Edge Ti -> Tj if an operation in Ti conflicts with and happens before Tj). If the graph contains NO cycles, the schedule is Conflict Serializable."}
            ]
        },
        "flashcards": [
            {"id": "fc_db1", "front": "ACID Acronym", "back": "Atomicity, Consistency, Isolation, Durability."},
            {"id": "fc_db2", "front": "3NF Definition", "back": "Must be in 2NF and contain no transitive functional dependencies (A -> B, B -> C)."},
            {"id": "fc_db3", "front": "CAP Theorem", "back": "Distributed systems can provide at most 2 of: Consistency, Availability, Partition Tolerance."}
        ]
    },

    "Data Structures & Algorithms": {
        "topics": ["Time & Space Complexity", "Arrays & Two Pointers", "Trees & BST", "Dynamic Programming", "Graphs & BFS/DFS"],
        "concepts": {
            "Time & Space Complexity": {
                "simple": "Asymptotic notation batata hai ki input size (N) grow hone par algorithm ka execution time aur memory usage kaise scale karta hai.",
                "step_by_step": [
                    "O(1) Constant: Hash table lookup, array index access.",
                    "O(log N) Logarithmic: Binary search on sorted array, balanced BST search.",
                    "O(N) Linear: Single loop traversal.",
                    "O(N log N) Linearithmic: Merge Sort, Quick Sort (average), Heap Sort.",
                    "O(N^2) Quadratic: Nested loops (Bubble sort, Selection sort).",
                    "O(2^N) Exponential: Recursive Fibonacci without memoization."
                ],
                "example": "Real-world analogy: Agar dictionary mein word khojna hai toh page-by-page dekhna O(N) hai, jabki beech se khol kar aadha ignore karna O(log N) Binary Search hai.",
                "summary": "O(1) < O(log N) < O(N) < O(N log N) < O(N^2) < O(2^N) < O(N!)."
            },
            "Dynamic Programming": {
                "simple": "Dynamic Programming complex problem ko smaller overlapping subproblems mein tod kar solve karta hai, aur unke solutions store (Memoize) kar leta hai taaki dobara compute na karna pade.",
                "step_by_step": [
                    "1. Overlapping Subproblems: Same subproblem baar baar calculate hota hai.",
                    "2. Optimal Substructure: Global optimal solution subproblems ke optimal solutions se banta hai.",
                    "Two Approaches:",
                    "  - Top-Down with Memoization: Recursion + Cache (dict/array).",
                    "  - Bottom-Up Tabulation: Iterative table filling from base cases."
                ],
                "example": "Real-world analogy: Agar 1+1+1+1=4 likha hai aur aage ek aur '+1' lagaya, toh aap dubara se 1+1... nahi jodte, aap '4+1=5' bolte ho kyunki pichla result yaad tha.",
                "summary": "DP = Recursion + Reusable Memory (Trading Space to save massive Time)."
            }
        },
        "mcqs": [
            {
                "id": "dsa_1",
                "topic": "Time & Space Complexity",
                "question": "What is the worst-case time complexity of Quick Sort?",
                "options": ["A) O(N log N)", "B) O(N)", "C) O(N^2)", "D) O(log N)"],
                "answer": "C",
                "explanation": "Quick Sort degrades to O(N^2) worst case when the chosen pivot is always the smallest or largest element (e.g., already sorted array without randomized pivot)."
            },
            {
                "id": "dsa_2",
                "topic": "Trees & BST",
                "question": "Which traversal of a Binary Search Tree (BST) produces sorted output in ascending order?",
                "options": ["A) Pre-order", "B) In-order", "C) Post-order", "D) Level-order"],
                "answer": "B",
                "explanation": "In-order traversal visits Left -> Root -> Right, which visits elements in ascending order in a BST."
            },
            {
                "id": "dsa_3",
                "topic": "Graphs & BFS/DFS",
                "question": "Which data structure is fundamentally used to implement Breadth-First Search (BFS)?",
                "options": ["A) Stack", "B) Priority Queue", "C) Queue", "D) Deque only"],
                "answer": "C",
                "explanation": "BFS explores nodes level by level using a FIFO Queue."
            }
        ],
        "viva": [
            {
                "id": "dsa_v1",
                "topic": "Graphs & BFS/DFS",
                "question": "What is the difference between BFS and DFS in graph traversal and space complexity?",
                "answer": "BFS traverses level-by-level using a Queue (O(V) memory for breadth). DFS traverses deep along paths using a Stack or recursion (O(H) memory proportional to depth). BFS guarantees the shortest path on unweighted graphs."
            }
        ],
        "exam_questions": {
            "short": [
                {"question": "Explain the 0/1 Knapsack Problem state transition recurrence (2 Marks).", "answer": "DP[i][w] = max(DP[i-1][w], value[i-1] + DP[i-1][w - weight[i-1]]) if weight[i-1] <= w, else DP[i-1][w]."}
            ],
            "long": [
                {"question": "Explain Dijkstra's Algorithm for Single Source Shortest Path with its time complexity. (5 Marks)", "answer": "Dijkstra maintains a distance array initialized to infinity (0 for source) and a Min-Heap. At each step, it extracts the unvisited node u with minimum distance, relaxes all its adjacent edges (if dist[u] + weight(u,v) < dist[v] then dist[v] = dist[u] + weight), and inserts updated distances into the Min-Heap until all reachable vertices are visited. Time complexity is O((V + E) log V) with a binary min-heap."}
            ]
        },
        "flashcards": [
            {"id": "fc_dsa1", "front": "Binary Search Time Complexity", "back": "O(log N) on sorted array. Search space is halved each iteration."},
            {"id": "fc_dsa2", "front": "In-order Traversal of BST", "back": "Left -> Root -> Right (Always produces strictly sorted ascending order)."},
            {"id": "fc_dsa3", "front": "Topological Sort", "back": "Linear ordering of vertices in Directed Acyclic Graph (DAG) where for edge u->v, u appears before v."}
        ]
    },

    "AI & Machine Learning": {
        "topics": ["Supervised vs Unsupervised", "Overfitting & Regularization", "Neural Networks & Backprop", "CNNs & Transformers", "Gradient Descent Optimization"],
        "concepts": {
            "Supervised vs Unsupervised": {
                "simple": "Supervised Learning mein model labeled dataset (input X + correct output Y) se train hota hai. Unsupervised Learning mein unlabeled data se hidden patterns/clusters khoje jaate hain.",
                "step_by_step": [
                    "Supervised: Classification (discrete labels, e.g., Spam vs Not Spam) & Regression (continuous values, e.g., House Price prediction).",
                    "Unsupervised: Clustering (K-Means, grouping customer segments) & Dimensionality Reduction (PCA).",
                    "Reinforcement Learning: Agent learns optimal actions via trial-and-error rewards and penalties in an environment."
                ],
                "example": "Real-world analogy: Supervised is like teacher checking student's test answers against answer key. Unsupervised is like giving a child mixed toys and watching them group by color on their own.",
                "summary": "Supervised = Labeled data (X -> Y). Unsupervised = Discovering patterns in raw X."
            },
            "Overfitting & Regularization": {
                "simple": "Overfitting tab hota hai jab model training data ko itna zyada rat leta hai (noise included) ki woh unseen test data par poor performance deta hai (High Variance). Regularization model complexity ko penalize karke generalization improve karti hai.",
                "step_by_step": [
                    "Overfitting Signs: High Training Accuracy, Low Validation/Test Accuracy.",
                    "Remedies:",
                    "  - L1 Regularization (Lasso): Adds absolute weights penalty (creates sparse weights/feature selection).",
                    "  - L2 Regularization (Ridge): Adds squared weights penalty (shrinks weights close to 0).",
                    "  - Dropout: Randomly disables neurons during training in Neural Networks.",
                    "  - Early Stopping & Data Augmentation."
                ],
                "example": "Real-world analogy: Ek student jo exam ke specific questions ke exact numbers rat leta hai par agar numbers thode badal diye jayein toh fail ho jata hai.",
                "summary": "Overfitting = High Variance. Regularization (L1/L2, Dropout) prevents overfitting and boosts generalization."
            }
        },
        "mcqs": [
            {
                "id": "aiml_1",
                "topic": "Overfitting & Regularization",
                "question": "Which regularization technique adds the sum of absolute values of coefficients to the loss function?",
                "options": ["A) L2 Ridge Regularization", "B) L1 Lasso Regularization", "C) Dropout", "D) Batch Normalization"],
                "answer": "B",
                "explanation": "L1 Lasso Regularization adds lambda * sum(|w|) and encourages sparse weight solutions."
            },
            {
                "id": "aiml_2",
                "topic": "Neural Networks & Backprop",
                "question": "What algorithm is used to compute gradients of the loss function with respect to weights using the chain rule?",
                "options": ["A) Forward Propagation", "B) Backpropagation", "C) K-Means", "D) Principal Component Analysis"],
                "answer": "B",
                "explanation": "Backpropagation applies the calculus chain rule backwards from output to input layers to compute partial derivatives."
            }
        ],
        "viva": [
            {
                "id": "aiml_v1",
                "topic": "Neural Networks & Backprop",
                "question": "What is the Vanishing Gradient problem and how do modern networks solve it?",
                "answer": "In deep networks with sigmoid/tanh activations, gradients become exponentially small as they propagate back through layers, stopping weights from updating. It is solved using ReLU activations, Residual Connections (ResNets), and Batch Normalization."
            }
        ],
        "exam_questions": {
            "short": [
                {"question": "Explain the Bias-Variance Tradeoff (2 Marks).", "answer": "Bias is error from erroneous assumptions in the learning algorithm (Underfitting). Variance is error from sensitivity to small fluctuations in training data (Overfitting). Optimal models minimize total error by finding the balanced sweet spot between bias and variance."}
            ],
            "long": [
                {"question": "Explain the Self-Attention mechanism in Transformer architectures. (5 Marks)", "answer": "Self-Attention allows input tokens to dynamically weigh relevance against all other tokens in a sequence. Inputs are projected into Query (Q), Key (K), and Value (V) matrices. The attention score is computed as: Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V. Multi-Head Attention runs multiple projections in parallel to capture different semantic relationships."}
            ]
        },
        "flashcards": [
            {"id": "fc_ai1", "front": "Precision vs Recall", "back": "Precision = TP / (TP + FP) [Accuracy of positive calls]. Recall = TP / (TP + FN) [Coverage of actual positives]."},
            {"id": "fc_ai2", "front": "ReLU Activation Function", "back": "f(x) = max(0, x). Fast computation, avoids vanishing gradient for positive values."},
            {"id": "fc_ai3", "front": "Confusion Matrix", "back": "Contains True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN)."}
        ]
    }
}

# -------------------------------------------------------------
# Core Study Mode Handlers & Exposed APIs
# -------------------------------------------------------------

@eel.expose
def startStudyMode(subject=None):
    """Activates Study Mode state and returns initial overview."""
    global STUDY_MODE_ACTIVE, ACTIVE_STUDY_SUBJECT
    STUDY_MODE_ACTIVE = True
    if subject and subject in STUDY_CURRICULUM:
        ACTIVE_STUDY_SUBJECT = subject
    
    init_study_tables()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO study_sessions (subject, mode) VALUES (?, 'Active')", (ACTIVE_STUDY_SUBJECT,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging study session: {e}")

    print(f"[Study Mode] Activated for: {ACTIVE_STUDY_SUBJECT}")
    return {
        "status": "active",
        "subject": ACTIVE_STUDY_SUBJECT,
        "message": f"AI Study Mode is now active for {ACTIVE_STUDY_SUBJECT}."
    }


@eel.expose
def stopStudyMode():
    """Deactivates Study Mode."""
    global STUDY_MODE_ACTIVE
    STUDY_MODE_ACTIVE = False
    print("[Study Mode] Deactivated.")
    return {
        "status": "inactive",
        "message": "AI Study Mode deactivated. Great session!"
    }


@eel.expose
def isStudyModeActive():
    return STUDY_MODE_ACTIVE


@eel.expose
def getStudySubjects():
    return list(STUDY_CURRICULUM.keys())


@eel.expose
def setStudySubject(subject):
    global ACTIVE_STUDY_SUBJECT
    if subject in STUDY_CURRICULUM:
        ACTIVE_STUDY_SUBJECT = subject
        return {"status": "success", "subject": ACTIVE_STUDY_SUBJECT}
    return {"status": "error", "message": "Subject not found"}


@eel.expose
def explainConcept(topic_query=None, subject=None, format_type="simple", is_hinglish=True):
    """
    Returns structured explanation for a topic:
    format_type can be: 'simple', 'step_by_step', 'example', or 'all'.
    """
    subj = subject or ACTIVE_STUDY_SUBJECT
    if subj not in STUDY_CURRICULUM:
        subj = "Computer Networks"

    curr_data = STUDY_CURRICULUM[subj]
    concepts = curr_data.get("concepts", {})

    # Match topic
    matched_topic = None
    if topic_query:
        query_lower = topic_query.lower()
        for t_name in concepts.keys():
            if t_name.lower() in query_lower or any(word in query_lower for word in t_name.lower().split()):
                matched_topic = t_name
                break

    if not matched_topic:
        matched_topic = list(concepts.keys())[0]

    concept = concepts[matched_topic]

    return {
        "status": "success",
        "subject": subj,
        "topic": matched_topic,
        "simple": concept.get("simple", ""),
        "step_by_step": concept.get("step_by_step", []),
        "example": concept.get("example", ""),
        "summary": concept.get("summary", "")
    }


@eel.expose
def getStudyMCQs(subject=None, topic=None, count=10):
    """Fetches high-yield MCQs for the specified subject/topic."""
    subj = subject or ACTIVE_STUDY_SUBJECT
    if subj not in STUDY_CURRICULUM:
        subj = "Computer Networks"

    all_mcqs = STUDY_CURRICULUM[subj].get("mcqs", [])
    if topic:
        filtered = [m for m in all_mcqs if topic.lower() in m.get("topic", "").lower()]
        if filtered:
            all_mcqs = filtered

    res = all_mcqs[:count]
    return {
        "status": "success",
        "subject": subj,
        "total": len(res),
        "mcqs": res
    }


@eel.expose
def getVivaQuestions(subject=None, count=5):
    """Returns viva / oral interview questions."""
    subj = subject or ACTIVE_STUDY_SUBJECT
    if subj not in STUDY_CURRICULUM:
        subj = "Computer Networks"

    viva_list = STUDY_CURRICULUM[subj].get("viva", [])
    return {
        "status": "success",
        "subject": subj,
        "questions": viva_list[:count]
    }


@eel.expose
def getExamQuestions(subject=None):
    """Returns short and long exam questions."""
    subj = subject or ACTIVE_STUDY_SUBJECT
    if subj not in STUDY_CURRICULUM:
        subj = "Computer Networks"

    exam_dict = STUDY_CURRICULUM[subj].get("exam_questions", {"short": [], "long": []})
    return {
        "status": "success",
        "subject": subj,
        "short_questions": exam_dict.get("short", []),
        "long_questions": exam_dict.get("long", [])
    }


@eel.expose
def getStudyFlashcards(subject=None):
    """Returns interactive flashcard deck."""
    subj = subject or ACTIVE_STUDY_SUBJECT
    if subj not in STUDY_CURRICULUM:
        subj = "Computer Networks"

    cards = STUDY_CURRICULUM[subj].get("flashcards", [])
    return {
        "status": "success",
        "subject": subj,
        "flashcards": cards
    }


@eel.expose
def recordQuizResult(subject, topic, score, total, incorrect_topics=None):
    """
    Logs quiz performance into SQLite and auto-detects weak topics.
    """
    if not subject:
        subject = ACTIVE_STUDY_SUBJECT
    if not topic:
        topic = "General Quiz"

    try:
        score = int(score)
        total = max(1, int(total))
        pct = int((score / total) * 100)
    except Exception:
        score, total, pct = 0, 1, 0

    if incorrect_topics is None:
        incorrect_topics = []

    init_study_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Log quiz history
    c.execute("""
        INSERT INTO quiz_history (subject, topic, score, total, pct, incorrect_topics)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (subject, topic, score, total, pct, json.dumps(incorrect_topics)))

    # Update weak topics table
    for inc_t in incorrect_topics:
        c.execute("""
            INSERT INTO weak_topics (subject, topic, error_count, last_tested, status)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP, 'Needs Revision')
            ON CONFLICT(subject, topic) DO UPDATE SET
                error_count = error_count + 1,
                last_tested = CURRENT_TIMESTAMP,
                status = 'Needs Revision'
        """, (subject, inc_t))

    # If score >= 80%, remove or mark mastered
    if pct >= 80:
        c.execute("""
            UPDATE weak_topics
            SET status = 'Mastered'
            WHERE subject = ? AND topic = ?
        """, (subject, topic))

    conn.commit()
    conn.close()

    print(f"[Study Analytics] Quiz recorded: {subject} - {score}/{total} ({pct}%). Weak topics logged: {len(incorrect_topics)}")
    return {
        "status": "success",
        "score": score,
        "total": total,
        "pct": pct,
        "weak_logged": len(incorrect_topics)
    }


@eel.expose
def getWeakTopics():
    """Fetches all topics flagged for revision."""
    init_study_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, subject, topic, error_count, last_tested, status
        FROM weak_topics
        WHERE status != 'Mastered'
        ORDER BY error_count DESC, last_tested DESC
    """)
    rows = c.fetchall()
    conn.close()

    weak_list = []
    for r in rows:
        weak_list.append({
            "id": r[0],
            "subject": r[1],
            "topic": r[2],
            "error_count": r[3],
            "last_tested": r[4],
            "status": r[5]
        })
    return weak_list


@eel.expose
def getStudyStats():
    """Calculates overall study metrics."""
    init_study_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Total quizzes
    c.execute("SELECT COUNT(*), AVG(pct) FROM quiz_history")
    quiz_count, avg_score = c.fetchone()

    # Weak topics count
    c.execute("SELECT COUNT(*) FROM weak_topics WHERE status != 'Mastered'")
    weak_count = c.fetchone()[0]

    # Sessions count
    c.execute("SELECT COUNT(*) FROM study_sessions")
    session_count = c.fetchone()[0]

    conn.close()

    return {
        "is_active": STUDY_MODE_ACTIVE,
        "active_subject": ACTIVE_STUDY_SUBJECT,
        "quiz_count": quiz_count or 0,
        "avg_score": int(avg_score or 0),
        "weak_count": weak_count or 0,
        "session_count": session_count or 0
    }


# -------------------------------------------------------------
# Spoken Voice Responses in Hinglish / Natural Tone
# -------------------------------------------------------------

def start_study_mode_voice(query=""):
    """Voice handler for 'Start study mode'."""
    subject = "Computer Networks"
    for s in STUDY_CURRICULUM.keys():
        if s.lower() in query.lower():
            subject = s
            break

    startStudyMode(subject)
    try:
        eel.openStudyModeModal()
    except Exception:
        pass

    return f"AI Study Mode start kar diya hai {subject} ke liye. Main simple explanations, MCQs aur viva practice ke liye taiyar hoon!"


def explain_simple_voice(query):
    """Voice handler for 'Explain this simply'."""
    cleaned = re.sub(r'^(explain|explain this|simple bhasha mein|simply|samjhao|what is|tell me about)\s+', '', query, flags=re.IGNORECASE).strip(' ?.')
    
    data = explainConcept(topic_query=cleaned if len(cleaned) > 2 else None)
    topic = data["topic"]
    simple_exp = data["simple"]
    example = data["example"]

    return f"{topic} ka simple explanation: {simple_exp} {example}"


def get_mcqs_voice(query):
    """Voice handler for 'Give me 10 MCQs' or 'Test me on networking'."""
    subject = None
    for s in STUDY_CURRICULUM.keys():
        if any(w in query.lower() for w in s.lower().split()):
            subject = s
            break

    data = getStudyMCQs(subject=subject, count=5)
    mcqs = data["mcqs"]
    if not mcqs:
        return "MCQ practice ke liye dashboard open kar diya hai."

    try:
        eel.openStudyQuizTab()
    except Exception:
        pass

    first_q = mcqs[0]
    opts = ", ".join(first_q["options"][:2])
    return f"Maine {data['subject']} ke practice MCQs load kar diye hain. Pehla sawal: {first_q['question']} Options: {opts} wagairah."


def get_viva_voice(query):
    """Voice handler for 'Take my viva'."""
    data = getVivaQuestions()
    qs = data.get("questions", [])
    if not qs:
        return "Viva practice session start kar diya hai dashboard par."

    try:
        eel.openStudyVivaTab()
    except Exception:
        pass

    first_viva = qs[0]
    return f"Viva Question: {first_viva['question']} Sochiye aur answer bataiye, phir main model answer explain karunga."


def get_weak_topics_voice():
    """Voice handler for 'Show my weak topics'."""
    weak = getWeakTopics()
    if not weak:
        return "Shabash Samendra! Abhi aapke paas koi flagged weak topics nahi hain. Aapne previous quizzes mein accha score kiya hai."

    topics = [f"{w['topic']} ({w['subject']})" for w in weak[:3]]
    return f"Aapke top weak topics hain: " + ", aur ".join(topics) + ". In par practice karne ke liye 'Revise today's topics' bol sakte hain."


def get_revision_voice():
    """Voice handler for 'Revise today's topics'."""
    weak = getWeakTopics()
    if weak:
        top_weak = weak[0]
        data = explainConcept(topic_query=top_weak["topic"], subject=top_weak["subject"])
        try:
            eel.openStudyConceptTab()
        except Exception:
            pass
        return f"Aapke weak topic '{top_weak['topic']}' ki quick revision: {data['simple']}"
    
    data = explainConcept()
    return f"Aaj ke active subject {ACTIVE_STUDY_SUBJECT} ki quick revision: {data['simple']}"
