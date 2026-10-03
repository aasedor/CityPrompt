import { createContext, useContext, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';

type Cutout = number[][] | null;
const CutoutContext = createContext<Cutout>(null);
const SetCutoutContext = createContext<Dispatch<SetStateAction<Cutout>>>(() => {});

/** Only the prepared-ground layer subscribes to cursor-driven cutout changes.
 * Keep the globe and saved design out of the draft's update/persistence path. */
export function StreetPreviewGroundProvider({children}: {children: ReactNode}) {
  const [cutout,setCutout] = useState<Cutout>(null);
  return <SetCutoutContext.Provider value={setCutout}>
    <CutoutContext.Provider value={cutout}>
      {children}
      {cutout && <group userData={{streetPreviewGround: true, editorPreview: true}} />}
    </CutoutContext.Provider>
  </SetCutoutContext.Provider>;
}
export const useStreetPreviewGround = () => useContext(CutoutContext);
export const useSetStreetPreviewGround = () => useContext(SetCutoutContext);
