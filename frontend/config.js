// Local Live Server should use the backend running on this computer. The
// deployment workflow replaces this generated file with the public HTTPS URL.
window.FASHION_MANAGER_API_URL = ['localhost', '127.0.0.1'].includes(window.location.hostname)
  ? 'http://127.0.0.1:8000'
  : 'https://fashion-manager.onrender.com';
