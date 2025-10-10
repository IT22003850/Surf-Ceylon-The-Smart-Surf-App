import React, { createContext, useState } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  // We use a single state object to store all user preferences, 
  // replacing the simple skillLevel state.
  const [userPreferences, setUserPreferences] = useState({
    skillLevel: 'Beginner', // 1. Beginner, Intermediate, Advanced (Current Feature)
    minWaveHeight: 0.5,      // 2. Minimum desired wave height (New Preference)
    maxWaveHeight: 1.5,      // 3. Maximum desired wave height (New Preference)
    tidePreference: 'Any',   // 4. Preferred tide (High, Low, Mid, Any) (New Preference)
    boardType: 'Longboard',  // 5. Board Type (affects wave type suitability) (New Preference)
    // In a real app, this might also contain a unique userId and auth token
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
