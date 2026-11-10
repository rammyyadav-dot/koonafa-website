/**
 * Koonafa Agency — Shared Navigation
 * Drop <div id="koonafa-nav"></div> + <script src="/nav.js"></script>
 * into any page. Nav auto-highlights the active link.
 */

(function () {

  /* ─── NAV LINKS ─── edit here to add/remove pages ─── */
  const LINKS = [
    { label: 'The Work',   href: 'https://koonafa.com/#work'     },
    { label: 'Services',   href: 'https://koonafa.com/#services-state' },
    { label: 'Packages',   href: 'https://koonafa.com/packages'  },
    { label: 'About',      href: 'https://koonafa.com/#about'    },
    { label: 'News',       href: 'https://koonafa.com/#news'     },
    { label: 'Contact',    href: 'https://koonafa.com/#contact'  },
  ];

  const WA_NUMBER  = '919172712982';
  const WA_MESSAGE = 'Hi Koonafa, I found your website and would like to discuss a project.';
  const SITE_URL   = 'https://koonafa.com/';

  /* ─── STYLES ─── injected once into <head> ─── */
  const CSS = `
    #kn-nav {
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 999;
      height: 60px;
      background: #0A0A0A;
      border-bottom: 1px solid #242424;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif;
      box-sizing: border-box;
    }
    #kn-nav * { box-sizing: border-box; }

    /* Logo */
    #kn-logo {
      display: flex;
      align-items: flex-start;
      gap: 3px;
      text-decoration: none;
      flex-shrink: 0;
    }
    #kn-logo-k {
      font-size: 24px;
      font-weight: 900;
      color: #FFFFFF;
      letter-spacing: -0.04em;
      line-height: 1;
    }
    #kn-logo-dot {
      width: 6px; height: 6px;
      background: #E5271A;
      border-radius: 50%;
      margin-top: 4px;
      flex-shrink: 0;
    }

    /* Links */
    #kn-links {
      display: flex;
      align-items: center;
      gap: 4px;
      list-style: none;
      margin: 0;
      padding: 0;
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
    }
    #kn-links a {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #6E6E6E;
      text-decoration: none;
      padding: 6px 14px;
      transition: color 0.2s;
    }
    #kn-links a:hover { color: #FFFFFF; }
    #kn-links a.kn-active {
      color: #FFFFFF;
      border-bottom: 2px solid #E5271A;
    }

    /* Right side */
    #kn-right {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-shrink: 0;
    }

    /* WhatsApp button */
    #kn-wa {
      display: flex;
      align-items: center;
      gap: 7px;
      background: #25D366;
      color: #FFFFFF;
      text-decoration: none;
      padding: 8px 16px;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      transition: background 0.2s;
      white-space: nowrap;
    }
    #kn-wa:hover { background: #1ebd5a; }
    #kn-wa svg { width: 14px; height: 14px; fill: #FFFFFF; flex-shrink: 0; }

    /* Hamburger (mobile) */
    #kn-burger {
      display: none;
      flex-direction: column;
      gap: 5px;
      cursor: pointer;
      padding: 6px;
      background: none;
      border: none;
    }
    #kn-burger span {
      display: block;
      width: 22px; height: 2px;
      background: #FFFFFF;
      transition: all 0.3s;
    }

    /* Mobile drawer */
    #kn-drawer {
      display: none;
      position: fixed;
      top: 60px; left: 0; right: 0;
      background: #0A0A0A;
      border-bottom: 1px solid #242424;
      padding: 16px 0;
      z-index: 998;
    }
    #kn-drawer.open { display: block; }
    #kn-drawer a {
      display: block;
      padding: 12px 32px;
      font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #6E6E6E;
      text-decoration: none;
      border-bottom: 1px solid #1A1A1A;
      transition: color 0.2s, background 0.2s;
    }
    #kn-drawer a:last-child { border-bottom: none; }
    #kn-drawer a:hover { color: #FFFFFF; background: #141414; }
    #kn-drawer a.kn-active { color: #FFFFFF; border-left: 3px solid #E5271A; }
    #kn-drawer-wa {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 12px 24px 4px;
      background: #25D366;
      color: #FFFFFF !important;
      padding: 12px 20px !important;
      border: none !important;
      text-decoration: none;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }
    #kn-drawer-wa svg { width: 15px; height: 15px; fill: #FFFFFF; }

    /* Body offset so content doesn't hide under fixed nav */
    body { padding-top: 60px !important; }

    /* Mobile breakpoint */
    @media (max-width: 768px) {
      #kn-nav { padding: 0 20px; }
      #kn-links { display: none; }
      #kn-burger { display: flex; }
      #kn-wa .kn-wa-label { display: none; }
      #kn-wa { padding: 8px 12px; }
    }
    @media (min-width: 769px) {
      #kn-drawer { display: none !important; }
    }
  `;

  /* ─── WA SVG ─── */
  const waSVG = `<svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>`;

  /* ─── BUILD HTML ─── */
  function buildNav() {
    const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
    const currentHref = window.location.href;

    /* Active link detection */
    function isActive(href) {
      if (href.includes('#')) {
        // hash links are active on root/index
        return currentPath === '' || currentPath === '/' ||
               currentHref.includes(href.split('#')[0]);
      }
      const linkPath = href.replace(/https?:\/\/[^/]+/, '').replace(/\/$/, '') || '/';
      return currentPath === linkPath;
    }

    /* Link items */
    const linkHTML = LINKS.map(l =>
      `<li><a href="${l.href}" ${isActive(l.href) ? 'class="kn-active"' : ''}>${l.label}</a></li>`
    ).join('');

    /* Drawer links */
    const drawerHTML = LINKS.map(l =>
      `<a href="${l.href}" ${isActive(l.href) ? 'class="kn-active"' : ''}>${l.label}</a>`
    ).join('');

    const waHref = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(WA_MESSAGE)}`;

    return `
      <nav id="kn-nav">
        <a id="kn-logo" href="${SITE_URL}">
          <span id="kn-logo-k">K</span>
          <span id="kn-logo-dot"></span>
        </a>

        <ul id="kn-links">${linkHTML}</ul>

        <div id="kn-right">
          <a id="kn-wa" href="${waHref}" target="_blank" rel="noopener">
            ${waSVG}
            <span class="kn-wa-label">WhatsApp Us</span>
          </a>
          <button id="kn-burger" aria-label="Menu" aria-expanded="false">
            <span></span><span></span><span></span>
          </button>
        </div>
      </nav>

      <div id="kn-drawer">
        ${drawerHTML}
        <a id="kn-drawer-wa" href="${waHref}" target="_blank" rel="noopener">
          ${waSVG} WhatsApp Us
        </a>
      </div>
    `;
  }

  /* ─── INJECT STYLES ─── */
  function injectStyles() {
    if (document.getElementById('kn-styles')) return;
    const style = document.createElement('style');
    style.id = 'kn-styles';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  /* ─── MOUNT ─── */
  function mount() {
    injectStyles();

    /* Find mount point or create one at top of body */
    let root = document.getElementById('koonafa-nav');
    if (!root) {
      root = document.createElement('div');
      root.id = 'koonafa-nav';
      document.body.insertBefore(root, document.body.firstChild);
    }
    root.innerHTML = buildNav();

    /* Hamburger toggle */
    const burger  = document.getElementById('kn-burger');
    const drawer  = document.getElementById('kn-drawer');
    const spans   = burger.querySelectorAll('span');

    burger.addEventListener('click', () => {
      const open = drawer.classList.toggle('open');
      burger.setAttribute('aria-expanded', open);
      /* Animate to X */
      if (open) {
        spans[0].style.transform = 'translateY(7px) rotate(45deg)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity   = '';
        spans[2].style.transform = '';
      }
    });

    /* Close drawer on link click */
    drawer.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        drawer.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        spans[0].style.transform = '';
        spans[1].style.opacity   = '';
        spans[2].style.transform = '';
      });
    });
  }

  /* Run after DOM ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

})();
