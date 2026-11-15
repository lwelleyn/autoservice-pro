const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

// Turns a FastAPI error body into one readable line.
// `detail` is a string for HTTPException and an array of issues for 422.
function errorMessage(body, status) {
  const detail = body?.detail;
  if (typeof detail === 'string' && detail) return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((issue) => {
        const field = (issue.loc || []).filter((part) => part !== 'body').join('.');
        return field ? `${field}: ${issue.msg}` : issue.msg;
      })
      .join('; ');
  }
  return `Request failed with status ${status}`;
}

async function request(path, { method = 'GET', body } = {}) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error(`Cannot reach the server at ${API_URL}. Is the backend running?`);
  }

  // Error pages from a proxy may not be JSON at all.
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(errorMessage(data, res.status));
  return data;
}

function resource(path) {
  return {
    list: () => request(path),
    get: (id) => request(`${path}/${id}`),
    create: (data) => request(path, { method: 'POST', body: data }),
    update: (id, data) => request(`${path}/${id}`, { method: 'PUT', body: data }),
    remove: (id) => request(`${path}/${id}`, { method: 'DELETE' }),
  };
}

export const clientsApi = resource('/clients');
export const carsApi = resource('/cars');
export const workOrdersApi = resource('/work-orders');
