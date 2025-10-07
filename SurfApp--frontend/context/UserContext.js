import React, { createContext, useState } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  // --- FIX IS HERE (removed extra text) ---
  const [skillLevel, setSkillLevel] = useState('Beginner'); 

  return (
    <UserContext.Provider value={{ skillLevel, setSkillLevel }}>
      {children}
    </UserContext.Provider>
  );
};