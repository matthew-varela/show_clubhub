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
       container.style.transition = 'transform 0.8s ease';
       sleep(800).then(() => {        // after slide completes
         index = (index + 1) % images.length;
         container.style.transition = 'none';
         container.style.transform  = 'translateX(0)';
         render();
       });
     }, 3000);
   }
   
   /* -------------------------------------------------
      SECTION 7:  Club Search Functionality
      ------------------------------------------------- */
   function setupClubSearch() {
     const searchButton = $('#searchButton');
     const clubSearch = $('#clubSearch');
     const searchResults = $('#searchResults');
     const collegeSearchButton = $('#collegeSearchButton');
     const collegeSelect = $('#collegeSelect');
     const collegeSearchResults = $('#collegeSearchResults');
   
     if (!searchButton || !clubSearch) return;  // not on explore_clubs.html
   
     // Direct search with debounce
     let searchTimeout;
     async function performSearch() {
       const query = clubSearch.value.trim();
       if (!query) {
         searchResults.innerHTML = '';
         return;
       }
   
       try {
         const response = await fetch('/api/clubs', {
           method: 'GET',
           credentials: 'include'
         });
         
         if (!response.ok) throw new Error('Failed to fetch clubs');
         
         const clubs = await response.json();
         const filteredClubs = clubs.filter(club => 
           club.name.toLowerCase().includes(query.toLowerCase())
         );
   
         // Display results
         searchResults.innerHTML = '';
         if (filteredClubs.length === 0) {
           searchResults.innerHTML = '<div class="no-results">No clubs found</div>';
           return;
         }
   
         filteredClubs.forEach(club => {
           const div = document.createElement('div');
           div.className = 'user-result-item';
           const link = document.createElement('a');
           link.href = `/clubpage_page?club_id=${club.id}`;
           link.textContent = club.name;
           div.appendChild(link);
           searchResults.appendChild(div);
         });
       } catch (error) {
         console.error('Search failed:', error);
         searchResults.innerHTML = '<div class="error">Error performing search</div>';
       }
     }
   
     // College-based search
     async function performCollegeSearch() {
       const collegeId = collegeSelect.value;
       if (!collegeId) {
         collegeSearchResults.innerHTML = '';
         return;
       }
   
       try {
         const response = await fetch(`/api/clubs/by_college/${collegeId}`, {
           method: 'GET',
           credentials: 'include'
         });
         
         if (!response.ok) throw new Error('Failed to fetch clubs');
         
         const clubs = await response.json();
   
         // Display results
         collegeSearchResults.innerHTML = '';
         if (clubs.length === 0) {
           collegeSearchResults.innerHTML = '<div class="no-results">No clubs found for this college</div>';
           return;
         }
   
         clubs.forEach(club => {
           const div = document.createElement('div');
           div.className = 'user-result-item';
           const link = document.createElement('a');
           link.href = `/clubpage_page?club_id=${club.id}`;
           link.textContent = club.name;
           div.appendChild(link);
           collegeSearchResults.appendChild(div);
         });
       } catch (error) {
         console.error('College search failed:', error);
         collegeSearchResults.innerHTML = '<div class="error">Error performing search</div>';
       }
     }
   
     // Event listeners
     searchButton.addEventListener('click', performSearch);
     clubSearch.addEventListener('input', () => {
       clearTimeout(searchTimeout);
       searchTimeout = setTimeout(performSearch, 300); // Debounce search
     });
     clubSearch.addEventListener('keypress', (e) => {
       if (e.key === 'Enter') performSearch();
     });
   
     collegeSearchButton.addEventListener('click', performCollegeSearch);
     collegeSelect.addEventListener('change', performCollegeSearch);
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
     setupClubSearch();
   
     // (Search, welcome modal, etc. kept exactly as in v1; copy them here
     //  if you were using those features on other pages.)
   });
   