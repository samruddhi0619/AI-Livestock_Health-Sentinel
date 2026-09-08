import React, { createContext, useState, useContext, useEffect } from 'react';
import en from '../locales/en.json';
import mr from '../locales/mr.json';

const LanguageContext = createContext();

const translations = {
  en,
  mr
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem('sentinel_lang') || 'en';
  });

  const setLanguage = (lang) => {
    localStorage.setItem('sentinel_lang', lang);
    setLanguageState(lang);
  };

  const t = (key) => {
    const localeData = translations[language] || en;
    return localeData[key] || en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
