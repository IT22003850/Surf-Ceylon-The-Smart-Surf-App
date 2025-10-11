import React, { createContext, useState } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [userPreferences, setUserPreferences] = useState({
    skillLevel: 'Beginner',
    minWaveHeight: 0.5,
    maxWaveHeight: 1.5,
    tidePreference: 'Any',
    boardType: 'Soft-top',
  });
  
  // --- THIS IS THE FIX ---
  // The 'value' prop now includes both the state (userPreferences)
  // and the function to update it (setUserPreferences).
  const value = { userPreferences, setUserPreferences };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};