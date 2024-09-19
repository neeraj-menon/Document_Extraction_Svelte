<!-- <script>
    import { goto } from '$app/navigation';  // SvelteKit navigation
  </script>
  
  <div>
    <h1>Welcome to the SvelteKit App</h1>

    <button on:click={() => goto('/login')}>Go to Login</button>
  </div> -->
  
  
  <script>
    import { goto } from '$app/navigation';
  </script>
  
  <style>
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
  </div>