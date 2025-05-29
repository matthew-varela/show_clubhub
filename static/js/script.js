// Wait for the DOM to load before running scripts
document.addEventListener('DOMContentLoaded', () => {
  console.log('Interactive navigation is ready!');

  // 1) Smooth scrolling for same-page anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // 2) Check login status on page load
  const checkLoginStatus = async () => {
    try {
      const response = await fetch('https://club-hub-app.com/api/current_user', {
        method: 'GET',
        credentials: 'include', // IMPORTANT so session cookies are sent
      });
      if (!response.ok) {
        throw new Error(`Network response was not OK. Status: ${response.status}`);
      }

      const data = await response.json();
      // data.user is either the user object or null
      if (data.user) {
        // Logged in user
        showLoggedInUI(data.user);
      } else {
        // Not logged in
        showLoggedOutUI();
      }
    } catch (error) {
      console.error('Error checking login status:', error);
      // In case of error, treat as logged out
      showLoggedOutUI();
    }
  };

  // Show/hide UI for logged-in user
  const showLoggedInUI = (user) => {
    // Hide login link
    const loginNavItem = document.getElementById('loginNavItem'); 
    if (loginNavItem) loginNavItem.style.display = 'none';

    // Show account link
    const accountNavItem = document.getElementById('accountNavItem'); 
    if (accountNavItem) accountNavItem.style.display = 'block';

    // Show and set mini profile pic
    const miniPic = document.getElementById('miniProfilePic');
    if (miniPic) {
      miniPic.style.display = 'block';
      miniPic.src = user.profile_image ? user.profile_image : '/static/images/blank-prof-pic.png';
    }

    console.log(`Hello, ${user.firstname}!`);
  };

  // Show/hide UI for logged-out user
  const showLoggedOutUI = () => {
    // Show login link
    const loginNavItem = document.getElementById('loginNavItem');
    if (loginNavItem) loginNavItem.style.display = 'block';

    // Hide account link
    const accountNavItem = document.getElementById('accountNavItem');
    if (accountNavItem) accountNavItem.style.display = 'none';

    // Hide mini profile pic
    const miniPic = document.getElementById('miniProfilePic');
    if (miniPic) {
      miniPic.style.display = 'none';
      miniPic.src = '/static/images/blank-prof-pic.png'; // reset to blank if you want
    }
  };

  // 3) Handle the Login Form (if present)
  const setupLoginForm = () => {
    const loginButton = document.getElementById('loginButton');
    if (!loginButton) return;  // If not on the login page, skip

    loginButton.addEventListener('click', async () => {
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();

      if (!username || !password) {
        alert('Please enter both username and password.');
        return;
      }

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
          const data = await response.json();
          alert(`Login successful! Hello, ${data.user.firstname}.`);
          window.location.href = '/';
        } else {
          const errorData = await response.json();
          alert(`Login failed: ${errorData.error}`);
        }
      } catch (error) {
        console.error('Error logging in:', error);
        alert('An error occurred during login.');
      }
    });
  };

  // 4) Handle Logout (if present)
  const setupLogoutLink = () => {
    // If you have a logout button on account.html, set it up similarly:
    // const logoutButton = document.getElementById('logoutButton');
    // if (logoutButton) {
    //   logoutButton.addEventListener('click', async () => {
    //     try {
    //       const response = await fetch('http://127.0.0.1:5000/api/logout', {
    //         method: 'POST',
    //         credentials: 'include'
    //       });
    //       ...
    //     } catch(err) {
    //       console.error(err);
    //     }
    //   });
    // }
  };

  // ========== NEW SLIDESHOW CODE ==========
  const images = [
    '/static/images/eng1.png',
    '/static/images/eng2.png',
    '/static/images/ross1.png',
    '/static/images/lacrosse1.png',
    '/static/images/med1.png',
    '/static/images/law2.png',
    '/static/images/quant1.png',
    '/static/images/law1.png',
    '/static/images/soccer1.png'
  ];

  const imagesOnScreen = 3;
  let currentIndex = 0;

  const slideshowElement = document.querySelector('.slideshow');

  function initializeSlideshow() {
    if (!slideshowElement) return;
    slideshowElement.innerHTML = '';

    // Preload all images
    images.forEach(src => {
      const img = new Image();
      img.src = src;
    });

    // Populate the first 3 images
    for (let i = 0; i < imagesOnScreen; i++) {
      const img = document.createElement('img');
      const imageIndex = (currentIndex + i) % images.length;
      img.src = images[imageIndex];
      slideshowElement.appendChild(img);
    }
  }

  function slideImages() {
    if (!slideshowElement) return;
    
    // Move the first image to the end
    const firstImage = slideshowElement.firstElementChild;
    slideshowElement.appendChild(firstImage);
    
    // Reset the transform
    slideshowElement.style.transition = 'none';
    slideshowElement.style.transform = 'translateX(0)';
    
    // Force a reflow
    slideshowElement.offsetHeight;
    
    // Add the transition back and move
    slideshowElement.style.transition = 'transform 0.8s ease';
    slideshowElement.style.transform = 'translateX(-33.3333%)';
  }

  initializeSlideshow();
  setInterval(slideImages, 3000);

  // ========== Initialize everything else ==========

  checkLoginStatus();
  setupLoginForm();
  setupLogoutLink();

  // Add welcome popup functionality
  function showWelcomePopup() {
    // Check if user has seen the popup before
    if (!localStorage.getItem('hasSeenWelcome')) {
      const modal = document.createElement('div');
      modal.className = 'welcome-modal';
      modal.innerHTML = `
        <div class="modal-content">
          <h2>Welcome to ClubHub!</h2>
          <p>We're excited to help you discover student organizations at the University of Michigan. 
             What are you most interested in?</p>
          <div class="modal-buttons">
            <button class="modal-button primary-button" onclick="handleInterest('academic')">Academic Clubs</button>
            <button class="modal-button secondary-button" onclick="handleInterest('social')">Social Activities</button>
            <button class="modal-button secondary-button" onclick="handleInterest('sports')">Sports & Recreation</button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
      modal.style.display = 'flex';
      
      // Store that user has seen the popup
      localStorage.setItem('hasSeenWelcome', 'true');
    }
  }

  function handleInterest(interest) {
    const modal = document.querySelector('.welcome-modal');
    if (modal) {
      modal.remove();
    }
    
    // You could use this interest to personalize the user's experience
    console.log(`User interested in: ${interest}`);
    
    // Optionally, you could store this preference and use it to filter clubs
    localStorage.setItem('userInterest', interest);
  }

  // Show welcome popup after a short delay
  setTimeout(showWelcomePopup, 1000);
});

// Second DOMContentLoaded block for clubs searching
document.addEventListener('DOMContentLoaded', () => {
  const clubSearch = document.getElementById('clubSearch');
  const searchButton = document.getElementById('searchButton');
  const searchResults = document.getElementById('searchResults');
  let allClubs = [];
  let debounceTimer;

  const renderSearchResults = (clubs) => {
    searchResults.innerHTML = '';
    if (!clubs || clubs.length === 0) {
      const none = document.createElement('div');
      none.textContent = 'No clubs found.';
      searchResults.appendChild(none);
      return;
    }
    clubs.forEach(club => {
      const resultItem = document.createElement('div');
      resultItem.className = 'club-result-item'; 

      const nameSpan = document.createElement('span');
      nameSpan.textContent = club.name;

      resultItem.addEventListener('click', () => {
        window.location.href = `clubpage.html?club_id=${club.id}`;
      });

      resultItem.appendChild(nameSpan);
      searchResults.appendChild(resultItem);
    });
  };

  const handleSearch = () => {
    const query = clubSearch.value.trim().toLowerCase();
    if (!query) {
      searchResults.innerHTML = '';
      return;
    }
    const filtered = allClubs.filter(club => 
      club.name.toLowerCase().includes(query)
    );
    renderSearchResults(filtered);
  };

  const handleInput = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      handleSearch();
    }, 300);
  };

  const fetchAllClubs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/clubs', {
        method: 'GET',
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      allClubs = await response.json();
    } catch (error) {
      console.error('Error fetching clubs:', error);
    }
  };

  if (clubSearch && searchButton && searchResults) {
    searchButton.addEventListener('click', handleSearch);
    clubSearch.addEventListener('input', handleInput);
    fetchAllClubs();
  }
});

// Third DOMContentLoaded block for the "Find Clubs By College" feature
document.addEventListener('DOMContentLoaded', () => {
  const collegeSelect = document.getElementById('collegeSelect');
  const collegeSearchButton = document.getElementById('collegeSearchButton');
  const collegeSearchResults = document.getElementById('collegeSearchResults');

  if (collegeSelect && collegeSearchButton && collegeSearchResults) {
    collegeSearchButton.addEventListener('click', async () => {
      const selectedCollegeId = collegeSelect.value;
      if (!selectedCollegeId) {
        alert('Please select a college.');
        return;
      }
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/clubs/by_college/${selectedCollegeId}`, {
          method: 'GET',
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error(`Server responded with status ${response.status}`);
        }
        const clubs = await response.json();
        renderCollegeResults(clubs);
      } catch (error) {
        console.error('Error fetching clubs by college:', error);
        alert('Failed to fetch clubs for this college.');
      }
    });

    function renderCollegeResults(clubs) {
      collegeSearchResults.innerHTML = '';
      if (!clubs || clubs.length === 0) {
        const none = document.createElement('div');
        none.textContent = 'No clubs found for this college.';
        collegeSearchResults.appendChild(none);
        return;
      }
      clubs.forEach(club => {
        const resultItem = document.createElement('div');
        resultItem.className = 'club-result-item'; 
        resultItem.textContent = club.name;

        resultItem.addEventListener('click', () => {
          window.location.href = `clubpage.html?club_id=${club.id}`;
        });

        collegeSearchResults.appendChild(resultItem);
      });
    }
  }
});
