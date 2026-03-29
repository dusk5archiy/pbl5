const BACKEND_PORT = process.env.NEXT_PUBLIC_BACKEND_PORT;
const AI_PORT = process.env.NEXT_PUBLIC_AI_PORT;
export const BACKEND_PREFIX = `http://localhost:${BACKEND_PORT}`
export const WS_BACKEND_PREFIX = `ws://localhost:${BACKEND_PORT}`
export const WS_AI_PREFIX = `ws://localhost:${AI_PORT}`