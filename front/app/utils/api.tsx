import { BACKEND_PREFIX } from "@/app/utils/env";

// ----------------------------------------------------------------------------

export async function fetchBackend(request: any, at: string) {
  return await fetch(BACKEND_PREFIX + at, {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request)
  });
}

// ----------------------------------------------------------------------------

export function getApi(onError: (_?: any) => void, at: string, request: Object) {
  return async () => {
    try {
      const response = await fetchBackend(request, at);
      if (!response.ok) onError();
      return await response.json();
    }
    catch (error) {
      onError(error);
    }
  };
}


// ----------------------------------------------------------------------------

