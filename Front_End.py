# Front_End.py

import asyncio
import json
import gradio as gr
import websockets

WS_URL = "ws://localhost:8000/ws"

async def query_sky_ws(prompt: str):
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(prompt)
            raw = await ws.recv()
            try:
                data = json.loads(raw)
                return {"reply": data.get("reply", ""), "trace": data.get("trace", [])}
            except json.JSONDecodeError:
                return {"reply": raw, "trace": []}
    except Exception as e:
        return {"reply": f"❌ Connection error: {e}", "trace": []}

async def respond(prompt: str, history):
    if history is None:
        history = []

    # Append user turn
    history.append({"role": "user", "content": prompt})
    yield history

    # Get Sky’s reply + trace
    resp = await query_sky_ws(prompt)
    reply, trace = resp["reply"], resp["trace"]

    md = reply
    if trace:
        md += "\n\n<details><summary>⚙️ Trace</summary>\n\n"
        md += "```text\n" + "\n".join(trace) + "\n```\n"
        md += "</details>"

    history.append({"role": "assistant", "content": md})
    yield history

# Sample queries (populate the textbox, not history)
SAMPLES = [
    "What is the weather like in Frankfurt am Main?",
    "What is the weather forecast for tomorrow in Paris?",
    "How is the weather going to develop over the next few days in Berlin?"
]

# CSS: hide <img> in avatars, inject emojis instead
css = """
#chatbot .avatar-container img {
  display: none !important;
}
#chatbot .message-row.user .avatar-container::before {
  content: "👤";
  font-size: 24px;
  display: inline-block;
  line-height: 1;
}
#chatbot .message-row.bot .avatar-container::before {
  content: "☁️";
  font-size: 24px;
  display: inline-block;
  line-height: 1;
}
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("# 🌥️ Sky Weather Chatbot")

    # No images—just placeholders for the CSS emoji pseudo-elements
    chatbot = gr.Chatbot(
        label="Chat",
        type="messages",
        avatar_images=(None, None),
        elem_id="chatbot",
    )

    prompt = gr.Textbox(show_label=False, placeholder="Ask about the weather…")
    prompt.submit(respond, [prompt, chatbot], [chatbot])
    prompt.submit(lambda: "", None, prompt)

    gr.Markdown("**Sample Queries**")
    for q in SAMPLES:
        gr.Button(q).click(
            fn=lambda *_ , txt=q: txt,
            inputs=None,
            outputs=prompt,
            queue=False
        )

if __name__ == "__main__":
    demo.launch()
