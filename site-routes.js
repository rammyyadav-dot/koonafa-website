/* Legacy #about links resolve to the single company About page.
   URL fragments never reach the server, so this small bridge handles old bookmarks. */
(() => {
  const aboutURL = 'https://www.koonafa.com/About';
  function redirectLegacyAbout() {
    if (window.location.hash.toLowerCase() === '#about') {
      window.location.replace(aboutURL);
      return true;
    }
    return false;
  }
  redirectLegacyAbout();
  window.addEventListener('hashchange', redirectLegacyAbout);
})();
