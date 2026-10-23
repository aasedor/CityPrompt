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
_DATA = Path(__file__).resolve().parents[1] / 'data'
_INCLUSIVE_PEOPLE = json.loads((_DATA / 'inclusive_people.json').read_text())
_REGISTRY = json.loads((_DATA / 'project_detail_models.json').read_text())
_PEOPLE_MODELS = frozenset(model for model in _REGISTRY['props']
                         if model.startswith(('people-pilot-', 'people-community-'))
                         or model in _INCLUSIVE_PEOPLE)


def is_people_model(variant: str) -> bool:
    return variant in _PEOPLE_MODELS


def resolve_people_action(variant: str, action: str | None) -> PeopleAction:
    """Apply the asset's captured-pose default and enforce its supported actions."""
    representation = _INCLUSIVE_PEOPLE.get(variant)
    if action is None:
        action = representation['defaultAction'] if representation else 'standing'
    if action not in PEOPLE_ACTIONS:
        raise ValueError('Unknown saved people action')
    if representation and action not in representation['supportedActions']:
        raise ValueError('Unsupported people action for this fixed-pose model')
    return action


def people_action_direction(project_details: dict | None) -> str:
    """Describe authored actions, conditional on source visibility, without a crowd brief.

    A saved-details instance represents the entire collection, not individual
    people. Action counts describe saved representations; groups also report
    their actual person count. Neither is a visible headcount or permission to
    bring offscreen actors into frame. Source poses bind identity.
    """
    counts: Counter[str] = Counter()
    representations: Counter[str] = Counter()
    person_count = 0
    for prop in (project_details or {}).get('props', []):
        variant = prop.get('variant', '')
        if not is_people_model(variant):
            continue
        action = resolve_people_action(variant, prop.get('people_action'))
        counts[action] += 1
        representation = _INCLUSIVE_PEOPLE.get(variant)
        person_count += representation['personCount'] if representation else 1
        if representation:
            representations[variant] += 1
    if not counts:
        return ''
    actions = '; '.join(f'{counts[action]} {_ACTION_TEXT[action]}'
                        for action in PEOPLE_ACTIONS if counts[action])
    walking = (
        'For visible walking people, use relaxed human weight transfer, heel-to-toe steps, '
        'opposing arm swing and individual timing; retain their captured route and speed '
        'while replacing low-polygon joint stiffness. '
    ) if counts['walking'] else ''
    fixed_poses = ''
    if representations:
        inventory = '; '.join(
            f"{count} representation(s) of {_INCLUSIVE_PEOPLE[variant]['description']} "
            f"({_INCLUSIVE_PEOPLE[variant]['personCount']} people per representation)"
            for variant, count in sorted(representations.items())
        )
        fixed_poses = (
            f'People represented by saved models: {person_count} (not a required visible headcount). '
            f'Fixed pose representation inventory: {inventory}. '
            'Fixed pose models are not animated in the 3D preview; their supported action describes '
            'the captured pose. Preserve each group arrangement, relative positions and child or '
            'infant proportions; a stroller group action applies to its adult, while the infant '
            'remains supported in the stroller. Preserve the actual mobility aids, guide dog and '
            'harness, wheelchairs, rollator, white cane and stroller shown in the source, including '
            'hand, foot, wheel and aid contact. Do not detach, remove, exchange or transform them, '
            'separate family groups or invent unsupported actions. '
        )
    return (
        'SAVED PEOPLE ACTIONS: For authored people actually visible in the source, preserve each '
        'person\'s identity, captured position and assigned action. Saved action inventory '
        f'(not a required visible headcount): {actions}. '
        'Action counts refer to saved representations; a family group is one representation. '
        'Use each captured pose to associate the action with its person; these saved actions '
        'take precedence over generic crowd directions. Animate the assigned action '
        'naturally in video and depict a faithful moment of it in a still image. '
        + walking + fixed_poses +
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
