async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

export function get(url) {
  return request(url);
}

export function post(url, body) {
  return request(url, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
