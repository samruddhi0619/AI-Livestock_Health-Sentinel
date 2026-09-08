// Centralized API Client for AI-Livestock Health Sentinel

export const API_BASE_URL = 'http://localhost:8000';

/**
 * Standardized HTTP fetch wrapper with authorization header, 
 * JSON & FormData handling, and unified error parsing.
 */
async function request(endpoint, options = {}) {
  const token = localStorage.getItem('sentinel_token');

  const headers = {
    ...options.headers,
  };

  // Add Authorization Bearer token if present
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Set Content-Type to application/json unless sending FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Handle 401 Unauthorized - Token Expired or Invalid
    if (response.status === 401) {
      // Clear token if unauthenticated
      localStorage.removeItem('sentinel_token');
      localStorage.removeItem('sentinel_user');
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register') && window.location.pathname !== '/') {
        window.location.href = '/login?expired=1';
      }
    }

    // Handle Non-2xx HTTP Errors
    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(d => d.msg || d.detail || JSON.stringify(d)).join('; ');
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // Response was not JSON
      }
      throw new Error(errorMessage);
    }

    // Parse JSON response
    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      throw new Error('Backend server is offline or unreachable. Please check backend connection at http://localhost:8000.');
    }
    throw error;
  }
}

// ---------------------------------------------------------------------------
// 1. Authentication API
// ---------------------------------------------------------------------------
export const authApi = {
  login: (credentials) => request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials)
  }),
  register: (userData) => request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),
  getMe: () => request('/api/auth/me', {
    method: 'GET'
  })
};

// ---------------------------------------------------------------------------
// 2. Livestock & Digital Passport API
// ---------------------------------------------------------------------------
export const animalsApi = {
  getAnimals: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/animals${query ? `?${query}` : ''}`, { method: 'GET' });
  },
  getAnimalById: (animalId) => request(`/api/animals/${animalId}`, { method: 'GET' }),
  registerAnimal: (animalData) => request('/api/animals', {
    method: 'POST',
    body: JSON.stringify(animalData)
  }),
  getPassport: (animalId) => request(`/api/animals/${animalId}/passport`, { method: 'GET' }),
  getQrCode: (qrToken) => request(`/api/animals/qr/${qrToken}`, { method: 'GET' })
};

// ---------------------------------------------------------------------------
// 3. Health Reports & Surveillance Map API
// ---------------------------------------------------------------------------
export const reportsApi = {
  submitHealthReport: (reportData) => request('/api/reports/health', {
    method: 'POST',
    body: JSON.stringify(reportData)
  }),
  getHealthReports: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/reports/health${query ? `?${query}` : ''}`, { method: 'GET' });
  },
  getHealthReportById: (reportId) => request(`/api/reports/health/${reportId}`, { method: 'GET' }),
  getSurveillanceMapData: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/reports/surveillance-map${query ? `?${query}` : ''}`, { method: 'GET' })
  }
};

// ---------------------------------------------------------------------------
// 4. ML Models & Multi-Modal Analysis API
// ---------------------------------------------------------------------------
export const analysisApi = {
  analyzeImage: (formDataOrObject) => {
    if (formDataOrObject instanceof FormData) {
      return request('/analysis/image', {
        method: 'POST',
        body: formDataOrObject
      });
    }
    return request('/analysis/image', {
      method: 'POST',
      body: JSON.stringify(formDataOrObject)
    });
  },
  analyzeSymptoms: (symptomData) => request('/analysis/symptoms', {
    method: 'POST',
    body: JSON.stringify(symptomData)
  }),
  analyzeEnvironment: (envData) => request('/analysis/environment', {
    method: 'POST',
    body: JSON.stringify(envData)
  }),
  analyzeMultiModal: (payload) => request('/analysis/multi-modal', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
};

// ---------------------------------------------------------------------------
// 5. Clinical Cases & Verification API
// ---------------------------------------------------------------------------
export const casesApi = {
  getCases: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/cases${query ? `?${query}` : ''}`, { method: 'GET' });
  },
  verifyCase: (caseId, payload) => request(`/api/cases/${caseId}/verify`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
};

// ---------------------------------------------------------------------------
// 6. Disease Clusters API (Haversine DBSCAN)
// ---------------------------------------------------------------------------
export const clustersApi = {
  getClusters: () => request('/api/clusters', { method: 'GET' }),
  getClusterById: (clusterId) => request(`/api/clusters/${clusterId}`, { method: 'GET' }),
  detectClusters: (params = {}) => request('/api/clusters/detect', {
    method: 'POST',
    body: JSON.stringify(params)
  })
};

// ---------------------------------------------------------------------------
// 7. Role-Specific Alerts API
// ---------------------------------------------------------------------------
export const alertsApi = {
  getAlerts: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/alerts${query ? `?${query}` : ''}`, { method: 'GET' });
  },
  getUnreadCount: () => request('/api/alerts/unread-count', { method: 'GET' }),
  markRead: (alertId) => request(`/api/alerts/${alertId}/read`, { method: 'POST' }),
  markAllRead: () => request('/api/alerts/read-all', { method: 'POST' }),
  dismissAlert: (alertId) => request(`/api/alerts/${alertId}/dismiss`, { method: 'POST' }),
  seedSamples: () => request('/api/alerts/seed-samples', { method: 'POST' })
};

export default {
  auth: authApi,
  animals: animalsApi,
  reports: reportsApi,
  analysis: analysisApi,
  cases: casesApi,
  clusters: clustersApi,
  alerts: alertsApi
};
