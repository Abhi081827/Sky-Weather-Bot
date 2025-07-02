
# 🌥️ Sky Weather Chatbot

A real-time AI-driven weather chatbot that streams current conditions and short-term forecasts over WebSockets using FastAPI, LangChain-Groq, and the OpenWeatherMap API. Users can ask up to 10 questions about temperature, sky conditions (sunny/cloudy), and wind speed (optional precipitation), and receive concise, friendly replies.

---

## 📋 Features

- **Real-time Chat** via WebSocket (`/ws`)  
- **Agent-Oriented Architecture** using LangChain-Groq  
- **Tool-Calling Pattern**: separate `OpenWeatherMapQuery` tool for geocoding, current weather, and forecast  
- **Traceable Reasoning**: “Thought → Action → Observation → Final Answer” callback logs  
- **Lightweight Front-End** in Gradio (or React) with sample-query buttons  
- **Modular Codebase**: clear separation of UI, backend, tools, and metadata  



---

## Prerequisites

* **Python** 3.9+
* API keys for:

  * [OpenWeatherMap](https://openweathermap.org/api)
  * [Groq Chat API](https://groq.dev)

---

## 📥 Installation & Setup

1. **Clone the repo**

   ```bash
   [git clone https://github.com/yourusername/weather-chatbot.git](https://github.com/Abhi081827/Sky-Weather-Bot.git)
   cd weather-chatbot
   ```

2. **Back-end**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows PowerShell
   pip install -r requirements.txt
   cp .env.example .env           # fill in your API keys
   ```

3. **Front-end**

   * **Gradio version**: no extra install, just:

     ```bash
     pip install gradio websockets
     ```


---

## 🚀 Running the Services

1. **Start FastAPI WebSocket Server**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Launch Front-end**

   * **Gradio**

     ```bash
     python Front_End.py
     # Opens at http://localhost:7860/
     ```

---

## 📁 Project Structure

```
weather-chatbot/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                    # FastAPI WebSocket server
├── prompts.py                 # System prompt & templates
├── tools/
│   └── openweathermap_query.py
├── agent/
│   └── setup_agent.py
├── utils/
│   └── location.py            # (optional IP→geo helper)
├── metadata/
│   └── store.py               # JSON session logs
└── Front_End.py               # Gradio chat UI
```

---

## 📚 References

* **OpenWeatherMap API**: [https://openweathermap.org/api](https://openweathermap.org/api)
* **LangChain Documentation**: [https://python.langchain.com](https://python.langchain.com)
* **Groq Chat API**: [https://groq.dev](https://groq.dev)
* **FastAPI**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* **Gradio**: [https://gradio.app/docs](https://gradio.app/docs)

---
