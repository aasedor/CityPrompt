"""Reference-specific finite wardrobe plan. Coordinates are source rest metres.

The image manifest and appearance_styles.json remain the visual authorities;
these values author their garment topology rather than replacing either source.
"""

PILOT_IDS = ('people-pilot-creative', 'people-community-kai', 'people-pilot-neighbour')


def outfit(top, bottom, shoe, **kw):
    return dict(dict(top=top, bottom=bottom, shoe=shoe, sleeve='long', lower='trousers',
                     leg_width=1., accessories=()), **kw)


WARDROBES = {
    'people-pilot-commuter': outfit('#95482f', '#242d39', '#ece6da', opening=True),
    'people-pilot-neighbour': outfit('#202b43', '#e3ddcd', '#544034'),
    'people-pilot-creative': dict(top='#929d86', bottom='#929d86', shoe='#e5ddcd', sleeve='short', lower='dress', hem=.55, leg_width=1., accessories=('belt',), wrap=True),
    'people-community-ava': outfit('#2d7774', '#303338', '#d5d4c9', accessories=('crescent_bag',), piping=True),
    'people-community-noah': dict(top='#363838', bottom='#a1acb5', shoe='#e4e3d3', sleeve='short', lower='trousers', leg_width=1.33, accessories=('sling', 'watch')),
    'people-community-zara': dict(top='#ac624a', bottom='#ac624a', shoe='#9c7351', sleeve='long', lower='dress', hem=.36, leg_width=1., accessories=('belt',), wrap=True, boot=True),
    'people-community-leo': outfit('#6f293d', '#514138', '#ced7de', stripes=True, collar=True, accessories=('cap',), leg_width=1.3),
    'people-community-imani': outfit('#cab998', '#594239', '#634a35', opening=True, blazer=True, leg_width=1.35),
    'people-community-luca': outfit('#345541', '#273442', '#66503d', hoodie=True),
    'people-community-nina': outfit('#735368', '#3a383d', '#4b2532', accessories=('shoulder_bag',), leg_width=1.4, cropped=True),
    'people-community-owen': outfit('#a28043', '#293440', '#6b4d35', plaid=True, collar=True, boot=True),
    'people-community-amara': outfit('#547c99', '#292b2e', '#eee5d2', opening=True, undershirt='#e4d58c', cropped=True, accessories=('backpack_olive',)),
    'people-community-mateo': dict(top='#a15a43', bottom='#3f4144', shoe='#eeeae2', sleeve='short', lower='trousers', leg_width=1., accessories=(), collar=True),
    'people-community-clara': outfit('#a39583', '#4d5c4d', '#9c7d5e', opening=True, coat=True),
    'people-community-kai': dict(top='#267c82', bottom='#c5c2b3', shoe='#e8e5d8', sleeve='short', lower='shorts', leg_width=1.3, accessories=('backpack',), socks=True),
    'people-community-ines': outfit('#8c523b', '#536c86', '#262a2c', opening=True, undershirt='#33363a', cropped=True, boot=True),
    'people-community-jules': outfit('#876341', '#354759', '#514333', opening=True, undershirt='#7c7b75', accessories=('beanie',), leg_width=1.28),
    'people-community-sana': dict(top='#92596b', bottom='#2d4355', shoe='#ede9e0', sleeve='threequarter', lower='trousers', leg_width=1.4, accessories=('tote_cream', 'books'), hightop=True),
    'people-community-felix': outfit('#355c45', '#788d9c', '#deddd4', hoodie=True, accessories=('backpack', 'laptop'), leg_width=1.28),
    'people-community-rhea': dict(top='#eee8d6', bottom='#2c3f51', shoe='#ac855e', sleeve='none', lower='skirt', hem=.34, leg_width=1., accessories=('tote_olive',), sandal=True),
    'people-community-andre': outfit('#3e4248', '#3e4248', '#25292b', opening=True, undershirt='#22262a', blazer=True),
    'people-community-elena': dict(top='#91aaad', bottom='#91aaad', shoe='#f2eee5', sleeve='none', lower='trousers', leg_width=1.4, accessories=('belt',)),
    'people-community-amir': dict(top='#897054', bottom='#c8b89c', shoe='#544332', sleeve='short', lower='trousers', leg_width=1., accessories=(), boot=True),
}


def coverage(wardrobe, coordinate, neck=1.51, shoulder=.215, wrist=.706):
    """Material underlay on the uncut source anatomy avoids open skin holes."""
    x, y, z = coordinate
    arm_limit = {'none': shoulder + .005, 'short': shoulder + .17,
                 'threequarter': wrist - .13, 'long': wrist - .035}[wardrobe['sleeve']]
    # A T-pose shoulder rises above the central neckline. Follow that surface
    # rather than cutting the entire garment with a horizontal neck plane.
    neckline = neck - .025 + max(0, abs(x) - (.055 if wardrobe.get('wrap') else .105)) * 2.2
    if wardrobe.get('wrap') and y < 0:
        neckline -= max(0, 1 - abs(x) / .115) * .17
    if z > .99 and z < neckline and abs(x) < arm_limit:
        if wardrobe.get('opening') and y < 0 and abs(x) < .06:
            return 'shirt'
        return 'jacket'
    if z < 1.04:
        if wardrobe['lower'] in ('dress', 'skirt'):
            return 'skin'
        if wardrobe['lower'] == 'shorts' and z < .60:
            return 'socks' if wardrobe.get('socks') and .11 < z < .31 else 'skin'
        if z > .10:
            return 'trousers'
    return 'skin'
