import { useEffect, useState, useCallback } from 'react';
import { Loader2, Bug, Lightbulb, HelpCircle, Trash2, MessageSquare, CheckCircle2, Eye, XCircle } from 'lucide-react';
import { feedbackApi } from '@/services/api';
import type { FeedbackItem, FeedbackCounts } from '@/services/api';

const STATUS_TABS = [
  { id: null, label: 'All' },
  { id: 'open', label: 'Open' },
  { id: 'reviewed', label: 'Reviewed' },
  { id: 'resolved', label: 'Resolved' },
  { id: 'dismissed', label: 'Dismissed' },
] as const;

const CATEGORY_ICON: Record<string, typeof Bug> = {
  bug: Bug,
  suggestion: Lightbulb,
  question: HelpCircle,
};

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-amber-500/15 text-amber-600',
  reviewed: 'bg-blue-500/15 text-blue-600',
  resolved: 'bg-emerald-500/15 text-emerald-600',
  dismissed: 'bg-neutral-500/15 text-neutral-500',
};

const STATUS_ICONS: Record<string, typeof Eye> = {
  open: MessageSquare,
  reviewed: Eye,
  resolved: CheckCircle2,
  dismissed: XCircle,
};

export function AdminFeedbackPage() {
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [counts, setCounts] = useState<FeedbackCounts | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [notesInput, setNotesInput] = useState<Record<string, string>>({});

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [feedbackItems, feedbackCounts] = await Promise.all([
        feedbackApi.inbox({ status_filter: statusFilter || undefined }),
        feedbackApi.counts(),
      ]);
      setItems(feedbackItems);
      setCounts(feedbackCounts);
    } catch {
      // handled by empty state
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStatusChange = async (id: string, newStatus: string) => {
    const updated = await feedbackApi.update(id, { status: newStatus });
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
    // Refresh counts
    feedbackApi.counts().then(setCounts);
  };

  const handleSaveNotes = async (id: string) => {
    const notes = notesInput[id];
    if (notes === undefined) return;
    const updated = await feedbackApi.update(id, { admin_notes: notes });
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
  };

  const handleDelete = async (id: string) => {
    await feedbackApi.delete(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
    feedbackApi.counts().then(setCounts);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary-950">Feedback Inbox</h1>
          <p className="mt-1 text-sm text-primary-950/50">
            Beta tester suggestions, bug reports, and questions
          </p>
        </div>
        {counts && (
          <div className="flex items-center gap-1 rounded-full bg-amber-500/15 px-3 py-1 text-sm font-semibold text-amber-600">
            {counts.open} open
          </div>
        )}
      </div>

      {/* Status tabs */}
      <div className="mb-4 flex gap-1 rounded-lg border border-primary-950/[0.06] bg-primary-950/[0.02] p-1">
        {STATUS_TABS.map((tab) => {
          const count = tab.id ? counts?.[tab.id as keyof FeedbackCounts] : counts?.total;
          return (
            <button
              key={tab.id ?? 'all'}
              onClick={() => setStatusFilter(tab.id)}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                statusFilter === tab.id
                  ? 'bg-white text-primary-950 shadow-sm'
                  : 'text-primary-950/50 hover:text-primary-950/70'
              }`}
            >
              {tab.label}
              {count != null && count > 0 && (
                <span className="rounded-full bg-primary-950/[0.06] px-1.5 py-0.5 text-[10px] font-semibold">
                  {count as number}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : items.length === 0 ? (
        <div className="py-16 text-center">
          <MessageSquare className="mx-auto h-10 w-10 text-primary-950/20" />
          <p className="mt-3 text-sm text-primary-950/40">No feedback items</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const CatIcon = CATEGORY_ICON[item.category] || MessageSquare;
            const StatusIcon = STATUS_ICONS[item.status] || MessageSquare;
            const isExpanded = expandedId === item.id;

            return (
              <div
                key={item.id}
                className="rounded-lg border border-primary-950/[0.06] bg-white transition-shadow hover:shadow-sm"
              >
                {/* Summary row */}
                <button
                  onClick={() => {
                    setExpandedId(isExpanded ? null : item.id);
                    if (!isExpanded && item.admin_notes) {
                      setNotesInput((prev) => ({ ...prev, [item.id]: item.admin_notes || '' }));
                    }
                  }}
                  className="flex w-full items-start gap-3 px-4 py-3 text-left"
                >
                  <div className="mt-0.5 flex-shrink-0">
                    <CatIcon size={16} className={item.category === 'bug' ? 'text-red-500' : item.category === 'question' ? 'text-blue-500' : 'text-amber-500'} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-primary-950 line-clamp-2">{item.text}</p>
                    <div className="mt-1 flex items-center gap-2 text-xs text-primary-950/40">
                      <span>{item.author_name || item.author_email}</span>
                      <span>·</span>
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                      {item.page_url && (
                        <>
                          <span>·</span>
                          <span className="truncate max-w-[120px]">{item.page_url}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className={`flex flex-shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${STATUS_COLORS[item.status] || ''}`}>
                    <StatusIcon size={11} />
                    {item.status}
                  </span>
                </button>

                {/* Expanded detail */}
                {isExpanded && (
                  <div className="border-t border-primary-950/[0.04] px-4 py-3">
                    {/* Full text */}
                    <p className="whitespace-pre-wrap text-sm text-primary-950">{item.text}</p>

                    {/* Status actions */}
                    <div className="mt-3 flex flex-wrap items-center gap-1.5">
                      <span className="mr-1 text-xs text-primary-950/40">Set status:</span>
                      {(['open', 'reviewed', 'resolved', 'dismissed'] as const).map((s) => {
                        const SIcon = STATUS_ICONS[s];
                        return (
                          <button
                            key={s}
                            onClick={() => handleStatusChange(item.id, s)}
                            disabled={item.status === s}
                            className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                              item.status === s
                                ? 'bg-primary-500/10 text-primary-600'
                                : 'bg-primary-950/[0.03] text-primary-950/50 hover:bg-primary-950/[0.06] hover:text-primary-950/70'
                            }`}
                          >
                            <SIcon size={11} />
                            {s}
                          </button>
                        );
                      })}
                    </div>

                    {/* Admin notes */}
                    <div className="mt-3">
                      <label className="text-xs font-medium text-primary-950/40">Admin Notes</label>
                      <textarea
                        value={notesInput[item.id] ?? item.admin_notes ?? ''}
                        onChange={(e) => setNotesInput((prev) => ({ ...prev, [item.id]: e.target.value }))}
                        className="mt-1 w-full resize-none rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.02] px-3 py-2 text-sm text-primary-950 placeholder:text-primary-950/30 focus:border-primary-500/40 focus:outline-none focus:ring-1 focus:ring-primary-500/20"
                        rows={2}
                        placeholder="Internal notes..."
                      />
                      <div className="mt-1 flex justify-end gap-2">
                        <button
                          onClick={() => handleSaveNotes(item.id)}
                          className="rounded-md bg-primary-600 px-3 py-1 text-xs font-medium text-white hover:bg-primary-500"
                        >
                          Save Notes
                        </button>
                      </div>
                    </div>

                    {/* Delete */}
                    <div className="mt-3 flex justify-end border-t border-primary-950/[0.04] pt-3">
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="flex items-center gap-1 text-xs text-red-500/60 hover:text-red-500"
                      >
                        <Trash2 size={12} />
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
