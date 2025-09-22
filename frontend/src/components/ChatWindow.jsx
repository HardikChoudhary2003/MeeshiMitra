import React, { useEffect, useRef } from 'react';

import Message from './Message';



import { FiZap } from 'react-icons/fi';



const TypingIndicator = () => (

  <div className="flex items-end gap-2 justify-start animate-fade-in">

    <FiZap className="text-primary" size={24} />

    <div className="bg-background text-on-background p-3 rounded-xl shadow-md">

      <div className="flex items-center space-x-1">

        <span className="h-2 w-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></span>

        <span className="h-2 w-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></span>

        <span className="h-2 w-2 bg-primary rounded-full animate-bounce"></span>

      </div>

    </div>

  </div>

);



const ChatWindow = ({ messages, isTyping }) => {

  const chatEndRef = useRef(null);



  // Auto-scroll to the latest message

  useEffect(() => {

    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  }, [messages, isTyping]);



  return (

    <main className="flex-1 overflow-y-auto p-6 space-y-4 bg-background">

      {messages.map((msg) => (

        <Message key={msg.id} message={msg} />

      ))}

      {isTyping && <TypingIndicator />}

      <div ref={chatEndRef} />

    </main>

  );

};



export default ChatWindow;