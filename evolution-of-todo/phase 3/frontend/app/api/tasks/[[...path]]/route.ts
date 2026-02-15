import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth-server";

// Helper function to forward requests to FastAPI backend
async function forwardToBackend(request: NextRequest) {
  // Get session to validate user is authenticated
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  // Get the path segments to construct the proper backend URL
  const url = new URL(request.url);
  const pathSegments = url.pathname.split('/api/tasks')[1]; // Get everything after /api/tasks
  const backendUrl = `${process.env.BACKEND_URL || 'https://asim1112-todo-ai-chatbot.hf.space'}/api/v1${pathSegments}${url.search || ''}`;

  // Prepare headers, potentially adding authentication if backend needs it
  const headers: Record<string, string> = {
    ...Object.fromEntries(request.headers.entries()),
    "Content-Type": "application/json",
  };

  // Forward the request to the FastAPI backend
  const backendResponse = await fetch(backendUrl, {
    method: request.method,
    headers: headers,
    body: request.body ? await request.text() : undefined,
  });

  // Return the response from the backend
  const responseBody = await backendResponse.text();

  return new NextResponse(responseBody, {
    status: backendResponse.status,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

export async function GET(request: NextRequest) {
  return forwardToBackend(request);
}

export async function POST(request: NextRequest) {
  return forwardToBackend(request);
}

export async function PUT(request: NextRequest) {
  return forwardToBackend(request);
}

export async function PATCH(request: NextRequest) {
  return forwardToBackend(request);
}

export async function DELETE(request: NextRequest) {
  return forwardToBackend(request);
}