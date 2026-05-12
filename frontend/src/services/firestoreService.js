import {
  collection,
  addDoc,
  query,
  where,
  orderBy,
  onSnapshot,
  updateDoc,
  deleteDoc,
  doc,
  getDocs,
  getDoc,
  Timestamp,
  limit,
  startAfter,
  writeBatch,
  increment,
} from 'firebase/firestore';
import { db } from '../config/firebaseConfig';

// ============ DOUBTS/CHAT SERVICES ============

// Create a new doubt
export const createDoubt = async (studentId, studentName, subject, title, description, attachmentUrl = null) => {
  try {
    const docRef = await addDoc(collection(db, 'doubts'), {
      studentId,
      studentName,
      subject,
      title,
      description,
      attachmentUrl,
      status: 'open', // open, resolved, closed
      createdAt: Timestamp.now(),
      updatedAt: Timestamp.now(),
      replies: [],
      resolved: false,
    });
    return docRef.id;
  } catch (error) {
    console.error('Error creating doubt:', error);
    throw error;
  }
};

// Get doubts with real-time listener
export const subscribeToDoubts = (filters = {}, callback) => {
  try {
    let q = collection(db, 'doubts');
    const conditions = [];

    if (filters.studentId) {
      conditions.push(where('studentId', '==', filters.studentId));
    }
    if (filters.subject) {
      conditions.push(where('subject', '==', filters.subject));
    }
    if (filters.status) {
      conditions.push(where('status', '==', filters.status));
    }

    if (conditions.length > 0) {
      q = query(
        collection(db, 'doubts'),
        ...conditions,
        orderBy('createdAt', 'desc')
      );
    } else {
      q = query(collection(db, 'doubts'), orderBy('createdAt', 'desc'));
    }

    return onSnapshot(q, (snapshot) => {
      const doubts = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(doubts);
    });
  } catch (error) {
    console.error('Error subscribing to doubts:', error);
    throw error;
  }
};

// Add reply to doubt
export const addDoubtReply = async (doubtId, userId, userName, reply, attachmentUrl = null) => {
  try {
    const doubtRef = doc(db, 'doubts', doubtId);
    const doubtDoc = await getDoc(doubtRef);

    if (doubtDoc.exists()) {
      const replies = doubtDoc.data().replies || [];
      replies.push({
        userId,
        userName,
        reply,
        attachmentUrl,
        timestamp: Timestamp.now(),
      });

      await updateDoc(doubtRef, {
        replies,
        updatedAt: Timestamp.now(),
      });
    }
  } catch (error) {
    console.error('Error adding doubt reply:', error);
    throw error;
  }
};

// Update doubt status
export const updateDoubtStatus = async (doubtId, status, resolved = false) => {
  try {
    await updateDoc(doc(db, 'doubts', doubtId), {
      status,
      resolved,
      updatedAt: Timestamp.now(),
    });
  } catch (error) {
    console.error('Error updating doubt status:', error);
    throw error;
  }
};

// ============ RESOURCES SERVICES ============

// Upload resource metadata to Firestore
export const createResource = async (title, description, subject, grade, resourceUrl, resourceType = 'pdf') => {
  try {
    const docRef = await addDoc(collection(db, 'resources'), {
      title,
      description,
      subject,
      grade,
      resourceUrl,
      resourceType, // pdf, video, image, document
      uploadedAt: Timestamp.now(),
      downloads: 0,
      rating: 0,
      reviews: [],
    });
    return docRef.id;
  } catch (error) {
    console.error('Error creating resource:', error);
    throw error;
  }
};

// ============ QUIZ SERVICES ============

// Create quiz
export const createQuiz = async (title, description, subject, grade, questions, timeLimit = 30) => {
  try {
    const docRef = await addDoc(collection(db, 'quizzes'), {
      title,
      description,
      subject,
      grade,
      questions, // Array of { question, options, correctAnswer, explanation }
      timeLimit,
      createdAt: Timestamp.now(),
      attempts: 0,
      averageScore: 0,
    });
    return docRef.id;
  } catch (error) {
    console.error('Error creating quiz:', error);
    throw error;
  }
};

// Get quizzes
export const subscribeToQuizzes = (filters = {}, callback) => {
  try {
    const conditions = [];

    if (filters.subject) {
      conditions.push(where('subject', '==', filters.subject));
    }
    if (filters.grade) {
      conditions.push(where('grade', '==', filters.grade));
    }

    let q;
    if (conditions.length > 0) {
      q = query(
        collection(db, 'quizzes'),
        ...conditions,
        orderBy('createdAt', 'desc')
      );
    } else {
      q = query(collection(db, 'quizzes'), orderBy('createdAt', 'desc'));
    }

    return onSnapshot(q, (snapshot) => {
      const quizzes = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(quizzes);
    });
  } catch (error) {
    console.error('Error subscribing to quizzes:', error);
    throw error;
  }
};

export const getQuizById = async (quizId) => {
  try {
    const quizRef = doc(db, 'quizzes', quizId);
    const quizDoc = await getDoc(quizRef);
    if (!quizDoc.exists()) return null;
    return { id: quizDoc.id, ...quizDoc.data() };
  } catch (error) {
    console.error('Error fetching quiz:', error);
    throw error;
  }
};

export const getResourcesByFilters = async (filters = {}) => {
  try {
    const conditions = [];
    if (filters.subject) conditions.push(where('subject', '==', filters.subject));
    if (filters.grade) conditions.push(where('grade', '==', filters.grade));
    if (filters.resourceType) conditions.push(where('resourceType', '==', filters.resourceType));

    let q;
    if (conditions.length > 0) {
      q = query(collection(db, 'resources'), ...conditions, orderBy('uploadedAt', 'desc'));
    } else {
      q = query(collection(db, 'resources'), orderBy('uploadedAt', 'desc'));
    }

    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error('Error fetching resources:', error);
    throw error;
  }
};

export const subscribeToResources = (filters = {}, callback) => {
  try {
    const conditions = [];

    if (filters.subject) {
      conditions.push(where('subject', '==', filters.subject));
    }
    if (filters.grade) {
      conditions.push(where('grade', '==', filters.grade));
    }
    if (filters.resourceType) {
      conditions.push(where('resourceType', '==', filters.resourceType));
    }

    let q;
    if (conditions.length > 0) {
      q = query(
        collection(db, 'resources'),
        ...conditions,
        orderBy('uploadedAt', 'desc')
      );
    } else {
      q = query(collection(db, 'resources'), orderBy('uploadedAt', 'desc'));
    }

    return onSnapshot(q, (snapshot) => {
      const resources = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(resources);
    });
  } catch (error) {
    console.error('Error subscribing to resources:', error);
    throw error;
  }
};

// Record quiz attempt
export const recordQuizAttempt = async (quizId, studentId, studentName, score, totalQuestions, timeSpent) => {
  try {
    await addDoc(collection(db, 'quizAttempts'), {
      quizId,
      studentId,
      studentName,
      score,
      totalQuestions,
      percentage: (score / totalQuestions) * 100,
      timeSpent,
      attemptedAt: Timestamp.now(),
    });

    // Update quiz stats and student progress
    const quizRef = doc(db, 'quizzes', quizId);
    const quizDoc = await getDoc(quizRef);
    if (quizDoc.exists()) {
      const currentAttempts = quizDoc.data().attempts || 0;
      const currentAverage = quizDoc.data().averageScore || 0;
      const newAttempts = currentAttempts + 1;
      const newAverage = ((currentAverage * currentAttempts) + (score / totalQuestions) * 100) / newAttempts;

      await updateDoc(quizRef, {
        attempts: newAttempts,
        averageScore: newAverage,
      });

      if (quizDoc.data().subject) {
        await recordStudentProgress(
          studentId,
          quizDoc.data().subject,
          quizDoc.data().title || 'Quiz',
          Math.round((score / totalQuestions) * 100),
          Timestamp.now()
        );
      }
    }
  } catch (error) {
    console.error('Error recording quiz attempt:', error);
    throw error;
  }
};

// ============ NOTIFICATIONS SERVICES ============

// Create notification
export const createNotification = async (userId, title, message, type = 'info', actionUrl = null) => {
  try {
    await addDoc(collection(db, 'notifications'), {
      userId,
      title,
      message,
      type, // info, success, warning, error, alert
      actionUrl,
      read: false,
      createdAt: Timestamp.now(),
    });
  } catch (error) {
    console.error('Error creating notification:', error);
    throw error;
  }
};

// Get user notifications
export const subscribeToNotifications = (userId, callback) => {
  try {
    const q = query(
      collection(db, 'notifications'),
      where('userId', '==', userId),
      orderBy('createdAt', 'desc'),
      limit(50)
    );

    return onSnapshot(q, (snapshot) => {
      const notifications = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(notifications);
    });
  } catch (error) {
    console.error('Error subscribing to notifications:', error);
    throw error;
  }
};

// Mark notification as read
export const markNotificationAsRead = async (notificationId) => {
  try {
    await updateDoc(doc(db, 'notifications', notificationId), {
      read: true,
    });
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};

// ============ PROGRESS TRACKING SERVICES ============

// Record student progress
export const recordStudentProgress = async (studentId, subject, topic, progress, lastUpdated) => {
  try {
    const progressRef = collection(db, 'studentProgress');
    const q = query(
      progressRef,
      where('studentId', '==', studentId),
      where('subject', '==', subject),
      where('topic', '==', topic)
    );

    const existingDocs = await getDocs(q);

    if (existingDocs.empty) {
      await addDoc(progressRef, {
        studentId,
        subject,
        topic,
        progress,
        lastUpdated: Timestamp.now(),
      });
    } else {
      const docId = existingDocs.docs[0].id;
      await updateDoc(doc(db, 'studentProgress', docId), {
        progress,
        lastUpdated: Timestamp.now(),
      });
    }
  } catch (error) {
    console.error('Error recording student progress:', error);
    throw error;
  }
};

// Get student progress
export const subscribeToStudentProgress = (studentId, callback) => {
  try {
    const q = query(
      collection(db, 'studentProgress'),
      where('studentId', '==', studentId)
    );

    return onSnapshot(q, (snapshot) => {
      const progress = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(progress);
    });
  } catch (error) {
    console.error('Error subscribing to student progress:', error);
    throw error;
  }
};

// ============ CHAT/MESSAGING SERVICES ============

// Create chat room for doubt/session
export const createChatRoom = async (participantIds, roomName, roomType = 'doubt') => {
  try {
    const docRef = await addDoc(collection(db, 'chatRooms'), {
      participantIds,
      roomName,
      roomType, // doubt, session, group
      createdAt: Timestamp.now(),
      lastMessageTime: Timestamp.now(),
      lastMessage: '',
      messageCount: 0,
    });
    return docRef.id;
  } catch (error) {
    console.error('Error creating chat room:', error);
    throw error;
  }
};

// Send message in chat room
export const sendChatMessage = async (roomId, senderId, senderName, message, attachmentUrl = null) => {
  try {
    // Add message to subcollection
    await addDoc(collection(db, 'chatRooms', roomId, 'messages'), {
      senderId,
      senderName,
      message,
      attachmentUrl,
      timestamp: Timestamp.now(),
      read: false,
    });

    // Update chat room metadata
    await updateDoc(doc(db, 'chatRooms', roomId), {
      lastMessageTime: Timestamp.now(),
      lastMessage: message.substring(0, 50),
      messageCount: increment(1),
    });
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

// Listen to chat messages in real-time
export const subscribeToChatMessages = (roomId, callback) => {
  try {
    const q = query(
      collection(db, 'chatRooms', roomId, 'messages'),
      orderBy('timestamp', 'asc')
    );

    return onSnapshot(q, (snapshot) => {
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
      }));
      callback(messages);
    });
  } catch (error) {
    console.error('Error subscribing to chat messages:', error);
    throw error;
  }
};

