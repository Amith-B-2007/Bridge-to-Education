import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import { storage } from '../config/firebaseConfig';

// Upload file to Cloud Storage
export const uploadFile = async (file, folder = 'uploads') => {
  try {
    // Create a unique filename
    const timestamp = Date.now();
    const filename = `${timestamp}_${file.name}`;
    const storageRef = ref(storage, `${folder}/${filename}`);

    // Upload file
    const snapshot = await uploadBytes(storageRef, file);

    // Get download URL
    const downloadUrl = await getDownloadURL(snapshot.ref);
    return downloadUrl;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

// Upload resource (PDF, document, etc.)
export const uploadResource = async (file, subject, grade) => {
  try {
    const folder = `resources/${subject}/${grade}`;
    return uploadFile(file, folder);
  } catch (error) {
    console.error('Error uploading resource:', error);
    throw error;
  }
};

// Upload user avatar/profile picture
export const uploadProfilePicture = async (file, userId) => {
  try {
    const folder = `profiles/${userId}`;
    return uploadFile(file, folder);
  } catch (error) {
    console.error('Error uploading profile picture:', error);
    throw error;
  }
};

// Upload quiz attachments
export const uploadQuizAttachment = async (file, quizId) => {
  try {
    const folder = `quizzes/${quizId}`;
    return uploadFile(file, folder);
  } catch (error) {
    console.error('Error uploading quiz attachment:', error);
    throw error;
  }
};

// Upload doubt attachments
export const uploadDoubtAttachment = async (file, doubtId) => {
  try {
    const folder = `doubts/${doubtId}`;
    return uploadFile(file, folder);
  } catch (error) {
    console.error('Error uploading doubt attachment:', error);
    throw error;
  }
};

// Delete file from Cloud Storage
export const deleteFile = async (fileUrl) => {
  try {
    const fileRef = ref(storage, fileUrl);
    await deleteObject(fileRef);
  } catch (error) {
    console.error('Error deleting file:', error);
    throw error;
  }
};
