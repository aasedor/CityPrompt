export interface ModelBenchmarkAssetStats {
  sha256: string;
  bytes: number;
  primitives: number;
  triangles: number;
  materials: number;
}

export interface ModelBenchmarkAsset {
  id: string;
  name: string;
  relativePath: string;
  comparisonKind?: 'optimization' | 'delivery-control';
  original: ModelBenchmarkAssetStats;
  optimized: ModelBenchmarkAssetStats;
}

export const MODEL_BENCHMARK_COUNTS = [1, 10, 25] as const;

export const MODEL_BENCHMARK_ASSETS: readonly ModelBenchmarkAsset[] = [
  {
    id: 'daylight-sawtooth-default',
    name: 'Daylight Sawtooth Factory · default',
    relativePath:
      'seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/'
      + 'daylight-sawtooth-factory-v98-extended/assembled--default--lod0.glb',
    original: {
      sha256: '274c5f16da5fa7ed452a1d0b15ad00af04c586921f8f2a5eb75c43d1baee5acb',
      bytes: 7_838_812,
      primitives: 2_011,
      triangles: 41_656,
      materials: 2_011,
    },
    optimized: {
      sha256: '8475ca4007007841bf6ed53eb91f23c278f3776f21fc803965b7501fdb907229',
      bytes: 3_922_560,
      primitives: 15,
      triangles: 41_656,
      materials: 15,
    },
  },
  {
    id: 'daylight-sawtooth-extended',
    name: 'Daylight Sawtooth Factory · extended',
    relativePath:
      'seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/'
      + 'daylight-sawtooth-v98-native-tiers/assembled--extended--lod0.glb',
    original: {
      sha256: '6d197e38aee4d223243bb0a25802273c1da298b23e6bce0825ff20fe1f1b2464',
      bytes: 17_608_336,
      primitives: 2_011,
      triangles: 41_656,
      materials: 2_011,
    },
    optimized: {
      sha256: 'b162147b7120b56715e826ab3b6e17dbd66d5c52d84146c35cf601c24a05eee8',
      bytes: 13_747_292,
      primitives: 15,
      triangles: 41_656,
      materials: 15,
    },
  },
  {
    id: 'old-montreal-textile',
    name: 'Old Montréal Textile',
    relativePath:
      'seed/model-library/objects/lego/3c9deca4-522d-4b7b-ad11-d4f291678077/'
      + 'old-montreal-textile-v98-native-tiers/assembled--extended--lod0.glb',
    original: {
      sha256: '4719dfc61229d706eb453711480943c32fd3e8f4ffa60e6f28da03bea7502c25',
      bytes: 18_461_184,
      primitives: 1_993,
      triangles: 39_624,
      materials: 1_993,
    },
    optimized: {
      sha256: '4d1acee1df114d998e0b3283537738c4bf762c86ce8cffc789f5520806b87fcc',
      bytes: 14_690_064,
      primitives: 12,
      triangles: 39_624,
      materials: 12,
    },
  },
  {
    id: 'restored-kyoto-machiya-control',
    name: 'Restored Kyoto Machiya · delivery A/A control',
    relativePath:
      'seed/model-library/objects/lego/651daf60-b797-4f95-b1e7-6364d6dc0665/'
      + 'restored-kyoto-machiya/assembled--default--lod0.glb',
    comparisonKind: 'delivery-control',
    original: {
      sha256: '5a785be0b30a37be50c1228cf0e5d00636b13f745bad753a103dcfc77a68bb9c',
      bytes: 43_953_548,
      primitives: 869,
      triangles: 12_820,
      materials: 10,
    },
    optimized: {
      sha256: '5a785be0b30a37be50c1228cf0e5d00636b13f745bad753a103dcfc77a68bb9c',
      bytes: 43_953_548,
      primitives: 869,
      triangles: 12_820,
      materials: 10,
    },
  },
];
