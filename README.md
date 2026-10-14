# ALL UNDISCOVERED

Ming Yuan’s Markdown blog, ready for GitHub Pages. Thirteen published articles and six music pages migrated from my1219.today. Original URLs are preserved as directory routes. Python runs during the build; visitors receive static HTML.

## Local preview

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m http.server 8000 --directory _site
```

Open http://localhost:8000. Build output is disposable; never edit `_site` directly.

## Publish on GitHub Pages

1. Create or inspect `mingyuan1219/mingyuan1219.github.io`. If it exists, preserve its existing content and make a branch before importing this project.
2. Put the contents of this directory in the repository root, including `.github`.
3. In **Settings → Pages**, select **GitHub Actions** as the source.
4. Push to `master`. The included workflow builds and deploys `_site`.
5. Verify the homepage, the current and dated legacy paths, images, Chinese text, and SoundCloud players at `https://mingyuan1219.github.io/`.

For a project repository instead, change `base_path` in `config.json` to `/REPOSITORY-NAME`. For a custom domain, change `url` to `https://my1219.today` and keep `base_path` empty.

## Keep writing

```sh
python3 scripts/new_post.py returning-to-writing "重新开始写作"
python3 scripts/new_post.py new-song "A new song" --kind song --topic Music
```

Edit the resulting Markdown file. Its front matter is JSON between `---` delimiters (valid YAML syntax), parsed by the build script. Use `article` or `song`, a topic, an ISO date, and a description. Set `status` to `published` when ready. Drafts do not enter the generated site, but any draft committed to a public repository is readable on GitHub; keep private drafts in Obsidian outside this repository.

For music, add SoundCloud player URLs to `players`. The build accepts only `w.soundcloud.com` embeds and provides recording links. Historical article dates come from the previous GitHub archive. Music dates remain empty where the public page did not establish a publication date; Notion creation dates were not treated as publication dates. New dated content sorts before the undated legacy archive.

## Domain cutover

Keep Super serving the domain while testing the Pages site. Verify ownership of `my1219.today` with GitHub, then set the custom domain in repository Pages settings before changing DNS. Point the apex domain using the provider’s supported ALIAS/ANAME or GitHub’s documented A records. Enable HTTPS after GitHub provisions the certificate. Confirm all old URLs before cancelling Super. Keep a copy of the former DNS records for rollback.

[GitHub Pages setup](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) · [Custom domain setup and DNS records](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

## Migration scope

The 12 pages linked on the current homepage were migrated from their live rendered content. Seven additional articles were recovered from the existing GitHub archive. The build contains 50 local image assets and eight SoundCloud recording embeds. No Obsidian project notes, private letters, credentials, or unselected essays are included. This is a homepage-linked inventory, not a claim that no unlinked pages exist. SoundCloud remains an external service. Page text is preserved; the homepage and About introduction are proposed new copy for review.
