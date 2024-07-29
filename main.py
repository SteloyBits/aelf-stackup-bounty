# import BeautifulSoup as bs4
import requests
import lxml
import re
import google.generativeai as genai
from google.colab import userdata
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings

# genai.configure(os.environ["API_KEY"])
# model = genai.GenerativeModel('models/gemini-1.5-flash')

# class GeminiEmbeddingFunction(EmbeddingFunction):
#   def __call__(self, input: Documents) -> Embeddings:
#     model = 'models/text-embedding-004'
#     title = "Custom query"
#     return genai.embed_content(model=model,
#                                 content=input,
#                                 task_type="retrieval_document",
#                                 title=title)["embedding"]

# def clean_text(text):
#     text = text.encode("ascii", "ignore").decode("ascii")

#     # Remove emojis using regex (optional)
#     emoji_pattern = re.compile(
#         "["
#         "\U0001F600-\U0001F64F"  # Emoticons
#         "\U0001F300-\U0001F5FF"  # Symbols & Pictograms
#         "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
#         "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
#         "\U00002500-\U00002BEF"  # Chinese, Japanese, Korean symbols & punctuation
#         "\U00002702-\U000027B0"
#         "\U00002702-\U000027B0"
#         "\U000024C2-\U0001F251"
#         "\U0001f926-\U0001f937"
#         "\U00010000-\U0010ffff"
#         "\u2640-\u2642"
#         "\u2600-\u2B55"
#         "\u200d"
#         "\u200b"
#         "\u200c"
#         "\u200e"
#         "\u2069"
#         "\u2066"
#         "\u2067"
#         "\u2068"
#         "\u23cf"
#         "\u23e9"
#         "\u231a"
#         "\ufe0f"  # Dingbats
#         "\u3030"
#         "]+", flags=re.UNICODE)
#     text = emoji_pattern.sub(r'', text)

#     return text

# def extract_content(html_content):
#     html_content = open(html_content, 'r').read()
#     soup = bs4.BeautifulSoup(html_content, 'lxml')

#     out_list = []
#     for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'pre', 'code']):
#         content_dict.get(element.name, []).append(clean_text(element.text))
#         out_list.extend(clean_text(element.text) + "\n")

#     return ''.join(word for word in out_list).replace('*', '')

# def create_chroma_db(documents, name):
#   chroma_client = chromadb.Client()
#   db = chroma_client.get_or_create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
#   db.add(documents=documents,
#     ids='1',
#     metadatas=[{"source": "aelf"}]
#     )
#   return db

# def get_relevant_files(query, db):
#   results = db.query(query_texts=[query], n_results=3)
#   return results["ids"][0]

# def query_rag(query, db):
#     files = get_relevant_files(query, db)
#     prompt = [all_files[int(f)] for f in files]
#     prompt.append("Generate a response to the query using the provided files. Here is the query.")
#     prompt.append(query)
#     return model.generate_content(prompt).text, [all_file_names[int(f)] for f in files]


# def main():
#     if __name__ == '__main__':
#         out = extract_content("./index.html")
#         new_file = open("out.txt", "w")
#         new_file.write(out)
#         new_file.close()

#         page_summary_prompt = f"""You are an assistant tailored for summarizing text for retrieval.
#                                    These summaries would contain any useful information for a developer that wants to solve an issue.
#                                    These summaries should contain full code snippets if any.
#                                    Note that the summaries will be turned into vector embeddings and used to retrieve the raw text.
#                                    Give a concise summary of the text that is well optimized for retrieval. Here is the text.
#                                 """
#         filer = genai.upload_file('out.txt')
#         response = model.generate_content([page_summary_prompt, filer])