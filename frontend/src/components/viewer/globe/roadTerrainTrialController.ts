export class TerrainTilesChangedError extends Error {}
export interface TerrainTrial {
  status:()=>{active:boolean;stale:boolean};
  setVisible:(show:boolean)=>void;
  dispose:()=>void;
}
export type TerrainTrialState='idle'|'measuring'|'refreshing'|'ready'|'original'|'error';

/** One owner, one in-flight build, three automatic attempts per manual request.
 * Late results are disposed and can never overwrite a newer view or unmount. */
export class RoadTerrainTrialController<T extends TerrainTrial> {
  trial:T|undefined;
  private abort:AbortController|undefined;
  private timer:ReturnType<typeof setTimeout>|undefined;
  private generation=0;
  private attempts=0;
  private disposed=false;
  private desired=false;
  constructor(private create:(signal:AbortSignal)=>Promise<T>,
    private changed:(state:TerrainTrialState,trial:T|undefined,error?:Error)=>void) {}

  private notify(state:TerrainTrialState,error?:Error) {
    if(!this.disposed)this.changed(state,this.trial,error);
  }
  private cancel() {
    this.generation++;this.abort?.abort();this.abort=undefined;
    clearTimeout(this.timer);this.timer=undefined;
  }
  build() {
    if(this.disposed)return;
    this.attempts=0;this.desired=true;void this.run();
  }
  show(show:boolean) {
    if(this.disposed)return;
    this.desired=show;
    if(!show){this.cancel();this.trial?.setVisible(false);this.notify('original');}
    else if(this.trial&&!this.trial.status().stale){this.trial.setVisible(true);this.notify('ready');}
    else this.build();
  }
  checkFreshness() {
    if(this.disposed||!this.trial?.status().stale)return;
    this.trial.dispose();this.trial=undefined;
    if(this.desired)this.schedule();else this.notify('original');
  }
  private schedule() {
    if(this.disposed||!this.desired)return;
    if(this.attempts>=3){
      this.notify('error',new Error('The map is still changing. Stop moving the view, then build the transition again.'));return;
    }
    this.attempts++;this.notify('refreshing');
    // Give a burst of tile events time to settle, without an unbounded loop.
    this.timer=setTimeout(()=>{this.timer=undefined;void this.run();},1500);
  }
  private async run() {
    this.cancel();this.trial?.dispose();this.trial=undefined;
    const generation=this.generation,abort=new AbortController();this.abort=abort;
    this.notify('measuring');
    try {
      const result=await this.create(abort.signal);
      if(this.disposed||abort.signal.aborted||generation!==this.generation){result.dispose();return;}
      this.trial=result;result.setVisible(this.desired);this.notify(this.desired?'ready':'original');
    } catch(error) {
      if(this.disposed||abort.signal.aborted||generation!==this.generation)return;
      if(error instanceof TerrainTilesChangedError)this.schedule();
      else this.notify('error',error instanceof Error?error:new Error('The trial could not be built.'));
    } finally {
      if(this.abort===abort)this.abort=undefined;
    }
  }
  dispose() {
    if(this.disposed)return;
    this.disposed=true;this.cancel();this.trial?.dispose();this.trial=undefined;
  }
}
