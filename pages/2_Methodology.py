import streamlit as st

from app_auth import require_authentication

st.set_page_config(page_title="Get or Not? — Methodology", page_icon="🧭")
require_authentication()

st.title("Methodology")

st.write(
    "This page documents how I applied concepts and practical techniques covered in the "
    "AI Champions course to build **Get or Not?**, a prototype chatbot for exploring Singapore "
    "government benefits. The project demonstrates learning across problem framing, prompt "
    "design, document retrieval, application development, testing, and responsible AI use."
)

st.subheader("1. Project purpose and course objective")
st.markdown(
    "**Get or Not?** helps users ask questions about government benefits using local reference "
    "documents based on information from **govbenefits.gov.sg**. It is intended as an educational "
    "prototype—not a final eligibility determination or financial decision tool.\n\n"
    "The main learning objective was to move from theoretical AI concepts to a working, documented "
    "application that a person from a non-specialist background could use."
)

st.markdown(
    "**Learning areas demonstrated:**\n"
    "- Framing a real-world problem for an AI solution\n"
    "- Understanding the difference between an ordinary chatbot and a grounded RAG application\n"
    "- Designing prompts and setting model parameters\n"
    "- Preparing, chunking, embedding, and retrieving PDF content\n"
    "- Building a usable interface with Streamlit\n"
    "- Applying authentication and basic session-state controls\n"
    "- Identifying inaccuracies, limitations, and responsible-use requirements"
)

st.subheader("2. Technical methodology and design choices")

st.markdown(
    "1. **PDF discovery:** the application scans `reference_docs/` for PDF files.\n"
    "2. **Text extraction:** pypdf extracts text from each page.\n"
    "3. **Chunking:** text is split into 1,000-character chunks with 200-character overlap. "
    "The chunk size keeps passages focused enough for retrieval, while overlap reduces the risk of "
    "splitting important criteria or payment details across chunk boundaries.\n"
    "4. **Embedding:** OpenAI `text-embedding-3-small` converts chunks into numerical representations "
    "of meaning. This is used because it supports semantic similarity search rather than keyword-only matching.\n"
    "5. **Vector storage:** LangChain and Chroma store the chunks and embeddings for similarity search. "
    "Chroma provides a lightweight local vectorstore suitable for this prototype.\n"
    "6. **Retrieval:** the app retrieves the six most relevant chunks for each question. Six is used as "
    "a practical balance: it provides relevant scheme context without overloading the model with excessive text.\n"
    "7. **Augmented generation:** retrieved text is added to a grounded system prompt before calling "
    "`gpt-4o-mini`. This model is used because it provides a suitable balance of response quality, cost, "
    "and speed for an educational prototype.\n"
    "8. **Temperature:** the app uses `0.2`. A lower temperature is chosen to make answers more consistent "
    "and reduce speculative wording when the response should follow the reference documents.\n"
    "9. **Interface:** Streamlit provides a simple multipage interface, authentication, chat controls, "
    "session-state conversation history, and visible configuration status.\n"
    "10. **Conversation:** Streamlit session state preserves chat messages during the session."
)

st.subheader("Use case: index reference PDFs")
st.graphviz_chart('''
digraph Indexing {
  graph [rankdir=TB]
  node [shape=box, style="rounded,filled", fillcolor="#EAF2F8"]
  start [shape=oval, label="Application starts"]
  scan [label="Scan reference_docs/*.pdf"]
  found [shape=diamond, label="PDFs found?"]
  missing [label="Warn that no PDFs are available"]
  extract [label="Extract text from each page"]
  readable [shape=diamond, label="Readable text found?"]
  split [label="Create overlapping text chunks"]
  hash [label="Hash PDF names and contents"]
  cache [shape=diamond, label="Cached vectorstore found?"]
  embed [label="Create text embeddings"]
  store [label="Build Chroma vectorstore"]
  ready [shape=oval, label="Show ready status"]
  failed [label="Show indexing error"]
  start -> scan -> found
  found -> missing [label="No"]
  found -> extract [label="Yes"]
  extract -> readable
  readable -> failed [label="No"]
  readable -> split [label="Yes"]
  split -> hash -> cache
  cache -> ready [label="Hit"]
  cache -> embed [label="Miss"]
  embed -> store -> ready
}
''')

st.subheader("Use case: answer a user question")
st.graphviz_chart('''
digraph GroundedAnswer {
  graph [rankdir=TB]
  node [shape=box, style="rounded,filled", fillcolor="#E8F5E9"]
  login [shape=oval, label="Authenticated user asks a question"]
  retrieve [label="Retrieve relevant PDF chunks"]
  prompt [label="Combine question and context in a grounded prompt"]
  generate [label="Generate a concise streamed response"]
  assess [shape=diamond, label="Answer supported by the context?"]
  answer [label="State schemes, criteria, and supported amounts"]
  unknown [label="State that the information was not found"]
  confirm [shape=oval, label="Suggest official GovPayouts confirmation"]
  login -> retrieve -> prompt -> generate -> assess
  assess -> answer [label="Yes"]
  assess -> unknown [label="No"]
  answer -> confirm
  unknown -> confirm
}
''')

st.subheader("Use case: no reference documents")
st.graphviz_chart('''
digraph NoReferenceAnswer {
  graph [rankdir=LR]
  node [shape=box, style="rounded,filled", fillcolor="#FFF4E5"]
  question [shape=oval, label="User asks a question"]
  check [shape=diamond, label="Vectorstore available?"]
  unavailable [label="Explain that no document context is available"]
  avoid [label="Avoid guessing scheme eligibility"]
  question -> check
  check -> unavailable [label="No"]
  unavailable -> avoid
}
''')

st.subheader("3. Reflection")
st.markdown(
    "This course helped me develop a better understanding of what happens behind the scenes in AI, "
    "beyond simply writing prompts or using a ready-made interface. I learned about concepts such as "
    "retrieval, embeddings, vector search, grounding responses in source documents, and applying "
    "model settings to influence consistency."
)
st.markdown(
    "The barrier to entry is now lower through vibecoding. As a novice, I could use AI-assisted tools "
    "to understand, modify, and troubleshoot code, making it easier to turn an idea into a working "
    "prototype and experiment with AI concepts in practice."
)
st.markdown(
    "However, building the chatbot showed that a working prototype is not necessarily a useful or "
    "accurate service. The project still requires considerable calibration through improved prompts, "
    "retrieval, testing, and handling unsupported questions."
)
st.markdown(
    "The surest and most accurate way for users to confirm eligibility remains the official government "
    "eligibility check. The chatbot is therefore best used as an educational starting point that helps "
    "users explore schemes and understand the types of information they may need, rather than as a "
    "final decision-making tool. The chatbot also provides a link to the official government eligibility check in the sidebar."
)
