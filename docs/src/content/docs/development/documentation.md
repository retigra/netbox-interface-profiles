---
title: Writing documentation
description: How the documentation is built, previewed and versioned.
sidebar:
  order: 2
---

The documentation is built with [Starlight](https://starlight.astro.build/) from the Markdown files in
`docs/src/content/docs/`. Every page has an **Edit page** link to its source on GitHub.

## Preview locally

Install Node.js 22 or later, then:

```bash
cd docs
npm ci
npm run dev
```

The site is served at <http://localhost:4321/netbox-interface-profiles/dev/> and reloads on every change. Run
`npm run build` to check that the site builds.

## Writing pages

- Add a Markdown file to one of the section folders: `getting-started/`, `guides/`, `reference/` or `development/`.
  It appears in the sidebar automatically, ordered by `sidebar.order` in its frontmatter.
- Every page needs a `title` and a `description` in its frontmatter.
- Link to other pages with relative links ending in a slash, e.g. `[synchronize](../synchronization/)`, so links
  work in every version.
- Use [asides](https://starlight.astro.build/guides/authoring-content/#asides) (`:::note`, `:::tip`, `:::caution`)
  for notes, and rename a page to `.mdx` to use
  [components](https://starlight.astro.build/components/using-components/) such as tabs and cards.

## Versions

Each version of the documentation is a separate build, published to its own folder on GitHub Pages by the
**Docs** workflow:

| Trigger                        | Published as                                                  |
| ------------------------------ | ------------------------------------------------------------- |
| Push to `main`                 | `/dev/`                                                       |
| Tag `vX.Y.Z`                   | `/X.Y/`, and `/latest/` when it is the newest release         |

Pre-release tags such as `v1.0.0-rc1` are not published. The workflow can also be run manually on `main` or a
release tag to rebuild that version.

The workflow keeps every published version on the `gh-pages` branch, together with `versions.json`, which feeds the
version selector, and an `index.html` that redirects to the latest release. Patch releases overwrite the folder of
their minor version, so the documentation of a release is updated by tagging a new patch release.

To remove a version, delete its folder and its entry in `versions.json` on the `gh-pages` branch, then run the
**Docs** workflow manually.
