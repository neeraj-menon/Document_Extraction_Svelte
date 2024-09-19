<script>
    // Redirect the user to the login URL
    function redirectToLogin() {
      window.location.href = 'http://localhost:5000/login'; // Flask login route
    }
  
    // Call redirectToLogin when component mounts
    import { onMount } from 'svelte';
    onMount(() => {
      redirectToLogin();
    });
  </script>
  
  <h1>Redirecting to login...</h1>
  