export interface StandaloneConfig {
  deploymentUrl: string;
  assistantId: string;
  langsmithApiKey?: string;
}

const CONFIG_KEY = "deep-agent-config";
const DEFAULT_CONFIG: StandaloneConfig = {
  deploymentUrl: "http://127.0.0.1:2025",
  assistantId: "journal_agent",
};

export function getConfig(): StandaloneConfig | null {
  if (typeof window === "undefined") return DEFAULT_CONFIG;

  const stored = localStorage.getItem(CONFIG_KEY);
  if (!stored) return DEFAULT_CONFIG;

  try {
    const config = JSON.parse(stored);
    if (config?.deploymentUrl === "http://127.0.0.1:2024") {
      return DEFAULT_CONFIG;
    }
    return config;
  } catch {
    return DEFAULT_CONFIG;
  }
}

export function saveConfig(config: StandaloneConfig): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
}
