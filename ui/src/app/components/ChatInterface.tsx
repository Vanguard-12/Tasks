"use client";

import React, { useCallback } from "react";
import { AgentDashboard } from "@/app/components/AgentDashboard";
import { Assistant } from "@langchain/langgraph-sdk";
import { useChatContext } from "@/providers/ChatProvider";

interface ChatInterfaceProps {
  assistant: Assistant | null;
}

export const ChatInterface = React.memo<ChatInterfaceProps>(({ assistant }) => {
  const {
    agentState,
    journalOverview,
    isLoading,
    isThreadLoading,
    sendMessage,
  } = useChatContext();

  const submitDisabled = isLoading || !assistant;

  const handleRunAgent = useCallback(() => {
    if (submitDisabled) return;
    sendMessage("run");
  }, [sendMessage, submitDisabled]);

  return (
    <div className="relative flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-slate-50">
      <div className="min-h-0 flex-1 overflow-hidden px-5 pb-24 pt-4">
        {isThreadLoading ? (
          <div className="flex h-full items-center justify-center rounded-xl border border-border bg-background p-8">
            <p className="text-muted-foreground">Загружаю состояние агента...</p>
          </div>
        ) : (
          <AgentDashboard
            state={agentState as Record<string, any>}
            overview={journalOverview}
            isRunning={isLoading}
          />
        )}
      </div>

      <div className="fixed bottom-6 right-6 z-50">
        <button
          type="button"
          onClick={handleRunAgent}
          disabled={submitDisabled}
          className="rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white shadow-xl shadow-black/20 transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
        >
          {isLoading ? "Агент работает..." : "Запуск агента"}
        </button>
      </div>
    </div>
  );
});

ChatInterface.displayName = "ChatInterface";
