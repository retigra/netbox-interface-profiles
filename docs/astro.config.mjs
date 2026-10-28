// @ts-check
import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';

import { repository, root, version } from './site.mjs';

export default defineConfig({
	site: 'https://wouterdebruijn.github.io',
	base: `${root}${version}/`,
	trailingSlash: 'always',
	integrations: [
		starlight({
			title: 'NetBox Interface Profiles',
			description: 'Assign roles to NetBox interfaces and keep their configuration in sync.',
			favicon: '/favicon.svg',
			logo: { src: './src/assets/logo.svg' },
			social: [{ icon: 'github', label: 'GitHub', href: `https://github.com/${repository}` }],
			editLink: { baseUrl: `https://github.com/${repository}/edit/main/docs/` },
			lastUpdated: true,
			customCss: ['./src/styles/custom.css'],
			components: {
				Banner: './src/components/Banner.astro',
				SiteTitle: './src/components/SiteTitle.astro',
			},
			sidebar: [
				{ label: 'Getting started', items: [{ autogenerate: { directory: 'getting-started' } }] },
				{ label: 'Guides', items: [{ autogenerate: { directory: 'guides' } }] },
				{ label: 'Reference', items: [{ autogenerate: { directory: 'reference' } }] },
				{ label: 'Development', items: [{ autogenerate: { directory: 'development' } }] },
			],
		}),
	],
});
