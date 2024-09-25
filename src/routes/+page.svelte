<!-- <script>
    import { goto } from '$app/navigation';  // SvelteKit navigation
  </script>
  
  <div>
    <h1>Welcome to the SvelteKit App</h1>

    <button on:click={() => goto('/login')}>Go to Login</button>
  </div> -->
  
  
  <!-- <script>
    import { goto } from '$app/navigation';
  </script>
  
  <style lang='postcss'>
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      max-width: 100%;
      background-color: #ffffff;
      padding: 0 1rem;
    }
  
    .header {
      font-size: 2rem;
      color: #333;
      margin-bottom: 1rem;
    }
  
    .description {
      text-align: center;
      color: #666;
      max-width: 600px;
      margin-bottom: 2rem;
    }
  
    .login-button {
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
      padding: 10px 20px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .login-button:hover {
      background-color: #0056b3;
    }
  </style>
  
  <div class="container">
    <h1 class="header">Welcome to DocEx</h1>
    <p class="description">
      DocEx is a software designed to assist healthcare professionals in analyzing and extracting valuable information from medical documents, specifically PDFs. It leverages cutting-edge Natural Language Processing (NLP) and Artificial Intelligence (AI) to streamline workflows and improve efficiency. Log In to get started!
    </p>
    <button class="login-button" on:click={() => goto('/login')}>Log In</button>
  </div> -->


  <!-- <script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let headerText = "Get answers. Find inspiration. Be more productive.";
    let subHeaderText = "Free to use. Easy to try. Just ask and DocEx can help you with writing, learning, and more.";
    let displayedHeaderText = "";
    let displayedSubHeaderText = "";

    const typeText = (text, setter, delay = 50) => {
        let index = 0;
        const interval = setInterval(() => {
            setter(text.slice(0, index + 1));
            index++;
            if (index === text.length) {
                clearInterval(interval);
            }
        }, delay);
    };

    onMount(() => {
        typeText(headerText, (text) => displayedHeaderText = text, 50); // Stream header text first
        setTimeout(() => {
            typeText(subHeaderText, (text) => displayedSubHeaderText = text, 30); // Stream sub-header after
        }, headerText.length * 50); // Delay sub-header streaming until after header finishes
    });
</script>

<style lang='postcss'>
  /* Full page layout */
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    max-width: 100%;
    background-color: #000; /* Dark background */
    color: #fff; /* White text */
    text-align: center;
    padding: 0 1rem;
  }

  /* Large header with clean, bold text */
  .header {
    font-size: 4rem;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .sub-header {
    font-size: 1.5rem;
    font-weight: 400;
    margin-bottom: 2rem;
  }

  /* Button design */
  .login-button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 50px;
    padding: 15px 30px;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.4);
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    position: relative;
    overflow: hidden;
  }

  .login-button:hover {
    background-color: #0056b3;
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0, 191, 255, 0.6);
  }

  .login-button svg {
    transform: rotate(-45deg);
    transition: transform 0.3s ease;
  }

  .login-button:hover svg {
    transform: rotate(0);
  }
</style>

<div class="container">
  <h1 class="header">{displayedHeaderText}</h1>
  <p class="sub-header">{displayedSubHeaderText}</p>
  
  <button class="login-button" on:click={() => goto('/login')}>
    Start now
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14m-7-7l7 7-7 7"/>
    </svg>
  </button>
</div> -->


<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  // Smooth scrolling to the "About" section
  const scrollToAbout = () => {
      const aboutSection = document.getElementById('about-section');
      if (aboutSection) {
          aboutSection.scrollIntoView({ behavior: 'smooth' });
      }
  };

  let headerText = "Get answers. Find inspiration. Be more productive.";
    let subHeaderText = "Easy to use. Just ask and MedData can help you analyze your Medical Reports.";
    let displayedHeaderText = "";
    let displayedSubHeaderText = "";

    const typeText = (text, setter, delay = 50) => {
        let index = 0;
        const interval = setInterval(() => {
            setter(text.slice(0, index + 1));
            index++;
            if (index === text.length) {
                clearInterval(interval);
            }
        }, delay);
    };

    onMount(() => {
        typeText(headerText, (text) => displayedHeaderText = text, 50); // Stream header text first
        setTimeout(() => {
            typeText(subHeaderText, (text) => displayedSubHeaderText = text, 30); // Stream sub-header after
        }, headerText.length * 50); // Delay sub-header streaming until after header finishes
    });
</script>

<style lang='postcss'>
/* Full page layout */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  max-width: 100%;
  background-color: #000; /* Dark background */
  color: #fff; /* White text */
  text-align: center;
  padding: 0 1rem;
}

/* Navbar styles */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 1rem 2rem;
  background-color: #111; /* Slightly lighter than the background */
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  cursor: pointer;
}

.navbar-links a {
  color: #fff;
  text-decoration: none;
  font-size: 1.2rem;
  margin-left: 1rem;
  cursor: pointer;
}

.navbar-links a:hover {
  color: #00bfff;
}

/* Large header with clean, bold text */
.header {
  font-size: 4rem;
  font-weight: bold;
  margin-top: 5rem; /* So it doesn't overlap with the navbar */
  margin-bottom: 1rem;
}

.sub-header {
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 2rem;
}

/* Button design */
.login-button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 30px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.4);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.login-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 191, 255, 0.6);
}

.login-button svg {
  transform: rotate(-45deg);
  transition: transform 0.3s ease;
}

.login-button:hover svg {
  transform: rotate(0);
}

/* About Section */
.about-section {
  margin-top: 50vh; /* Push the section further down */
  padding: 4rem 2rem;
  max-height: 100%;
  background-color: #111; /* Different background to separate sections */
  color: #fff;
  text-align: center;
}

.about-section h2 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.about-section p {
  font-size: 1.2rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>

<!-- Navigation Bar -->
<nav class="navbar">
<!-- Changed the div to a button element for accessibility -->
<button class="navbar-brand" on:click={() => goto('/')} aria-label="Go to homepage">
  MedData
</button>
<div class="navbar-links">
  <!-- Fixed accessibility issues by adding href and role -->
  <a href="#about-section" role="button" on:click={scrollToAbout} on:keydown={(e) => e.key === 'Enter' && scrollToAbout()}>
    About
  </a>
</div>
</nav>

<!-- Main content -->
<div class="container">
  <h1 class="header">{displayedHeaderText}</h1>
  <p class="sub-header">{displayedSubHeaderText}</p>

<button class="login-button" on:click={() => goto('/login')}>
  Start now
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14m-7-7l7 7-7 7"/>
  </svg>
</button>
</div>

<!-- About section -->
<section id="about-section" class="about-section">
<h2>About MedData</h2>
<p>
  MedData is a software designed to assist healthcare professionals in analyzing and extracting valuable information from medical report PDFs. It leverages cutting-edge Natural Language Processing (NLP) and Artificial Intelligence (AI) to streamline workflows and improve efficiency.
</p>
</section>

