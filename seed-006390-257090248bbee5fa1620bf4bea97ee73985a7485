import { useState } from 'react';
import { MessageSquarePlus, X, Send, Loader2, Bug, Lightbulb, HelpCircle, Check } from 'lucide-react';
import { feedbackApi } from '@/services/api';
import { useAuthStore } from '@/store';

const CATEGORIES = [
  { id: 'suggestion', label: 'Suggestion', icon: Lightbulb, color: 'text-amber-500' },
  { id: 'bug', label: 'Bug Report', icon: Bug, color: 'text-red-500' },
  { id: 'question', label: 'Question', icon: HelpCircle, color: 'text-blue-500' },
] as const;

export function FeedbackWidget() {
  const { isAuthenticated } = useAuthStore();
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState<string>('suggestion');
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  if (!isAuthenticated) return null;

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      await feedbackApi.submit({
        category,
        text: text.trim(),
        page_url: window.location.pathname,
      });
      setSubmitted(true);
      setText('');
      setTimeout(() => {
        setSubmitted(false);
        setOpen(false);
      }, 2000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to send — please try again';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Floating trigger button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-5 right-5 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg transition-transform hover:scale-110 hover:bg-primary-500 active:scale-95"
        title="Send feedback"
      >
        <MessageSquarePlus size={20} />
      </button>

      {/* Feedback panel */}
      {open && (
        <div className="fixed bottom-20 right-5 z-50 w-80 rounded-xl border border-primary-950/[0.08] bg-white shadow-elevated animate-scale-in">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-primary-950/[0.06] px-4 py-3">
            <h3 className="text-sm font-semibold text-primary-950">Send Feedback</h3>
            <button onClick={() => setOpen(false)} className="text-primary-950/40 hover:text-primary-950">
              <X size={16} />
            </button>
          </div>

          {submitted ? (
            <div className="flex flex-col items-center gap-2 px-4 py-8">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-500">
                <Check size={20} />
              </div>
              <p className="text-sm font-medium text-primary-950">Thanks for your feedback!</p>
            </div>
          ) : (
            <div className="px-4 py-3">
              {/* Category selector */}
              <div className="mb-3 flex gap-1.5">
                {CATEGORIES.map((cat) => {
                  const Icon = cat.icon;
                  return (
                    <button
                      key={cat.id}
                      onClick={() => setCategory(cat.id)}
                      className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg border px-2 py-1.5 text-xs font-medium transition-colors ${
                        category === cat.id
                          ? 'border-primary-500/30 bg-primary-500/10 text-primary-700'
                          : 'border-primary-950/[0.06] text-primary-950/50 hover:border-primary-950/[0.12]'
                      }`}
                    >
                      <Icon size={13} className={category === cat.id ? cat.color : ''} />
                      {cat.label}
                    </button>
                  );
                })}
              </div>

              {/* Text input */}
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={
                  category === 'bug'
                    ? 'Describe what happened and what you expected...'
                    : category === 'question'
                    ? 'What would you like to know?'
                    : 'How can we make this better?'
                }
                className="w-full resize-none rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.02] px-3 py-2 text-sm text-primary-950 placeholder:text-primary-950/30 focus:border-primary-500/40 focus:outline-none focus:ring-1 focus:ring-primary-500/20"
                rows={4}
                maxLength={5000}
              />
              <div className="mt-1 text-right text-[10px] text-primary-950/30">{text.length}/5000</div>

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={!text.trim() || submitting}
                className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {submitting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                {submitting ? 'Sending...' : 'Submit'}
              </button>
              {error && (
                <p className="mt-2 text-xs text-red-500">{error}</p>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
}
