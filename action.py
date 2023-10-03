#!/usr/bin/env python3

import argparse
from github import Github, GithubException
import json
import os
import sys

NOTE = "\n\n*Note: This comment is automatically posted and updated by the " \
       "Comment GitHub Action.* "

def gh_tuple_split(s):
    sl = s.split('/')
    if len(sl) != 2:
        raise RuntimeError("Invalid org or dst format")

    return sl[0], sl[1]

def main():

    parser = argparse.ArgumentParser(
        description="GH Action script for contribution management",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--note', action='store',
                        required=False,
                        help='Note string.')

    parser.add_argument('-m', '--message', action='store',
                        required=False,
                        help='Messages to post.')

    parser.add_argument('-r', '--reaction', action='store',
                        required=False,
                        help='Reaction to check for.')

    print(sys.argv)

    args = parser.parse_args()

    note = NOTE
    if args.note:
        note = args.note
    if not note.startswith("\n\n"):
        note = "\n\n" + note

    # Retrieve main env vars
    action = os.environ.get('GITHUB_ACTION', None)
    workflow = os.environ.get('GITHUB_WORKFLOW', None)
    org_repo = os.environ.get('GITHUB_REPOSITORY', None)

    print(f'Running action {action} from workflow {workflow} in {org_repo}')

    evt_name = os.environ.get('GITHUB_EVENT_NAME', None)
    evt_path = os.environ.get('GITHUB_EVENT_PATH', None)
    workspace = os.environ.get('GITHUB_WORKSPACE', None)

    print(f'Event {evt_name} in {evt_path} and workspace {workspace}')

    token = os.environ.get('GITHUB_TOKEN', None)
    if not token:
        sys.exit('Github token not set in environment, please set the '
                 'GITHUB_TOKEN environment variable and retry.')

    if not ("pull_request" in evt_name):
        sys.exit(f'Invalid event {evt_name}')

    with open(evt_path, 'r') as f:
        evt = json.load(f)

    pr = evt['pull_request']
    user = pr['user']
    login = user['login']

    print(f'user: {login} PR: {pr["title"]}')

    gh = Github(token)

    org, repo = gh_tuple_split(org_repo)

    print(f'org: {org} repo: {repo}')

    tk_usr = gh.get_user()
    gh_repo = gh.get_repo(org_repo)
    gh_pr = gh_repo.get_pull(int(pr['number']))

    comment = None
    for c in gh_pr.get_issue_comments():
        if c.user.login == tk_usr.login and note in c.body:
            comment = c
            break

    message = args.message + note
    found = False
    if not comment:
        print('Creating comment')
        gh_pr.create_issue_comment(message)
    else:
        print('Updating comment')
        comment.edit(message)
        if args.reaction:
            for r in comment.get_reactions():
                print(r.content)
                if r.user == gh_pr.user and r.content == args.reaction:
                    print(f"Found reaction {args.reaction} by pr-user in comment")
                    found = True

    with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
        print(f"found_reaction={found}", file=fh)

    sys.exit(0)

if __name__ == '__main__':
    main()
