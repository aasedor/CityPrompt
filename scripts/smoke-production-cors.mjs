#!/usr/bin/env node

const API_ORIGIN = (process.env.PRODUCTION_API_ORIGIN || 'https://threed-platform-api.onrender.com').replace(/\/$/, '');
const FRONTEND_ORIGINS = (process.env.PRODUCTION_FRONTEND_ORIGINS || [
  'https://cityprompt.ca',
  'https://www.cityprompt.ca',
  'https://threed-platform-frontend.onrender.com',
].join(','))
  .split(',')
  .map((origin) => origin.trim().replace(/\/$/, ''))
  .filter(Boolean);

const ENDPOINTS = [
  { label: 'health', path: '/health', method: 'GET', preflight: false },
  { label: 'login', path: '/api/v1/auth/login', method: 'POST', headers: 'content-type' },
  { label: 'google oauth', path: '/api/v1/auth/oauth/google', method: 'GET' },
  { label: 'projects', path: '/api/v1/projects', method: 'GET', headers: 'authorization' },
  { label: 'render generate', path: '/api/v1/render/generate', method: 'POST', headers: 'authorization,content-type' },
];

function fail(message) {
  console.log(`FAIL ${message}`);
  process.exitCode = 1;
}

async function checkHealth(endpoint) {
  const response = await fetch(`${API_ORIGIN}${endpoint.path}`);
  if (!response.ok) {
    fail(`${endpoint.label}: expected 2xx from ${endpoint.path}, got ${response.status}`);
    return;
  }
  console.log(`PASS ${endpoint.label}: ${response.status}`);
}

async function checkPreflight(origin, endpoint) {
  const headers = {
    Origin: origin,
    'Access-Control-Request-Method': endpoint.method,
  };
  if (endpoint.headers) {
    headers['Access-Control-Request-Headers'] = endpoint.headers;
  }

  const response = await fetch(`${API_ORIGIN}${endpoint.path}`, {
    method: 'OPTIONS',
    headers,
  });

  const allowedOrigin = response.headers.get('access-control-allow-origin');
  if (!response.ok) {
    fail(`${endpoint.label}: ${origin} preflight returned ${response.status}`);
    return;
  }
  if (allowedOrigin !== origin) {
    fail(`${endpoint.label}: expected access-control-allow-origin ${origin}, got ${allowedOrigin || '(missing)'}`);
    return;
  }

  console.log(`PASS ${endpoint.label}: ${origin}`);
}

if (FRONTEND_ORIGINS.length === 0) {
  fail('No frontend origins configured');
} else {
  console.log(`API: ${API_ORIGIN}`);
  console.log(`Frontend origins: ${FRONTEND_ORIGINS.join(', ')}`);

  for (const endpoint of ENDPOINTS) {
    if (endpoint.preflight === false) {
      await checkHealth(endpoint);
      continue;
    }
    for (const origin of FRONTEND_ORIGINS) {
      await checkPreflight(origin, endpoint);
    }
  }
}
