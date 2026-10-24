import {useEffect,useState} from 'react';

/** Use one Blob URL for the native player and download. Large data URLs are
 * kept for API transport only, and are never assigned to the media element. */
export function LocalVideoPreview({source,mimeType,showPlayer=true}:{source:string;mimeType:string;showPlayer?:boolean}) {
  const [media,setMedia]=useState<{source:string;url:string;failed:boolean}|null>(null);
  const [error,setError]=useState(false);
  useEffect(()=>{
    let url:string|undefined;
    setError(false);
    try {
      const encoded=source.split(',')[1];
      if(!source.startsWith('data:video/') || !encoded)throw new Error('Invalid preview');
      const binary=atob(encoded), bytes=new Uint8Array(binary.length);
      for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
      url=URL.createObjectURL(new Blob([bytes],{type:mimeType}));
      setMedia({source,url,failed:false});
    }catch {setMedia(null);setError(true);}
    return ()=>{if(url)URL.revokeObjectURL(url);};
  },[source,mimeType]);
  const current=media?.source===source?media:null;
  return <>
    {current && showPlayer && <video key={current.url} controls muted playsInline preload="metadata"
      className="aspect-video max-h-36 w-full rounded-lg bg-black object-contain"
      aria-label="Local route preview" src={current.url}
      onError={()=>setMedia(value=>value?.url===current.url?{...value,failed:true}:value)}/>}
    {(error||current?.failed) && <p role="alert" className="my-2 text-xs text-amber-200">This browser cannot play the preview here. Download the preview to watch it in a video player, or try another browser.</p>}
    <a href={current?.url??source} download={`city-prompt-guide.${mimeType.includes('mp4')?'mp4':'webm'}`}
      className="mt-2 inline-flex min-h-11 items-center rounded-full border border-white/20 px-3 text-[11px] font-bold text-white">Download preview</a>
  </>;
}
