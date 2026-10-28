// Client-side helpers for switching between documentation versions.
//
// versions.json lives in the root of the GitHub Pages site and is updated by the docs workflow on every
// deploy, so older builds learn about newer versions without being rebuilt.

export interface Versions {
	/** The newest release, which is also published as "latest". Null until the first release. */
	latest: string | null;
	/** Every published version, "dev" first and releases newest first. */
	versions: string[];
}

let versions: Promise<Versions | null> | undefined;

/** Fetch versions.json once per page. Resolves to null when it is unavailable, e.g. in local development. */
export function loadVersions(root: string): Promise<Versions | null> {
	versions ??= fetch(`${root}versions.json`)
		.then((response) => (response.ok ? response.json() : null))
		.catch(() => null);
	return versions;
}

/** Return the URL of the current page in another version, falling back to that version's home page. */
export async function urlForVersion(root: string, current: string, target: string): Promise<string> {
	const home = `${root}${target}/`;
	const page = location.pathname.slice(`${root}${current}/`.length);
	if (!page) return home;

	const url = home + page;
	const response = await fetch(url, { method: 'HEAD' }).catch(() => null);
	return response?.ok ? url + location.hash : home;
}
