// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src (AuthContext.js)
// Date: 2026-05-15
// ---------------------------------------------------------------------------
import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

// Function: AuthProvider
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const mockProfiles = [
    { id: 'good', name: 'Alice', score: 785, label: 'Alice - Good Credit Score (785)' },
    { id: 'bad', name: 'Bob', score: 540, label: 'Bob - Bad Credit Score (540)' }
  ];

  // Function: login
  const login = (profileId) => {
    const selected = mockProfiles.find(p => p.id === profileId);
    setUser(selected);
  };

  // Function: resetSelection
  const resetSelection = () => setUser(null);

  // Clears the mock local session (selected persona). Used by Logout so the
  // module's own local auth state is reset before redirecting to the portal.
  // Function: logout
  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, resetSelection, logout, mockProfiles }}>
      {children}
    </AuthContext.Provider>
  );
};

// Function: useAuth
export const useAuth = () => useContext(AuthContext);