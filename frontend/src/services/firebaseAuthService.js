import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  setPersistence,
  browserLocalPersistence,
} from 'firebase/auth';
import { auth } from '../config/firebaseConfig';

// Sign Up
export const firebaseSignUp = async (email, password, displayName, role = 'student') => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Update profile with display name
    await updateProfile(user, {
      displayName: displayName,
    });

    // Store additional user data in localStorage
    localStorage.setItem(`user_${user.uid}_role`, role);
    localStorage.setItem(`user_${user.uid}_profile`, JSON.stringify({
      uid: user.uid,
      email: user.email,
      displayName: displayName,
      role: role,
      createdAt: new Date().toISOString(),
    }));

    return {
      uid: user.uid,
      email: user.email,
      displayName: displayName,
      role: role,
    };
  } catch (error) {
    console.error('Sign up error:', error);
    throw error;
  }
};

// Sign In
export const firebaseSignIn = async (email, password) => {
  try {
    await setPersistence(auth, browserLocalPersistence);
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    const role = localStorage.getItem(`user_${user.uid}_role`) || 'student';
    const userData = {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      role: role,
    };

    localStorage.setItem('currentUser', JSON.stringify(userData));
    return userData;
  } catch (error) {
    console.error('Sign in error:', error);
    throw error;
  }
};

// Sign Out
export const firebaseSignOut = async () => {
  try {
    await signOut(auth);
    localStorage.removeItem('currentUser');
  } catch (error) {
    console.error('Sign out error:', error);
    throw error;
  }
};

// Auth State Listener
export const onAuthChange = (callback) => {
  return onAuthStateChanged(auth, (user) => {
    if (user) {
      const role = localStorage.getItem(`user_${user.uid}_role`) || 'student';
      const userData = {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        role: role,
        photoURL: user.photoURL,
      };
      localStorage.setItem('currentUser', JSON.stringify(userData));
      callback(userData);
    } else {
      localStorage.removeItem('currentUser');
      callback(null);
    }
  });
};

// Get Current User
export const getCurrentUser = () => {
  const currentUser = localStorage.getItem('currentUser');
  return currentUser ? JSON.parse(currentUser) : null;
};

// Get Current Firebase User
export const getCurrentFirebaseUser = () => {
  return auth.currentUser;
};
