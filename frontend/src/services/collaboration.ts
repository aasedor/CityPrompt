import { useMemo } from 'react';

export interface CollaborationUser {
  id: string;
  name: string;
  email: string;
  color: string;
  connected_at: string;
}

export interface CursorInfo {
  userId: string;
  name: string;
  color: string;
  position: [number, number, number];
  target: [number, number, number];
}

type EditHandler = ((message: {
  userId: string;
  name: string;
  buildingId: string;
  changes: Record<string, unknown>;
}) => void) | null;
type SelectHandler = ((message: {
  userId: string;
  name: string;
  buildingId: string;
}) => void) | null;

/**
 * Compatibility adapter while optional live collaboration is unavailable.
 * The former relay did not enforce project access. Do not open or retry a
 * socket until the server has a secured connection and recipient lifecycle.
 * Shared project reads and saves use the authenticated HTTP APIs.
 */
export function useCollaboration(_projectId: string | undefined, _userName?: string) {
  return useMemo(() => ({
    status: 'unavailable' as const,
    unavailableReason: 'Live collaboration is paused. Shared project access and saving remain available.',
    users: [] as CollaborationUser[],
    cursors: new Map<string, CursorInfo>(),
    connectionId: null as string | null,
    isConnected: false,
    followingUserId: null as string | null,
    sendCursor: (_position: [number, number, number], _target: [number, number, number]) => {},
    sendSelect: (_buildingId: string | null) => {},
    sendEdit: (_buildingId: string, _changes: Record<string, unknown>) => {},
    onEdit: (_handler: EditHandler) => {},
    onSelect: (_handler: SelectHandler) => {},
    onCamera: (_handler: ((cursor: CursorInfo) => void) | null) => {},
    setFollowing: (_userId: string | null) => {},
  }), []);
}
