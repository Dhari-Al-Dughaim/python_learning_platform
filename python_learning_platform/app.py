import streamlit as st
import io
import contextlib
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openai
from PIL import Image

# إعداد مفتاح OpenAI مباشرة (غير آمن للنشر العام)
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# تهيئة الجلسة
if "progress" not in st.session_state:
    st.session_state.progress = [False] * 10
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = [None] * 10
if "lesson_page" not in st.session_state:
    st.session_state.lesson_page = 0
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful Python tutor. Only answer Python programming questions in a simple, clear way. If a question is not about Python, politely ask the student to ask about Python programming only."}
    ]


# --- بيانات الدروس مع روابط فيديو فقط ---
lessons = [
    {
        "title": "Lesson 1: Printing in Python",
        "desc": "Learn how to print messages to the screen using the print() function.",
        "video": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
        "example": 'print("Hello, world!")',
        "quiz": [
            {"question": "What does the following code print?\n\nprint('Python')",
             "options": ["Python", "'Python'", "print('Python')", "Error"],
             "answer": "Python"}
        ]
    },
    {
        "title": "Lesson 2: Variables",
        "desc": "Understand variables and how to store values in Python.",
        "video": "https://www.youtube.com/watch?v=CqvZ3vGoGs0",
        "example": 'name = "Dhari"\nage = 23\nprint(name)\nprint(age)',
        "quiz": [
            {"question": "Which of the following is a valid variable name in Python?",
             "options": ["2value", "user_name", "user-name", "user name"],
             "answer": "user_name"}
        ]
    },
    {
        "title": "Lesson 3: Data Types",
        "desc": "Explore Python's main data types: int, float, str, bool.",
        "video": "https://www.youtube.com/watch?v=khKv-8q7YmY",
        "example": 'a = 10\nb = 2.5\nc = "Hello"\nd = True\nprint(type(a), type(b), type(c), type(d))',
        "quiz": [
            {"question": "What type is the value `3.14` in Python?",
             "options": ["int", "float", "str", "bool"],
             "answer": "float"}
        ]
    },
    {
        "title": "Lesson 4: User Input",
        "desc": "Read input from the user using the input() function.",
        "video": "https://www.youtube.com/watch?v=cOjPI2V9V4c",
        "example": '# input only works in terminal, try assigning a value\nguest = "Alice"\nprint("Welcome", guest)',
        "quiz": [
            {"question": "Which function is used to get user input in Python?",
             "options": ["scan()", "input()", "read()", "get()"],
             "answer": "input()"}
        ]
    },
    {
        "title": "Lesson 5: Conditions (if/else)",
        "desc": "Use if, elif, and else to make decisions in your code.",
        "video": "https://www.youtube.com/watch?v=f4KOjWS_KZs",
        "example": 'x = 7\nif x > 5:\n    print("x is greater than 5")\nelse:\n    print("x is 5 or less")',
        "quiz": [
            {"question": "What is printed if x = 3 in the following code?\n\nx = 3\nif x > 5:\n    print('A')\nelse:\n    print('B')",
             "options": ["A", "B", "Error", "Nothing"],
             "answer": "B"}
        ]
    },
    {
        "title": "Lesson 6: Loops",
        "desc": "Repeat actions using for and while loops.",
        "video": "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ",
        "example": 'for i in range(5):\n    print("Number:", i)',
        "quiz": [
            {"question": "How many times will this print?\n\nfor i in range(3):\n    print(i)",
             "options": ["1", "2", "3", "4"],
             "answer": "3"}
        ]
    },
    {
        "title": "Lesson 7: Lists",
        "desc": "Store and process multiple values using lists.",
        "video": "https://www.youtube.com/watch?v=W8KRzm-HUcc",
        "example": 'my_list = [1, 2, 3, 4]\nfor item in my_list:\n    print(item)',
        "quiz": [
            {"question": "What is the correct way to access the first item in a list called data?",
             "options": ["data(0)", "data[0]", "data[1]", "data.first()"],
             "answer": "data[0]"}
        ]
    },
    {
        "title": "Lesson 8: Functions",
        "desc": "Define and use functions to organize your code.",
        "video": "https://www.youtube.com/watch?v=9Os0o3wzS_I",
        "example": 'def greet(name):\n    print("Hello", name)\ngreet("Dhari")',
        "quiz": [
            {"question": "Which keyword is used to define a function in Python?",
             "options": ["def", "function", "func", "define"],
             "answer": "def"}
        ]
    },
    {
        "title": "Lesson 9: Dictionaries",
        "desc": "Use dictionaries to store key-value pairs.",
        "video": "https://www.youtube.com/watch?v=daefaLgNkw0",
        "example": 'person = {"name": "Dhari", "age": 23}\nprint(person["name"], person["age"])',
        "quiz": [
            {"question": "What will be output for:\nperson = {'name':'Ali', 'age':20}\nprint(person['name'])",
             "options": ["Ali", "20", "name", "Error"],
             "answer": "Ali"}
        ]
    },
    {
        "title": "Lesson 10: Exceptions",
        "desc": "Handle errors in your code using try and except.",
        "video": "https://www.youtube.com/watch?v=bKPIcoou9N8",
        "example": 'try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print("Cannot divide by zero!")',
        "quiz": [
            {"question": "Which block catches errors in Python?",
             "options": ["try", "except", "catch", "error"],
             "answer": "except"}
        ]
    },
]

# Dashboard
num_completed = sum(st.session_state.progress)
total_lessons = len(lessons)
quiz_scores = [score if score is not None else 0 for score in st.session_state.quiz_scores]
total_quiz_score = sum(quiz_scores)
max_possible_score = sum([len(l["quiz"]) for l in lessons])
progress_ratio = num_completed / total_lessons if total_lessons > 0 else 0
if progress_ratio == 1:
    msg = "🏅 Excellent! You completed all lessons."
elif progress_ratio > 0.5:
    msg = "👏 Keep going, you're more than halfway done!"
elif progress_ratio > 0:
    msg = "🚀 Good start! Keep learning."
else:
    msg = "Start your Python journey now!"

col1, col2, col3 = st.columns(3)
col1.metric("Lessons Completed", f"{num_completed} / {total_lessons}")
col2.metric("Quiz Score", f"{total_quiz_score} / {max_possible_score}")
col3.metric("Progress", f"{int(progress_ratio*100)}%")
st.progress(progress_ratio)
st.info(msg)
st.markdown('<hr style="border:1.5px solid #1583e9; border-radius:6px;">', unsafe_allow_html=True)

# عرض الدروس (بدون أي embed)
page_size = 4
page_count = (len(lessons) + page_size - 1) // page_size
page = st.session_state.lesson_page

for idx in range(page * page_size, min((page + 1) * page_size, len(lessons))):
    lesson = lessons[idx]
    completed = st.session_state.progress[idx]
    score = st.session_state.quiz_scores[idx]
    st.markdown(f"### {lesson['title']}{' ✅' if completed else ''}")
    st.write(lesson['desc'])
    st.markdown(f"**[🎥 Watch the lesson video here]({lesson['video']})**")
    st.markdown("**Try it yourself:**")
    user_code = st.text_area("", lesson["example"], height=85, key=f"code_{idx}")
    run_code = st.button("Run Code", key=f"btn_{idx}")
    if run_code:
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(user_code)
            st.success("Output:")
            st.code(output.getvalue())
        except Exception as e:
            st.error(f"Error: {e}")
    st.markdown("**Quiz:**")
    correct = 0
    total = len(lesson["quiz"])
    user_answers = []
    for qidx, q in enumerate(lesson["quiz"]):
        user_choice = st.radio(q["question"], q["options"], key=f"quiz_{idx}_{qidx}")
        user_answers.append(user_choice)
    check_quiz = st.button("Check Quiz", key=f"quizbtn_{idx}")
    if check_quiz:
        for qidx, q in enumerate(lesson["quiz"]):
            if user_answers[qidx] == q["answer"]:
                correct += 1
        st.session_state.quiz_scores[idx] = correct
        if correct == total:
            st.success(f"Perfect! {correct}/{total} correct 🎉")
            st.session_state.progress[idx] = True
            st.rerun()
        else:
            st.warning(f"{correct}/{total} correct. Try again!")
    if score is not None and score == total:
        st.success("Lesson completed ✅")
    st.markdown("---")

# Pagination (Next/Previous)
col_prev, col_empty, col_next = st.columns([1,8,1])
with col_prev:
    if page > 0:
        if st.button("⬅️ Previous"):
            st.session_state.lesson_page -= 1
            st.rerun()
with col_next:
    if page < page_count - 1:
        if st.button("Next ➡️"):
            st.session_state.lesson_page += 1
            st.rerun()

# شهادة PDF عند الإنجاز
def create_certificate(username):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(300, 700, "Certificate of Completion")
    c.setFont("Helvetica", 18)
    c.drawCentredString(300, 650, f"Presented to: {username}")
    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 600, f"For completing the Python course.")
    c.drawCentredString(300, 560, f"Date: {date.today().isoformat()}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(300, 510, "Congratulations!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

if sum(st.session_state.progress) == len(lessons):
    st.markdown('<div style="background:#f0f7ff; border-radius:10px; padding:1.2rem 1rem; box-shadow: 0 1px 8px 0 rgba(21,131,233,0.11); margin: 1.2rem 0 1rem 0;">', unsafe_allow_html=True)
    st.success("🎉 You completed all lessons! Download your certificate:")
    username = st.text_input("Enter your name for the certificate:", value="Your Name")
    if st.button("Download Certificate (PDF)", key="download_cert"):
        cert = create_certificate(username)
        st.download_button("Download PDF", cert, file_name=f"{username}_certificate.pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# زر المساعد الذكي
st.markdown("----")
if st.button("🤖 Open AI Python Assistant", key="open_ai_assistant"):
    st.session_state.chat_open = True

def render_chat_widget():
    st.markdown("---")
    st.markdown("### 🤖 AI Python Assistant")
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(
                f"<div style='background:#f3f6fd;border-radius:7px;padding:0.7rem 1rem;margin-bottom:0.8rem;color:#2b3556;'><b>Assistant:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )
    user_input = st.text_input("Ask me about Python:", key="chat_input")
    if st.button("Send", key="chat_send"):
        if user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=st.session_state.chat_history,
                        temperature=0.1,
                        max_tokens=512,
                    )
                    answer = response.choices[0].message["content"]
                except Exception as e:
                    answer = f"Error: {e}"
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
    if st.button("Close Chat", key="chat_close"):
        st.session_state.chat_open = False

if st.session_state.chat_open:
    render_chat_widget()
