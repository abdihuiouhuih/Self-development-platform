import os, base64, random, time
import streamlit as st

st.set_page_config(page_title="منصة التطوير الذاتي الشاملة", page_icon="🚀",
                   layout="wide", initial_sidebar_state="collapsed")

# ===================== إعدادات =====================
MODEL = "claude-haiku-4-5-20251001"   # سريع ورخيص، غيّره لو تبي أقوى
MAX_USER_MSGS = 40                    # حد الرسائل لكل زائر (يحميك من الفاتورة)
BG_DIR = "backgrounds"                # ضع الصور هنا: home.jpg / fitness.jpg / habits.jpg / study.jpg / ai_chat.jpg

SYSTEM_PROMPT = """أنت مساعد «منصة التطوير الذاتي الشاملة» من تطوير عبد الله.
تكلم بلهجة سعودية بيضاء ودودة وخفيفة، كأنك صديق، وبردود قصيرة ومفيدة (3-6 أسطر غالباً).
أقسام المنصة: 🏋️ التحدي الرياضي (حساب السعرات BMR/TDEE والبروتين والماء حسب الهدف)،
🚫 تحدي العادات (خطة لكسر عادة حسب المحفز)، 📚 التحدي الدراسي (نصائح لـ 11 تخصصاً)، 🤖 المساعد الذكي (أنت).
ساعد في: اختيار التخصص، الدراسة، الرياضة والتغذية العامة، كسر العادات، التحفيز وتنظيم الوقت.
وجّه المستخدم للقسم المناسب في المنصة عند الحاجة، ولا تخترع ميزات غير موجودة.
لا تشخّص أمراضاً ولا تعطِ علاجات؛ في الحالات الصحية أو النفسية الجادة انصح بمراجعة مختص.
إذا خرج السؤال عن التطوير الذاتي رد باختصار ثم أرجعه بلطف لمواضيع المنصة."""

QUICK = ["محتار في التخصص", "كيف أنزل وزني؟", "أبغى أكسر عادة السهر", "ذاكر بطريقة أفضل"]

# ===================== حالة الجلسة =====================
def reset_ai_messages():
    st.session_state.ai_messages = [{"role": "assistant", "content":
        "يا هلا والله! أنا مساعدك في «منصة التطوير الذاتي الشاملة» 👋 "
        "محتار بتخصص؟ تبي تنزل وزنك؟ تبي تكسر عادة؟ فضفض لي وش شاغل بالك."}]

st.session_state.setdefault("current_page", "home")
st.session_state.setdefault("nav", 0)
if "ai_messages" not in st.session_state:
    reset_ai_messages()

def go(page):
    st.session_state.current_page = page
    st.session_state.nav += 1
    st.rerun()

# ===================== الخلفيات =====================
@st.cache_data(show_spinner=False)
def load_bg(name):
    for n in (name, "home"):
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = os.path.join(BG_DIR, f"{n}.{ext}")
            if os.path.exists(p):
                mime = "jpeg" if ext in ("jpg", "jpeg") else ext
                with open(p, "rb") as f:
                    return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()
    return None

# ===================== التصميم =====================
def inject_css(page):
    ab = "A" if st.session_state.nav % 2 == 0 else "B"   # تبديل اسم الأنيميشن يعيد تشغيله عند كل انتقال
    bg = load_bg(page)
    bg_css = (f"linear-gradient(rgba(10,14,20,.80), rgba(10,14,20,.92)), url('{bg}') center/cover fixed"
              if bg else "linear-gradient(-45deg,#0b0f16,#10243a,#0d2a22,#1b1633)")
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
html, body, [class*="css"], [data-testid="stMarkdownContainer"] {{ font-family:'Cairo',sans-serif; }}

[data-testid="stAppViewContainer"] {{
    background: {bg_css}; background-size: {'cover' if bg else '400% 400%'};
    {'' if bg else 'animation: drift 20s ease infinite;'}
    color:#c9d4e0; direction:rtl; text-align:right;
}}
[data-testid="stHeader"] {{ background:transparent; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
[data-testid="stBottom"] > div {{ background:transparent; }}
.block-container {{ max-width:1100px; padding-top:2rem; padding-bottom:5rem;
    animation: fade{ab} .75s cubic-bezier(.22,1,.36,1); }}
[data-testid="stSlider"], [data-testid="stSelectSlider"] {{ direction:ltr; }}

/* ستارة الانتقال: تغطي الشاشة ثم تنكشف بنعومة */
.veil {{ position:fixed; inset:0; background:#0a0e14; z-index:9998; pointer-events:none;
    opacity:0; animation: veil{ab} .8s ease forwards; }}
@keyframes veilA {{ 0%{{opacity:1}} 100%{{opacity:0}} }}
@keyframes veilB {{ 0%{{opacity:1}} 100%{{opacity:0}} }}
@keyframes fadeA {{ from{{opacity:0; transform:translateY(24px) scale(.985)}} to{{opacity:1; transform:none}} }}
@keyframes fadeB {{ from{{opacity:0; transform:translateY(24px) scale(.985)}} to{{opacity:1; transform:none}} }}
@keyframes drift {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}

h1.hero {{ text-align:center; font-weight:800; font-size:3rem; margin:.5rem 0;
    background:linear-gradient(90deg,#7ee787,#539bf5); -webkit-background-clip:text; color:transparent; }}
p.sub {{ text-align:center; color:#9aa9b9; font-size:1.15rem; line-height:1.9; }}

.card {{ padding:26px; border-radius:22px; text-align:center; margin-bottom:14px; min-height:210px;
    background:rgba(22,27,34,.62); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,.09);
    transition:.35s; }}
.card:hover {{ border-color:#539bf5; transform:translateY(-6px); box-shadow:0 14px 34px rgba(83,155,245,.18); }}
.card h2 {{ color:#fff; font-weight:700; }}

div.stButton > button {{ width:100%; border-radius:14px; height:3.4em; background:#238636; color:#fff;
    font-weight:700; border:none; transition:.3s; margin-bottom:22px; }}
div.stButton > button:hover {{ background:#2ea043; color:#fff; transform:translateY(-2px);
    box-shadow:0 6px 18px rgba(46,160,67,.4); }}

.advice-box {{ padding:15px 18px; border-right:5px solid #539bf5; background:rgba(34,39,46,.75);
    backdrop-filter:blur(8px); border-radius:8px; margin:10px 0; }}
[data-testid="stChatMessage"] {{ background:rgba(28,33,40,.7); border-radius:16px; backdrop-filter:blur(8px); }}
[data-testid="stMetric"] {{ background:rgba(22,27,34,.65); border:1px solid rgba(255,255,255,.08);
    border-radius:16px; padding:14px; }}
.seo-section, .brand-box {{ margin-top:30px; padding:24px; border-radius:18px; text-align:center;
    background:rgba(22,27,34,.6); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,.08); }}
.seo-section h2, .brand-box span {{ color:#539bf5; }}
.seo-section p {{ line-height:1.9; }}
.footer-text {{ position:fixed; bottom:0; left:0; padding:8px 15px; background:#0a0e14;
    color:#539bf5; font-size:14px; font-weight:700; z-index:999; }}

@media (prefers-reduced-motion: reduce) {{ .veil, .block-container {{ animation:none; }} }}
</style>
<div class="veil"></div>
<div class="footer-text">حقوق التطوير محفوظة لـ عبد الله © 2026</div>
""", unsafe_allow_html=True)

def back_button(key):
    if st.button("⬅️ العودة للرئيسية", key=key):
        go("home")

def advice(text):
    st.markdown(f"<div class='advice-box'>{text}</div>", unsafe_allow_html=True)

# ===================== الذكاء الاصطناعي =====================
def get_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")

TOPICS = [
    (["تخصص", "محتار", "دراس", "مجال", "جامعة"], [
        "الحيرة طبيعية! قلي وش تحب أكثر: التقنية، الطب، الأرقام، ولا التعامل مع الناس؟ وأرشح لك. وتقدر تشوف نصايح كل تخصص في التحدي الدراسي 📚",
        "جرب تسأل نفسك: وش المجال اللي تقدر تتعلمه ساعات وما تمل؟ هذا غالباً هو تخصصك. جرب التحدي الدراسي عندنا."]),
    (["وزن", "رجيم", "سعرات", "دهون", "رياض", "تمرين", "عضل"], [
        "النزول الصحي يبي عجز سعرات بسيط وثبات، مو تجويع. ادخل التحدي الرياضي وحط بياناتك وأحسب لك سعراتك وبروتينك 🏋️",
        "ابدأ بحساب احتياجك من التحدي الرياضي، وبعدها امشِ عليه أسبوعين وقيّم النتيجة."]),
    (["عادة", "عادات", "سهر", "تدخين", "ادمان", "إدمان", "جوال"], [
        "كسر العادة يبدأ بمعرفة المحفز. ادخل تحدي العادات، اكتب العادة وحدد وش يشغلها، وتطلع لك خطة 🚫",
        "لا تحاول تقطعها مرة وحدة، استبدلها بشي ثاني وقلل تدريجياً. جرب مختبر العادات."]),
    (["مذاكرة", "ذاكر", "امتحان", "اختبار", "تركيز"], [
        "جرب البومودورو: 25 دقيقة تركيز و5 راحة، وبعدها اشرح اللي ذاكرته بكلامك (تقنية فينمان) 🍅"]),
]
DEFAULT = ["يا هلا! ما فهمت قصدك 100%، بس أقدر أساعدك في الدراسة والرياضة والعادات. وش تبي نبدأ فيه؟"]

def local_stream(q):
    reply = next((random.choice(r) for kws, r in TOPICS if any(k in q for k in kws)), random.choice(DEFAULT))
    for w in reply.split(" "):
        yield w + " "
        time.sleep(0.03)

def llm_stream(history, key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msgs = [m for m in history][-12:]
        while msgs and msgs[0]["role"] != "user":
            msgs.pop(0)
        with client.messages.stream(model=MODEL, max_tokens=600, system=SYSTEM_PROMPT, messages=msgs) as s:
            for t in s.text_stream:
                yield t
    except Exception:
        yield "صار عندي خلل بسيط في الاتصال 😅 جرب ترسل مرة ثانية بعد شوي."

# ===================== الصفحات =====================
def page_home():
    st.markdown("<h1 class='hero'>🚀 منصة التطوير الذاتي الشاملة</h1>"
                "<p class='sub'>الدراسة والرياضة وتغيير العادات ومساعد ذكي، كلها في مكان واحد.</p>",
                unsafe_allow_html=True)
    cards = [
        ("fitness", "🏋️ التحدي الرياضي", "احسب سعراتك وبروتينك واحصل على نصائح تناسب هدفك."),
        ("study", "📚 التحدي الدراسي", "خطط ونصائح تخصصية ترفع مستواك الأكاديمي."),
        ("habits", "🚫 تحدي العادات", "استراتيجيات عملية لكسر العادات السلبية وبناء أفضل منها."),
        ("ai_chat", "🤖 المساعد الذكي", "اسأله عن الدراسة أو الرياضة أو العادات وسولف معه."),
    ]
    cols = st.columns(2)
    for i, (page, title, desc) in enumerate(cards):
        with cols[i % 2]:
            st.markdown(f"<div class='card'><h2>{title}</h2><p>{desc}</p></div>", unsafe_allow_html=True)
            if st.button("ادخل", key=f"btn_{page}"):
                go(page)
    st.markdown("""<div class="seo-section"><h2>منصة التطوير الذاتي الشاملة</h2>
        <p>منصة تفاعلية تساعدك على تطوير نفسك: التحدي الرياضي، تحدي العادات، التحدي الدراسي، ومساعد الذكاء الاصطناعي.</p></div>
        <div class="brand-box"><span>منصة التطوير الذاتي الشاملة</span><br>تطوير الذات • الدراسة • الرياضة • العادات • الذكاء الاصطناعي</div>""",
                unsafe_allow_html=True)

def page_fitness():
    st.title("🏋️ التحدي الرياضي الذكي")
    back_button("back_fit")
    c1, c2 = st.columns(2)
    with c1:
        gender = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True)
        weight = st.number_input("الوزن (كجم):", 30.0, 250.0, 75.0)
        height = st.number_input("الطول (سم):", 100.0, 250.0, 175.0)
        age = st.number_input("العمر:", 10, 90, 22)
    with c2:
        acts = {"خامل جداً": 1.2, "تمارين خفيفة (1-2 يوم)": 1.375, "نشاط متوسط (3-4 أيام)": 1.55,
                "نشاط مكثف (5-6 أيام)": 1.725, "محترف/بطل رياضي": 1.9}
        activity = st.radio("نشاطك الأسبوعي:", list(acts))
        goal = st.selectbox("هدفك:", ["تنشيف (خسارة دهون)", "تضخيم (بناء عضل)", "لياقة عامة"])
    if st.button("📊 توليد التقرير والنصائح"):
        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "ذكر" else -161)
        tdee = bmr * acts[activity]
        target = tdee - 500 if "تنشيف" in goal else tdee + 400 if "تضخيم" in goal else tdee
        m = st.columns(4)
        m[0].metric("سعرات المحافظة", f"{int(tdee)}")
        m[1].metric("هدفك اليومي", f"{int(target)}")
        m[2].metric("بروتين (جم)", f"{int(weight * 1.8)}")
        m[3].metric("ماء (لتر)", f"{weight * 0.035:.1f}")
        tips = ["✅ **قاعدة الـ 10%:** لا تزد شدة تمارينك أكثر من 10% أسبوعياً.",
                "💧 **الترطيب:** اشرب الماء قبل التمرين وأثناءه وبعده.",
                "😴 **الاستشفاء:** العضلات تنمو وقت النوم، لا تقلل ساعاتك.",
                "🍎 **التغذية:** وزّع البروتين على وجباتك.",
                "⏱️ **الراحة:** يوم راحة على الأقل بين تمارين نفس العضلة.",
                "🧘 **الإحماء:** 5-10 دقائق تحمية تقلل الإصابات."]
        for t in random.sample(tips, 3):
            advice(t)
        st.caption("التقديرات عامة وليست بديلاً عن استشارة مختص تغذية.")

def page_habits():
    st.title("🚫 مختبر تغيير العادات")
    back_button("back_habits")
    c1, c2 = st.columns(2)
    with c1:
        habit = st.text_input("ما العادة التي تود كسرها؟ (مثلاً: السهر، السكريات)")
        st.select_slider("صعوبتها عليك:", ["سهلة", "متوسطة", "صعبة", "إدمان"])
    with c2:
        trigger = st.selectbox("المحفز الرئيسي:", ["الملل", "التوتر", "أصدقاء السوء", "الفراغ", "الوقت (مثلاً قبل النوم)"])
    if st.button("🚀 حلل العادة وضع الخطة"):
        tips = {"الملل": "استبدل العادة بنشاط يشغل يديك وعقلك.",
                "التوتر": "جرب التنفس العميق أو المشي 5 دقائق عند الرغبة.",
                "أصدقاء السوء": "غيّر البيئة وقلل الاحتكاك بالمحفزات.",
                "الفراغ": "اعمل جدولاً يومياً واضحاً يملأ أوقات الفراغ.",
                "الوقت (مثلاً قبل النوم)": "غيّر روتين هذا الوقت بالكامل."}
        st.markdown(f"### 🛡️ خطة التخلص من {habit or 'العادة'}")
        st.info(f"📍 **نصيحة للمحفز ({trigger}):** {tips[trigger]}")
        general = ["✨ **قاعدة الـ 5 ثوانٍ:** إذا جتك الرغبة تحرك فوراً لشي ثاني.",
                   "🔗 **ربط العادات:** اربط عادة جيدة بروتين موجود عندك.",
                   "📉 **التدرج:** خطوات صغيرة تقدر تستمر عليها.",
                   "📝 **التدوين:** سجل متى ولماذا تظهر الرغبة."]
        for g in random.sample(general, 2):
            advice(g)

STUDY = {
    "هندسة الشبكات": ["تدرب على GNS3 و EVE-NG.", "احصل على CCNA قبل التخرج.", "افهم OSI Model جيداً."],
    "الأمن السيبراني": ["تعلم أساسيات Linux.", "مارس تحديات CTF.", "Security+ بداية ممتازة."],
    "الذكاء الاصطناعي": ["أتقن الرياضيات الأساسية.", "تعلم Pandas و Scikit-learn.", "ابنِ مشاريع ببيانات حقيقية."],
    "علوم الحاسب": ["ركز على هياكل البيانات.", "حل مسائل برمجية يومياً.", "افهم إدارة الذاكرة."],
    "الطب": ["استخدم Anki للتكرار المتباعد.", "اربط المعلومة بالحالة السريرية.", "راجع باستمرار."],
    "الهندسة الميكانيكية": ["أتقن برامج CAD.", "افهم الديناميكا الحرارية.", "تابع التصنيع الحديث."],
    "إدارة الأعمال": ["تعلم Excel و Power BI.", "اقرأ في القيادة.", "افهم التسويق الرقمي."],
    "المحاسبة": ["افهم IFRS.", "تدرب على برامج المحاسبة.", "ركز على دقة الأرقام."],
    "القانون": ["درب نفسك على الصياغة القانونية.", "تابع الأحكام القضائية.", "شارك في المحاكم الصورية."],
    "التمريض": ["اهتم بالجانب الإنساني.", "أتقن مهارات الطوارئ.", "تعلم قياس المؤشرات الحيوية."],
    "الهندسة الكهربائية": ["ركز على الطاقة والتحكم.", "أتقن MATLAB.", "افهم الدوائر والأنظمة المدمجة."],
}

def page_study():
    st.title("📚 مركز التميز الأكاديمي")
    back_button("back_study")
    major = st.selectbox("اختر تخصصك:", list(STUDY))
    st.success(f"📌 **خطة التميز لتخصص {major}:**")
    for t in STUDY[major]:
        st.write(f"- {t}")
    st.markdown("---")
    st.subheader("💡 نصائح دراسية عامة")
    general = ["🍅 **البومودورو:** 25 دقيقة دراسة ثم استراحة.", "🎧 **البيئة:** قلل المشتتات، الجوال بعيد عنك.",
               "🖍️ **الخرائط الذهنية:** حوّل المعلومات المعقدة لرسومات.", "👨‍🏫 **فينمان:** اشرح ما درسته بكلماتك."]
    for g in random.sample(general, 2):
        advice(g)

def page_ai():
    st.title("🤖 المساعد الذكي")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ العودة للرئيسية", key="back_ai"):
            go("home")
    with c2:
        if st.button("🗑️ محادثة جديدة", key="clear_ai"):
            reset_ai_messages()
            st.rerun()

    for m in st.session_state.ai_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("فضفض لي أو اسألني عن أي شيء...")
    if len(st.session_state.ai_messages) == 1:
        qc = st.columns(len(QUICK))
        for i, q in enumerate(QUICK):
            if qc[i].button(q, key=f"q{i}"):
                prompt = q

    if prompt:
        used = sum(m["role"] == "user" for m in st.session_state.ai_messages)
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            if used >= MAX_USER_MSGS:
                reply = "وصلت للحد الأقصى من الرسائل في هذي الجلسة، ابدأ محادثة جديدة 🙏"
                st.markdown(reply)
            else:
                key = get_key()
                gen = llm_stream(st.session_state.ai_messages, key) if key else local_stream(prompt)
                reply = st.write_stream(gen)
        st.session_state.ai_messages.append({"role": "assistant", "content": reply})

# ===================== التشغيل =====================
PAGES = {"home": page_home, "fitness": page_fitness, "habits": page_habits,
         "study": page_study, "ai_chat": page_ai}
page = st.session_state.current_page
inject_css(page)
PAGES[page]()
