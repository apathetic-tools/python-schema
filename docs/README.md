# GitHub Pages Documentation

This directory contains the Jekyll documentation site for Apathetic Python Schema, designed to be deployed to GitHub Pages.

## Local Development

To preview the documentation locally:

1. Install Jekyll and dependencies:
   ```bash
   cd docs
   bundle install
   ```

2. Run the Jekyll server:
   ```bash
   bundle exec jekyll serve
   ```

3. Open your browser to `http://localhost:4000/python-schema/`

   Note: The baseurl is `/python-schema`, so make sure to include it in the local URL.

## Deployment

GitHub Pages will automatically build and deploy this site when:
- Changes are pushed to the `main` branch (if Pages is configured to use `main` branch)
- Changes are pushed to the `gh-pages` branch (if Pages is configured to use `gh-pages` branch)

The site will be available at:
- `https://apathetic-tools.github.io/python-schema/`

### GitHub Pages Configuration

1. Go to your repository settings on GitHub
2. Navigate to **Pages** in the left sidebar
3. Under **Source**, select:
   - **Branch**: `main` (or `gh-pages` if using that branch)
   - **Folder**: `/docs` (if using docs folder) or `/ (root)` (if using root)
4. Click **Save**

GitHub Pages will automatically build the site using Jekyll and the `Gemfile` in the `docs/` directory.

## Configuration

The site configuration is in `_config.yml`. Key settings:
- `baseurl`: Set to `/python-schema` (matches the repository name)
- `url`: Set to `https://apathetic-tools.github.io`
- `theme`: Uses the `minima` theme (GitHub Pages default)
- Dark mode: Auto-detects user preference via `prefers-color-scheme`, defaults to dark mode

## Theme Customization

The site uses the `minima` theme with custom dark mode styles:
- Custom SCSS in `_sass/custom.scss` provides dark mode support
- Auto-detects user's color scheme preference
- Defaults to dark mode if no preference is set

## Structure

- `index.md` - Homepage
- `installation.md` - Installation guide
- `quickstart.md` - Quick start guide
- `api.md` - Complete API reference
- `examples.md` - Usage examples
- `custom-logger.md` - Custom logger guide
- `contributing.md` - Contributing guide

## Notes

- All markdown files use Jekyll front matter with `layout: default`
- Links use Jekyll's `relative_url` filter for proper GitHub Pages URLs
- The site uses the `minima` theme which is supported by GitHub Pages
- Dark mode styles are defined in `_sass/custom.scss` and are automatically included by the theme

