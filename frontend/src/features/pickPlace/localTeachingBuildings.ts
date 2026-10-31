import data from '@/data/localTeachingBuildings.json';
import type { PlaceAsset } from './assetRegistry';

/** Finite reviewed architectural-clay trials; activation/publication is separate. */
export const localTeachingBuildings = (enabled: boolean): PlaceAsset[] =>
  enabled ? data.models.map(row => row.asset as unknown as PlaceAsset) : [];
export const localTeachingLessons = (enabled: boolean) => enabled ? data.lessons : {};
export const localTeachingHistory = (enabled: boolean) => enabled ? data.history : {};
export const localTeachingStyles = (enabled: boolean) => enabled ? data.styles : {};

// Keep the conditions visible to Rollup so production drops the trial payload.
export const LOCAL_TEACHING_BUILDINGS = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localTeachingBuildings(true) : [];
export const LOCAL_TEACHING_LESSONS = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localTeachingLessons(true) : {};
export const LOCAL_TEACHING_HISTORY = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localTeachingHistory(true) : {};
export const LOCAL_TEACHING_STYLES = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localTeachingStyles(true) : {};
