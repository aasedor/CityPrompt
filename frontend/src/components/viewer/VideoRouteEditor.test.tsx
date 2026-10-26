import '@testing-library/jest-dom/vitest';
import {fireEvent,render,screen} from '@testing-library/react';
import {describe,it,expect,vi} from 'vitest';
import {VideoRouteEditor} from './VideoRouteEditor';
describe('camera route editing',()=>{
  it('draws a replacement route, undoes edits, and restores the original when cancelled',()=>{
    const change=vi.fn(),close=vi.fn(),points=[{x:.2,y:.3},{x:.6,y:.7}];
    render(<VideoRouteEditor points={points} onChange={change} onClose={close}/>);
    fireEvent.click(screen.getByRole('button',{name:'Draw new route'}));
    expect(change).toHaveBeenLastCalledWith([]);
    const target=screen.getByLabelText('Camera route drawing area');
    vi.spyOn(target,'getBoundingClientRect').mockReturnValue({left:0,top:0,width:100,height:100} as DOMRect);
    fireEvent.click(target,{clientX:40,clientY:60});
    expect(change).toHaveBeenLastCalledWith([{x:.4,y:.6}]);
    fireEvent.click(screen.getByRole('button',{name:'Undo route edit'}));
    expect(change).toHaveBeenLastCalledWith([]);
    fireEvent.click(screen.getByRole('button',{name:'Cancel route edits'}));
    expect(change).toHaveBeenLastCalledWith(points);expect(close).toHaveBeenCalledOnce();
  });
  it('moves a selected point and removes it without appending accidental points',()=>{
    const change=vi.fn();
    render(<VideoRouteEditor points={[{x:.2,y:.3},{x:.6,y:.7}]} onChange={change} onClose={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button',{name:'Select route point 1'}));
    const target=screen.getByLabelText('Camera route drawing area');
    vi.spyOn(target,'getBoundingClientRect').mockReturnValue({left:0,top:0,width:100,height:100} as DOMRect);
    fireEvent.click(target,{clientX:30,clientY:40});
    expect(change).toHaveBeenLastCalledWith([{x:.3,y:.4},{x:.6,y:.7}]);
    fireEvent.click(screen.getByRole('button',{name:'Select route point 2'}));
    fireEvent.click(screen.getByRole('button',{name:'Remove selected point'}));
    expect(change).toHaveBeenLastCalledWith([{x:.3,y:.4}]);
  });
});
