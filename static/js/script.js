/* -------------------------------------------------
   ClubHub – client-side logic  (v2, 29 May 2025)
   ------------------------------------------------- */

   const $ = (sel,         parent = document) => parent.querySelector(sel);   // tiny helper
   const $$ = (sel,        parent = document) => [...parent.querySelectorAll(sel)];
   const sleep = (ms = 0) => new Promise(r => setTimeout(r, ms));
   
   /* -------------------------------------------------
      SECTION 1:  Navbar login / logout handling
      ------------------------------------------------- */
   async function fetchCurrentUser() {
     try {
       const r = await fetch('/api/current_user', { credentials: 'include' });
       if (!r.ok) throw new Error(r.status);
       const { user } = await r.json();
       return user ?? null;
     } catch (err) {
       console.error('[current_user] request failed:', err);
       return null;
     }
   }
   
   function updateNavbarUI(user) {
    const loginLink   = $('#loginNavItem');
    const picWrapper  = $('#profilePicNavItem');
    const miniPic     = $('#miniProfilePic');
  
    const show = el => el && (el.style.display = '');
    const hide = el => el && (el.style.display = 'none');
  
    if (user) {
      hide(loginLink);
      show(picWrapper);
      show(miniPic);
  
      // ── choose the correct avatar ──────────────────────────────
      if (user.profile_image && user.profile_image.trim() !== '') {
        // data-URI?  → use as-is.   ordinary URL?  → add cache-buster.
        if (user.profile_image.startsWith('data:')) {
          miniPic.src = user.profile_image;
        } else {
          miniPic.src = `${user.profile_image}?t=${Date.now()}`;
        }
      } else {
        miniPic.src = '/static/images/blank-prof-pic.png';
      }
  
      miniPic.onclick = () => (window.location.href = '/account_page');
    } else {
      show(loginLink);
      hide(picWrapper);
    }
  }
   
   async function ensureNavbar() {                      // run at page-load
     const user = await fetchCurrentUser();
     updateNavbarUI(user);
   }
   
   /* -------------------------------------------------
      SECTION 2:  Login form (only on login.html)
      ------------------------------------------------- */
   function setupLoginForm() {
     const btn = $('#loginButton');
     if (!btn) return;                                  // not on this page
   
     btn.addEventListener('click', async () => {
       const username = $('#username').value.trim();
       const password = $('#password').value.trim();
       if (!username || !password) { alert('Enter both fields'); return; }
   
       try {
         const r = await fetch('/api/login', {
           method: 'POST',
           credentials: 'include',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ username, password })
         });
         if (!r.ok) {
           const { error } = await r.json();
           throw new Error(error || `status ${r.status}`);
         }
         // success:  refresh to home; navbar will auto-populate
         window.location.href = '/';
       } catch (err) {
         console.error('login failed:', err);
         alert(`Login failed: ${err.message}`);
       }
     });
   }
   
   /* -------------------------------------------------
      SECTION 3:  Logout button (only where it exists)
      ------------------------------------------------- */
   function setupLogoutButton() {
     const btn = $('#logoutButton');
     if (!btn) return;                                  // not on this page
   
     btn.style.display = 'inline-block';
     btn.addEventListener('click', async () => {
       try {
         await fetch('/api/logout', { method: 'POST', credentials: 'include' });
         window.location.href = '/';
       } catch {
         alert('Logout failed.  Please try again.');
       }
     });
   }
   
   /* -------------------------------------------------
      SECTION 4:  Smooth scrolling for on-page anchors
      ------------------------------------------------- */
   function setupSmoothScroll() {
     $$('a[href^="#"]').forEach(a =>
       a.addEventListener('click', e => {
         e.preventDefault();
         const target = $(a.getAttribute('href'));
         target?.scrollIntoView({ behavior: 'smooth' });
       })
     );
   }
   
   /* -------------------------------------------------
      SECTION 5:  Home-page slideshow
      ------------------------------------------------- */
   function setupSlideshow() {
     const container = $('.slideshow');
     if (!container) return;                            // not on home.html
   
     const images = [
       '/static/images/eng1.png', '/static/images/eng2.png', '/static/images/ross1.png',
       '/static/images/lacrosse1.png', '/static/images/med1.png', '/static/images/law2.png',
       '/static/images/quant1.png', '/static/images/law1.png', '/static/images/soccer1.png'
     ];
     const VISIBLE = 3;
     let index = 0;
   
     // pre-load
     images.forEach(src => { const img = new Image(); img.src = src; });
   
     function render() {
       container.innerHTML = '';
       for (let i = 0; i < VISIBLE; ++i) {
         const img = document.createElement('img');
         img.src = images[(index + i) % images.length];
         container.appendChild(img);
       }
     }
   
     render();
     setInterval(() => {
       container.style.transform = 'translateX(-33.3333%)';
       container.style.transition = 'transform 1.5s ease';
       sleep(1000).then(() => {        // after slide completes
         index = (index + 1) % images.length;
         container.style.transition = 'none';
         container.style.transform  = 'translateX(0)';
         render();
       });
     }, 3000);
   }
   
   /* -------------------------------------------------
      SECTION 6:  Universal start-up
      ------------------------------------------------- */
   document.addEventListener('DOMContentLoaded', () => {
     console.log('🚀 ClubHub script v2 loaded');
     ensureNavbar();
     setupLoginForm();
     setupLogoutButton();
     setupSmoothScroll();
     setupSlideshow();
   
     // (Search, welcome modal, etc. kept exactly as in v1; copy them here
     //  if you were using those features on other pages.)
   });
   