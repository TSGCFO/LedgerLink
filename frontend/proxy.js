import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();

// Enable CORS for all requests
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  
  next();
});

// Proxy all requests to the Vite server
app.use('/', createProxyMiddleware({
  target: 'http://localhost:5176',
  changeOrigin: true,
  ws: true,
  onProxyReq: (proxyReq, req, res) => {
    // Add a host header that Vite will accept
    proxyReq.setHeader('Host', 'localhost');
  }
}));

// Start the proxy server on port 3000
const PORT = 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Proxy server running on port ${PORT}`);
});
