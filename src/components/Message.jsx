// src/components/Message.jsx
import React from 'react';

import { FiUser, FiZap } from 'react-icons/fi';

const Message = ({ message }) => {
  const { text, sender, timestamp } = message;
  const isAI = sender === 'ai';

  const bubbleClasses = isAI
    ? 'bg-white text-on-background self-start'
    : 'bg-primary text-primary-foreground self-end';

  const containerClasses = isAI ? 'justify-start' : 'justify-end';

  const Avatar = isAI ? FiZap : FiUser;

  return (
    <div className={`flex items-end gap-2 animate-fade-in ${containerClasses}`}>
      {isAI && <Avatar className="text-primary" size={24} />}
      <div className={`max-w-md md:max-w-lg p-3 rounded-xl shadow-md ${bubbleClasses}`}>
        <p className="text-sm">{text}</p>
        <span className={`text-xs mt-1 block ${isAI ? 'text-gray-400' : 'text-primary-foreground/80'}`}>
          {timestamp}
        </span>
      </div>
      {!isAI && <Avatar className="text-gray-400" size={24} />}
    </div>
  );
};

export default Message;
