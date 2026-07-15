# Bee-static directory rules

Use this file as a compact, editable record of confirmed repository conventions. Validate every rule against the current repository before relying on it.

## Confirmed from the request

- Store downloaded iconfont artifacts under the repository-root shape `hashIconfontDir/<hash>/...`.
- Check whether `hashIconfontDir` exists. Reuse it only when it is a real directory; create it after confirmation when absent; stop when the path is a file or symbolic link.
- Downloaded iconfont directories normally use the shape `font_<project-id>_<hash>`, such as `/Users/chen_wei/Downloads/font_4071061_semole6prt`.
- Extract only the final underscore-delimited segment (`semole6prt`) as the destination hash folder. Place the selected directory's contents directly under `hashIconfontDir/semole6prt/`.
- Do not include the `font_<project-id>_` prefix in the repository destination.
- If the selected folder does not match the confirmed naming pattern, do not infer a hash from modification time or file contents; ask the user.

## Destination inference

Rank evidence from strongest to weakest:

1. An exact destination supplied by the user.
2. The final hash extracted from a matching `font_<project-id>_<hash>` source directory and placed below the fixed `hashIconfontDir` root.
3. A matching path embedded in a manifest, stylesheet, generated iconfont file, or source-code CDN reference.
4. An existing directory for the same project, asset family, and artifact identity.
5. Recent Git history showing the same file family placed in a particular tree.
6. Filename or visual-content similarity alone.

Require multiple signals when choosing a hash directory. Do not select the lexically greatest or most recently modified hash merely because it is newest. Do not derive a new hash unless the repository or build pipeline contains a confirmed deterministic rule.

When several existing hashes are plausible, show the candidates with evidence and ask the user to choose before the final upload confirmation.

## Public URL convention

Use the confirmed test CDN prefix:

`https://static-cdn-test.mifengjiaoyu.com/`

Append the URL-encoded repository-relative file path directly to this prefix. For example:

`hashIconfontDir/deadbeef/iconfont.woff2`

becomes:

`https://static-cdn-test.mifengjiaoyu.com/hashIconfontDir/deadbeef/iconfont.woff2`

Check the final URL before confirmation. Treat 2xx/3xx as a name collision and explicit overwrite risk, 404/410 as available, and every other result as unknown and blocking.
