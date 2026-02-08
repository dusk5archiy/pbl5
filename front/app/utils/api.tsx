'use server'

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

export async function getApi(at: string, request: Object) {
  return async () => {
    try {
      const response = await fetchBackend(request, at);
      return response;
    }
    catch (error) {
      console.log("[-- ERROR --] Error:")
      console.log(error);
      throw error;
    }
  };
}


// ----------------------------------------------------------------------------

