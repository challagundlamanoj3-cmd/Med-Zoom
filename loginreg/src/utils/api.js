// Utility file for API calls
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export const api = {
  // Auth endpoints
  login: `${API_BASE_URL}/login`,
  signup: `${API_BASE_URL}/signup`,
  sendOtp: `${API_BASE_URL}/send-otp`,
  getUser: `${API_BASE_URL}/user`,
  logout: `${API_BASE_URL}/logout`,
  health: `${API_BASE_URL}/health`
};

export default api;