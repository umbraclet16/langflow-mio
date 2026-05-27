export interface StatusConfigEntry {
  label: string;
  textClass: string;
}

export const STATUS_CONFIG: Record<string, StatusConfigEntry> = {
  ready: {
    label: "就绪",
    textClass: "text-accent-emerald-foreground",
  },
  ingesting: {
    label: "摄入中",
    textClass: "text-accent-amber-foreground",
  },
  failed: {
    label: "失败",
    textClass: "text-destructive",
  },
  cancelling: {
    label: "取消中",
    textClass: "text-accent-amber-foreground",
  },
  empty: {
    label: "空",
    textClass: "text-muted-foreground",
  },
};

export const BUSY_STATUSES = ["ingesting", "cancelling"] as const;

export const isBusyStatus = (status?: string): boolean =>
  BUSY_STATUSES.includes(status as (typeof BUSY_STATUSES)[number]);
