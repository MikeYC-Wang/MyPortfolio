// import axios from 'axios';

const api = axios.create({

  baseURL: import.meta.env.PROD ? 'https://portfolio-api-a21d.onrender.com' : '',
  withCredentials: true,
});

export default api;