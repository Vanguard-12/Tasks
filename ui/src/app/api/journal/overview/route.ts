import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

type Submission = Record<string, any>;

function parseEnv(text: string) {
  const env: Record<string, string> = {};
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index === -1) continue;
    const key = line.slice(0, index).trim();
    const value = line.slice(index + 1).trim().replace(/^['"]|['"]$/g, "");
    env[key] = value;
  }
  return env;
}

async function loadProjectEnv() {
  const projectRoot = path.resolve(process.cwd(), "..");
  const envPath = path.join(projectRoot, ".env");
  const examplePath = path.join(projectRoot, ".env.example");
  try {
    return parseEnv(await readFile(envPath, "utf8"));
  } catch {
    return parseEnv(await readFile(examplePath, "utf8"));
  }
}

function statusOf(submission: Submission) {
  return typeof submission.status === "string" ? submission.status.toLowerCase() : "";
}

function feedbackOf(submission: Submission) {
  const parts = [];
  if (typeof submission.reworkComment === "string" && submission.reworkComment.trim()) {
    parts.push(submission.reworkComment.trim());
  }
  if (typeof submission.grade?.feedback === "string" && submission.grade.feedback.trim()) {
    parts.push(submission.grade.feedback.trim());
  }
  return Array.from(new Set(parts)).join("\n\n");
}

function bucketOf(submission: Submission) {
  if (submission.grade?.value === true || statusOf(submission) === "done") return "done";
  if (statusOf(submission) === "ready_for_review") return "review";
  return "todo";
}

export async function GET() {
  try {
    const env = await loadProjectEnv();
    const baseUrl = (env.JOURNAL_API_BASE_URL || "https://platform.brojs.ru/jrnl-bh").replace(/\/$/, "");
    const token = env.JOURNAL_API_TOKEN;
    const courseId = env.COURSE_ID;
    if (!token || !courseId) {
      return NextResponse.json(
        { ok: false, error: "JOURNAL_API_TOKEN or COURSE_ID is missing in .env" },
        { status: 400 }
      );
    }

    const url = new URL(`${baseUrl}/api/v2/submission/my`);
    url.searchParams.set("courseId", courseId);
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) {
      const body = await response.text();
      return NextResponse.json(
        { ok: false, error: `Journal API failed with HTTP ${response.status}`, body },
        { status: response.status }
      );
    }

    const payload = await response.json();
    const submissions: Submission[] = Array.isArray(payload.body)
      ? payload.body.filter((item: unknown) => item && typeof item === "object")
      : [];
    const stats = { total: submissions.length, done: 0, review: 0, todo: 0 };
    const assignments = submissions.map((submission) => {
      const bucket = bucketOf(submission);
      stats[bucket as "done" | "review" | "todo"] += 1;
      const task = submission.task && typeof submission.task === "object" ? submission.task : {};
      return {
        taskId: task._id || task.id || "",
        taskTitle: task.title || task._id || task.id || "Untitled assignment",
        submissionId: submission._id || submission.id || "",
        status: statusOf(submission) || "unknown",
        bucket,
        isRevision: bucket === "todo" && Boolean(feedbackOf(submission)),
        teacherFeedback: feedbackOf(submission),
      };
    });

    return NextResponse.json({ ok: true, stats, assignments });
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
