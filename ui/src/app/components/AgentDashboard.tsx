"use client";

import type React from "react";
import {
  AlertTriangle,
  CheckCircle2,
  CircleDot,
  ClipboardCheck,
  Clock3,
  FileCode2,
  GitBranch,
  Loader2,
  Radio,
  Send,
  ShieldCheck,
} from "lucide-react";
import type { JournalOverview } from "@/app/hooks/useChat";

type AgentDashboardProps = {
  state: Record<string, any>;
  overview: JournalOverview | null;
  isRunning: boolean;
};

type Assignment = Record<string, any>;

const EMPTY = "—";

function text(value: unknown, fallback = EMPTY) {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function statusText(status: string) {
  const map: Record<string, string> = {
    done: "Зачтено",
    accepted: "Зачтено",
    completed: "Зачтено",
    solved: "Зачтено",
    review: "На проверке",
    ready_for_review: "На проверке",
    todo: "К выполнению",
    new: "К выполнению",
    running: "В работе",
    needs_repair: "Доработка",
    checks_failed: "Ошибки проверок",
    publishing: "Публикация",
    submitted: "Отправлено",
    finished: "Готово",
    failed: "Ошибка",
  };
  return map[status] ?? status;
}

function statusStyle(status: string) {
  if (["done", "accepted", "completed", "solved", "submitted", "finished"].includes(status)) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }
  if (["review", "ready_for_review", "publishing"].includes(status)) {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }
  if (["todo", "new", "running"].includes(status)) {
    return "border-sky-200 bg-sky-50 text-sky-700";
  }
  return "border-red-200 bg-red-50 text-red-700";
}

function titleOf(assignment: Assignment) {
  return text(
    assignment.taskTitle || assignment.title || assignment.name || assignment.taskId || assignment._id || assignment.id,
    "Без названия"
  );
}

function assignmentKey(assignment: Assignment) {
  return String(assignment.taskId || assignment.submissionId || assignment.taskTitle || assignment.title);
}

function assignmentStatus(assignment: Assignment, runtime: boolean) {
  return runtime ? text(assignment.status, "running") : text(assignment.bucket || assignment.submissionStatus, "unknown");
}

function mergeAssignments(overviewAssignments: Assignment[], runtimeAssignments: Assignment[]) {
  const byId = new Map<string, Assignment>();
  for (const assignment of overviewAssignments) {
    byId.set(assignmentKey(assignment), assignment);
  }
  for (const assignment of runtimeAssignments) {
    const key = assignmentKey(assignment);
    byId.set(key, { ...(byId.get(key) ?? {}), ...assignment, runtime: true });
  }
  return Array.from(byId.values());
}

function findActiveAssignment(assignments: Assignment[]) {
  const active = assignments.find((assignment) => {
    const status = text(assignment.status, "");
    return status && !["finished", "submitted", "done", "accepted"].includes(status);
  });
  return active ?? assignments.at(-1);
}

export function AgentDashboard({ state, overview, isRunning }: AgentDashboardProps) {
  const runtimeAssignments = Object.values(state.ui_assignments ?? {}) as Assignment[];
  const overviewAssignments = overview?.assignments ?? [];
  const assignments = runtimeAssignments.length
    ? mergeAssignments(overviewAssignments, runtimeAssignments)
    : overviewAssignments;
  const stats = state.assignment_stats?.total ? state.assignment_stats : overview?.stats;
  const events = Array.isArray(state.ui_events) ? state.ui_events.slice(-30).reverse() : [];
  const activeAssignment = findActiveAssignment(runtimeAssignments);
  const currentNode = text(state.node, isRunning ? "запуск" : "ожидание запуска");
  const isLoaded = overview !== null || Boolean(stats);

  return (
    <section className="grid h-full min-h-0 grid-rows-[auto_auto_1fr] gap-4">
      <header className="overflow-hidden rounded-2xl border border-border bg-background shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-gradient-to-r from-slate-950 via-slate-900 to-slate-800 px-5 py-4 text-white">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">
              Journal.bh Assignment Agent
            </p>
            <h1 className="mt-1 text-2xl font-semibold">Панель выполнения заданий</h1>
          </div>
          <div className="flex items-center gap-3 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm backdrop-blur">
            {isRunning ? <Loader2 className="size-4 animate-spin text-sky-300" /> : <Radio className="size-4 text-slate-300" />}
            <span>{isRunning ? "Агент работает" : "Агент остановлен"}</span>
            <span className="h-4 w-px bg-white/20" />
            <span className="max-w-[260px] truncate text-slate-200">{currentNode}</span>
          </div>
        </div>

        <div className="grid gap-3 p-4 md:grid-cols-4">
          <Metric label="Всего заданий" value={stats?.total ?? 0} icon={<ClipboardCheck className="size-5" />} />
          <Metric label="Зачтено" value={stats?.done ?? 0} tone="success" icon={<ShieldCheck className="size-5" />} />
          <Metric label="На проверке" value={stats?.review ?? 0} tone="warning" icon={<Clock3 className="size-5" />} />
          <Metric label="К выполнению" value={stats?.todo ?? 0} tone="info" icon={<CircleDot className="size-5" />} />
        </div>
      </header>

      {overview?.ok === false ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          Не удалось загрузить сводку из Journal.bh: {overview.error}
        </div>
      ) : !isLoaded ? (
        <div className="rounded-xl border border-border bg-sidebar px-4 py-3 text-sm text-muted-foreground">
          Загружаю актуальные статусы заданий из Journal.bh...
        </div>
      ) : null}

      <div className="grid min-h-0 gap-4 xl:grid-cols-[360px_minmax(420px,1fr)_390px]">
        <Panel
          title="Задания курса"
          subtitle={assignments.length ? `${assignments.length} заданий из API` : "ожидание данных"}
        >
          <AssignmentList assignments={assignments} runtimeAssignments={runtimeAssignments} />
        </Panel>

        <Panel
          title="Текущее выполнение"
          subtitle={activeAssignment ? titleOf(activeAssignment) : "активного задания нет"}
          accent
        >
          <ActiveWork assignment={activeAssignment} isRunning={isRunning} stats={stats} />
        </Panel>

        <Panel
          title="Ход работы"
          subtitle={events.length ? `${events.length} последних событий` : "событий пока нет"}
        >
          <Timeline events={events} isRunning={isRunning} />
        </Panel>
      </div>
    </section>
  );
}

function AssignmentList({
  assignments,
  runtimeAssignments,
}: {
  assignments: Assignment[];
  runtimeAssignments: Assignment[];
}) {
  if (!assignments.length) {
    return <EmptyState title="Список пуст" text="Когда API вернет задания, они появятся здесь до запуска агента." />;
  }

  const activeKey = findActiveAssignment(runtimeAssignments) ? assignmentKey(findActiveAssignment(runtimeAssignments)!) : "";

  return (
    <div className="space-y-2">
      {assignments.map((assignment) => {
        const runtime = Boolean(assignment.runtime);
        const status = assignmentStatus(assignment, runtime);
        const active = assignmentKey(assignment) === activeKey;
        return (
          <article
            key={assignmentKey(assignment)}
            className={`rounded-xl border p-3 transition ${
              active ? "border-sky-300 bg-sky-50 shadow-sm" : "border-border bg-background"
            }`}
          >
            <div className="mb-2 flex items-center justify-between gap-2">
              <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${statusStyle(status)}`}>
                {statusText(status)}
              </span>
              {assignment.isRevision ? (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                  доработка
                </span>
              ) : null}
            </div>
            <h3 className="line-clamp-2 text-sm font-semibold text-primary">{titleOf(assignment)}</h3>
            <p className="mt-1 truncate text-xs text-muted-foreground">
              {text(assignment.submissionStatus || assignment.status || assignment.bucket)}
            </p>
          </article>
        );
      })}
    </div>
  );
}

function ActiveWork({
  assignment,
  isRunning,
  stats,
}: {
  assignment?: Assignment;
  isRunning: boolean;
  stats?: Record<string, number>;
}) {
  if (!assignment) {
    const todo = stats?.todo ?? 0;
    return (
      <div className="flex h-full min-h-[420px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-background p-8 text-center">
        <ShieldCheck className="mb-4 size-12 text-emerald-600" />
        <h3 className="text-xl font-semibold text-primary">
          {todo > 0 ? "Агент готов к запуску" : "Нет заданий для выполнения"}
        </h3>
        <p className="mt-2 max-w-md text-sm text-muted-foreground">
          {todo > 0
            ? "Нажми закрепленную кнопку запуска. Здесь появится карточка выбранного задания, проверки, review, commit и отправка."
            : "По актуальной сводке все задания уже зачтены или находятся на проверке. Когда появится доработка, она будет показана в этом блоке."}
        </p>
      </div>
    );
  }

  const checks = Array.isArray(assignment.checks) ? assignment.checks : [];
  const failedChecks = checks.filter((check: any) => check?.ok === false);
  const review = assignment.review && typeof assignment.review === "object" ? assignment.review : {};
  const changedFiles = Array.isArray(assignment.changedFiles) ? assignment.changedFiles : [];
  const events = Array.isArray(assignment.events) ? assignment.events.slice(-8).reverse() : [];
  const status = text(assignment.status, isRunning ? "running" : "todo");

  return (
    <div className="space-y-4">
      <section className="rounded-xl border border-border bg-background p-4">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3 className="text-xl font-semibold text-primary">{titleOf(assignment)}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Submission {text(assignment.submissionId)} · node {text(assignment.currentNode)}
            </p>
          </div>
          <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusStyle(status)}`}>
            {statusText(status)}
          </span>
        </div>

        {assignment.teacherFeedback ? (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            <div className="mb-1 font-semibold">Комментарий преподавателя</div>
            {assignment.teacherFeedback}
          </div>
        ) : null}
      </section>

      <div className="grid gap-3 md:grid-cols-3">
        <SmallCard
          title="Sanity checks"
          value={failedChecks.length ? `${failedChecks.length} ошибок` : checks.length ? "Пройдены" : "Ожидание"}
          bad={failedChecks.length > 0}
        />
        <SmallCard
          title="LLM review"
          value={review.acceptable === false ? "Нужны правки" : review.summary ? "Принято" : "Ожидание"}
          bad={review.acceptable === false}
        />
        <SmallCard title="Файлы" value={String(changedFiles.length)} icon={<FileCode2 className="size-4" />} />
      </div>

      <section className="rounded-xl border border-border bg-background p-4">
        <div className="mb-3 flex items-center gap-2 font-semibold">
          <GitBranch className="size-4" />
          Git и отправка
        </div>
        <dl className="grid gap-2 text-sm">
          <Info label="Ветка" value={text(assignment.branch)} />
          <Info label="Коммит" value={text(assignment.commitSha).slice(0, 12)} />
          <Info label="Ответ" value={text(assignment.submissionContent)} />
        </dl>
      </section>

      <section className="rounded-xl border border-border bg-background p-4">
        <h4 className="mb-3 font-semibold">Измененные файлы</h4>
        {changedFiles.length ? (
          <div className="grid gap-2 sm:grid-cols-2">
            {changedFiles.map((file: string) => (
              <div key={file} className="truncate rounded-lg bg-sidebar px-3 py-2 text-sm">
                {file}
              </div>
            ))}
          </div>
        ) : (
          <EmptyLine text="Файлы еще не менялись." />
        )}
      </section>

      <section className="rounded-xl border border-border bg-background p-4">
        <h4 className="mb-3 font-semibold">События задания</h4>
        {events.length ? (
          <div className="space-y-2">
            {events.map((event: any, index: number) => (
              <div key={`${event.node}-${event.time}-${index}`} className="grid gap-2 rounded-lg bg-sidebar p-2 text-sm sm:grid-cols-[150px_1fr]">
                <span className="font-medium">{text(event.node)}</span>
                <span className="text-muted-foreground">{text(event.message)}</span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyLine text="Событий по заданию пока нет." />
        )}
      </section>
    </div>
  );
}

function Timeline({ events, isRunning }: { events: Assignment[]; isRunning: boolean }) {
  if (!events.length) {
    return (
      <EmptyState
        title={isRunning ? "Жду первое событие" : "Агент еще не запускался"}
        text="После запуска здесь будет живой журнал: загрузка API, выбор задания, анализ, правки, проверки, commit, push и отправка."
      />
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event: any, index: number) => (
        <article key={`${event.time}-${event.node}-${index}`} className="relative rounded-xl border border-border bg-background p-3">
          <div className="mb-1 flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-primary">{text(event.node)}</span>
            <span className="text-xs text-muted-foreground">{formatTime(event.time)}</span>
          </div>
          <p className="text-sm text-muted-foreground">{text(event.message)}</p>
        </article>
      ))}
    </div>
  );
}

function Panel({
  title,
  subtitle,
  children,
  accent = false,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <section className={`flex min-h-0 flex-col overflow-hidden rounded-2xl border shadow-sm ${
      accent ? "border-sky-200 bg-sky-50/40" : "border-border bg-sidebar/70"
    }`}>
      <div className="border-b border-border bg-background/90 px-4 py-3">
        <h2 className="font-semibold text-primary">{title}</h2>
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-3">{children}</div>
    </section>
  );
}

function Metric({
  label,
  value,
  tone,
  icon,
}: {
  label: string;
  value: number;
  tone?: "success" | "warning" | "info";
  icon: React.ReactNode;
}) {
  const color =
    tone === "success"
      ? "text-emerald-600 bg-emerald-50"
      : tone === "warning"
        ? "text-amber-600 bg-amber-50"
        : tone === "info"
          ? "text-sky-600 bg-sky-50"
          : "text-slate-700 bg-slate-100";

  return (
    <div className="flex items-center gap-3 rounded-xl border border-border bg-sidebar p-3">
      <div className={`rounded-lg p-2 ${color}`}>{icon}</div>
      <div>
        <div className="text-3xl font-semibold text-primary">{value}</div>
        <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      </div>
    </div>
  );
}

function SmallCard({
  title,
  value,
  bad,
  icon,
}: {
  title: string;
  value: string;
  bad?: boolean;
  icon?: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-background p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-semibold">{title}</span>
        {icon ?? (bad ? <AlertTriangle className="size-4 text-red-600" /> : <CheckCircle2 className="size-4 text-emerald-600" />)}
      </div>
      <p className={bad ? "text-sm font-medium text-red-700" : "text-sm text-muted-foreground"}>{value}</p>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[88px_1fr] gap-2">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="truncate font-medium">{value}</dd>
    </div>
  );
}

function EmptyState({ title, text: body }: { title: string; text: string }) {
  return (
    <div className="flex h-full min-h-[240px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-background p-6 text-center">
      <Send className="mb-3 size-8 text-muted-foreground" />
      <h3 className="font-semibold text-primary">{title}</h3>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">{body}</p>
    </div>
  );
}

function EmptyLine({ text: value }: { text: string }) {
  return <div className="rounded-lg border border-dashed border-border bg-sidebar p-3 text-center text-sm text-muted-foreground">{value}</div>;
}

function formatTime(value: unknown) {
  if (typeof value !== "string") return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
