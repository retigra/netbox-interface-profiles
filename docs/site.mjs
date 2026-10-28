// Build settings shared by the Astro config and the version components.
//
// Every version of the docs is a separate build, published to its own folder on GitHub Pages
// (e.g. /netbox-interface-profiles/0.1/). The version to build is set with DOCS_VERSION.

export const repository = 'wouterdebruijn/netbox-interface-profiles';

/** Path of the GitHub Pages project site, which holds every version folder and versions.json. */
export const root = '/netbox-interface-profiles/';

/** Version being built: "dev" for main, "X.Y" for a release, or "latest" for the newest release. */
export const version = process.env.DOCS_VERSION || 'dev';
