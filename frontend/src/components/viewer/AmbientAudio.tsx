import { useEffect, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useViewerStore } from '@/store';

/**
 * Ambient audio system for walkthrough mode.
 * Uses Web Audio API (no external dependencies) to provide:
 * - Subtle low-frequency ambient drone for environmental presence
 * - Footstep click sounds synced with head bob phase
 *
 * Only active during walkthrough (firstPerson mode + isWalkthroughActive).
 * Cleans up all audio nodes on walkthrough exit.
 */
export function AmbientAudio() {
  const { settings, isWalkthroughActive } = useViewerStore();
  const isActive = isWalkthroughActive && settings.cameraMode === 'firstPerson';

  const ctxRef = useRef<AudioContext | null>(null);
  const droneRef = useRef<OscillatorNode | null>(null);
  const droneGainRef = useRef<GainNode | null>(null);
  const lastStepPhase = useRef(0);

  // Start/stop audio context based on walkthrough state
  useEffect(() => {
    if (!isActive) {
      // Cleanup
      if (droneRef.current) {
        try { droneRef.current.stop(); } catch { /* already stopped */ }
        droneRef.current = null;
      }
      if (ctxRef.current && ctxRef.current.state !== 'closed') {
        ctxRef.current.close().catch(() => {});
        ctxRef.current = null;
      }
      droneGainRef.current = null;
      lastStepPhase.current = 0;
      return;
    }

    // Create audio context and ambient drone
    const ctx = new AudioContext();
    ctxRef.current = ctx;

    // Ambient drone — very subtle 60Hz sine wave
    const droneOsc = ctx.createOscillator();
    droneOsc.type = 'sine';
    droneOsc.frequency.value = 60;

    const droneGain = ctx.createGain();
    droneGain.gain.value = 0.02;
    droneGainRef.current = droneGain;

    droneOsc.connect(droneGain);
    droneGain.connect(ctx.destination);
    droneOsc.start();
    droneRef.current = droneOsc;

    return () => {
      if (droneRef.current) {
        try { droneRef.current.stop(); } catch { /* already stopped */ }
        droneRef.current = null;
      }
      if (ctxRef.current && ctxRef.current.state !== 'closed') {
        ctxRef.current.close().catch(() => {});
        ctxRef.current = null;
      }
      droneGainRef.current = null;
    };
  }, [isActive]);

  // Sync footstep clicks with head bob phase
  useFrame(() => {
    if (!isActive || !ctxRef.current || ctxRef.current.state !== 'running') return;
    if (!settings.headBobEnabled) return;

    const ctx = ctxRef.current;
    const now = performance.now() / 1000;
    // Head bob uses a sin wave at ~walking frequency (~2 steps/sec)
    // We detect zero-crossings going positive as step events
    const bobFreq = 2 * settings.moveSpeed;
    const phase = Math.sin(now * bobFreq * Math.PI * 2);
    const prevPhase = lastStepPhase.current;

    // Detect upward zero crossing (step impact moment)
    if (prevPhase <= 0 && phase > 0) {
      playStepClick(ctx);
    }
    lastStepPhase.current = phase;
  });

  return null;
}

/**
 * Play a short percussive click to simulate a footstep.
 * Uses a brief oscillator burst at 200-300Hz with fast decay.
 */
function playStepClick(ctx: AudioContext) {
  const osc = ctx.createOscillator();
  osc.type = 'triangle';
  osc.frequency.value = 200 + Math.random() * 100; // 200-300Hz variation

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.04, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);

  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + 0.1);
}
