const DB_NAME = 'RuralShikshaDB';
const DB_VERSION = 1;

class DB {
  constructor() {
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // resources store
        if (!db.objectStoreNames.contains('resources')) {
          const resourceStore = db.createObjectStore('resources', {
            keyPath: 'id'
          });
          resourceStore.createIndex('grade', 'grade', { unique: false });
          resourceStore.createIndex('subject', 'subject', { unique: false });
          resourceStore.createIndex('chapter', 'chapter', { unique: false });
          resourceStore.createIndex('grade_subject',
            ['grade', 'subject'], { unique: false });
        }

        // quizzes store
        if (!db.objectStoreNames.contains('quizzes')) {
          const quizStore = db.createObjectStore('quizzes', {
            keyPath: 'id'
          });
          quizStore.createIndex('grade_subject',
            ['grade', 'subject'], { unique: false });
          quizStore.createIndex('chapter', 'chapter', { unique: false });
        }

        // quiz_attempts store
        if (!db.objectStoreNames.contains('quiz_attempts')) {
          const attemptStore = db.createObjectStore('quiz_attempts', {
            keyPath: 'id'
          });
          attemptStore.createIndex('timestamp', 'timestamp',
            { unique: false });
          attemptStore.createIndex('quiz_id', 'quiz_id',
            { unique: false });
        }

        // tutor_sessions store
        if (!db.objectStoreNames.contains('tutor_sessions')) {
          const tutorStore = db.createObjectStore('tutor_sessions', {
            keyPath: 'id'
          });
          tutorStore.createIndex('created_at', 'created_at',
            { unique: false });
        }

        // pending_actions store
        if (!db.objectStoreNames.contains('pending_actions')) {
          db.createObjectStore('pending_actions', {
            keyPath: 'id',
            autoIncrement: true
          });
        }
      };
    });
  }

  async add(storeName, data) {
    const tx = this.db.transaction([storeName], 'readwrite');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.add(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async put(storeName, data) {
    const tx = this.db.transaction([storeName], 'readwrite');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.put(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async get(storeName, key) {
    const tx = this.db.transaction([storeName], 'readonly');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getAll(storeName) {
    const tx = this.db.transaction([storeName], 'readonly');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getByIndex(storeName, indexName, value) {
    const tx = this.db.transaction([storeName], 'readonly');
    const store = tx.objectStore(storeName);
    const index = store.index(indexName);
    return new Promise((resolve, reject) => {
      const request = index.getAll(value);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async delete(storeName, key) {
    const tx = this.db.transaction([storeName], 'readwrite');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.delete(key);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clear(storeName) {
    const tx = this.db.transaction([storeName], 'readwrite');
    const store = tx.objectStore(storeName);
    return new Promise((resolve, reject) => {
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async saveResources(resources) {
    for (const resource of resources) {
      await this.put('resources', resource);
    }
  }

  async getResourcesByGradeSubject(grade, subject) {
    return this.getByIndex('resources', 'grade_subject', [grade, subject]);
  }

  async saveQuizzesForGrade(grade, quizzes) {
    for (const quiz of quizzes) {
      quiz.grade = grade;
      await this.put('quizzes', quiz);
    }
  }

  async getQuizzesByGradeSubject(grade, subject) {
    return this.getByIndex('quizzes', 'grade_subject', [grade, subject]);
  }

  async savePendingAction(action) {
    return this.add('pending_actions', {
      ...action,
      created_at: new Date().toISOString(),
      retries: 0
    });
  }

  async getPendingActions() {
    return this.getAll('pending_actions');
  }

  async clearPendingAction(id) {
    return this.delete('pending_actions', id);
  }

  async updatePendingAction(id, updates) {
    const action = await this.get('pending_actions', id);
    if (action) {
      await this.put('pending_actions', { ...action, ...updates });
    }
  }
}

export default new DB();
