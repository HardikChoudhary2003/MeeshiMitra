// src/components/ChatInput.jsx
import React, { useState, useEffect, useRef } from 'react';
import { FiMic, FiSend } from 'react-icons/fi';

const ChatInput = ({ onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // Setup Speech Recognition on component mount
  useEffect(() => {
    // Check if the browser supports the Web Speech API
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      console.error("This browser doesn't support SpeechRecognition.");
      // Optionally, disable the mic button here
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false; // Set to false to automatically stop when the user stops speaking
    recognition.interimResults = true; // Show interim results as the user speaks
    recognition.lang = 'en-US'; // Set language

    recognitionRef.current = recognition;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    // Process the speech recognition results
    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // CHANGED: Update the input value directly with the final or interim transcript
      setInputValue(finalTranscript || interimTranscript);
    };
  }, []); // Empty dependency array ensures this runs only once

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleMicClick = () => {
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
    } else {
      setInputValue(''); // Clear input before starting a new recognition
      recognition.start();
    }
  };

  // Your JSX with added visual feedback for the mic button
  return (
    <footer className="bg-white p-4 border-t border-gray-200">
      <form onSubmit={handleSubmit} className="flex items-center space-x-3">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask me anything or hold the mic to speak..."
          className="flex-1 w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          type="button"
          onClick={handleMicClick}
          // ADDED: Dynamic styling for visual feedback while listening
          className={`p-3 rounded-full transition-colors duration-200 ${
            isListening
              ? 'bg-red-500 text-white animate-pulse'
              : 'text-gray-500 hover:text-purple-600 hover:bg-purple-100'
          }`}
        >
          <FiMic size={22} />
        </button>
        <button
          type="submit"
          className="p-3 bg-purple-600 text-white rounded-full hover:bg-purple-700 disabled:bg-purple-300 transition-colors duration-200"
          disabled={!inputValue.trim()}
        >
          <FiSend size={22} />
        </button>
      </form>
    </footer>
  );
};

export default ChatInput;