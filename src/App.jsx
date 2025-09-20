// src/App.jsx
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import SearchResults from './components/SearchResults';

function App() {
  const [messages, setMessages] = useState([
  {
    id: 1,
    text: "Hi! I'm Meesho Mitra, your AI shopping assistant. Tell me what you're looking for!",
    sender: 'ai',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  },
]);
  const [isTyping, setIsTyping] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  const handleSendMessage = async (text) => {
    const newMessage = {
      id: messages.length + 1,
      text,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
    setIsTyping(true);
    setSearchResults([]); // Clear previous results

    try {
      const response = await fetch(`http://localhost:5000/search?q=${encodeURIComponent(text)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const results = await response.json();
      
      const aiResponse = {
        id: messages.length + 2,
        text: results.length > 0 ? `I found these results for "${text}":` : `I couldn't find any results for "${text}". Try another search!`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prevMessages => [...prevMessages, aiResponse]);
      setSearchResults(results);

    } catch (error) {
      console.error("Failed to fetch search results:", error);
      const errorResponse = {
        id: messages.length + 2,
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prevMessages => [...prevMessages, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background text-on-background font-sans">
      <Header />
      <div className="flex-1 overflow-y-auto">
        <ChatWindow messages={messages} isTyping={isTyping} />
        {searchResults.length > 0 && <SearchResults results={searchResults} />}
      </div>
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default App;
