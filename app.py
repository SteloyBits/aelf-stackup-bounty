import bs4
import requests
import lxml
import re
import os
import streamlit as st

html_files = [filen for filen in os.listdir('./aelf_docs') if filen.endswith('.html')]

def clean_text(text):

    # Remove control characters
    text = text.encode("ascii", "ignore").decode("ascii")

    # Remove emojis using regex (optional)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictograms
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002500-\U00002BEF"  # Chinese, Japanese, Korean symbols & punctuation
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u200b"
        "\u200c"
        "\u200e"
        "\u2069"
        "\u2066"
        "\u2067"
        "\u2068"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # Dingbats
        "\u3030"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    return text

def extract_content(html_content):
    html_content = open(html_content, 'r').read()
    soup = bs4.BeautifulSoup(html_content, 'lxml')

    out_list = []
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'pre', 'code']):
        out_list.extend(clean_text(element.text) + "\n")
    
    soup_txt = ''.join(word for word in out_list).replace('*', '')
    return soup_txt

page_summary_prompt = f"""You are an assistant tailored for summarizing text for retrieval.
  These summaries would contain any useful information for a developer that wants to solve an issue.
  These summaries should contain full code snippets if any.
  Note that the summaries will be turned into vector embeddings and used to retrieve the raw text.
  Give a concise summary of the text that is well optimized for retrieval. Here is the text."""

import google.generativeai as genai

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('models/gemini-1.5-flash')

text_summaries = []

for f in html_files:
    response = model.generate_content([page_summary_prompt, extract_content(f)])

    text_summaries.append(response.text)

class GeminiEmbeddingFunction(EmbeddingFunction):
  def __call__(self, input: Documents) -> Embeddings:
    model = 'models/text-embedding-004'
    title = "Custom query"
    return genai.embed_content(model=model,
                                content=input,
                                task_type="retrieval_document",
                                title=title)["embedding"]

def create_chroma_db(documents, name):
  chroma_client = chromadb.Client()
  db = chroma_client.get_or_create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
  
  for i, d in enumerate(documents):
    db.add(
      documents=d,
      ids=str(i)
    )
  return db
  
ldb = create_chroma_db(text_summaries, "aelf")

def get_relevant_files(query, db):
  results = db.query(query_texts=[query], n_results=3)
  return results["ids"][0]

def query_rag(query, db):
  files = get_relevant_files(query, db)
  prompt = [text_summaries[int(f)] for f in files]
  prompt.append("Generate a response to the query using the provided files. Here is the query.")
  prompt.append(query)
  return model.generate_content(prompt).text

def main(user_prompt):
  semi_result = query_rag(user_prompt, ldb)

  last_prompt = """You are a summarising agent. Summarise the following text to briefly explain the key idea outlined in the text without directly referring to the text.
                 Make your output like as if you were writing a blog post in markdown format, giving step-by-step guides to a developer.
                 Here is the text:"""

  last_response = model.generate_content([last_prompt, semi_result.replace('#', '')])
  return last_response.text


st.set_page_config(page_title="aelf RAG", page_icon=":robot:")
st.title("aelf RAG")
st.write("Enter your questions about the aelf documentation and get a direct response in seconds")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Your Prompt"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = main(user_prompt=user_prompt)
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
