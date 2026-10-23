"""Saved actor actions: one bounded, server-owned direction for image and video."""
from collections import Counter
import json
from pathlib import Path
from typing import Literal, get_args


PeopleAction = Literal[
    'standing', 'walking', 'running', 'sitting', 'talking', 'lying_down',
    'waving', 'using_phone', 'reading', 'waiting', 'looking_around', 'pointing',
    'stretching', 'dancing', 'cheering',
]
PEOPLE_ACTIONS = get_args(PeopleAction)
_ACTION_TEXT = {action: action.replace('_', ' ') for action in PEOPLE_ACTIONS}
_ACTION_TEXT['using_phone'] = 'using a phone'
_REGISTRY = json.loads((Path(__file__).resolve().parents[1] / 'data/project_detail_models.json').read_text())
_PEOPLE_MODELS = frozenset(model for model in _REGISTRY['props']
                         if model.startswith(('people-pilot-', 'people-community-')))


def is_people_model(variant: str) -> bool:
    return variant in _PEOPLE_MODELS


def people_action_direction(project_details: dict | None) -> str:
    """Describe authored actions, conditional on source visibility, without a crowd brief.

    A saved-details instance represents the entire collection, not individual
    people. Counts therefore describe saved intent, never a visible headcount or
    permission to bring offscreen actors into frame. Source poses bind identity.
    """
    counts: Counter[str] = Counter()
    for prop in (project_details or {}).get('props', []):
        if not is_people_model(prop.get('variant', '')):
            continue
        action = prop.get('people_action')
        if action is None:
            action = 'standing'
        if action not in PEOPLE_ACTIONS:
            raise ValueError('Unknown saved people action')
        counts[action] += 1
    if not counts:
        return ''
    actions = '; '.join(f'{counts[action]} {_ACTION_TEXT[action]}'
                        for action in PEOPLE_ACTIONS if counts[action])
    walking = (
        'For visible walking people, use relaxed human weight transfer, heel-to-toe steps, '
        'opposing arm swing and individual timing; retain their captured route and speed '
        'while replacing low-polygon joint stiffness. '
    ) if counts['walking'] else ''
    return (
        'SAVED PEOPLE ACTIONS: For authored people actually visible in the source, preserve each '
        'person\'s identity, captured position and assigned action. Saved action inventory '
        f'(not a required visible headcount): {actions}. '
        'Use each captured pose to associate the action with its person; these saved actions '
        'take precedence over generic crowd or walking directions. Animate the assigned action '
        'naturally in video and depict a faithful moment of it in a still image. '
        + walking +
        'Do not add actors, reveal offscreen people, duplicate people or invent background activity. '
        'Keep seated people on their authored support and lying people on their placement surface; '
        'do not invent seats, props, routes or interactions. Keep ground contact and occlusion. '
        'Actions never authorize moving buildings, streets, paths, terrain or furniture.'
    )


def append_people_action_direction(prompt: str, direction: str, *, max_length: int = 32_000) -> str:
    """Keep the authoritative action suffix even when custom text fills the budget."""
    if not direction:
        return prompt
    if prompt.endswith(direction):
        prompt = prompt[:-len(direction)].rstrip()
    suffix = '\n\n' + direction
    if len(suffix) > max_length:
        raise ValueError('Prompt limit cannot fit saved people actions')
    return prompt[:max_length - len(suffix)].rstrip() + suffix
