// src/components/Header.jsx
import React from 'react';
import { FiBell, FiUser, FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from 'next-themes';

const Header = () => {
  const { theme, setTheme } = useTheme();

  return (
    <header className="bg-primary text-primary-foreground shadow-md p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold">Meesho Mitra</h1>
      <div className="flex items-center space-x-4">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="hover:bg-primary/80 p-2 rounded-full transition-colors"
        >
          {theme === 'dark' ? <FiSun size={22} /> : <FiMoon size={22} />}
        </button>
        <button className="relative hover:bg-primary/80 p-2 rounded-full transition-colors">
          <FiBell size={22} />
          <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-secondary ring-2 ring-primary"></span>
        </button>
        <button className="hover:bg-primary/80 p-2 rounded-full transition-colors">
          <FiUser size={22} />
        </button>
      </div>
    </header>
  );
};

export default Header;
