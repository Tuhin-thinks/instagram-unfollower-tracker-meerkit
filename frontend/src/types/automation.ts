export interface FollowingUser {
  user_id: string
  username: string
  full_name: string
  is_private: boolean
  profile_pic_url: string
  follower_count: number | null
  following_count: number | null
  follows_you: boolean
}

export interface FollowingUsersResponse {
  users: FollowingUser[]
  total: number
  followers_total: number
  following_total: number
}

export interface AutomationCacheWindowMetrics {
  cache_hits: number
  api_calls: number
  total_reads: number
  efficiency_percent: number
}

export interface AutomationCacheSizeResponse {
  generated_at: string
  instagram_user_id: string
  cache_scope: string
  cache_size_bytes: number
  cache_file_count: number
}

export interface AutomationCacheCategoryMetrics {
  category: string
  all_time: AutomationCacheWindowMetrics
  last_24h: AutomationCacheWindowMetrics
}

export interface AutomationCacheEfficiencyResponse {
  generated_at: string
  instagram_user_id: string
  all_time: AutomationCacheWindowMetrics
  last_24h: AutomationCacheWindowMetrics
  cache_size: {
    cache_size_bytes: number
    cache_file_count: number
    cache_scope: string
  }
  per_category: AutomationCacheCategoryMetrics[]
}

export type AutomationStatus =
  | 'draft'
  | 'staged'
  | 'queued'
  | 'running'
  | 'partial'
  | 'completed'
  | 'error'
  | 'cancelled'

export interface AutomationActionItem {
  item_id: string
  display_username: string | null
  raw_input: string
  status: string
  exclusion_reason: string | null
  error: string | null
  executed_at: string | null
}

export interface AutomationAction {
  action_id: string
  app_user_id: string
  reference_profile_id: string
  action_type: AutomationActionType
  status: AutomationStatus
  config: Record<string, unknown> | null
  total_items: number
  completed_items: number
  failed_items: number
  skipped_items: number
  error: string | null
  queued_at: string | null
  started_at: string | null
  completed_at: string | null
  create_date: string
  update_date: string
  items_by_status?: Record<string, AutomationActionItem[]>
}

export type AutomationActionType = 'batch_follow' | 'batch_unfollow'

export interface AutomationActionsResponse {
  actions: AutomationAction[]
  total: number
}

export interface AutomationActionResult {
  action_id: string
  action_type: string
  status: string
  selected_count: number
  excluded_count: number
  selected_items: { raw_input: string; display_username: string | null }[]
  excluded_items: { raw_input: string; exclusion_reason: string | null }[]
}

export interface SafelistEntry {
  safelist_id: string
  list_type: string
  raw_input: string
  normalized_username: string | null
  normalized_user_id: string | null
  identity_key: string
  create_date: string
}

export interface SafelistResponse {
  list_type: string
  entries: SafelistEntry[]
  total: number
}
