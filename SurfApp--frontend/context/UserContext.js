import React, { createContext, useState } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  // Stores all preferences needed for Model 2 (Suitability Score)
  const [userPreferences, setUserPreferences] = useState({
    skillLevel: 'Beginner', 
    minWaveHeight: 0.5,      
    maxWaveHeight: 1.5,      
    tidePreference: 'Any',   
    boardType: 'Longboard',  
  }); 

  // Combined setter function
  const updatePreferences = (newPrefs) => {
    setUserPreferences(prev => ({ ...prev, ...newPrefs }));
  };

  return (
    <UserContext.Provider value={{ userPreferences, updatePreferences }}>
      {children}
    </UserContext.Provider>
  );
};