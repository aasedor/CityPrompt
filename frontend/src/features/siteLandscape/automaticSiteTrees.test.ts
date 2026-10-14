import { describe, expect, it } from 'vitest';
import { mergeSavedSiteLandscape } from './automaticSiteTrees';

describe('site settings saved after background landscape compilation', () => {
  it('preserves the compiled recipe and saved preference without losing unsaved site edits', () => {
    const recipe = {state:'compiled',source_hash:'current'};
    expect(mergeSavedSiteLandscape({community_3d_landscape:null, community_3d_landscape_mode:'automatic',
      community_3d_automatic_trees:true, site_name:'Unsaved name'},
    {community_3d_landscape:recipe,community_3d_automatic_trees:true})).toEqual({
      community_3d_landscape:recipe,community_3d_landscape_mode:undefined,
      community_3d_automatic_trees:true,site_name:'Unsaved name',
    });
  });
  it('does not restore a landscape removed elsewhere while the site form was open', () => {
    expect(mergeSavedSiteLandscape({community_3d_landscape:{state:'compiled'},community_3d_automatic_trees:true},
      {community_3d_landscape_mode:'placed_objects_only',community_3d_automatic_trees:false})).toMatchObject({
      community_3d_landscape:undefined,community_3d_landscape_mode:'placed_objects_only',community_3d_automatic_trees:false,
    });
  });
});
