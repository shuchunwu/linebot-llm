# linebot-llm
```
. 
├── app.py
├── linebot.py
├── requirements.txt
├── essay/ 
│     ├── __init__.py
│     └── llm.py
├── restaurant/ 
│     ├── __init__.py
│     ├── data/ 
│     │     ├── blog.md
│     │     ├── google-map.json
│     │     └── faq.qa
│     ├── extractor.py
│     └── llm.py
├── youtube/ 
│     ├── __init__.py
│     └── llm.py
└── README.md
```
(English version is below)
-------------------------------------------------

# 專案簡介
這個專案是一個基於 FastAPI 的應用程式，整合了 LINE Bot 和多個 LLM（大語言模型）來處理不同主題的查詢，包括論文、YouTube 影片和餐廳資訊。使用者可以透過 LINE Bot 發送訊息，系統會根據使用者選擇的主題，使用相應的 LLM 來處理查詢並回覆結果。

## 主要流程架構
1. **啟動應用程式**
應用程式的入口是 [`app.py`](./app.py)，啟動 FastAPI 伺服器並初始化所需的模型和嵌入模型。

```python
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
```

2. **處理 LINE Bot Webhook**
當 LINE Bot 接收到訊息時，會觸發 [`/webhook`](./app.py) 路由，並由 `callback` 函數處理請求。

```python
@app.post("/webhook")
async def callback(request: Request):
    # 處理請求邏輯
```

3. **提取訊息**
使用 [`linebot.py`](./linebot.py)中的 `LineBot` 類別來提取訊息。

```python
payload = linebot.extract_message(body=body)
```

4. **主題選擇**
根據使用者的訊息，選擇相應的主題（論文、YouTube、餐廳）。

```python
if message.strip().lower() in set(["essay","youtube","restaurant"]):
    # 設定主題
```

5. **處理查詢**
根據選擇的主題，使用相應的 LLM 來處理查詢。

**論文查詢**

使用 [`llm.py`](./essay/llm.py) 中的 `summarize_essay` 函數來處理論文查詢。

```python
res = summarize_essay(query=message, llm=llm, embed_model=embed_model)
```

**YouTube 查詢**
使用 [`llm.py`](./youtube/llm.py) 中的 `build_youtube_query_engine` 和 `get_youtube_transcript_info` 函數來處理 YouTube 查詢。

```python
res = build_youtube_query_engine(youtube_link=message, llm=llm, embed_model=embed_model)
res = get_youtube_transcript_info(query=message)
```

**餐廳查詢**
使用 [`llm.py`](./restaurant/llm.py) 中的 `build_restaurant_query_engine` 和 `get_restaurant_info` 函數來處理餐廳查詢。

```python
res = get_restaurant_info(query=message)
```

6. **回覆訊息**
使用 [`linebot.py`](./linebot.py) 中的 `reply_message` 函數來回覆訊息。

```python
linebot.reply_message(reply_token=reply_token, message=res)
```

## 模組項目
我們使用python版本3.11.9。模組項目列在 [`requirements.txt`](./requirements.txt) 中，可以使用以下命令安裝：

```sh
pip install -r requirements.txt
```

## 資料處理
### FAQ 資料
FAQ 資料存儲在 [`faq.qa`](./restaurant/data/faq.qa) 中，使用 [`extractor.py`](./restaurant/extractor.py) 中的 `FaqExtractor` 類別來處理。

### 部落格資料
部落格資料存儲在 [`blog.md`](./restaurant/data/blog.md) 中，使用 [`extractor.py`](./restaurant/extractor.py) 中的 `BlogExtractor` 類別來處理。

### Google Map 資料
Google Map 資料存儲在 [`google-map.json`](./restaurant/data/google-map.json) 中，使用 [`extractor.py`](./restaurant/extractor.py) 中的 `GoogleMapExtractor` 類別來處理。

## 結論
這個專案整合了多個 LLM 來處理不同主題的查詢，並通過 LINE Bot 與使用者互動。整個流程從接收訊息、選擇主題、處理查詢到回覆訊息，實現了一個完整的查詢處理系統。

-------------------------------------------------

# Project Overview
This project is a FastAPI-based application that integrates LINE Bot and multiple LLMs (Large Language Models) to handle queries on different topics, including essays, YouTube videos, and restaurant information. Users can send messages via LINE Bot, and the system will process the query using the appropriate LLM based on the selected topic and reply with the result.

## Main Workflow Structure
1. **Start the Application**
   The entry point of the application is [`app.py`](./app.py), which starts the FastAPI server and initializes the required models and embedding models.

   ```python
   if __name__ == "__main__":
       uvicorn.run(app, host="127.0.0.1", port=3000)
    ```

2. **Handle LINE Bot Webhook** 
   When the LINE Bot receives a message, it triggers the [`/webhook`](./app.py) route, and the callback function handles the request.

```python
@app.post("/webhook")
async def callback(request: Request):
    # Request handling logic
```

3. **Extract Message** Use the `LineBot` class in [`linebot.py`](./linebot.py) to extract the message.

```python
payload = linebot.extract_message(body=body)
```

4. **Topic Selection** Based on the user's message, select the appropriate topic (essay, YouTube, restaurant).

```python
if message.strip().lower() in set(["essay", "youtube", "restaurant"]):
    # Set topic
```

5. **Process Query** Use the corresponding LLM to process the query based on the selected topic.

**Essay Query**

Use the `summarize_essay` function in [`llm.py`](./essay/llm.py) to process essay queries.

```python
res = summarize_essay(query=message, llm=llm, embed_model=embed_model)
```

**YouTube Query**

Use the `build_youtube_query_engine` and `get_youtube_transcript_info` functions in [`llm.py`](./youtube/llm.py) to process YouTube queries.

```python
res = build_youtube_query_engine(youtube_link=message, llm=llm, embed_model=embed_model)
res = get_youtube_transcript_info(query=message)
```

**Restaurant Query**

Use the `build_restaurant_query_engine` and `get_restaurant_info functions` in [`llm.py`](./restaurant/llm.py) to process restaurant queries.

```python
res = get_restaurant_info(query=message)
```

6. **Reply Message** Use the `reply_message` function in [`linebot.py`](./linebot.py) to reply to the message.

```python
linebot.reply_message(reply_token=reply_token, message=res)
```

## Dependencies
We usd python version 3.11.9. Dependencies are listed in [`requirements.txt`](./requirements.txt) and can be installed using the following command:

```sh
pip install -r requirements.txt
```

## Data Processing
### FAQ Data

FAQ data is stored in [`faq.qa`](./restaurant/data/faq.qa) and processed using the `FaqExtractor` class in [`extractor.py`](./restaurant/extractor.py).

### Blog Data

Blog data is stored in [`blog.md`](./restaurant/data/blog.md) and processed using the `BlogExtractor` class in [`extractor.py`](./restaurant/extractor.py).

### Google Map 資料

Google Map data is stored in [`google-map.json`](./restaurant/data/google-map.json) and processed using the `GoogleMapExtractor` class in [`extractor.py`](./restaurant/extractor.py).

## Conclusion
This project integrates multiple LLMs to handle queries on different topics and interacts with users through LINE Bot. The entire process, from receiving messages, selecting topics, processing queries to replying to messages, implements a complete query processing system. 
