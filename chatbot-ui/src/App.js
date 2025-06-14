import React, { useState } from "react";

export default function App() {
  const [username, setUsername] = useState("");
  const [inputName, setInputName] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);

  const handleLogin = async () => {
    if (!inputName.trim()) return;
    setUsername(inputName);

    // Auto-register for now (simplified)
    await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: inputName,
        name: inputName,
        education: "Not specified",
        business: "None",
        interests: "General",
      }),
    });

    setRegistered(true);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          message: input,
        }),
      });

      const data = await response.json();
      const botMessage = { sender: "bot", text: data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      alert("Something went wrong. Check if Flask server is running.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (!registered) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Welcome to Gemini AI</h2>
        <p>Enter a username to begin chatting:</p>
        <input
          type="text"
          value={inputName}
          onChange={(e) => setInputName(e.target.value)}
          style={{ padding: 8, fontSize: 16 }}
        />
        <button onClick={handleLogin} style={{ marginLeft: 10, padding: 8 }}>
          Start Chat
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Hello {username} 👋</h2>
      <div style={{ maxHeight: "300px", overflowY: "auto", border: "1px solid #ccc", padding: 10 }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
            <p><strong>{msg.sender}:</strong> {msg.text}</p>
          </div>
        ))}
        {loading && <p>Typing...</p>}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        style={{ width: "80%", marginTop: 10 }}
      />
      <button onClick={handleSend} disabled={loading} style={{ marginLeft: 10 }}>
        Send
      </button>
    </div>
  );
}






