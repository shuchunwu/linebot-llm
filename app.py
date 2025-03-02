from essay.llm import summarize_essay
from youtube.llm import build_youtube_query_engine, get_youtube_transcript_info, clean_youtube_transcript_history
from restaurant.llm import build_restaurant_query_engine, get_restaurant_info
from linebot import LineBot
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from fastapi import FastAPI, Request, Response, status
from dotenv import load_dotenv
import uvicorn

load_dotenv()

llm = Ollama(model="llama3.2", request_timeout=600, temperature=0.5)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
linebot = LineBot()
app = FastAPI()
user_topics = {}
user_youtube_transcripts = {}

build_restaurant_query_engine(llm=llm, embed_model=embed_model)

@app.post("/webhook")
async def callback(request: Request):
    """
    deal with the webhook from linebot

    Args:
        request (Request): HTTP request

    Returns:
        Response: HTTP response
    """
    body = await request.body()
    try:
        payload = linebot.extract_message(body=body)
        print(payload)

        user_id = payload["user_id"]
        group_id = payload["group_id"]
        message = payload["message"]
        reply_token = payload["reply_token"]

        if message == "選單" or message.strip().lower() == "menu":
            return Response(content="OK", status_code=status.HTTP_200_OK)
        
        if message.strip().lower() in set(["essay","youtube","restaurant"]):
            topic = None
            res = ""
            if message.strip().lower() == "essay":
                topic = "essay"
                res = "請提供論文關鍵字:\nPlease provide the keyword of the essay:"
            elif message.strip().lower() == "youtube":
                topic = "youtube"
                res = "請提供YouTube影片連結:\nPlease provide the YouTube video link:"
            elif message.strip().lower() == "restaurant":
                topic = "restaurant"
                res = "你想問什麼餐廳資訊嗎?\nWhat restaurant information would you like to ask?"
            
            user_topics[user_id] = topic
            linebot.reply_message(reply_token=reply_token, message=res)
            return Response(content="OK", status_code=status.HTTP_200_OK)
        
        if user_id not in user_topics:
            res = "請先輸入\"選單\"，來選擇主題(論文、YouTube、餐廳)\nPlease type \"menu\" to choose a topic (essay, YouTube, restaurant)"
            linebot.reply_message(reply_token=reply_token, message=res)
            return Response(content="OK", status_code=status.HTTP_200_OK)
        
        topic = user_topics[user_id]
        res = ""
        if topic == "essay":
            res = summarize_essay(query=message, llm=llm, embed_model=embed_model)
            del user_topics[user_id]
        elif topic == "youtube":
            if user_id not in user_youtube_transcripts:
                user_youtube_transcripts[user_id] = message
                res = build_youtube_query_engine(youtube_link=message, llm=llm, embed_model=embed_model)
                if res:
                    res += "\n請重新輸入：\nPlease re-enter:"
                    del user_youtube_transcripts[user_id]
                else:
                    res = "YouTube 影片連結已收到，請問您有什麼問題？(輸入\"結束\"以結束對話)\nYouTube video link received, what would you like to ask?(type \"end\" to end the conversation)"
            else:
                if message == "結束" or message.strip().lower() == "end":
                    clean_youtube_transcript_history()
                    res = "對話已結束，感謝您的使用！(輸入\"選單\"來開啟選單選擇主題)\nConversation ended, thank you for using!(type \"menu\" to open the menu to choose a topic)"
                    del user_topics[user_id]
                    del user_youtube_transcripts[user_id]
                else:
                    res = get_youtube_transcript_info(query=message)
        elif topic == "restaurant":
            res = get_restaurant_info(query=message)
            del user_topics[user_id]

        if res:
            linebot.reply_message(reply_token=reply_token, message=res)
        
        return Response(content="OK", status_code=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error handling webhook from linebot: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
