// Prerender SPA routes to static HTML using puppeteer + sirv.
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import sirv from 'sirv'
import puppeteer from 'puppeteer'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distDir = path.resolve(__dirname, '..', 'dist')
const BASE = '/MyPortfolio/'
const ORIGIN = 'https://mikeyc-wang.github.io'
const API_BASE = process.env.VITE_API_BASE_URL || 'https://portfolio-api-a21d.onrender.com'
const PORT = 4173

const STATIC_ROUTES = [
  '/MyPortfolio/',
  '/MyPortfolio/blog',
  '/MyPortfolio/projects',
  '/MyPortfolio/lab',
]

function fetchWithTimeout(url, ms = 60000) {
  return Promise.race([
    fetch(url),
    new Promise((_, rej) => setTimeout(() => rej(new Error('fetch timeout: ' + url)), ms)),
  ])
}

async function getBlogIds() {
  try {
    console.log('[prerender] fetching posts from', API_BASE + '/api/posts')
    const res = await fetchWithTimeout(API_BASE + '/api/posts', 60000)
    if (!res.ok) throw new Error('status ' + res.status)
    const data = await res.json()
    const posts = Array.isArray(data) ? data : (data.posts || data.data || [])
    const ids = posts.map((p) => p.id ?? p.slug).filter(Boolean)
    console.log('[prerender] fetched', ids.length, 'posts')
    return ids
  } catch (e) {
    console.warn('[prerender] WARN: could not fetch posts -', e.message)
    return []
  }
}

function startServer() {
  // Always serve the SPA index.html for any HTML navigation, so puppeteer
  // bootstraps the app rather than reading any previously-prerendered file.
  const indexHtml = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8')
  const serveAssets = sirv(distDir, { dev: false, single: false, etag: true })
  const server = http.createServer((req, res) => {
    if (req.url && req.url.startsWith('/MyPortfolio')) {
      req.url = req.url.slice('/MyPortfolio'.length) || '/'
    }
    const accept = req.headers['accept'] || ''
    const isAsset = /\.[a-zA-Z0-9]+(\?.*)?$/.test(req.url || '')
    if (!isAsset && accept.includes('text/html')) {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(indexHtml)
      return
    }
    serveAssets(req, res, () => {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(indexHtml)
    })
  })
  return new Promise((resolve) => {
    server.listen(PORT, () => resolve(server))
  })
}

function routeToFilePath(route) {
  // route like /MyPortfolio/blog/123 -> dist/blog/123/index.html
  let rel = route.replace(BASE, '')
  if (rel === '' || rel === '/') return path.join(distDir, 'index.html')
  rel = rel.replace(/^\/+|\/+$/g, '')
  return path.join(distDir, rel, 'index.html')
}

async function prerenderRoute(browser, route) {
  const url = `http://127.0.0.1:${PORT}${route}`
  const page = await browser.newPage()
  try {
    // Intercept relative /api/* calls and redirect to the production API
    await page.setRequestInterception(true)
    page.on('request', async (req) => {
      const u = req.url()
      const localMatch = u.match(/^https?:\/\/127\.0\.0\.1:\d+(\/api\/.*)$/)
      const remoteMatch = u.startsWith(API_BASE + '/api/')
      const m = localMatch ? localMatch : (remoteMatch ? [u, u.slice(API_BASE.length)] : null)
      if (m) {
        try {
          const upstream = await fetch(API_BASE + m[1], { method: req.method() })
          const buf = Buffer.from(await upstream.arrayBuffer())
          await req.respond({
            status: upstream.status,
            headers: {
              'content-type': upstream.headers.get('content-type') || 'application/json',
              'access-control-allow-origin': 'http://127.0.0.1:' + PORT,
              'access-control-allow-credentials': 'true',
            },
            body: buf,
          })
        } catch (e) {
          await req.respond({ status: 502, body: 'proxy error: ' + e.message })
        }
      } else {
        req.continue()
      }
    })
    page.on('pageerror', (e) => console.warn('[prerender] pageerror', route, '-', e.message))
    page.on('console', (msg) => {
      const t = msg.type()
      if (t === 'error' || t === 'warning') console.warn('[prerender] console.' + t, route, '-', msg.text())
    })
    page.on('requestfailed', (req) => console.warn('[prerender] reqfail', route, '-', req.url(), req.failure()?.errorText))
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 })
    // give Vue/async data a tick to settle
    await new Promise((r) => setTimeout(r, 800))
    const html = await page.content()
    const outFile = routeToFilePath(route)
    fs.mkdirSync(path.dirname(outFile), { recursive: true })
    fs.writeFileSync(outFile, html, 'utf8')
    console.log('[prerender] wrote', path.relative(distDir, outFile))
  } catch (e) {
    console.warn('[prerender] FAIL', route, '-', e.message)
  } finally {
    await page.close()
  }
}

function writeSitemap(allRoutes) {
  const today = new Date().toISOString().slice(0, 10)
  const urls = allRoutes.map((r) => {
    const loc = ORIGIN + r
    let changefreq = 'monthly'
    let priority = '0.8'
    if (r === BASE) { priority = '1.0' }
    else if (r === BASE + 'blog') { changefreq = 'weekly'; priority = '0.8' }
    else if (r.startsWith(BASE + 'blog/')) { changefreq = 'weekly'; priority = '0.6' }
    return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>`
  }).join('\n')
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`
  fs.writeFileSync(path.join(distDir, 'sitemap.xml'), xml, 'utf8')
  console.log('[prerender] wrote sitemap.xml with', allRoutes.length, 'urls')
}

async function main() {
  const ids = await getBlogIds()
  const blogRoutes = ids.map((id) => `${BASE}blog/${id}`)
  const routes = [...STATIC_ROUTES, ...blogRoutes]

  const server = await startServer()
  console.log('[prerender] static server up on', PORT)
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] })
  try {
    for (const r of routes) {
      await prerenderRoute(browser, r)
    }
  } finally {
    await browser.close()
    server.close()
  }

  writeSitemap(routes)
  console.log('[prerender] done')
}

main().catch((e) => {
  console.error('[prerender] fatal', e)
  process.exit(1)
})
