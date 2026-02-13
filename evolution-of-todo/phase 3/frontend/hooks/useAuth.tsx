"use client";

import { createContext, useContext, useCallback, ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import type { User, AuthState } from "@/types";

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const session = authClient.useSession();

  const isLoading = session.isPending;
  const isAuthenticated = !!session.data?.user;
  const user: User | null = session.data?.user
    ? { userId: session.data.user.id, email: session.data.user.email }
    : null;
  const error: string | null = session.error?.message ?? null;

  const signIn = useCallback(
    async (email: string, password: string) => {
      const { error } = await authClient.signIn.email({
        email,
        password,
        callbackURL: "/dashboard",
      });
      if (error) {
        throw new Error(error.message ?? "Sign in failed");
      }
      router.push("/dashboard");
    },
    [router]
  );

  const signUp = useCallback(
    async (email: string, password: string) => {
      const { error } = await authClient.signUp.email({
        email,
        password,
        name: email.split("@")[0],
        callbackURL: "/dashboard",
      });
      if (error) {
        throw new Error(error.message ?? "Sign up failed");
      }
      router.push("/dashboard");
    },
    [router]
  );

  const handleSignOut = useCallback(() => {
    authClient.signOut({
      fetchOptions: {
        onSuccess: () => router.push("/"),
      },
    });
  }, [router]);

  const clearError = useCallback(() => {
    // useSession manages error state; no-op for compatibility
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        error,
        signIn,
        signUp,
        signOut: handleSignOut,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function useRequireAuth(): AuthState & { isReady: boolean } {
  const { user, isAuthenticated, isLoading, error } = useAuth();
  const router = useRouter();

  // Use useEffect to handle navigation side effect
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/signin");
    }
  }, [isLoading, isAuthenticated, router]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    isReady: !isLoading && isAuthenticated,
  };
}

export function useRedirectIfAuthenticated(): void {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Use useEffect to handle navigation side effect
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isLoading, isAuthenticated, router]);
}
