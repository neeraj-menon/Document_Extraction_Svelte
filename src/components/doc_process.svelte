<script>
  import { onMount } from 'svelte';

    // import pdfThumbnail from '../../DocEx_frontend/icons/pdf.png';
    // import promptThumbnail from '../../DocEx_frontend/icons/txt.png';

  
  let pdfFile = null;
  let promptFile = null;
  let pdfFilename = '';
  let promptFilename = '';
  let jsonResponse = '';
  let processing = false;
  let errorMessage = '';
  let pdfThumbnail = '/icons/pdf.png';
  let promptThumbnail = '/icons/txt.png';
  let processingStatus = '';
  let progressPercentage = 0;
  let downloadUrl = ''; // URL to download the JSON result
  let userEmail = '';

  // Chatbot state
  let chatData = []; // Holds the current chat session
  let chat_Data = []; // Holds the current chat session
  let chatContainer = []; // Holds the current chat session
  let chatHistory = []; // Holds the list of previous chats
  let selectedChat = null; // The chat currently selected from history
  let fetchChatHistoryError = null; // Error handling for chat history
  let isPanelOpen = false; // Controls the visibility of the chat history panel
  let userInput = ''; // The user's input in the chatbox

  // Add missing declarations
  let fetchResultsHistoryError = null; // Error handling for results history
  let resultsHistory = []; // Holds the list of previous results



    
  onMount(async () => {
        const response = await fetch('http://localhost:5000/user_profile', {
            credentials: 'include' // Include cookies for session
        });
        
        if (response.ok) {
            const data = await response.json();
            userEmail = data.email; // Store the user's email
        } else {
            // Handle error (e.g., user not authenticated)
            console.error('Failed to fetch user profile');
        }
    });




    // Handle drag over for both PDF and Prompt
    function handleDragOver(event) {
        event.preventDefault(); // Prevent default behavior to allow file dropping
    }

    // Handle drop event for PDF file
    function handlePDFDrop(event) {
        event.preventDefault(); // Prevent default behavior
        const file = event.dataTransfer.files[0]; // Get the first file
        if (file && file.type === 'application/pdf') {
            pdfFilename = file.name; // Store filename for display
            pdfThumbnail = pdfThumbnail; // You can also generate a thumbnail if needed
        }
    }

    // Handle drop event for Prompt file
    function handlePromptDrop(event) {
        event.preventDefault(); // Prevent default behavior
        const file = event.dataTransfer.files[0]; // Get the first file
        if (file && file.type === 'text/plain') {
            promptFilename = file.name; // Store filename for display
            promptFilename = promptFilename
        }
    }

    // // Handle file upload for PDF from the input element
    // function handlePDFUpload(event) {
    //     const file = event.target.files[0];
    //     pdfFilename = file.name;
    //     pdfThumbnail = URL.createObjectURL(file); // Generate a URL for the PDF file
    // }

    // // Handle file upload for Prompt from the input element
    // function handlePromptUpload(event) {
    //     const file = event.target.files[0];
    //     promptFilename = file.name;
    //     // Handle any further processing for the .txt file
    // }







  // Function to handle PDF file upload and store its name
  const handlePDFUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
          pdfFile = file;
          pdfFilename = file.name;
          pdfThumbnail = pdfThumbnail;
      }
  };

  // Function to handle prompt file upload and store its name
  const handlePromptUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
          promptFile = file;
          promptFilename = file.name;
          promptThumbnail = promptThumbnail;
      }
  };

  const getProgress = () => {
      const eventSource = new EventSource('http://localhost:5000/progress');
      eventSource.onmessage = function(event) {
          progressPercentage = parseInt(event.data);
          if (progressPercentage === 100) {
              processingStatus = 'Processing completed!';
              eventSource.close();  // Close the connection when complete
          }
      };
  };

  // Function to process the files and send the form data
  const processFiles = async () => {
      if (!pdfFile || !promptFile) {
          errorMessage = 'Please upload both PDF and Prompt files.';
          return;
      }

      const formDataPDF = new FormData();
      formDataPDF.append('pdf_file', pdfFile, pdfFile.name);
      formDataPDF.append('filename', pdfFilename);

      const formDataPrompt = new FormData();
      formDataPrompt.append('prompt_file', promptFile, promptFile.name);
      formDataPrompt.append('filename', promptFilename);

      try {

        await startNewChat();
          processing = true;
          progressPercentage = 0; // Reset progress
          getProgress(); // Simulate progress locally for now

          processingStatus = 'Uploading PDF...';
          errorMessage = '';

          // Upload PDF file
          const pdfResponse = await fetch('http://localhost:5000/upload_pdf', {
              method: 'POST',
              body: formDataPDF,
          });
          const pdfResult = await pdfResponse.json();
          if (pdfResponse.status !== 200) {
              throw new Error(pdfResult.error || 'Error uploading PDF');
          }

          processingStatus = 'Uploading Prompt...';
          // Upload Prompt file
          const promptResponse = await fetch('http://localhost:5000/upload_prompt', {
              method: 'POST',
              body: formDataPrompt,
          });
          const promptResult = await promptResponse.json();
          if (promptResponse.status !== 200) {
              throw new Error(promptResult.error || 'Error uploading Prompt');
          }

          processingStatus = 'Processing files...';
          // Process the files
          const processResponse = await fetch('http://localhost:5000/process_pdf', {
              method: 'POST',
              credentials: 'include',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  pdf_file: pdfResult.pdf_path,
                  prompt_file: promptResult.prompt_content,
              }),
          });

          const processData = await processResponse.json();
          if (processResponse.status !== 200) {
              throw new Error(processData.error || 'Error processing files');
          }

          jsonResponse = JSON.stringify(processData, null, 4);
          processingStatus = 'Processing completed!';
          progressPercentage = 100; // Set to complete when done

          // Set the download URL for the JSON file
          downloadUrl = `http://localhost:5000/download_results?pdf_filename=${pdfFilename}`;
      } catch (error) {
          errorMessage = error.message || 'Something went wrong';
          processingStatus = 'Error occurred';
          progressPercentage = 0; // Reset on error
      } finally {
          processing = false;
      }
  };

  // Function to handle chatbot query submission
  const sendMessage = async () => {
      if (!userInput) return;

      const newMessage = {
          content: userInput,
          role: 'user',
      };

      // Append the new message to the current chat
      chatData = [...chatData, newMessage];
      userInput = ''; // Clear input box

      // Save the updated chat to the backend
      // await saveChat();

      try {
          const response = await fetch('http://localhost:5000/chat', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ message: newMessage.content }),
          });
          const data = await response.json();
          const chatResponse = data.reply;  // Assuming your backend returns a 'reply' field

          // Add chatbot response to chatData
          chatData = [...chatData, { role: 'bot', content: chatResponse }];
          // await saveChat();
      } catch (error) {
          console.error('Error getting chatbot response:', error);
      }
  };


//   async function startNewChat() {
//         try {
//             // Send POST request to the new chat route
//             const response = await fetch('http://localhost:5000/new_chat', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//             });
            
//             if (response.ok) {
//                 const result = await response.json();
//                 // console.log(result.message);

//                 // Clear all chat containers
//                 console.log("Loaded extracted data:", result.extracted_data)
//                 jsonResponse = JSON.stringify(chatData.extracted_data, null, 4);
//                 chatData = [];
//                 chat_Data = [];
//                 chatContainer = [];

//                 // Optionally clear user input
//                 userInput = '';
//             } else {
//                 console.error('Failed to start a new chat');
//             }
//         } catch (error) {
//             console.error('Error:', error);
//         }
//     }




async function startNewChat() {
    try {
        // Send POST request to the new chat route
        const response = await fetch('http://localhost:5000/new_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const result = await response.json();

            // Clear all chat containers
            chatData = [];
            chat_Data = [];
            chatContainer = [];

            // Set jsonResponse to display the extracted data
            jsonResponse = result.extracted_data;

            // Optionally clear user input
            userInput = '';
        } else {
            console.error('Failed to start a new chat');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}











  // Function to fetch the results history
  const fetchResultsHistory = async () => {
      try {
          const response = await fetch('http://localhost:5000/results_history');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          const data = await response.json();
          // console.log("Data: ",data);
          resultsHistory = data;
      } catch (error) {
          fetchResultsHistoryError = error.message || 'Failed to fetch results history';
      }
  };


  // Function to fetch chat history
  const fetchChatHistory = async () => {
      try {
          const response = await fetch('http://localhost:5000/chat_history');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          const data = await response.json();
          console.log("Data: ",data);
          chatHistory = Array.isArray(data) ? data : []; // Ensure chatHistory is always an array
          
      } catch (error) {
          fetchChatHistoryError = error.message || 'Failed to fetch chat history';
      }
  };

  // Function to load a selected chat
  const loadChat = async (chat) => {
      selectedChat = chat;
      // Clear the chat display before loading the previous chat
    chatData = [];  // Clear current chat messages
    chat_Data = []; // Clear any additional chat data if necessary
      try {
          const response = await fetch(`http://localhost:5000/load_chat?chat_id=${chat.chat_id}`);
          if (!response.ok) {
              throw new Error('Failed to load chat');
          }

          const chatData = await response.json(); // Load chat data
          console.log('Loaded chat:', chatData.prompts);
          chat_Data = chatData.prompts
          jsonResponse = chatData.extracted_data;

      } catch (error) {
          console.error('Error loading chat:', error);
          // Reset chat data or handle the error as needed
          chatData = [];
      }
  };

  // Toggle the side panel
  const togglePanel = () => {
      isPanelOpen = !isPanelOpen;
  };

  // Fetch results history and chat history when the component is initialized
  onMount(() => {
    fetchResultsHistory();
      fetchChatHistory();
  });

  const handleLogout = () => {
      window.location.href = 'http://localhost:5000/logout'; // Redirect to the Flask logout endpoint
  };

</script>

<!-- Add the navigation bar -->
<!-- <div class="navbar">
  <div class="navbar-content">
      <button on:click={togglePanel} class="prev-chat-button">
        {isPanelOpen ? 'Close Chat History' : 'Open Chat History'}
      </button>
      <span class="logo">DocEx</span>
      <button on:click={handleLogout} class="logout-button">
          Logout
      </button>
  </div>
</div> -->



<!-- Add the navigation bar -->
<div class="navbar">
    <div class="navbar-content">
        <button on:click={togglePanel} class="prev-chat-button">
          {#if isPanelOpen}
            <!-- Close icon (X) -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          {:else}
            <!-- Menu icon (hamburger) -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          {/if}
        </button>
        <span class="logo">MedData</span>
        <span class="user-email">Welcome, {userEmail}</span> <!-- Display the user's email here -->
        <button on:click={handleLogout} class="logout-button">
            <!-- Logout icon -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H3" />
            </svg>
        </button>
        
    </div>
  </div>
  




<div class="flex justify-between p-4">
  <!-- Left Panel -->
  <div class="left-panel {isPanelOpen ? 'shifted' : ''}">
      <!-- <h1 class="text-2xl font-bold mb-4">Document Processing</h1> -->




      
      <div class="flex justify-between items-start mb-4">
        <!-- PDF Upload Container -->
        <div class="mb-4 min-w-[400px]">
            <label for="pdf" class="block text-lg font-medium mb-2">Upload PDF</label>
            <div
                role="button"
                aria-label="Upload PDF"
                on:drop={handlePDFDrop}
                on:dragover={handleDragOver}
                on:click={() => document.getElementById('pdf').click()}
                on:keydown={(e) => e.key === 'Enter' && document.getElementById('pdf').click()}
                tabindex="0"
                class="border-2 border-dashed border-gray-400 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition ease-in-out duration-300"
            >
                {#if pdfThumbnail}
                    <img src={pdfThumbnail} alt="PDF Thumbnail" class="mt-2 w-12 h-auto mx-auto"/>
                {/if}
                {#if pdfFilename}
                    <p class="text-gray-600 mt-1">Selected file: {pdfFilename}</p>
                {:else}
                    <p class="text-gray-600">Drag & drop a PDF file here, or <button 
                        class="border border-blue-500 text-blue-500 px-2 py-1 rounded-md hover:bg-blue-500 hover:text-white transition ease-in-out duration-300"
                    >
                        browse
                    </button></p>
                {/if}
                <input type="file" id="pdf" accept=".pdf" class="hidden" on:change={handlePDFUpload}/>
            </div>
        </div>
    
        <!-- Prompt Upload Container -->
        <div class="mb-4 min-w-[400px]">
            <label for="prompt" class="block text-lg font-medium mb-2">Upload Prompt</label>
            <div
                role="button"
                aria-label="Upload Prompt"
                on:drop={handlePromptDrop}
                on:dragover={handleDragOver}
                on:click={() => document.getElementById('prompt').click()}
                on:keydown={(e) => e.key === 'Enter' && document.getElementById('prompt').click()}
                tabindex="0"
                class="border-2 border-dashed border-gray-400 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition ease-in-out duration-300"
            >
                {#if promptThumbnail}
                    <img src={promptThumbnail} alt="Prompt Thumbnail" class="mt-2 w-12 h-auto mx-auto"/>
                {/if}
                {#if promptFilename}
                    <p class="text-gray-600 mt-1">Selected file: {promptFilename}</p>
                {:else}
                    <p class="text-gray-600">Drag & drop a text file here, or <button 
                        class="border border-blue-500 text-blue-500 px-2 py-1 rounded-md hover:bg-blue-500 hover:text-white transition ease-in-out duration-300"
                    >
                        browse
                    </button></p>
                {/if}
                <input type="file" id="prompt" accept=".txt" class="hidden" on:change={handlePromptUpload}/>
            </div>
        </div>
    <!-- </div> -->
    




    <div class="process-files">

      <button on:click={processFiles} disabled={processing} class="process-button bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50">
        {#if processing}
        <svg class="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
        </svg>
    {:else}
    <!-- <img src="/icons/process.png" alt="Process Files" class="w-6 h-6 ">
    <span class="tooltip-text bg-gray-700 text-white text-sm rounded py-1 px-2 absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 transition-opacity duration-300">
        Process Files
      </span> -->
      Process Files
    {/if}
      </button>
      </div>
      </div>


      {#if errorMessage}
          <div class="text-red-500 mt-4">{errorMessage}</div>
      {/if}

      {#if processing}
          <div>
              <p>{processingStatus}</p>
              <div class="progress-bar">
                  <div class="progress" style="width: {progressPercentage}%;"></div>
              </div>
              <p>Progress: {progressPercentage}%</p>
          </div>
      {/if}

      <!-- Chatbot -->
      <div class="w-full mt-6">
        <img src="/icons/chatbot.png" alt="AI Assistant" class="w-6 h-6 mr-2">
    
        <!-- AI Assistant Text -->
        <h2 class="text-xl  mb-2">AI Assistant</h2>
          <div class="chat-container">
              <div class="chat-messages">
                {#if chat_Data && chat_Data.length > 0}
                    {#each chat_Data as { prompt, response }, index}
                        <div class="chat-message user" key={index}>
                            <strong>User:</strong> {prompt}
                        </div>
                        <div class="chat-message bot" key={index}>
                            <strong>Response:</strong> {response}
                        </div>
                    {/each}
                {:else}
                    <p></p>
                {/if}
                  {#each chatData as message}
                      <div class="chat-message {message.role}">
                          <strong>{message.role}:</strong> {message.content}
                      </div>
                  {/each}
                {#if chatContainer.length === 0}
                    <!-- <p>No chats yet. Start a conversation!</p> -->
                {:else}
                  {#each chatContainer as chatMessage}
                      <div class="chat-message">
                          {chatMessage}
                      </div>
                  {/each}
                {/if}
              </div>

              <!-- Input for user to type and send messages -->
            <div class="chat-input flex items-center justify-center h-full">
                <input
                    type="text"
                    placeholder="Ask me anything about the processed results..."
                    class="placeholder-centered"
                    bind:value={userInput}
                />
                <button on:click={sendMessage} class="send-msg-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l18-9-9 18-2-7-7-2z" />
                    </svg>
                </button>
            </div>

          </div>
      </div>
  </div>

  <!-- Right Panel -->
  <div class="right-panel {isPanelOpen ? 'shifted' : ''}">
      <!-- {#if jsonResponse}
          <div class="p-4 border border-gray-300 bg-gray-100">
              <h3 class="text-xl font-semibold mb-2">Processed Result:</h3>
              <pre class="whitespace-pre-wrap">{jsonResponse}</pre>

              
              <a href={downloadUrl} download class="bg-green-500 text-white py-2 px-4 rounded mt-4 inline-block hover:bg-green-600">
                  Download JSON Result
              </a>
          </div>
      {/if} -->

      {#if jsonResponse}
  <div class="processed-container p-6 bg-gray-50 rounded-xl shadow-md border border-gray-200">
    <h3 class="text-xl font-semibold mb-4 text-gray-800">Processed Result:</h3>

    <!-- Scrollable JSON response -->
    <div class="json-container">
      <pre class="whitespace-pre-wrap text-gray-700">{jsonResponse}</pre>
    </div>

    <!-- Download button for the JSON file -->
    <a 
      href={downloadUrl} 
      download 
      class="download_json bg-green-500 text-white py-2 px-6 rounded-lg mt-4 inline-block hover:bg-green-600 transition duration-200 ease-in-out flex justify-center items-center"
    >
    <img src="/icons/download_json.png" alt="Download" class="w-5 h-5">
      <!-- <span>Download JSON Result</span> -->
       <!-- Tooltip -->
  <span class="tooltip-text bg-gray-700 text-white text-sm rounded py-1 px-2 absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 transition-opacity duration-300">
    Download JSON
  </span>
    </a>
  </div>
{/if}

      </div>


      <!-- Side Panel -->
      <!-- {#if isPanelOpen} -->
          <div class="side-panel {isPanelOpen ? 'open' : ''}">
            <h3 class="text-lg text-center p-4">Previous Chats</h3>

              {#if fetchChatHistoryError}
                  <div class="text-red-500">{fetchChatHistoryError}</div>
              {:else if chatHistory.length > 0}
                <button on:click={startNewChat} class="new-chat-btn">+ Start New Chat</button>
                  {#each chatHistory as chat}
                      <button
                          class="chat-item"
                          on:click={() => loadChat(chat)}
                          on:keydown={(e) => e.key === 'Enter' && loadChat(chat)}
                          tabindex="0"
                      >
                          <p>{chat.description}</p>
                      </button>
                  {/each}
              {:else}
                  <p class="flex justify-center items-center h-screen text-center">No chat history available.</p>
              {/if}
          </div>
      <!-- {/if} -->
  <!-- </div> -->
</div>

<style lang='postcss'> 
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');


:global(body) {
    background-color: #ffffff; /* Light background color to complement the navbar */
    font-family: 'Poppins', sans-serif; /* Set a clean font for better readability */
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  .navbar {
  /* position: fixed; */
  top: 0;
  width: 100%;
  height: 60px; /* Adjust this height according to your navbar */
  background-color: #212122;
  color: rgb(27, 27, 27);
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.user-email{
    margin-left: 50px;
    margin-top: 10px;
    font-size: 13px;
    color: white;
}


.left-panel {
  width: 60%;              /* Equivalent to 'w-1/2' (50% width) */
  padding-right: 1rem;     /* Equivalent to 'pr-4' (padding-right 1rem or 16px) */
  transition: margin-left 0.3s ease;
  margin-left: 0;
}

.left-panel.shifted {
  margin-left: 250px; /* Same width as the side panel */
}

.right-panel {
  width: 40%;              /* Equivalent to 'w-1/2' (50% width) */
  padding-left: 1rem;      /* Equivalent to 'pl-4' (padding-left 1rem or 16px) */
  transition: margin-left 0.3s ease;
  margin-left: 0;
}

.process-files{
    margin-top: 30px;
    
}

.process-button{
    border-radius: 50px;
    position: relative;
    background: linear-gradient(135deg, #1d4ed8 0%, #6278c0 100%);
}

.process-button:hover {
    visibility: visible;
    opacity: 1;
    background: linear-gradient(135deg, #11328b 0%, #6278c0 100%);
}

/* .process-button:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
} */

.prev-chat-button {
    background-color: #212122; 
    /* background: linear-gradient(135deg, #919dbe 0%, #f6f6f8 100%); */
    color: white;
    padding: 0.5rem 1rem; 
    border-radius: 0.375rem; 
    margin-top: 7px;
    cursor: pointer; 
    margin-left: 20px;
}

  .navbar-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
  }

  .logo {
      font-size: 1.5em;
      font-weight: bold;
      margin-right: 400px;
      margin-left: 800px;
      margin-top: 10px;
      color: white;
  }

  .logout-button {
      background-color: #212122; /* Red color */
      color: white;
      border: 1px solid white;
      padding: 10px 20px;
      font-size: 1em;
      cursor: pointer;
      border-radius: 5px;
      margin-right: 20px;
      margin-left: 10px;
      margin-top: 9px;
      border-radius: 50px;
  }

  .logout-button:hover {
      background-color: #b3acac; /* Darker red */
  }

  .progress-bar {
    width: 100%;
    height: 8px; /* Thinner height */
    background-color: #e0e0e0; /* Subtle, modern background color */
    border-radius: 50px; /* More rounded for a sleek look */
    overflow: hidden;
    margin: 12px 0; /* Slightly more spacing for a cleaner feel */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.progress {
    height: 100%;
    background-color: #00c853; /* Sleek modern green color */
    width: 0;
    transition: width 0.3s ease-in-out; /* Smooth, quick transition */
    border-radius: 50px; /* Rounded edges for modern effect */
}

  .chat-container {
      display: flex;
      flex-direction: column;
      height: 575px; /* Adjust the height as needed */
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      background-color: #f9f9f9;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(0, 0, 0, 0.08); /* More prominent shadow */
  }

  /* Add a slight elevation effect on hover */
.chat-container:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08), 0 6px 12px rgba(0, 0, 0, 0.04);
}

/* Optional: Scrollbar styling */
.chat-messages::-webkit-scrollbar {
    width: 8px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background-color: #9ca3af; /* Subtle gray thumb color */
    border-radius: 8px;
    border: 2px solid #f8fafc; /* Matches the container background */
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background-color: #6b7280; /* Slightly darker hover color */
}

  .chat-messages {
    display: flex;
    flex-direction: column;
      height: 590px;
      overflow-y: auto;
      background-color: #f8fafc;;
      padding: 10px;
      margin-bottom: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }


  /* User message styling */
.chat-message.user {
    max-width: 70%;
    margin: 8px 0;
    padding: 12px 16px;
    border-radius: 20px;
    background: linear-gradient(135deg, #1d4ed8 0%, #6278c0 100%); /* Blue gradient */
    color: white;
    align-self: flex-end;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); /* Soft shadow for depth */
    border-bottom-right-radius: 0;
    font-size: 13.5px;
    /* font-weight: bold; */
}

/* Bot message styling */
.chat-message.bot {
    max-width: 70%;
    margin: 8px 0;
    padding: 12px 16px;
    border-radius: 20px;
    background: linear-gradient(135deg, #059669 0%, #33c49b 100%); /* Green gradient */
    color: white;
    align-self: flex-start;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    border-bottom-left-radius: 0;
    font-size: 13.5px;
    /* font-weight: bold; */
}

  .chat-input {
      display: flex;
      align-items: center;
      padding: 10px;
      border-top: 1px solid #ddd;
      background: #fff;
      height: 60px; /* Set a fixed height for the input area */
  }

  .chat-input input {
      width: 80%;
      padding: 10px;
      margin-right: 10px;
      margin-top: 25px;
  }

  .placeholder-centered {
  display: block; /* Ensure the placeholder is displayed as a block element */
  margin-bottom: 30px; /* Center the placeholder vertically */
}

  .chat-input button {
      padding: 10px 20px;
  }

  .send-msg-btn{
    /* background-color: #2563eb;  */
    background: linear-gradient(135deg, #1d4ed8 0%, #6278c0 100%);
      color: white;
      border: none;
      /* padding: 20px 20px; */
      font-size: 1em;
      cursor: pointer;
      border-radius: 50px;
      align-items: center;
      margin-left: 90px;
      margin-top: 1px;

  }

  .send-msg-btn:hover {
    /* background-color: #1b51c5; Darker blue on hover */
    background: linear-gradient(135deg, #11328b 0%, #6278c0 100%);
}

.send-msg-btn svg {
    width: 16px;
    height: 16px;
    stroke-width: 2;
    stroke: white; /* Icon color */
}



  .new-chat-btn {
      /* background-color: red;
      color: white; */
      /* border: 1px solid black; */
      background-color: #b3acac; /* Red color */
      color: white;
      border: none;
      padding: 10px 20px;
      font-size: 0.95em;
      cursor: pointer;
      border-radius: 5px;
      margin-top: 20px;
      margin-bottom: 20px;
      margin-left: 10px;
      margin-right: 10px;
      width: 90%;
  }

  .new-chat-btn:hover {
      background-color: #212122; /* Darker red */
  }


  .processed-container{
    height: 837px; /* Adjust height as needed */
  }

  /* Modernized container for scrollable JSON response */
.json-container {
    height: 697px; /* Adjust height as needed */
    overflow-y: auto;
    background-color: #f8fafc; /* Light gray background for readability */
    padding: 20px;
    border: 1px solid #e5e7eb; /* Light border */
    border-radius: 8px; /* Smoother corner radius */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* Subtle shadow for depth */
    font-family: 'Poppins', sans-serif; /* Modern font */
    color: #111827; /* Dark text color */
    font-size: 14px;
    line-height: 1.6;
}

/* Custom scrollbar styling for WebKit browsers */
.json-container::-webkit-scrollbar {
    width: 8px;
}

.json-container::-webkit-scrollbar-track {
    background-color: #f1f1f1; /* Light track color */
    border-radius: 8px;
}

.json-container::-webkit-scrollbar-thumb {
    background-color: #9ca3af; /* Subtle gray thumb color */
    border-radius: 8px;
    border: 2px solid #f8fafc; /* Matches the container background */
}

.json-container::-webkit-scrollbar-thumb:hover {
    background-color: #6b7280; /* Slightly darker hover color */
}

/* Hover effect for better user experience */
.json-container:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08); /* Elevation on hover */
    transition: box-shadow 0.2s ease-in-out;
}

.download_json{
    border: none;
    position: relative;
    /* padding: 20px 20px; */
    background: linear-gradient(135deg, #059669 0%, #33c49b 100%);
    width: 70px;
    font-size: 1em;
    cursor: pointer;
    border-radius: 50px;
    align-items: center;
    margin-top: 20px;
    /* margin-right: 50%;
    margin-left: 50%; */
    border-radius: 50px;

}

.tooltip-text {
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.download_json:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

  /* Sidebar styles */
  .side-panel {
  position: fixed;
  top: 60px;
  left: 0;
  width: 0;
  height: 100%;
  /* background-color: #f4f4f4; */
  background-color: #ffffff;
  overflow-x: hidden;
  overflow-y: auto;
  transition: width 0.1s ease;
  /* box-shadow: 2px 0 5px rgba(0, 0, 0, 0.5); */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  /* padding: 20px 10px;  */
}

.side-panel.open {
  width: 250px; /* Define the width of the open panel */
}

/* Ensure each chat item takes a full line */
.chat-item {
  display: flex; /* Each chat item will be displayed in its own line */
  padding: 10px;
  background-color: white;
  width:90%;
  margin-bottom: 10px;
  margin-left: 10px;
  margin-right: 10px;
  margin-top: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
}

/* Add hover effect */
.chat-item:hover {
  background-color: #b3acac;
  color: white;
}

/* Optional: Customize the scrollbar (webkit browsers only) */
.side-panel::-webkit-scrollbar {
  width: 8px;
}

.side-panel::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 4px;
}

.side-panel::-webkit-scrollbar-thumb:hover {
  background-color: #555;
}


</style>
