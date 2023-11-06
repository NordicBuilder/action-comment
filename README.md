# action-comment

Post or update a comment on a pull request.<br/>
In an update case it will check if a given reaction is present by the pull request author

## Usage
``` yaml

- uses: nordicbuilder/action-comment@v0.1
  with:
    # Token needed to post comments and add commits
    github-token: ''

    # The message to be posted
    message: ''

    # The note line. This is used to find the same comment for updating
    note: ''

    # The reaction emote to check if present.
    reaction:
```

## Outputs
The action provides these outputs:
* `found_reaction`: whether the reaction was found (`'true'` or `'false'`)
