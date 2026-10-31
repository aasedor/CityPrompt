import { Component, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import type { SiteZone } from '@/types';
import { buildingAssetRevision } from '@/features/pickPlace/buildingAssetRecovery';

/** A failed request must leave the rest of the scene usable. One automatic
 * retry handles an interrupted download; later attempts use Retry 3D update. */
export class BuildingModelBoundary extends Component<{
  children: ReactNode; fallback: ReactNode; request: string | string[]; zone?: SiteZone;
}, { failed: boolean }> {
  state = { failed: false };
  private automaticRetries = 0;
  private retryTimer?: ReturnType<typeof setTimeout>;
  static getDerivedStateFromError() { return { failed: true }; }
  private retry = () => {
    if (!this.state.failed) return;
    clearTimeout(this.retryTimer);
    useGLTF.clear(this.props.request);
    this.setState({ failed: false });
  };
  private manualRetry = () => { this.automaticRetries = 0; this.retry(); };
  componentDidMount() { window.addEventListener('cityprompt:retry-native-buildings', this.manualRetry); }
  componentWillUnmount() {
    clearTimeout(this.retryTimer);
    window.removeEventListener('cityprompt:retry-native-buildings', this.manualRetry);
  }
  componentDidCatch() {
    if (this.automaticRetries++ === 0) {
      this.retryTimer = setTimeout(this.retry, 500);
      return;
    }
    const zone = this.props.zone;
    if (zone) window.dispatchEvent(new CustomEvent('cityprompt:native-building-error', { detail: {
      zoneId: zone.id, revision: buildingAssetRevision(zone),
      message: `${zone.properties?.development_archetype_label || zone.name || 'A building'} could not load its detailed model. Choose Retry 3D update. Your saved design is preserved.`,
    } }));
  }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}
