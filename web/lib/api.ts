import type { ReportJob } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      `Could not reach the API at ${API_URL}. Start the backend with: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
    );
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).join(", ")
          : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function parseApp(input: string): Promise<{ app_id: string }> {
  return request("/api/parse", {
    method: "POST",
    body: JSON.stringify({ input }),
  });
}

export async function createReport(
  app_id: string,
  options?: { us_only?: boolean; demo?: boolean }
): Promise<{ report_id: string }> {
  return request("/api/reports", {
    method: "POST",
    body: JSON.stringify({
      app_id,
      us_only: options?.us_only ?? false,
      demo: options?.demo ?? false,
    }),
  });
}

export async function getReport(report_id: string): Promise<ReportJob> {
  if (report_id === "demo") {
    return request("/api/reports/demo");
  }
  return request(`/api/reports/${report_id}`);
}

export async function getDemoReport(): Promise<ReportJob> {
  return request("/api/reports/demo");
}
