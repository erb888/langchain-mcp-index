from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def get_retriever():
  docs = SimpleDirectoryReader('./data').load_data()
  index = VectorStoreIndex.from_documents(docs)
  return index.as_retriever(similarity_top_k=3)
