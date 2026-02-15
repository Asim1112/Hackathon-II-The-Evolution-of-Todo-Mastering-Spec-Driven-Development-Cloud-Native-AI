import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

// Add error logging
const handler = toNextJsHandler(auth);

export const GET = async (req: Request) => {
  try {
    return await handler.GET(req);
  } catch (error) {
    console.error("[AUTH] GET Error:", error);
    return new Response(JSON.stringify({ error: "Authentication error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

export const POST = async (req: Request) => {
  try {
    return await handler.POST(req);
  } catch (error) {
    console.error("[AUTH] POST Error:", error);
    return new Response(JSON.stringify({ error: "Authentication error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};
