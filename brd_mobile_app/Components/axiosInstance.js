import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://172.20.10.4:5000',
  timeout: 1000000000000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

export default axiosInstance;