"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type ChatMessage = {
  id: number;
  sender: "user" | "bot" | "event";
  text: string;
};

type ServerMessage = {
  type: "bot" | "event";
  text: string;
  event?: string;
};

const WS_URL = "ws://127.0.0.1:8000/ws/chat";
const STREAM_URL = "http://127.0.0.1:8000/chat/stream";
const QUICK_COMMANDS = ["help", "list", "categories", "cheapest", "most expensive"];

type ChatBotProps = {
  // called when the server broadcasts a product change, so the page can refresh
  onProductEvent?: () => void;
};

export default function ChatBot({ onProductEvent }: ChatBotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [open, setOpen] = useState(true);
  const [streaming, setStreaming] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const nextIdRef = useRef(0);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  // keep the latest callback without reconnecting the socket when it changes
  const onProductEventRef = useRef(onProductEvent);

  useEffect(() => {
    onProductEventRef.current = onProductEvent;
  }, [onProductEvent]);

  function addMessage(sender: ChatMessage["sender"], text: string) {
    const id = nextIdRef.current++;
    setMessages((current) => [...current, { id, sender, text }]);
    return id;
  }

  // add streamed text to a message that is already on screen
  function appendToMessage(id: number, text: string) {
    setMessages((current) =>
      current.map((message) =>
        message.id === id ? { ...message, text: message.text + text } : message
      )
    );
  }

  // CONNECT WEBSOCKET
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      let data: ServerMessage;
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }

      if (data.type === "event") {
        addMessage("event", data.text);
        onProductEventRef.current?.();
      } else {
        addMessage("bot", data.text);
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  // AUTO SCROLL TO NEWEST MESSAGE
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, open]);

  // the bot's answer is streamed: read it piece by piece and show each piece right away
  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || streaming) return;

    addMessage("user", trimmed);
    setInput("");
    setStreaming(true);

    const botId = addMessage("bot", "");
    try {
      const response = await fetch(`${STREAM_URL}?message=${encodeURIComponent(trimmed)}`);
      if (!response.ok || !response.body) {
        throw new Error(`status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        appendToMessage(botId, decoder.decode(value, { stream: true }));
      }
    } catch {
      appendToMessage(botId, "Sorry, I couldn't reach the server.");
    } finally {
      setStreaming(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sendMessage(input);
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex w-80 flex-col items-end sm:w-96">
      {open && (
        <div className="mb-2 flex h-[28rem] w-full flex-col overflow-hidden rounded-lg border border-gray-600 bg-gray-900 text-white shadow-xl">
          <div className="flex items-center justify-between border-b border-gray-700 bg-gray-800 px-3 py-2">
            <span className="font-semibold">Product Bot</span>
            <span className="flex items-center gap-1 text-xs text-gray-300">
              <span
                className={`inline-block h-2 w-2 rounded-full ${
                  connected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              {connected ? "Online" : "Offline"}
            </span>
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto p-3 text-sm">
            {messages.map((message) =>
              message.sender === "event" ? (
                <p
                  key={message.id}
                  className="text-center text-xs italic text-yellow-300"
                >
                  {message.text}
                </p>
              ) : (
                <div
                  key={message.id}
                  className={`flex ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <p
                    className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 ${
                      message.sender === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-100"
                    }`}
                  >
                    {message.text}
                  </p>
                </div>
              )
            )}
            <div ref={bottomRef} />
          </div>

          <div className="flex flex-wrap gap-1 border-t border-gray-700 px-2 pt-2">
            {QUICK_COMMANDS.map((command) => (
              <button
                key={command}
                type="button"
                onClick={() => sendMessage(command)}
                disabled={!connected}
                className="rounded-full bg-gray-700 px-2 py-0.5 text-xs hover:bg-gray-600 disabled:opacity-50"
              >
                {command}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2 p-2">
            <input
              type="text"
              placeholder={connected ? "Ask about products..." : "Connecting..."}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              disabled={!connected}
              className="flex-1 rounded border border-gray-600 bg-gray-800 p-2 text-sm text-white placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={!connected || !input.trim()}
              className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="rounded-full bg-blue-600 px-4 py-2 text-white shadow-lg hover:bg-blue-700"
      >
        {open ? "Close chat" : "Chat with bot"}
      </button>
    </div>
  );
}
