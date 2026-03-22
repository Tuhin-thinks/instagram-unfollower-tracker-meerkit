import { ref } from 'vue'
import { listAutomationActions } from './api'
import type { AutomationAction, AutomationActionType, AutomationStatus } from '../types/automation'

const STORAGE_KEY = 'nfi.automation.jobs.v1'
const ACTIVE_STATUSES: Set<AutomationStatus> = new Set(['staged', 'queued', 'running'])

interface AutomationJobRecord {
  profileId: string
  actionType: AutomationActionType
  actionId: string
  status: AutomationStatus
  updatedAt: string
}

const jobsByKey = ref<Record<string, AutomationJobRecord>>(loadJobs())

function makeKey(profileId: string, actionType: AutomationActionType): string {
  return `${profileId}:${actionType}`
}

function isActiveStatus(status: AutomationStatus): boolean {
  return ACTIVE_STATUSES.has(status)
}

function loadJobs(): Record<string, AutomationJobRecord> {
  if (typeof window === 'undefined') {
    return {}
  }
  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return {}
  }
  try {
    const parsed = JSON.parse(raw) as Record<string, AutomationJobRecord>
    return parsed && typeof parsed === 'object' ? parsed : {}
  } catch {
    return {}
  }
}

function persistJobs(): void {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(jobsByKey.value))
}

function upsertJob(record: AutomationJobRecord): void {
  jobsByKey.value = {
    ...jobsByKey.value,
    [makeKey(record.profileId, record.actionType)]: record,
  }
  persistJobs()
}

export function registerAutomationJob(action: AutomationAction): void {
  upsertJob({
    profileId: action.reference_profile_id,
    actionType: action.action_type,
    actionId: action.action_id,
    status: action.status,
    updatedAt: new Date().toISOString(),
  })
}

export function updateAutomationJob(actionId: string, status: AutomationStatus): void {
  const entry = Object.entries(jobsByKey.value).find(([, value]) => value.actionId === actionId)
  if (!entry) {
    return
  }
  const [key, value] = entry
  jobsByKey.value = {
    ...jobsByKey.value,
    [key]: {
      ...value,
      status,
      updatedAt: new Date().toISOString(),
    },
  }
  persistJobs()
}

export function clearAutomationJob(actionId: string): void {
  const next = { ...jobsByKey.value }
  let changed = false
  for (const [key, value] of Object.entries(next)) {
    if (value.actionId === actionId) {
      delete next[key]
      changed = true
    }
  }
  if (!changed) {
    return
  }
  jobsByKey.value = next
  persistJobs()
}

export function getRegisteredAutomationJob(
  profileId: string,
  actionType: AutomationActionType,
): AutomationJobRecord | null {
  return jobsByKey.value[makeKey(profileId, actionType)] ?? null
}

export async function recoverAutomationJobForType(
  profileId: string,
  actionType: AutomationActionType,
): Promise<AutomationAction | null> {
  const res = await listAutomationActions()
  const matching = res.actions
    .filter((action) => action.action_type === actionType)
    .sort((a, b) => {
      const left = Date.parse(a.update_date || a.create_date)
      const right = Date.parse(b.update_date || b.create_date)
      return right - left
    })

  const active = matching.find((action) => isActiveStatus(action.status))
  if (!active) {
    const registered = getRegisteredAutomationJob(profileId, actionType)
    if (registered) {
      clearAutomationJob(registered.actionId)
    }
    return null
  }

  registerAutomationJob(active)
  return active
}

export function useAutomationJobRegistry() {
  return {
    jobsByKey,
  }
}
