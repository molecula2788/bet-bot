from datetime import datetime, timedelta
import config

usage_bet_create_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Usage*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-create resolve_date vote_end_date question choice1 choice2 ...'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Example*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-create "2021-10-23 23:59:59" "2021-05-01 23:59:59" \"Cât o să fie euro?\" \"4.9 - 4.95\" \"4.95 - 4.96\" \"4.96 - 4.97\"'
	}
    }
]

usage_bet_create_text = 'Usage: bet-create resolve_date question choice1 choice2 ...'

def bet_created_blocks(bet_id, question, user):
    return [
	{
	    'type': 'section',
	    'text': {
		'type': 'mrkdwn',
		'text': '*New bet*'
	    }
	},
	{
	    'type': 'section',
	    'text': {
		'type': 'mrkdwn',
		'text': f'\"{question}\", created by <@{user}>'
	    }
	},
        {
            'type': 'section',
            'text': {
		'type': 'mrkdwn',
		'text': f'Run `@{config.my_name} bet-info {bet_id}` for more details'
            }
        }
]

def bet_created_text(bet_id, question):
    return f'New bet: \"{question}\"'

usage_bet_info_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Usage*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-info id'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Example*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-info 1234'
	}
    }
]

usage_bet_info_text = 'Usage: bet-info id'

bet_not_found_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': 'Bet not found'
	}
    }
]

bet_not_found_text = 'Bet not found'

def invalid_choice_blocks(choice):
    return [
        {
	    'type': 'section',
	    'text': {
	        'type': 'mrkdwn',
	        'text': f'Invalid choice: {choice}'
	    }
        }
    ]

def invalid_choice_text(choice):
    return f'Invalid choice: {choice}'

def bet_info_blocks(bet_id, question, choices, correct_choice_id,
                    resolve_date_ts, voting_end_date_ts, votes, user_info):
    question_text = ''
    question = question.split('\n')

    question_text = f'*{question[0]}*'

    for line in question[1:]:
        if len(line) > 0:
            question_text += f'\n*{line}*'
        else:
            question_text += f'\n'

    b = [
        {
	    'type': 'section',
	    'text': {
	        'type': 'mrkdwn',
	        'text': f'{question_text}'
	}
        }
    ]

    for i, c in enumerate(choices):
        choice_id, choice = c
        if correct_choice_id:
            if choice_id == correct_choice_id:
                s = f'*{i+1})* {choice} :white_check_mark:'
            else:
                s = f'*{i+1})* {choice} :x:'
        else:
            s = f'*{i+1})* {choice}'

        choice = [
            {
                'type': 'section',
		'text': {
		    'type': 'mrkdwn',
		    'text': s
		}
	    }
        ]

        if choice_id in votes:
            users = votes[choice_id]

            for user_id, ts in users:
                ctx = {
                    'type': 'context',
                    'elements': []
                }

                img_url = user_info[user_id]['avatar_url']
                user_name = user_info[user_id]['name']

                ctx['elements'].append({
                    'type': 'image',
                    'image_url': img_url,
                    'alt_text': user_name
                })

                ctx['elements'].append({
                    'type': 'mrkdwn',
                    'text': '{} since {}'.format(
                        user_name,
                        datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
                })
                choice.append(ctx)
        b.extend(choice)

    resolve_date = datetime.fromtimestamp(resolve_date_ts)
    voting_end_date = datetime.fromtimestamp(voting_end_date_ts)

    b.extend([
        {
            'type': 'divider'
        },
        {
            'type': 'section',
            'text': {
	        'type': 'mrkdwn',
	        'text': 'Resolves on {}'.format(resolve_date.strftime('%Y-%m-%d %H:%M:%S'))
            }
        },
        {
            'type': 'section',
            'text': {
	        'type': 'mrkdwn',
	        'text': 'Voting ends on {}'.format(voting_end_date.strftime('%Y-%m-%d %H:%M:%S'))
            }
        },
        {
            'type': 'section',
            'text': {
	        'type': 'mrkdwn',
	        'text': f'Use `@{config.my_name} vote id option_number` to vote. Example: `@{config.my_name} vote {bet_id} 2`'
            }
        }
    ])

    return b

bet_info_text = 'Bet info'

usage_bet_vote_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Usage*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> vote bet-id choice'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Example*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> vote 10 3'
	}
    }
]

usage_bet_vote_text = 'Usage: vote bet-id choice'

def vote_registered_blocks(question, choice):
    return [
        {
	    'type': 'section',
	    'text': {
	        'type': 'mrkdwn',
	        'text': '*Vote registered*'
	    }
        },
        {
	    'type': 'section',
	    'text': {
	        'type': 'mrkdwn',
	        'text': f'*Question*: {question}'
	    }
        },
        {
	    'type': 'section',
	    'text': {
	        'type': 'mrkdwn',
	        'text': f'*Your choice*: {choice}'
	    }
        }
    ]

vote_registered_text = 'Vote registered'

def bets_blocks(text, truncated):
    b = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*Ongoing bets*'
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'plain_text',
		'text': text
            }
        }
    ]

    if truncated:
        b.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Output has been truncated. Use `@{config.my_name} bets-all` to see all bets'
            }
        })
    b.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Use `@{config.my_name} bet-info id` for more details'
            }
        }
    )
    return b

bet_not_active_text = 'Bet not active'

bet_vote_has_ended = 'Voting has ended for this bet'

bet_vote_not_ended = 'Voting is still ongoing for this bet'

usage_bet_resolve_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Usage*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-resolve bet-id choice'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Example*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-resolve 10 3'
	}
    }
]

usage_bet_resolve_text = 'Usage: bet-resolve bet-id choice'

def bet_resolved_blocks(bet_id, question, correct_choice, winners):
    b = [
        {
            'type': 'section',
            'text': {
	        'type': 'mrkdwn',
	        'text': f'*Bet {bet_id} has ended*'
	    }
        },
        {
            'type': 'divider'
        },
        {
            'type': 'section',
            'text': {
	        'type': 'mrkdwn',
	        'text': f'*Question was:* {question}\n*Correct answer:* {correct_choice}'
	    }
        }
    ]

    winners_str = 'Congrats to the winners:\n'

    winners = sorted(winners, key = lambda p: p[1])
    for user_id, vote_ts, bet_end_ts in winners:
        vote_date = datetime.fromtimestamp(vote_ts)
        bet_end_date = datetime.fromtimestamp(bet_end_ts)

        delta = bet_end_date - vote_date

        s = f'<@{user_id}>: {delta.days} days {delta.seconds} seconds before\n'

        winners_str += s

    b.append({
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
	    'text': winners_str
        }
    })

    return b

def bet_resolved_text(bet_id, question, correct_choice):
    return f'Bet ended. Question was {question}. Correct answer: {correct_choice}'

usage_bet_delete_blocks = [
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Usage*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-delete id'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '*Example*'
	}
    },
    {
	'type': 'section',
	'text': {
	    'type': 'mrkdwn',
	    'text': '> bet-delete 1234'
	}
    }
]

usage_bet_delete_text = 'Usage: bet-delete id'

def user_joined_blocks(user_id):
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Welcome <@{user_id}>! Type `@{config.my_name} bets` to see ongoing bets, or `@{config.my_name} help` to see all the possible commands. Also check the pinned posts for more explanations'
            }
        }
    ]

help_blocks = [
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*Help*'
	}
    },
    {
        'type': 'divider'
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*bets* - view ongoing bets'
	}
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*bets-all* - view all bets, more detailed'
	}
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*my-bets* - view bets you\'ve taken part in'
	}
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*bet-info* - view details about one bet'
	}
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*vote* - vote in a bet'
	}
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'*bet-create* - create a bet'
	}
    },
    {
        'type': 'divider'
    },
    {
        'type': 'section',
        'text': {
	    'type': 'mrkdwn',
	    'text': f'All commands should be prefixed with the bot\'s name (e.g. `@{config.my_name} bets`)\nAll commands can take a `help` argument'
	}
    }
]
