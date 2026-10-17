import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { usePavingEditor } from './PavingEditor';
import { projectBenchContext, projectBenchFrame } from './projectBenches';
import type { PavingSurface } from './pavingSurfaces';

function Trial() {
  const [surfaces, change] = useState<PavingSurface[]>([]);
  const context = projectBenchContext(projectBenchFrame([], []));
  const editor = usePavingEditor({surfaces,change,context,locked:false,onActivate:()=>{}});
  return <>{editor.controls}<svg>{editor.plan}</svg>
    {[[0,0],[40,0],[40,18],[0,18],[30,18]].map(([x,y],i)=><button key={i} onClick={()=>editor.click({x,y})}>Point {i}</button>)}
    <output aria-label="Saved surface data">{JSON.stringify(surfaces)}</output></>;
}
describe('drawn parking controls',()=>{
  it('draws a lot, counts fixed spaces, changes direction and preserves its recipe when editing corners',()=>{
    render(<Trial/>);
    fireEvent.click(screen.getByRole('button',{name:'Draw parking lot'}));
    for(let i=0;i<4;i++)fireEvent.click(screen.getByRole('button',{name:`Point ${i}`}));
    fireEvent.click(screen.getByRole('button',{name:'Finish parking lot'}));
    expect(screen.getByText(/24 parking spaces/)).toBeInTheDocument();
    expect(screen.getByRole('combobox',{name:'Parking row direction'})).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Parking row direction'),{target:{value:'90'}});
    expect(screen.getByText(/16 parking spaces/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Paving corner'),{target:{value:'2'}});
    fireEvent.click(screen.getByRole('button',{name:'Move paving corner'}));
    fireEvent.click(screen.getByRole('button',{name:'Point 4'}));
    const saved=JSON.parse(screen.getByLabelText('Saved surface data').textContent!);
    expect(saved[0]).toMatchObject({material:'asphalt',parking:{version:1,rowAngle:90}});
    expect(screen.getByRole('button',{name:'Select parking lot 1'})).toHaveAttribute('aria-pressed','true');
  });
});
