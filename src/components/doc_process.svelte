<script>
  import { onMount } from 'svelte';

  let pdfFile = null;
  let promptFile = null;
  let pdfFilename = '';
  let promptFilename = '';
  let jsonResponse = '';
  let processing = false;
  let errorMessage = '';
  let pdfThumbnail = '';
  let promptThumbnail = '';
  let processingStatus = '';
  let progressPercentage = 0;
  let downloadUrl = ''; // URL to download the JSON result

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

  // Function to handle PDF file upload and store its name
  const handlePDFUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
          pdfFile = file;
          pdfFilename = file.name;
          pdfThumbnail = URL.createObjectURL(file);
      }
  };

  // Function to handle prompt file upload and store its name
  const handlePromptUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
          promptFile = file;
          promptFilename = file.name;
          promptThumbnail = URL.createObjectURL(file);
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

  // Function to save the chat to the backend
  // const saveChat = async () => {
  //     try {
  //         const response = await fetch('http://localhost:5000/save_chat', {
  //             method: 'POST',
  //             headers: { 'Content-Type': 'application/json' },
  //             body: JSON.stringify({
  //                 session_id: selectedChat ? selectedChat.session_id : `conversation_${new Date().toISOString()}`,
  //                 chat: chatData
  //             }),
  //         });

  //         if (!response.ok) {
  //             throw new Error('Failed to save chat');
  //         }

  //         console.log('Chat saved successfully');
  //     } catch (error) {
  //         console.error('Error saving chat:', error);
  //     }
  // };

  // Function to start a new chat
  // const startNewChat = async () => {
  //     try {
  //         const response = await fetch('http://localhost:5000/new_chat', {
  //             method: 'POST',
  //             headers: {
  //                 'Content-Type': 'application/json',
  //             },
  //             body: JSON.stringify({ session_id: Date.now() }), // Generate a unique session ID
  //         });
  //         if (response.status !== 200) {
  //             throw new Error('Error starting new chat');
  //         }
  //         // Clear the messages array to start a fresh conversation
  //         chatData = [];
  //     } catch (error) {
  //         errorMessage = error.message || 'Failed to start a new chat';
  //     }
  // };


  async function startNewChat() {
        try {
            // Send POST request to the new chat route
            const response = await fetch('http://localhost:5000/new_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(result.message);

                // Clear all chat containers
                chatData = [];
                chat_Data = [];
                chatContainer = [];

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
      try {
          const response = await fetch(`http://localhost:5000/load_chat?chat_id=${chat.chat_id}`);
          if (!response.ok) {
              throw new Error('Failed to load chat');
          }

          const chatData = await response.json(); // Load chat data
          console.log('Loaded chat:', chatData.prompts);
          chat_Data = chatData.prompts

          // Assuming you want to update the chat display with the loaded data
          // For example, update a chatbox with chatData
          // updateChatBox(chatData);
      } catch (error) {
          console.error('Error loading chat:', error);
          // Reset chat data or handle the error as needed
          chatData = [];
      }
  };

  // Example function to update chatbox (customize as needed)
  const updateChatBox = (chatData) => {
      // Implementation to display chatData in the UI
      // For example, set chat data in a chatbox component
      console.log('Updating chatbox with:', chatData);
  };

  // Toggle the side panel
  const togglePanel = () => {
      isPanelOpen = !isPanelOpen;
  };

  // Fetch results history and chat history when the component is initialized
  // fetchResultsHistory();
  // fetchChatHistory();

  onMount(() => {
    fetchResultsHistory();
      fetchChatHistory();
  });

  const handleLogout = () => {
      window.location.href = 'http://localhost:5000/logout'; // Redirect to the Flask logout endpoint
  };

</script>

<!-- Add the navigation bar -->
<div class="navbar">
  <div class="navbar-content">
      <button on:click={togglePanel} class="prev-chat-button">
        {isPanelOpen ? 'Close Chat History' : 'Open Chat History'}
      </button>
      <span class="logo">DocEx</span>
      <button on:click={handleLogout} class="logout-button">
          Logout
      </button>
  </div>
</div>

<div class="flex justify-between p-4">
  <!-- Left Panel -->
  <div class="w-1/2 pr-4">
      <h1 class="text-2xl font-bold mb-4">Document Processing</h1>

      <div class="mb-4">
          <label for="pdf" class="block text-lg font-medium">Upload PDF</label>
          <input type="file" id="pdf" accept=".pdf" on:change={handlePDFUpload} class="mt-2"/>
          {#if pdfThumbnail}
              <img src={pdfThumbnail} alt="PDF Thumbnail" class="mt-2 w-32 h-auto"/>
          {/if}
          {#if pdfFilename}
              <p class="text-gray-600 mt-1">Selected file: {pdfFilename}</p>
          {/if}
      </div>

      <div class="mb-4">
          <label for="prompt" class="block text-lg font-medium">Upload Prompt</label>
          <input type="file" id="prompt" accept=".txt" on:change={handlePromptUpload} class="mt-2"/>
          {#if promptThumbnail}
              <img src={promptThumbnail} alt="Prompt Thumbnail" class="mt-2 w-32 h-auto"/>
          {/if}
          {#if promptFilename}
              <p class="text-gray-600 mt-1">Selected file: {promptFilename}</p>
          {/if}
      </div>

      <button on:click={processFiles} disabled={processing} class="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50">
          {processing ? 'Processing...' : 'Process Files'}
      </button>

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
          <h2 class="text-xl font-bold mb-2">Chatbot</h2>
          <div class="chat-container">
              <div class="chat-messages">
                  {#each chatData as message}
                      <div class="chat-message {message.role}">
                          <strong>{message.role}:</strong> {message.content}
                      </div>
                  {/each}
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
                    <p>No messages to display.</p>
                {/if}
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
              <div class="chat-input">
                  <input
                      type="text"
                      placeholder="Ask me anything about the processed results..."
                      bind:value={userInput}
                  />
                  <button on:click={sendMessage} class="send-msg-btn">Send</button>
                  <!-- <button on:click={startNewChat} class="new-chat-btn">Start New Chat</button> -->
              </div>
          </div>
      </div>
  </div>

  <!-- Right Panel -->
  <div class="w-1/2 pl-4">
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
        <div class="p-4 border border-gray-300 bg-gray-100">
          <h3 class="text-xl font-semibold mb-2">Processed Result:</h3>

          <!-- Scrollable JSON response -->
          <div class="json-container">
            <pre class="whitespace-pre-wrap">{jsonResponse}</pre>
          </div>

          <!-- Download button for the JSON file -->
          <a href={downloadUrl} download class="bg-green-500 text-white py-2 px-4 rounded mt-4 inline-block hover:bg-green-600">
            Download JSON Result
          </a>
        </div>
      {/if}


      <!-- Results History -->
      <!-- <div class="results-history mt-6">
          <h2 class="text-xl font-bold mb-2">Results History</h2>
          {#if fetchResultsHistoryError}
              <div class="text-red-500">{fetchResultsHistoryError}</div>
          {:else if resultsHistory.length > 0}
              <ul>
                  {#each resultsHistory as result}
                      <li class="mb-2">
                          <a href={result.downloadUrl} class="text-blue-500 hover:underline">{result.filename}</a>
                          <span class="ml-2 text-gray-500">({result.date})</span>
                      </li>
                  {/each}
              </ul>
          {:else}
              <p>No results history available.</p>
          {/if}
      </div> -->

      <!-- Side Panel Button -->
      <!-- <button on:click={togglePanel} class="bg-gray-500 text-white py-2 px-4 rounded mt-4">
          {isPanelOpen ? 'Close Chat History' : 'Open Chat History'}
      </button> -->

      <!-- Side Panel -->
      {#if isPanelOpen}
          <div class="side-panel">
              <h3 class="text-lg font-bold">Previous Chats</h3>
              {#if fetchChatHistoryError}
                  <div class="text-red-500">{fetchChatHistoryError}</div>
              {:else if chatHistory.length > 0}
                <button on:click={startNewChat} class="new-chat-btn">Start New Chat</button>
                  {#each chatHistory as chat}
                      <button
                          class="chat-item"
                          on:click={() => loadChat(chat)}
                          on:keydown={(e) => e.key === 'Enter' && loadChat(chat)}
                          tabindex="0"
                      >
                          <p>{chat.chat_id}</p>
                      </button>
                  {/each}
              {:else}
                  <p>No chat history available.</p>
              {/if}
          </div>
      {/if}
  </div>
</div>

<style lang='postcss'> 
  /* .navbar {
      background-color: #333;
      color: white;
      padding: 10px;
  } */
  .navbar {
  /* position: fixed; */
  top: 0;
  width: 100%;
  height: 60px; /* Adjust this height according to your navbar */
  background-color: #333;
  color: white;
  z-index: 1000;
}


.prev-chat-button {
    background-color: #6b7280; 
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
  }

  .logout-button {
      background-color: #f44336; /* Red color */
      color: white;
      border: none;
      padding: 10px 20px;
      font-size: 1em;
      cursor: pointer;
      border-radius: 5px;
      margin-right: 20px;
      margin-left: 70px;
      margin-top: 7px;
  }

  .logout-button:hover {
      background-color: #d32f2f; /* Darker red */
  }

  .progress-bar {
      width: 100%;
      background-color: #f3f3f3;
      border-radius: 8px;
      overflow: hidden;
      margin: 10px 0;
  }

  .progress {
      height: 24px;
      background-color: #4caf50;
      width: 0;
      transition: width 0.4s ease;
  }

  .chat-container {
      display: flex;
      flex-direction: column;
      height: 400px; /* Adjust the height as needed */
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      background-color: #f9f9f9;
  }

  .chat-messages {
      height: 300px;
      overflow-y: auto;
      background-color: #f9f9f9;
      padding: 10px;
      margin-bottom: 10px;
  }

  .chat-message.user {
      text-align: right;
  }

  .chat-message.bot {
      text-align: left;
  }

  .chat-input {
      display: flex;
      align-items: center;
      padding: 10px;
      border-top: 1px solid #ddd;
      background: #fff;
  }

  .chat-input input {
      width: 80%;
      padding: 10px;
      margin-right: 10px;
  }

  .chat-input button {
      padding: 10px 20px;
  }

  .send-msg-btn{
    background-color: #2563eb; 
      color: white;
      border: none;
      padding: 20px 20px;
      font-size: 1em;
      cursor: pointer;
      border-radius: 5px;
      align-items: center;
      margin-left: 70px;
      margin-top: 10px;

  }

  .new-chat-btn {
      /* background-color: red;
      color: white; */
      background-color: #f44336; /* Red color */
      color: white;
      border: none;
      padding: 10px 20px;
      font-size: 0.95em;
      cursor: pointer;
      border-radius: 5px;
      margin-top: 20px;
      margin-bottom: 20px;
  }

  /* Container for scrollable JSON response */
  .json-container {
    max-height: 730px; /* Adjust height as needed */
    overflow-y: auto;  /* Enable vertical scrolling */
    background-color: #ffffff; /* Optional: white background for readability */
    padding: 10px;
    border: 1px solid #ccc; /* Optional: border to separate the scrollable area */
    border-radius: 4px;
  }

  /* Optional: Custom scrollbar styling (for WebKit browsers) */
  .json-container::-webkit-scrollbar {
    width: 8px;
  }

  .json-container::-webkit-scrollbar-thumb {
    background-color: #888;
    border-radius: 4px;
  }

  .json-container::-webkit-scrollbar-thumb:hover {
    background-color: #555;
  }



  /* .results-history {
      margin-top: 16px;
  }

  .results-history a {
      color: #007bff;
      text-decoration: none;
  }

  .results-history a:hover {
      text-decoration: underline;
  } */

  /* .side-panel {
      position: absolute;
      top: 0;
      left: 0;
      width: 300px;
      height: 100%;
      background: #f8f9fa;
      border-left: 1px solid #ddd;
      padding: 10px;
      overflow-y: auto;
      z-index: 1000;
  } */

    /* .side-panel {
    position: fixed;
    top: 60px; 
    left: 0;
    width: 300px;
    height: calc(100% - 60px); 
    background-color: #f8f9fa;
    border-right: 1px solid #ddd;
    z-index: 999; 
    overflow-y: auto;
    transition: transform 0.3s ease-in-out;
  }

  .chat-item {
      cursor: pointer;
      padding: 5px;
      border-bottom: 1px solid #ddd;
  }

  .chat-item:hover {
      background-color: #eee;
  } */

  /* Sidebar styles */
.side-panel {
  width: 200px; /* Adjust the width as needed */
  background-color: #f0f0f0; /* Optional: light background for the sidebar */
  padding: 10px;
  position: absolute; /* Ensure it is positioned correctly */
  top: 60px; /* Adjust this to be below the navbar */
  left: 0;
  height: calc(100vh - 60px); /* Full height minus the navbar height */
  overflow-y: auto; /* Scrollable content */
  z-index: 999; /* Ensure it's below the navbar but above other elements */
}

/* Ensure each chat item takes a full line */
.chat-item {
  display: block; /* Each chat item will be displayed in its own line */
  padding: 10px;
  background-color: white;
  margin-bottom: 10px;
  margin-top: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

/* Add hover effect */
.chat-item:hover {
  background-color: #e0e0e0;
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
