'use server'

import { BACKEND_PREFIX } from "@/app/utils/env";

// ----------------------------------------------------------------------------

export async function callApi(at: string, request: Object) {
  try {
    const response = await fetch(BACKEND_PREFIX + at, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });
    return await response.json();
  }
  catch (error) {
    console.log("[-- ERROR --] Error:")
    console.log(error);
    throw error;
  }
}


// ----------------------------------------------------------------------------

