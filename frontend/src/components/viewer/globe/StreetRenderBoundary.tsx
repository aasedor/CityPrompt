import { Component, useEffect, type ReactNode } from 'react';
import type { SiteZone } from '@/types';
import { nativeStreetRevision } from './nativeStreetReadiness';

/** Keep an invalid street editable and prevent incomplete geometry from passing capture checks. */
export function StreetRenderProblem({ zone, message, preview = false }: { zone: SiteZone; message: string; preview?: boolean }) {
  const revision = nativeStreetRevision(zone);
  useEffect(() => {
    if (preview) return;
    // Publish after the project's status listener has mounted, including on reload.
    const timer = window.setTimeout(() => window.dispatchEvent(new CustomEvent('cityprompt:native-street-error', {
      detail: { zoneId: zone.id, revision,
        message: `${zone.name || 'Street'}: ${message} Select the street to adjust its route, or choose Retry 3D update.` },
    })), 0);
    return () => window.clearTimeout(timer);
  }, [zone.id, zone.name, revision, message, preview]);
  return <group userData={{ nativeStreetZone: zone.id, nativeStreetRevision: revision,
    nativeStreetStatus: 'error', streetGroundZoneId: zone.id, streetGroundStatus: 'unavailable' }} />;
}

class Boundary extends Component<{ zone: SiteZone; preview?: boolean; children: ReactNode }, { message: string | null }> {
  state = { message: null as string | null };
  static getDerivedStateFromError(error: unknown) {
    return { message: error instanceof Error ? error.message : 'The street geometry could not be prepared.' };
  }
  retry = () => this.setState({ message: null });
  componentDidMount() { window.addEventListener('cityprompt:retry-native-streets', this.retry); }
  componentWillUnmount() { window.removeEventListener('cityprompt:retry-native-streets', this.retry); }
  render() {
    return this.state.message === null ? this.props.children
      : <StreetRenderProblem zone={this.props.zone} preview={this.props.preview} message={this.state.message} />;
  }
}

/** Geometry builders can throw before the GLB loader's existing boundary mounts. */
export function StreetRenderBoundary(props: { zone: SiteZone; preview?: boolean; children: ReactNode }) {
  return <Boundary key={JSON.stringify([nativeStreetRevision(props.zone), props.zone.updated_at])} {...props} />;
}
