import hashlib
import os
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from pypdf import PdfReader

from app_auth import require_authentication

load_dotenv(Path(__file__).with_name(".env"))


def get_openai_api_key() -> str:
  try:
    if "OPENAI_API_KEY" in st.secrets:
      return st.secrets["OPENAI_API_KEY"]
  except Exception:
    pass

  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env or Streamlit Secrets.")
  return api_key

REFERENCE_PDF_DIR = Path(__file__).with_name("reference_docs")
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.2
RETRIEVAL_K = 6

st.set_page_config(page_title="Get or Not?", page_icon="🤖")
require_authentication()

def load_and_split(pdf_path: Path):
  reader = PdfReader(str(pdf_path))
  documents = []
  for page_number, page in enumerate(reader.pages, start=1):
    page_text = page.extract_text() or ""
    if page_text.strip():
      documents.append(
        Document(
          page_content=page_text,
          metadata={"source": pdf_path.name, "page": page_number},
        )
      )

  splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
  )
  return splitter.split_documents(documents)

@st.cache_resource
def build_vectorstore(_chunks: list[Document], chunks_key: str) -> Chroma:
  embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=get_openai_api_key(),
  )
  return Chroma.from_documents(_chunks, embeddings)

@st.cache_resource
def load_reference_vectorstore(
  pdf_paths: tuple[str, ...],
  files_hash: str,
) -> tuple[Chroma, int]:
  chunks = []
  for pdf_path in pdf_paths:
    chunks.extend(load_and_split(Path(pdf_path)))
  if not chunks:
    raise ValueError("The reference PDFs contain no extractable text.")
  return build_vectorstore(chunks, files_hash), len(chunks)

def retrieve_context(vectorstore: Chroma, query: str, k: int = 4) -> str:
  retriever = vectorstore.as_retriever(search_kwargs={"k": k})
  documents = retriever.invoke(query)
  return "\n\n---\n\n".join(document.page_content for document in documents)

system_prompt_no_doc = (
  "Say briefly that no reference documents are currently available, so you cannot assess "
  "scheme eligibility or provide a reliable result. Ask the user to add or consult the official documents."
)

def build_rag_system_prompt(context: str) -> str:
  return (
    "You answer Singapore government-benefit questions using only the provided context. "
    "For an eligibility question: (1) briefly list the schemes that may be relevant, "
    "(2) state only eligibility criteria and payment amounts explicitly supported by the context, "
    "and (3) clearly identify missing personal details needed to confirm eligibility. "
    "Do not invent criteria, dates, amounts, or application results. "
    "Keep the answer concise and use short bullets. If a scheme cannot be confirmed from the context, "
    "say so explicitly. End with: 'Confirm the final result on the official GovPayouts portal.'\n\n"
    f"Context:\n{context}"
  )

st.title("Get or Not?")
if "chat_started" not in st.session_state:
  st.session_state.chat_started = False

with st.expander("**Important Notice**", expanded=not st.session_state.chat_started):
  st.markdown(
    "This web application is a prototype developed for "
    "**educational purposes only.** The information provided here is **NOT "
    "intended for real-world usage** and should not be relied upon for making "
    "any decisions, especially those related to financial, legal, or healthcare matters.\n\n"
    "**Furthermore, please be aware that the LLM may generate inaccurate or "
    "incorrect information. You assume full responsibility for how you use any "
    "generated output.**\n\n"
    "Always consult with qualified professionals for accurate and personalised advice."
  )

def mark_chat_started():
  st.session_state.chat_started = True

if "messages" not in st.session_state:
  st.session_state.messages = []

with st.sidebar:
  st.header("⚙️ Status")
  reference_files = tuple(sorted(REFERENCE_PDF_DIR.glob("*.pdf")))
  indexed_chunk_count = 0
  if reference_files:
    try:
      files_digest = hashlib.sha256()
      for pdf_path in reference_files:
        files_digest.update(pdf_path.name.encode("utf-8"))
        files_digest.update(pdf_path.read_bytes())
      vectorstore, indexed_chunk_count = load_reference_vectorstore(
        tuple(str(pdf_path) for pdf_path in reference_files),
        files_digest.hexdigest(),
      )
      st.session_state.vectorstore = vectorstore
      st.success(f"Ready! Indexed {indexed_chunk_count} chunks from {len(reference_files)} PDF(s).")
    except Exception:
      traceback.print_exc()
      st.session_state.pop("vectorstore", None)
      st.error("Could not index the reference PDFs. Check the files and API key.")
  else:
    st.warning(f"Place your reference PDF files in: {REFERENCE_PDF_DIR}")
    st.session_state.pop("vectorstore", None)

  with st.expander("Configuration"):
    st.caption(f"Model: {MODEL_NAME}")
    st.caption(f"Temperature: {TEMPERATURE}")
    st.caption(f"Chunks retrieved per question: {RETRIEVAL_K}")
    reference_names = ", ".join(path.name for path in reference_files) or "None"
    st.caption(f"Reference PDFs: {reference_names}")
    st.caption(f"Indexed chunks: {indexed_chunk_count}")
    st.markdown("**RAG system prompt**")
    st.text(build_rag_system_prompt("[Retrieved document passages appear here]"))
    st.markdown("**No-reference fallback**")
    st.text(system_prompt_no_doc)

  if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.session_state.chat_started = False
    st.rerun()
  if st.button("Log out"):
    st.session_state.authenticated = False
    st.session_state.messages = []
    st.session_state.pop("vectorstore", None)
    st.rerun()
  st.markdown(
    "**Confirm eligibility:** "
    "[Log in to GovPayouts](https://www.govpayouts.gov.sg/cds/main/login)"
  )

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.write(message["content"])

prompt = st.chat_input("Type a message...", on_submit=mark_chat_started)

if prompt:
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.write(prompt)

  try:
    api_key = get_openai_api_key()

    client = OpenAI(api_key=api_key)
    if "vectorstore" in st.session_state:
      context = retrieve_context(st.session_state.vectorstore, prompt, RETRIEVAL_K)
      active_system_prompt = build_rag_system_prompt(context)
    else:
      active_system_prompt = system_prompt_no_doc

    api_messages = [
      {"role": "system", "content": active_system_prompt},
      *st.session_state.messages,
    ]
    stream = client.chat.completions.create(
      model=MODEL_NAME,
      messages=api_messages,
      temperature=TEMPERATURE,
      stream=True,
    )
    with st.chat_message("assistant"):
      reply = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": reply})
  except Exception:
    traceback.print_exc()
    fallback_reply = "Sorry, something went wrong. Please try again."
    st.error(fallback_reply)
    st.session_state.messages.append({"role": "assistant", "content": fallback_reply})