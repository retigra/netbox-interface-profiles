// Register a published version in the GitHub Pages site and regenerate its root files.
//
// Usage: node scripts/update-versions.mjs <site directory> <version>
//
// Writes versions.json (read by the version selector), index.html (redirects to the latest release, or to dev
// before the first release) and 404.html (sends unknown pages to the 404 page of their version).
// Prints "latest" when <version> is the newest release, so the workflow knows to publish it as /latest/ too.

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { root } from '../site.mjs';

const [siteDir, version] = process.argv.slice(2);
if (!siteDir || !version) {
	console.error('Usage: node scripts/update-versions.mjs <site directory> <version>');
	process.exit(1);
}

const file = join(siteDir, 'versions.json');
const { versions } = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : { versions: [] };

/** Sort "dev" first, then releases newest first. */
const compare = (a, b) => {
	if (a === 'dev' || b === 'dev') return a === 'dev' ? -1 : 1;
	const [aMajor, aMinor] = a.split('.').map(Number);
	const [bMajor, bMinor] = b.split('.').map(Number);
	return bMajor - aMajor || bMinor - aMinor;
};

const all = [...new Set([...versions, version])].sort(compare);
const latest = all.find((v) => v !== 'dev') ?? null;

writeFileSync(file, `${JSON.stringify({ latest, versions: all }, null, 2)}\n`);

const home = `${root}${latest ? 'latest' : 'dev'}/`;
writeFileSync(
	join(siteDir, 'index.html'),
	`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<meta http-equiv="refresh" content="0; url=${home}">
<link rel="canonical" href="${home}">
</head>
<body><a href="${home}">Continue to the documentation</a></body>
</html>
`,
);

writeFileSync(
	join(siteDir, '404.html'),
	`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page not found</title>
<script>
	const root = ${JSON.stringify(root)};
	const version = location.pathname.startsWith(root) ? location.pathname.slice(root.length).split('/')[0] : '';
	fetch(root + 'versions.json')
		.then((response) => response.json())
		.then(({ latest, versions }) => (version === 'latest' ? Boolean(latest) : versions.includes(version)))
		.catch(() => false)
		.then((known) => location.replace(known ? root + version + '/404.html' : root));
</script>
</head>
<body><a href="${root}">Page not found. Continue to the documentation</a></body>
</html>
`,
);

if (version === latest) console.log('latest');
