from llama_index.readers.papers import ArxivReader
from llama_index.core import VectorStoreIndex

loader = ArxivReader()

def summarize_essay(query, llm, embed_model, max_results=1):
    """
    Summarize the essay based on the keyword

    Args:
        query (string): input from user, usually the keyword of the essay
        llm: model for language model
        embed_model: model for embedding
        max_results (int, optional): number of results you would like to show. Defaults to 1.

    Raises:
        Exception: if llm or embed_model is not provided, or getting data from loader failed

    Returns:
        self-defined string: detailed information of the essay and summary of the essay
    """

    if not llm or not embed_model:
        raise Exception("No llm or embed_model")

    try:
        documents = loader.load_data(
            search_query=query,
            max_results=max_results
        )
    except Exception as e:
        return str(e)
    
    metadata = documents[0].metadata # document[0] is the most relevant one
    title = metadata["Title of this paper"]
    author = metadata["Authors"] 
    publish_date = metadata["Date published"]
    url = metadata["URL"]

    index = VectorStoreIndex.from_documents(
        documents=documents,
        embed_model=embed_model
    )

    query_engine = index.as_query_engine(llm=llm)
    res = query_engine.query("請詳細列點解釋文章的各個觀點")

    return f"文章標題 Title：{title}\n作者 Author：{author}\n發布時間 Publish Date：{publish_date}\nURL：{url}\n{res}"
