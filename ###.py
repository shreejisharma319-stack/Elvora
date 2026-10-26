import streamlit as st
from openai import OpenAI
import random
import time

# 1. Page Configuration
st.set_page_config(page_title="Smart Study Assistant", layout="wide", page_icon="🎓")

# ==========================================
# 🎨 DYNAMIC THEME SYSTEM & STYLING
# ==========================================

# 1. Initialize Theme Session State
if 'selected_theme' not in st.session_state:
    st.session_state.selected_theme = "Playful Tech Blue"

# 2. Theme Color Definitions
if st.session_state.selected_theme == "Luxury Burgundy":
    bg_color = "#1A0307"
    text_color = "#F4E3D7"
    card_bg = "linear-gradient(135deg, #3B0D16, #24050C)"
    btn_bg = "#6E1B2A"
    card_border = "#4A121E"
else:  # Playful Tech Blue (Default)
    bg_color = "#EBF4FF"
    text_color = "#1E293B"
    card_bg = "linear-gradient(135deg, #60A5FA, #3B82F6)"
    btn_bg = "#2563EB"
    card_border = "#93C5FD"

# 3. Custom CSS Injection
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: {btn_bg};
        color: white;
        border: none;
        font-weight: bold;
    }}
    .welcome-card {{
        background: {card_bg};
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid {card_border};
    }}
    .user-msg {{
        background-color: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border-left: 5px solid {btn_bg};
        color: {text_color};
    }}
    .bot-msg {{
        background-color: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid {card_border};
        margin-bottom: 20px;
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

# 4. Sidebar Theme Picker
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 App Theme Vibe")
theme_choice = st.sidebar.radio(
    "Select Aesthetic",
    ["Playful Tech Blue", "Luxury Burgundy"],
    index=0 if st.session_state.selected_theme == "Playful Tech Blue" else 1
)

if theme_choice != st.session_state.selected_theme:
    st.session_state.selected_theme = theme_choice
    st.rerun()

# --- 2. SAFE API KEY PLACEHOLDER ---
USER_API_KEY = st.secrets.get("USER_API_KEY", "sk-proj-PASTE_YOUR_ACTUAL_KEY_HERE")
# 3. Permanent Memory Setup
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'quiz_raw' not in st.session_state: st.session_state.quiz_raw = None
if 'flash_raw' not in st.session_state: st.session_state.flash_raw = None
if 'paper_raw' not in st.session_state: st.session_state.paper_raw = None
if 'timetable_raw' not in st.session_state: st.session_state.timetable_raw = None
if 'score_submitted' not in st.session_state: st.session_state.score_submitted = False

# --- SUB-TOPIC BANK FOR DYNAMIC RANDOMIZATION ---
TOPIC_BANK = {
    "Science": ["Chemical Reactions", "Life Processes", "Light Reflection & Refraction", "Electricity", "Magnetic Effects", "Our Environment", "Carbon Compounds", "Acid, Bases & Salts"],
    "Mathematics": ["Real Numbers", "Polynomials", "Linear Equations", "Quadratic Equations", "Arithmetic Progressions", "Triangles", "Coordinate Geometry", "Trigonometry", "Probability"],
    "English": ["Reading Comprehension", "Tenses", "Modals", "Reported Speech", "Subject-Verb Concord", "Analytical Paragraphs", "Formal Letter Writing", "Literature Masterworks"],
    "Social Studies": ["The Rise of Nationalism in Europe", "Nationalism in India", "Resources and Development", "Agriculture", "Power Sharing", "Federalism", "Development", "Sectors of the Indian Economy"],
    "PCM": ["Kinematics & Mechanics", "Organic Chemistry Mechanisms", "Calculus & Limits", "Thermodynamics", "Electrostatics", "Chemical Bonding", "Matrices & Determinants", "Wave Optics"],
    "PCB": ["Human Physiology", "Genetics & Evolution", "Plant Reproduction", "Cell Biology", "Ecology & Ecosystems", "Biomolecules", "Microbes in Human Welfare", "Structural Organization"],
    "Commerce": ["Accountancy Principles", "Macroeconomics Concepts", "Business Environment", "Marketing Management", "Financial Markets", "Consumer Protection", "National Income", "Banking Systems"],
    "Humanities": ["Modern World History", "Political Theory", "Human Geography", "Social Structures", "International Relations", "Indian Constitution", "Macro Sociology", "Cultural Studies"],
    "Artificial Intelligence": ["Machine Learning Models", "Neural Networks & Deep Learning", "Natural Language Processing", "Computer Vision Principles", "AI Ethics & Bias", "Data Preprocessing Techniques", "Reinforcement Learning"],
    "Engineering": ["Thermodynamics & Fluid Mechanics", "Data Structures & Algorithms", "Circuit Analysis & Electronics", "Material Science", "Object-Oriented Programming", "Digital Logic Design", "Control Systems"],
    "Medicine": ["Human Anatomy & Histology", "Pharmacology & Drug Mechanics", "Pathology of Diseases", "Clinical Immunology", "Microbiology & Infectious Diseases", "Cardiovascular Systems", "Neurology"],
    "Law": ["Constitutional Law Foundations", "Criminal Jurisprudence", "Contract Law & Tort", "International Humanitarian Law", "Corporate Governance & Regulations", "Intellectual Property Rights", "Legal Ethics"],
    "Business": ["Strategic Corporate Management", "Financial Planning & Analysis", "Consumer Behavior & Marketing", "Supply Chain Logistics", "Human Resource Optimization", "Entrepreneurial Venture Design", "Micro-Economics"],
    "Fashion": ["Textile Science & Materials", "History of Global Costume", "Fashion Merchandising & Retail", "Garment Construction & Draping", "Apparel Design Aesthetics", "Sustainable Fashion Eco-systems", "Trend Forecasting"]
}

# Helper to generate unique subtopics and seed tags
def get_random_prompt_args(subject):
    topic = random.choice(TOPIC_BANK.get(subject, ["General Curriculum"]))
    unique_seed = str(time.time()) + "_" + str(random.randint(1000, 9999))
    return topic, unique_seed

# --- QUOTE INITIALIZATION ---
if 'current_quote' not in st.session_state:
    quotes = [
        "“The beautiful thing about learning is that no one can take it away from you.” — B.B. King",
        "“The expert in anything was once a beginner.” — Helen Hayes",
        "“Success is the sum of small efforts, repeated day in and day out.” — Robert Collier"
    ]
    st.session_state.current_quote = random.choice(quotes)

try:
    client = OpenAI(api_key=USER_API_KEY)

    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.title("⚙️ Study Settings")
        level = st.selectbox("Level", ["School (Grade 1-10)", "High School", "University"])
       
        if level == "School (Grade 1-10)":
            g_num = st.slider("Grade", 1, 10, 1)
            display_level = f"Grade {g_num}"
            sub_choice = st.selectbox("Subject", ["Science", "Mathematics", "English", "Social Studies"])
        elif level == "High School":
            sub_choice = st.selectbox("Stream", ["PCM", "PCB", "Commerce", "Humanities"])
            display_level = "High School"
        else:
            sub_choice = st.selectbox("Major", ["Artificial Intelligence", "Engineering", "Medicine", "Law", "Business", "Fashion"])
            display_level = "University"

        st.divider()
        mode = st.radio("Activity:", [
            "💬 Smart Tutor", 
            "🧠 Interactive Quiz", 
            "🗂️ Flashcards", 
            "📝 Practice Paper",
            "📅 Study Timetable"
        ])
        st.divider()
        st.success("🔥 5 Day Study Streak!")

    # --- ✨ WELCOME CARD HERO ---
    st.markdown(f"""
        <div class="welcome-card">
            <h1>Welcome Back, Scholar! 🎓</h1>
            <p style='font-size: 1.2em; font-style: italic; opacity: 0.9;'>{st.session_state.current_quote}</p>
        </div>
        """, unsafe_allow_html=True)

    st.header(f"📍 {display_level} | {sub_choice}")

    # 1. FLASHCARDS MODULE
    if mode == "🗂️ Flashcards":
        if st.button("✨ Generate Flashcards"):
            topic, seed = get_random_prompt_args(sub_choice)
            with st.spinner("AI is crafting fresh cards..."):
                res = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role":"user","content":f"Create 5 brand new flashcards for {display_level} {sub_choice} focusing on topic '{topic}'. [Unique ID: {seed}]. Strictly use format 'Question | Answer' on each line."}],
                    temperature=0.95
                )
                st.session_state.flash_raw = res.choices[0].message.content
       
        if st.session_state.flash_raw:
            lines = [line.strip() for line in st.session_state.flash_raw.split('\n') if "|" in line]
            for i, card in enumerate(lines):
                parts = card.split("|")
                if len(parts) >= 2:
                    q_text = parts[0].strip()
                    a_text = parts[1].strip()
                    with st.expander(f"🎴 Card {i+1}: {q_text}"):
                        st.info(f"**Answer:** {a_text}")

    # 2. INTERACTIVE QUIZ MODULE
    elif mode == "🧠 Interactive Quiz":
        if st.button("✨ Generate New Quiz"):
            st.session_state.score_submitted = False
            topic, seed = get_random_prompt_args(sub_choice)
            with st.spinner("Generating fresh quiz..."):
                p_quiz = f"""Create 3 completely new Multiple Choice Questions for {display_level} {sub_choice} on the sub-topic '{topic}'. [Request ID: {seed}].
Ensure these questions are unique and varied.
Strictly use this format:
Q: [Question Text]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Correct: [Letter]"""
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role":"user","content":p_quiz}],
                    temperature=0.95
                )
                st.session_state.quiz_raw = res.choices[0].message.content

        if st.session_state.quiz_raw:
            raw_blocks = st.session_state.quiz_raw.split("Q:")
            valid_questions = [block.strip() for block in raw_blocks if "Correct:" in block]

            for i, q_data in enumerate(valid_questions):
                lines = [l.strip() for l in q_data.split('\n') if l.strip()]
                if len(lines) >= 5:
                    st.markdown(f"### Question {i+1}")
                    st.write(lines[0])
                    opts = [l for l in lines if l.startswith(('A)', 'B)', 'C)', 'D)'))]
                    
                    ans_letter = "A"
                    for l in lines:
                        if "Correct:" in l:
                            ans_letter = l.split(":")[-1].strip()

                    user_ans = st.radio(f"Select answer for Q{i+1}:", opts, key=f"q_radio_{i}_{time.time()}")

                    if st.session_state.score_submitted:
                        if user_ans.startswith(ans_letter):
                            st.success(f"✅ Correct! Answer: {ans_letter}")
                        else:
                            st.error(f"❌ Incorrect. Correct Answer: {ans_letter}")
           
            if valid_questions and not st.session_state.score_submitted:
                if st.button("📊 Submit Results"):
                    st.session_state.score_submitted = True
                    st.balloons()
                    st.rerun()

    # 3. PRACTICE PAPER MODULE
    elif mode == "📝 Practice Paper":
        if st.button("📄 Practise Paper"):
            topic, seed = get_random_prompt_args(sub_choice)
            cbse_prompt = f"""Generate a brand new final term exam paper for {display_level} {sub_choice} based on CBSE Board pattern. Focus heavily on the topic unit: '{topic}'. [Unique Seed: {seed}].
Include:
Section A (5 unique MCQs - 1 mark each)
Section B (3 Short Answer Questions - 3 marks each)
Section C (2 Long Answer Questions - 5 marks each)
Add instructions at top and 'End of Paper' at bottom."""
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[{"role":"user","content":cbse_prompt}], 
                stream=True,
                temperature=0.90
            )
            st.session_state.paper_raw = st.write_stream(stream)
            st.rerun()
       
        if st.session_state.paper_raw:
            st.markdown("### 📝 CBSE Mock Examination")
            st.text_area("Final Term Paper", st.session_state.paper_raw, height=450)
            st.download_button("📥 Download Paper (TXT)", st.session_state.paper_raw, file_name=f"Practise_{sub_choice}_Paper.txt")

    # 4. SMART TUTOR MODULE
elif mode == "💬 Smart Tutor":
    st.subheader("💬 Ask Your Tutor")
    uploaded_image = st.file_uploader("📷 Upload an image of a problem, diagram, or textbook question (optional)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Problem Image", use_container_width=True)
        uploaded_image.seek(0)

    p = st.chat_input("Ask a question or explain the uploaded image...")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="user-msg"><b>🙋 You:</b> {chat["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-msg"><b>🤖 Tutor:</b><br>{chat["answer"]}</div>', unsafe_allow_html=True)
        
    if p or uploaded_image:
        display_text = p if p else "[Uploaded Image with no text]"
        
        if uploaded_image:
            base64_img = encode_image(uploaded_image)
            user_content = [
                {"type": "text", "text": p if p else "Please solve or explain this image for me in detail."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                }
            ]
        else:
            user_content = p

        with st.spinner("AI Tutor is analyzing..."):
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_content}],
                stream=True
            )
            ai_response = st.write_stream(stream)
            
        st.session_state.chat_history.append({"question": display_text, "answer": ai_response})
        st.rerun()

    # 5. STUDY TIMETABLE MODULE
    elif mode == "📅 Study Timetable":
        if st.button("📅 Generate Study Schedule"):
            topic, seed = get_random_prompt_args(sub_choice)
            timetable_prompt = f"""Create a unique weekly study timetable for a {display_level} student preparing for {sub_choice}, with extra focus on '{topic}'. [ID: {seed}].
Make it structured day-by-day (Monday to Sunday) with time blocks, strategies, and review goals in clean markdown tables."""
            
            stream = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":timetable_prompt}], stream=True, temperature=0.90)
            st.session_state.timetable_raw = st.write_stream(stream)
            st.rerun()
                
        if st.session_state.timetable_raw:
            st.markdown("### 📅 Weekly Prep Schedule")
            st.markdown(st.session_state.timetable_raw)
            st.download_button("📥 Download Timetable (TXT)", st.session_state.timetable_raw, file_name=f"{sub_choice}_Preparation_Plan.txt")

except Exception as e:
    st.error(f"⚠️ Connection Error: {e}") 
