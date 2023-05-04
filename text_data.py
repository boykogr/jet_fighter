from random import choice

default_names = [
    'Dead Baron',
    'Captain Crash',
    'Yossarian',
    'Thunderbolt',
    'Major Screw-up',
    'Rocketman',
    'Lt. Limpdick',
    'General Failure',
    'Captain Major',
    'Kamikaze Girl'
]

empty_names = [
    'Empty loser',
    'Empty Vessel',
    'Identity Crisis',
    'The Invisible',
    'Coward'
]

mission_texts = {
    1: [
        'Destroy as many Spy Balloons as you can',
        'Enemy presence: Minimal',
        'Mission time: 30 seconds',
        'Press any key to start'
    ],
    2: [
        'Protect our secrets from the Spy Balloons',
        'Enemy presence: Light',
        'Mission time: 30 seconds',
        'Press any key to start'
    ],
    3: [
        'Protect the sector',
        'Enemy presence: Medium',
        'Mission time: 45 seconds',
        'Press any key to start'
    ],
    4: [
        'Survive and destroy the enemy Spy Balloons',
        'Enemy presence: Heavy',
        'Mission time: 60 seconds',
        'Press any key to start'
    ],
    5: [
        'We were betrayed! Mission compromised!',
        'Enemy presence: Very heavy',
        'Survive for as long as you can',
        'Press any key to start'
    ]
}

intact_texts = [
    "Plane intact! You're a legend + 200",
    'Aircraft undamaged! Additional +200 fame',
    'Not a scratch! + 200 fame'
]
damaged_texts = [
    'Plane fully repaired',
    'We bought you a new plane, son.',
    'Aircraft fixed and ready for flight'
]


def mission_outcome(intact, total_points, mission_points):
    if intact:
        return [
            choice(intact_texts),
            f'Fame gained in the mission: {mission_points}',
            f'Total fame: {total_points}',
            'Press any key to continue'
        ]
    else:
        return [
            choice(damaged_texts),
            f'Fame gained in the mission: {mission_points}',
            f'Total fame: {total_points}',
            'Press any key to continue'
        ]

end_texts = [
    ['You were killed in action,',
     'but it was Easter.',
     'Jesus was resurrected',
     'and everybody rejoiced',
     'Nobody was sad about you.',
     'Press any key to continue'],
    ['You survived the crash,',
     'but you were taken prisoner',
     'in a GULAG in North Carolina.',
     'Deemed too annoying, you were soon released',
     'in the woods, where you met a bear.',
     'It lived happily ever after.',
     'Press any key to continue'],
    ['You ejected a moment before impact,',
     'or as your fake girlfriend calls it - "Not again!".',
     'You survived to live in shame with this memory.',
     'Press any key to continue'],
    ['You gained so much fame,',
     'that you got the nickname "Fameboy"',
     'and had several massage parlours',
     'in Thailand named after you.',
     'Press any key to continue'],
    ['You performed so badly, that you were',
     'deemed an enemy of the state.',
     'Your father disowned you, but you later learned',
     'he was never your father, he just owned you.',
     'Press any key to continue'],
    ['You gained some fame and lived',
     'as a small local celebrity',
     'on the bottom of the ocean until you died.',
     'Press any key to continue'],
    ['You fell in the ocean and a turtle dragged you to the shore',
     'You were captured by the local Home Owners Association',
     "They made you the newest addition to the local zoo's exhibit.",
     'Visitors come from far and wide to marvel',
     'at your impressive gaming skills',
     'Press any key to continue'],
    ["You survived the war, but your ego didn't",
     "You're now known as the most annoying person on the planet",
     "with a talent for reminding everyone how good",
     'you were at that one game that one time.',
     'Press any key to continue'],
    ["Congratulations, you've beaten the game!",
     "But now what? You realize you've spent",
     "so much time playing that you've",
     "forgotten how to do anything else.",
     'Time to start all over again.',
     'Press any key to continue'],
    ["You managed to eject just in time,",
     "but your parachute malfunctioned",
     "and you landed in a clown convention.",
     "You've never been more afraid in your life.",
     "Press any key to continue"],
    ["Congratulations, you've become a viral sensation.",
     "The video of your failed barrel roll has millions of views.",
     "Press any key to continue"]
]
