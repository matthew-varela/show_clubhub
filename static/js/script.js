/* -------------------------------------------------
   ClubHub – client‑side logic (single file)
   ------------------------------------------------- */

/***** helper functions for welcome modal *****/
function closeModal() {
  const modal = document.querySelector('.welcome-modal');
  if (modal) modal.remove();
}

function handleInterest(interest) {
  closeModal();
  console.log(`User interested in: ${interest}`);
  localStorage.setItem('userInterest', interest);
}

/***** main *****/// everything runs once after the DOM is ready

document.addEventListener('DOMContentLoaded', () => {
  console.log('ClubHub script loaded ✅');

  /* -------------------------------------------------
     1) Smooth scrolling for same‑page anchors
     ------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      e.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) target.scrollIntoView({behavior: 'smooth', block: 'start'});
    });
  });

  /* -------------------------------------------------
     2)  LOGIN / LOGOUT  UI helpers
     ------------------------------------------------- */
  const loginNavItem   = document.getElementById('loginNavItem');
  const accountNavItem = document.getElementById('accountNavItem');
  const miniPic        = document.getElementById('miniProfilePic');

  // Show/hide UI for logged-in user
  const showLoggedInUI = (user) => {
    // Hide login link
    if (loginNavItem) {
      loginNavItem.style.display = 'none';
    }

    // Show profile picture navigation
    const profilePicNavItem = document.getElementById('profilePicNavItem');
    if (profilePicNavItem) {
      profilePicNavItem.style.display = 'flex';
    }

    // Show and set mini profile pic
    if (miniPic) {
      miniPic.style.display = 'block';
      // Check if user has a profile image and it's not empty
      if (user.profile_image && user.profile_image.trim() !== '') {
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        miniPic.src = `${user.profile_image}?t=${timestamp}`;
        // Add error handling for the image
        miniPic.onerror = function() {
          console.error('Failed to load profile image:', user.profile_image);
          this.src = '/static/images/blank-prof-pic.png';
        };
      } else {
        miniPic.src = '/static/images/blank-prof-pic.png';
      }

      // Add click handler to ensure navigation works
      const profileLink = miniPic.closest('.profile-link');
      if (profileLink) {
        profileLink.addEventListener('click', (e) => {
          e.preventDefault();
          window.location.href = '/account_page';
        });
      }
    }

    console.log(`Hello, ${user.firstname}!`);
  };

  // Show/hide UI for logged-out user
  const showLoggedOutUI = () => {
    // Show login link
    if (loginNavItem) {
      loginNavItem.style.display = 'block';
    }

    // Hide profile picture navigation
    const profilePicNavItem = document.getElementById('profilePicNavItem');
    if (profilePicNavItem) {
      profilePicNavItem.style.display = 'none';
    }

    // Hide mini profile pic
    if (miniPic) {
      miniPic.style.display = 'none';
    }
  };

  async function checkLoginStatus() {
    try {
      const r = await fetch('/api/current_user', {
        method: 'GET',
        credentials: 'include'
      });
      if (!r.ok) throw new Error(r.status);
      const {user} = await r.json();
      user ? showLoggedInUI(user) : showLoggedOutUI();
    } catch (err) {
      console.error('Login‑check failed:', err);
      showLoggedOutUI();
    }
  }

  /* Login form (only exists on login.html) */
  function setupLoginForm() {
    const btn = document.getElementById('loginButton');
    if (!btn) return;

    btn.addEventListener('click', async () => {
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();
      if (!username || !password) return alert('Please enter both fields.');
      try {
        const r = await fetch('/api/login', {
          method: 'POST',
          credentials: 'include',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({username, password})
        });
        if (!r.ok) {
          const {error} = await r.json();
          return alert(`Login failed: ${error}`);
        }
        const {user} = await r.json();
        showLoggedInUI(user);
        window.location.href = '/';
      } catch (err) {
        console.error(err);
        alert('Login error – see console');
      }
    });
  }

  /* -------------------------------------------------
     3)  SLIDESHOW banner
     ------------------------------------------------- */
  const images = [
    '/static/images/eng1.png', '/static/images/eng2.png', '/static/images/ross1.png',
    '/static/images/lacrosse1.png', '/static/images/med1.png', '/static/images/law2.png',
    '/static/images/quant1.png', '/static/images/law1.png', '/static/images/soccer1.png'
  ];
  const imagesOnScreen = 3;
  let currentIndex = 0;
  const slideshowEl = document.querySelector('.slideshow');

  function initializeSlideshow() {
    if (!slideshowEl) return;
    slideshowEl.innerHTML = '';
    images.forEach(src => { const img = new Image(); img.src = src; }); // preload
    for (let i=0;i<imagesOnScreen;i++) {
      const img = document.createElement('img');
      img.src = images[(currentIndex+i)%images.length];
      slideshowEl.appendChild(img);
    }
  }

  function slideImages() {
    if (!slideshowEl) return;
    const first = slideshowEl.firstElementChild;
    slideshowEl.appendChild(first);
    slideshowEl.style.transition = 'none';
    slideshowEl.style.transform  = 'translateX(0)';
    slideshowEl.offsetHeight; // force reflow
    slideshowEl.style.transition = 'transform 0.8s ease';
    slideshowEl.style.transform  = 'translateX(-33.3333%)';
  }

  initializeSlideshow();
  setInterval(slideImages, 3000);

  /* -------------------------------------------------
     4)  CLUB SEARCH  (explore_clubs.html)
     ------------------------------------------------- */
  const clubSearch      = document.getElementById('clubSearch');
  const searchButton    = document.getElementById('searchButton');
  const searchResults   = document.getElementById('searchResults');
  let   allClubs        = [];
  let   debounceTimer;

  function renderSearchResults(list) {
    if (!searchResults) return;
    searchResults.innerHTML = '';
    if (!list || !list.length) {
      searchResults.textContent = 'No clubs found.';
      return;
    }
    list.forEach(club => {
      const item = document.createElement('div');
      item.className = 'club-result-item';
      item.textContent = club.name;
      item.addEventListener('click', () => {
        window.location.href = `clubpage.html?club_id=${club.id}`;
      });
      searchResults.appendChild(item);
    });
  }

  function doClubSearch() {
    const q = clubSearch.value.trim().toLowerCase();
    if (!q) return searchResults && (searchResults.innerHTML='');
    const filtered = allClubs.filter(c => c.name.toLowerCase().includes(q));
    renderSearchResults(filtered);
  }

  async function fetchAllClubs() {
    try {
      const r = await fetch('/api/clubs', {credentials:'include'});
      if (!r.ok) throw new Error(r.status);
      allClubs = await r.json();
    } catch (err) {
      console.error('Club fetch error:', err);
    }
  }

  if (clubSearch && searchButton && searchResults) {
    searchButton.addEventListener('click', doClubSearch);
    clubSearch.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(doClubSearch, 300);
    });
    fetchAllClubs();
  }

  /* -------------------------------------------------
     5)  "Find by college" feature
     ------------------------------------------------- */
  const collegeSelect        = document.getElementById('collegeSelect');
  const collegeSearchButton  = document.getElementById('collegeSearchButton');
  const collegeSearchResults = document.getElementById('collegeSearchResults');

  if (collegeSelect && collegeSearchButton && collegeSearchResults) {
    collegeSearchButton.addEventListener('click', async () => {
      const id = collegeSelect.value;
      if (!id) return alert('Select a college');
      try {
        const r = await fetch(`/api/clubs/by_college/${id}`, {credentials:'include'});
        if (!r.ok) throw new Error(r.status);
        const clubs = await r.json();
        renderCollegeResults(clubs);
      } catch (err) {
        console.error('College club fetch error:', err);
        alert('Failed to fetch clubs.');
      }
    });

    function renderCollegeResults(list) {
      collegeSearchResults.innerHTML = '';
      if (!list.length) return collegeSearchResults.textContent = 'No clubs found.';
      list.forEach(club => {
        const item = document.createElement('div');
        item.className = 'club-result-item';
        item.textContent = club.name;
        item.addEventListener('click', () => {
          window.location.href = `clubpage.html?club_id=${club.id}`;
        });
        collegeSearchResults.appendChild(item);
      });
    }
  }

  /* -------------------------------------------------
     6)  Welcome popup (once per browser)
     ------------------------------------------------- */
  function showWelcomePopup() {
    if (localStorage.getItem('hasSeenWelcome')) return;
    const modal = document.createElement('div');
    modal.className = 'welcome-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <h2>Welcome to ClubHub!</h2>
        <p>We're excited to help you discover student organizations at the University of Michigan. What are you most interested in?</p>
        <div class="modal-buttons">
          <button class="modal-button primary-button"   onclick="handleInterest('academic')">Academic Clubs</button>
          <button class="modal-button secondary-button" onclick="handleInterest('social')">Social Activities</button>
          <button class="modal-button secondary-button" onclick="handleInterest('sports')">Sports & Recreation</button>
        </div>
      </div>`;
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    localStorage.setItem('hasSeenWelcome', 'true');
  }
  setTimeout(showWelcomePopup, 1000);

  /* -------------------------------------------------
     7)  Kick things off
     ------------------------------------------------- */
  checkLoginStatus();
  setupLoginForm();
  // future: setupLogoutLink();
});
