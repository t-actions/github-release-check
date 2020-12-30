# Release Assets Check Actions

Github Actions to check release assets SHA256

Need to have a sha256 file in release assets.
```bash
sha256sum * > something.sha256
```

## Usage

```yaml
- uses: t-actions/release-check@master
  with:
    # Release tags, split by space
    # Default is the latest release
    tag: ''

    # Github token for related repository
    # Default: ${{ github.token }}
    token: ''

    # Github repository for the tag
    # Default: ${{ github.repository }}
    repo: ''
```
