# Koonafa Website - Deployment Guide

## 🚀 Quick Deployment Steps

### Option 1: GitHub Pages (Recommended)

1. **Enable GitHub Pages:**
   - Go to: https://github.com/rammyyadav-dot/koonafa-website/settings/pages
   - Source: Deploy from `main` branch
   - Folder: `/ (root)`
   - Click "Save"

2. **Your site will be live at:**
   - https://rammyyadav-dot.github.io/koonafa-website

3. **Custom Domain Setup (koonafa.com):**
   - Upload the `CNAME` file to your repository root
   - In Cloudflare DNS settings, add:
     ```
     Type: CNAME
     Name: @
     Target: rammyyadav-dot.github.io
     Proxy: DNS only (grey cloud)
     ```
   - Wait 5-10 minutes for DNS propagation
   - Enable "Enforce HTTPS" in GitHub Pages settings

### Option 2: Cloudflare Pages

1. **Connect Repository:**
   - Go to Cloudflare Dashboard → Pages
   - Click "Create a project"
   - Connect to GitHub: rammyyadav-dot/koonafa-website
   - Branch: main
   - Build settings: None (static HTML)

2. **Custom Domain:**
   - Automatically uses koonafa.com
   - SSL/TLS automatically configured

### Option 3: Direct Hosting (cPanel/FTP)

1. **Upload Files via FTP:**
   ```
   Server: ftp.koonafa.com
   Username: [your-username]
   Password: [your-password]
   ```

2. **Upload these files to public_html:**
   - koonafa-global.html (rename to index.html)
   - All image files (palm-jumeirah.webp, hero-*.png)
   - sitemap.xml
   - robots.txt
   - favicon.svg

## 📋 File Upload Checklist

### Essential Files (MUST upload)
- [x] koonafa-global.html → rename to **index.html**
- [x] palm-jumeirah.webp
- [x] hero-beach-resort.png
- [x] hero-burj-al-arab.png
- [x] hero-infinity-pool.png
- [x] sitemap.xml
- [x] robots.txt
- [x] CNAME (for custom domain)

### Optional but Recommended
- [x] favicon.svg
- [x] README.md
- [x] .gitignore

## 🔧 Post-Deployment Configuration

### 1. Update HTML File Reference
In `index.html` (or koonafa-global.html), ensure image paths are correct:
```html
<!-- Hero carousel should reference: -->
url('palm-jumeirah.webp')
url('hero-beach-resort.png')
url('hero-burj-al-arab.png')
url('hero-infinity-pool.png')
```

### 2. Add Favicon to HTML
Add this to the `<head>` section:
```html
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="apple-touch-icon" href="favicon.svg">
```

### 3. Add Analytics (Optional)
Before closing `</head>` tag:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 4. Submit to Search Engines
After deployment:
- Google Search Console: https://search.google.com/search-console
- Bing Webmaster Tools: https://www.bing.com/webmasters
- Submit sitemap: https://koonafa.com/sitemap.xml

## ✅ Testing Checklist

After deployment, test:
- [ ] Homepage loads (https://koonafa.com)
- [ ] Hero carousel auto-rotates every 5 seconds
- [ ] All 4 hero images load correctly
- [ ] Navigation links scroll to sections
- [ ] Mobile responsive design works
- [ ] Association logos marquee scrolls
- [ ] Contact email link works (Hello@koonafa.com)
- [ ] All sector cards display correctly
- [ ] Page load speed < 3 seconds
- [ ] SSL certificate is active (HTTPS)

## 🐛 Troubleshooting

**Images not loading?**
- Check file names match exactly (case-sensitive)
- Ensure all images are in the same directory as index.html
- Check browser console for 404 errors

**Carousel not rotating?**
- Check JavaScript console for errors
- Ensure all 4 slide divs have correct class names
- Verify setInterval function is running

**Custom domain not working?**
- Wait 10-15 minutes for DNS propagation
- Check CNAME file contains only: koonafa.com
- Verify DNS records in Cloudflare

**SSL/HTTPS not working?**
- Enable "Enforce HTTPS" in GitHub Pages settings
- Use Cloudflare SSL/TLS settings (Full mode)

## 📞 Support

For deployment issues:
- GitHub: @rammyyadav-dot
- Email: Hello@koonafa.com

---

**Last Updated:** May 5, 2026
