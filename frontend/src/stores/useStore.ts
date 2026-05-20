// Zustand Store para estado global
import { create } from 'zustand';
import { User } from '../services/authService';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setAuthenticated: (value: boolean) => void;
  setLoading: (value: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create <AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setLoading: (isLoading) => set({ isLoading }),
  
  logout: () => set({ user: null, isAuthenticated: false }),
}));

interface SubmissionState {
  submissions: any[];
  currentSubmission: any | null;
  isLoading: boolean;
  setSubmissions: (submissions: any[]) => void;
  setCurrentSubmission: (submission: any) => void;
  setLoading: (value: boolean) => void;
  addSubmission: (submission: any) => void;
}

export const useSubmissionStore = create<SubmissionState>((set, get) => ({
  submissions: [],
  currentSubmission: null,
  isLoading: false,
  
  setSubmissions: (submissions) => set({ submissions }),
  setCurrentSubmission: (currentSubmission) => set({ currentSubmission }),
  setLoading: (isLoading) => set({ isLoading }),
  
  addSubmission: (submission) => {
    const current = get().submissions;
    set({ submissions: [submission, ...current] });
  },
}));
