// User data storage utility for localStorage
export interface UserPreferences {
  interests: string[];
  strengths: string[];
  savedAt: string;
}

const USER_PREFS_KEY = "synapsis_user_preferences";

export const userStorage = {
  // Save user preferences to localStorage
  savePreferences: (interests: string[], strengths: string[]): void => {
    const prefs: UserPreferences = {
      interests,
      strengths,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(USER_PREFS_KEY, JSON.stringify(prefs));
    console.log("User preferences saved:", prefs);
  },

  // Retrieve user preferences from localStorage
  getPreferences: (): UserPreferences | null => {
    const stored = localStorage.getItem(USER_PREFS_KEY);
    if (!stored) return null;
    try {
      return JSON.parse(stored);
    } catch (e) {
      console.error("Failed to parse stored preferences:", e);
      return null;
    }
  },

  // Clear user preferences
  clearPreferences: (): void => {
    localStorage.removeItem(USER_PREFS_KEY);
    console.log("User preferences cleared");
  },

  // Export preferences as text (for debugging/export)
  exportAsText: (): string => {
    const prefs = userStorage.getPreferences();
    if (!prefs) return "No preferences saved";
    return `
Interests: ${prefs.interests.join(", ")}
Strengths: ${prefs.strengths.join(", ")}
Saved at: ${prefs.savedAt}
    `.trim();
  },
};
