import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth, API_BASE_URL } from './AuthContext';

const SyncContext = createContext();

// Helper to open IndexedDB
const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('sentinel_offline_db', 1);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending_assessments')) {
        db.createObjectStore('pending_assessments', { keyPath: 'local_id', autoIncrement: true });
      }
    };
    
    request.onsuccess = (event) => {
      resolve(event.target.result);
    };
    
    request.onerror = (event) => {
      reject(event.target.error);
    };
  });
};

export const SyncProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);
  const [syncStatus, setSyncStatus] = useState('SYNCED'); // SYNCED, OFFLINE, SYNCING
  const { token } = useAuth();

  // Listen to network status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setSyncStatus('SYNCING');
      syncPendingRecords();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus('OFFLINE');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial check
    updatePendingCount();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [token]);

  const updatePendingCount = async () => {
    try {
      const db = await openDB();
      const transaction = db.transaction('pending_assessments', 'readonly');
      const store = transaction.objectStore('pending_assessments');
      const countRequest = store.count();
      
      countRequest.onsuccess = () => {
        setPendingCount(countRequest.result);
        if (countRequest.result > 0) {
          if (navigator.onLine) {
            syncPendingRecords();
          } else {
            setSyncStatus('OFFLINE');
          }
        } else {
          setSyncStatus(navigator.onLine ? 'SYNCED' : 'OFFLINE');
        }
      };
    } catch (err) {
      console.error("IndexedDB error", err);
    }
  };

  const saveOfflineRecord = async (animalId, payload) => {
    try {
      const db = await openDB();
      const transaction = db.transaction('pending_assessments', 'readwrite');
      const store = transaction.objectStore('pending_assessments');
      
      const record = {
        animal_id: animalId,
        payload: payload,
        created_at: new Date().toISOString(),
        sync_status: 'PENDING'
      };
      
      store.add(record);
      
      transaction.oncomplete = () => {
        updatePendingCount();
        console.log("Offline health record saved successfully in IndexedDB.");
      };
    } catch (err) {
      console.error("Failed to save offline record", err);
    }
  };

  const getOfflineRecords = () => {
    return new Promise(async (resolve, reject) => {
      try {
        const db = await openDB();
        const transaction = db.transaction('pending_assessments', 'readonly');
        const store = transaction.objectStore('pending_assessments');
        const request = store.getAll();
        
        request.onsuccess = () => {
          resolve(request.result);
        };
        request.onerror = () => {
          reject(request.error);
        };
      } catch (err) {
        reject(err);
      }
    });
  };

  const syncPendingRecords = async () => {
    if (!navigator.onLine || !token) {
      return;
    }
    
    try {
      const db = await openDB();
      const transaction = db.transaction('pending_assessments', 'readwrite');
      const store = transaction.objectStore('pending_assessments');
      const request = store.getAll();
      
      request.onsuccess = async () => {
        const records = request.result;
        if (records.length === 0) {
          setSyncStatus('SYNCED');
          return;
        }
        
        setSyncStatus('SYNCING');
        
        for (const record of records) {
          try {
            const res = await fetch(`${API_BASE_URL}/api/assessment/submit/${record.animal_id}`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify(record.payload)
            });
            
            if (res.ok) {
              // Successfully synced, remove from IndexedDB
              const deleteTx = db.transaction('pending_assessments', 'readwrite');
              const deleteStore = deleteTx.objectStore('pending_assessments');
              deleteStore.delete(record.local_id);
            }
          } catch (syncErr) {
            console.error(`Failed to sync record ${record.local_id}`, syncErr);
          }
        }
        
        updatePendingCount();
      };
    } catch (err) {
      console.error("Sync error", err);
      setSyncStatus('FAILED');
    }
  };

  return (
    <SyncContext.Provider value={{ isOnline, pendingCount, syncStatus, saveOfflineRecord, getOfflineRecords, syncPendingRecords }}>
      {children}
    </SyncContext.Provider>
  );
};

export const useSync = () => useContext(SyncContext);
