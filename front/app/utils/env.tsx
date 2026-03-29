const BACKEND_PORT = process.env.NEXT_PUBLIC_BACKEND_PORT;
const AI_PORT = process.env.NEXT_PUBLIC_AI_PORT;

const BACKEND_HOST = typeof window === 'undefined' ? 'localhost' : window.location.hostname;
export const BACKEND_PREFIX = `http://${BACKEND_HOST}:${BACKEND_PORT}`
export const WS_BACKEND_PREFIX = `ws://${BACKEND_HOST}:${BACKEND_PORT}`
export const WS_AI_PREFIX = `ws://${BACKEND_HOST}:${AI_PORT}`