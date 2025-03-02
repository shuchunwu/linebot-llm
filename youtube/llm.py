from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.core import VectorStoreIndex
from llama_index.readers.youtube_transcript.utils import is_youtube_video
from llama_index.core import Document, Settings
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.memory import ChatMemoryBuffer

def youtube_role(user_query):
    """
    define the role information for youtube transcript

    Args:
        user_query (string): input from user, youtube link or question

    Returns:
        system_query (string): defined role information with user query
    """

    system_query = ""

    # M (Mission)
    system_query += "你的目的是協助民眾了解影片內提到的內容。\n"

    # A (Assignee)
    system_query += "你是一位根據影片內容而設的專家，懂多國語言。\n"

    # T (Task)
    system_query += "請負責從提供的逐字稿和歷史談話中找到答案。\n若提問與該影片的逐字稿內容無關，或是資料來源無法找到相關的資訊，請以禮貌的方式拒絕，並清楚告知你的服務範圍。\n"

    # E (Expectation)
    system_query += "語氣應該是友善和耐心的，風格應該是清晰和簡潔的，然後請盡量以條列式的方式回答，請全部用使用者詢問的語言回應，請勿使用任何簡體中文，除非專有名詞否則請勿中英文夾雜，不使用任何Markdown語法回應。\n"

    # Query
    system_query += f"底下是使用者的提問: {user_query}"

    return system_query

loader = YoutubeTranscriptReader()

SUPPORTED_LANGUAGES = [
    'zh-TW', 'zh-Hant', 'zh', 'zh-Hans', 'en', 'de' , 'fr', 'es', 'ja', 'ko', 'pt', 'ru', 'ar', 'hi', 'it', 'tr', 'vi', 'th', 'id', 'ms', 'tl', 'nl', 'pl', 'sv', 'da', 'fi', 'no', 'hu', 'cs', 'sk', 'ro', 'uk', 'el', 'bg', 'sr', 'hr', 'sl', 'et', 'lv', 'lt', 'sq', 'mk', 'bs', 'is', 'ga', 'cy', 'mt', 'eu', 'gl', 'ca', 'eu', 'la', 'af', 'xh', 'zu', 'ny', 'st', 'tn', 'ss', 'ts', 've', 'nr', 'sw', 'rw', 'rn', 'lg', 'lu', 'mg', 'sn', 'nd', 'ny'
]

chat_engine = None

def build_youtube_query_engine(youtube_link, llm, embed_model):
    """
    create a chat engine for youtube transcript

    Args:
        youtube_link (string): youtube link to get transcript
        llm: model to use for language modeling
        embed_model: model to use for embedding

    Raises:
        Exception: error message if failed to load transcripts

    Returns:
        None
    """

    if not llm or not embed_model:
        raise Exception("No llm or embed_model")
    
    # get youtube transcript
    all_documents = []
    if is_youtube_video(youtube_link):
        try:
            print("Loading YouTube transcript...")
            documents = loader.load_data(ytlinks=[youtube_link], languages=SUPPORTED_LANGUAGES)
            for doc in documents:
                    content = doc.get_content()
                    metadata = {"source": youtube_link}
                    document = Document(text=content, extra_info=metadata)
                    all_documents.append(document)

            print(f"Transcript for {youtube_link}:")
            print(all_documents)

        except Exception as e:
            print(f"Error loading transcripts: {e}")
            return f"Error loading transcripts: {e}"
    else:
        print(f"Not a valid youtube link: {youtube_link}")
        return f"Not a valid youtube link: {youtube_link}"
    
    Settings.chunk_size = 300 # default 512
    Settings.chunk_overlap = 50 # default 20
    
    # Build index
    print("Building index...")
    index = VectorStoreIndex.from_documents(
        documents=all_documents,
        embed_model=embed_model
    )

    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
    # Build chat engine
    print("Building chat engine...")
    global chat_engine
    chat_engine = index.as_chat_engine(
        chat_mode=ChatMode.CONDENSE_PLUS_CONTEXT,
        memory=memory,
        llm=llm
    )
    print("Chat engine built successfully.")

def get_youtube_transcript_info(query):
    """
    get the answer from chat engine

    Args:
        query (string): input from user, the question to ask

    Returns:
        res.response: answer from chat engine
    """

    system_prompt = youtube_role(query)
    print("Querying chat engine...")
    res = chat_engine.chat(system_prompt)
    print("Query completed.")
    return res.response

def clean_youtube_transcript_history():
    """
    clean youtube chat engine history
    """
    chat_engine.chat_history.clear()
