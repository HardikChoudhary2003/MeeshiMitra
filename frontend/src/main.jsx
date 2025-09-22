import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css'; // Imports the global styles and Tailwind CSS
import { ThemeProvider } from 'next-themes';

// This finds the <div id="root"></div> in your index.html
// and injects the entire React application into it.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
