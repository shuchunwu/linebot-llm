from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from restaurant.extractor import FaqExtractor, BlogExtractor, GoogleMapExtractor
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.response.pprint_utils import pprint_response

query_engine = None

def build_restaurant_query_engine(llm, embed_model):
    """
    Build a query engine for restaurant information retrieval.

    Args:
        llm: model to use for language modeling
        embed_model: model to use for embedding
    """

    # Load data
    qa_docs = SimpleDirectoryReader(
        input_files=["./restaurant/data/faq.qa"],
        file_extractor={".qa": FaqExtractor()}
    ).load_data()
    blog_docs = SimpleDirectoryReader(
        input_files=["./restaurant/data/blog.md"],
        file_extractor={".md": BlogExtractor()}
    ).load_data()
    gogle_map_docs = SimpleDirectoryReader(
        input_files=["./restaurant/data/google-map.json"],
        file_extractor={".json": GoogleMapExtractor()}
    ).load_data()

    # Build index
    qa_index = VectorStoreIndex.from_documents(
        documents=qa_docs,
        embed_model=embed_model
    )
    blog_index = VectorStoreIndex.from_documents(
        documents=blog_docs,
        embed_model=embed_model
    )
    google_map_index = SummaryIndex.from_documents(
        documents=gogle_map_docs,
        embed_model=embed_model
    )

    # Build query engine
    qa_query_engine = qa_index.as_query_engine(llm=llm)
    blog_query_engine = blog_index.as_query_engine(llm=llm)
    google_map_query_engine = google_map_index.as_query_engine(llm=llm)

    # Build query tool
    faq_tool = QueryEngineTool.from_defaults(
        query_engine=qa_query_engine,
        description="依據餐廳的FAQ資訊提供解答"
    )
    blog_tool = QueryEngineTool.from_defaults(
        query_engine=blog_query_engine,
        description="針對餐廳的任何往紅或Youtuber撰寫的美食評論及部落格文章"
    )
    google_map_tool = QueryEngineTool.from_defaults(
        query_engine=google_map_query_engine,
        description="針對Google Map上的評論與評分"
    )

    # Build query router
    global query_engine
    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=[
            faq_tool, 
            blog_tool, 
            google_map_tool
        ],
        llm=llm
    )

def get_restaurant_info(query):
    res = query_engine.query(query)
    pprint_response(res, show_source=True)
    return res.response
