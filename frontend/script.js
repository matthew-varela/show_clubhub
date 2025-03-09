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
      const response = await fetch('http://127.0.0.1:5000/api/current_user', {
        method: 'GET',
        credentials: 'include', // IMPORTANT so session cookies are sent
      });
      if (!response.ok) {
        throw new Error(`Network response was not OK. Status: ${response.status}`);
      }

      const data = await response.json();
      // data.user is either the user object or null/undefined
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
      miniPic.src = user.profile_image ? user.profile_image : 'blank-prof-pic.png';
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
      miniPic.src = 'blank-prof-pic.png'; // reset to blank if you want
    }
  };

  // 3) Handle the Login Form (if present)
  const setupLoginForm = () => {
    const loginButton = document.getElementById('loginButton');
    if (!loginButton) return;  // If not on the login page, skip this

    loginButton.addEventListener('click', async () => {
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();

      if (!username || !password) {
        alert('Please enter both username and password.');
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:5000/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',  // Must include to set session cookie
          body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
          const data = await response.json();
          alert(`Login successful! Hello, ${data.user.firstname}.`);
          // Redirect to home (or any page)
          window.location.href = 'home.html';
        } else {
          // e.g., 401: invalid credentials
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
    // If you have a logout button/link on account.html, you could set it up here
    // e.g.:
    // const logoutButton = document.getElementById('logoutButton');
    // if (logoutButton) {
    //   logoutButton.addEventListener('click', async () => {
    //     ...
    //   });
    // }
  };

  // ========== NEW SLIDESHOW CODE ==========

  // Array of image file paths (place these images in your project folder)
  const images = [
    'eng1.png',
    'eng2.png',
    'ross1.png',
    'lacrosse1.png',
    'med1.png',
    'law2.png',
    'quant1.png',
    'law1.png',
    'soccer1.png'
  ];

  // We want 3 images shown at once
  const imagesOnScreen = 3;
  // Current index for tracking which image to bring in on the right
  let currentIndex = 0;

  // Grab the slideshow element from the DOM
  const slideshowElement = document.querySelector('.slideshow');

  // Initialize the slideshow
  function initializeSlideshow() {
    if (!slideshowElement) return;

    // Clear any existing images
    slideshowElement.innerHTML = '';

    // Populate the first 3 images
    for (let i = 0; i < imagesOnScreen; i++) {
      const img = document.createElement('img');
      const imageIndex = (currentIndex + i) % images.length;
      img.src = images[imageIndex];
      slideshowElement.appendChild(img);
    }
  }

  // Slide the images by 1 position
  function slideImages() {
    if (!slideshowElement) return;

    // Slide left by one image width (33.3333%)
    slideshowElement.style.transform = 'translateX(-33.3333%)';

    // When transition finishes, rearrange DOM
    slideshowElement.addEventListener('transitionend', handleTransitionEnd, { once: true });
  }

  function handleTransitionEnd() {
    // Remove left-most <img>
    slideshowElement.removeChild(slideshowElement.firstElementChild);

    // Advance the currentIndex
    currentIndex = (currentIndex + 1) % images.length;

    // Create a new img for the right side
    const newImg = document.createElement('img');
    // The new image index will be (currentIndex + 2) modulo images.length 
    // because we want 3 total images (positions 0, 1, 2).
    // The last slot is (imagesOnScreen - 1) = 2 ahead of currentIndex.
    const newImageIndex = (currentIndex + (imagesOnScreen - 1)) % images.length;
    newImg.src = images[newImageIndex];
    slideshowElement.appendChild(newImg);

    // Reset transform to 0 so we see the new 3 images side-by-side
    slideshowElement.style.transition = 'none'; // turn off transitions momentarily
    slideshowElement.style.transform = 'translateX(0)';

    // Force reflow to apply the transform reset
    slideshowElement.offsetHeight; // read a property for reflow

    // Re-enable transition for next movement
    slideshowElement.style.transition = 'transform 0.8s ease';
  }

  // Call slideshow initialization
  initializeSlideshow();
  // Set the interval to slide every 3 seconds
  setInterval(slideImages, 3000);

  // ========== Initialize everything else ==========

  checkLoginStatus();
  setupLoginForm();
  setupLogoutLink();
});

document.addEventListener('DOMContentLoaded', () => {
  const clubSearch = document.getElementById('clubSearch');
  const searchButton = document.getElementById('searchButton');
  const searchResults = document.getElementById('searchResults');
  let allClubs = [];    // to store all clubs
  let debounceTimer;

  /**
   * Renders the list of matched clubs to the DOM.
   * @param {Array} clubs - Array of club objects [{id, name, ...}, ...].
   */
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
      resultItem.className = 'club-result-item'; // For potential CSS styling

      // Just text (no pic for clubs)
      const nameSpan = document.createElement('span');
      nameSpan.textContent = club.name;

      // Click -> go to the clubpage
      resultItem.addEventListener('click', () => {
        window.location.href = `clubpage.html?club_id=${club.id}`;
      });

      resultItem.appendChild(nameSpan);
      searchResults.appendChild(resultItem);
    });
  };

  /**
   * Handle search input (client-side filtering)
   */
  const handleSearch = () => {
    const query = clubSearch.value.trim().toLowerCase();
    if (!query) {
      // if empty, clear results
      searchResults.innerHTML = '';
      return;
    }

    // Filter from allClubs array
    const filtered = allClubs.filter(club => 
      club.name.toLowerCase().includes(query)
    );
    renderSearchResults(filtered);
  };

  /**
   * Debounced input handler
   */
  const handleInput = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      handleSearch();
    }, 300);
  };

  /**
   * Fetch all clubs from /api/clubs once on page load
   */
  const fetchAllClubs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/clubs', {
        method: 'GET',
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      allClubs = await response.json();  // store in global array
    } catch (error) {
      console.error('Error fetching clubs:', error);
    }
  };

  // Attach event listeners
  searchButton.addEventListener('click', handleSearch);
  clubSearch.addEventListener('input', handleInput);

  // Initial fetch on load
  fetchAllClubs();
});

document.addEventListener('DOMContentLoaded', () => {
  // ... your existing DOMContentLoaded code ...

  // 1. Grab references to the DOM elements
  const collegeSelect = document.getElementById('collegeSelect');
  const collegeSearchButton = document.getElementById('collegeSearchButton');
  const collegeSearchResults = document.getElementById('collegeSearchResults');

  // 2. Add event listener to the "Search" button
  collegeSearchButton.addEventListener('click', async () => {
    // Get the selected college ID
    const selectedCollegeId = collegeSelect.value;

    // If no selection, bail out
    if (!selectedCollegeId) {
      alert('Please select a college.');
      return;
    }

    try {
      // 3. Fetch the clubs from our new endpoint
      const response = await fetch(`http://127.0.0.1:5000/api/clubs/by_college/${selectedCollegeId}`, {
        method: 'GET',
        credentials: 'include' // if your app uses session cookies
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      // 4. Parse the response JSON
      const clubs = await response.json();

      // 5. Render the results
      renderCollegeResults(clubs);

    } catch (error) {
      console.error('Error fetching clubs by college:', error);
      alert('Failed to fetch clubs for this college.');
    }
  });

  // Helper function to display results
  function renderCollegeResults(clubs) {
    // Clear any old results
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

      // Optional: make it clickable to go to clubpage
      resultItem.addEventListener('click', () => {
        window.location.href = `clubpage.html?club_id=${club.id}`;
      });

      collegeSearchResults.appendChild(resultItem);
    });
  }

});
