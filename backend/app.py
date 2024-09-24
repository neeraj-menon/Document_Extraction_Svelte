import os
import json
import shutil
import datetime
from flask import Flask, request, jsonify, send_file, Response, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from text_processing import process_text
from authlib.integrations.flask_client import OAuth
from functools import wraps
import secrets

import time
import os
from groq import Groq
import json
import shutil
import datetime
from flask_cors import CORS
from flask_session import Session  # Import Session
from flask import Flask, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from text_processing import process_text
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from authlib.jose import jwt
from functools import wraps
import os
import secrets
import redis

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Replace with a secure secret key

# Configure session to use Redis
app.config['SESSION_TYPE'] = 'redis'                     # Store sessions in Redis
app.config['SESSION_PERMANENT'] = False                  # Sessions will expire on browser close
app.config['SESSION_USE_SIGNER'] = True                  # Sign the session cookie for integrity
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)  # Connect to Redis

# Initialize the Flask-Session extension
Session(app)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# Configure the OAuth client with Auth0 directly with hardcoded values
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id='qLihQMXNaEl08heMIy21cTzySyvgGjgq',
    client_secret='RY2VuhtEI_O4MMvw7XIeHgDPDfk0H_yZmx4F1GlSb79u2_KEQYD6dI-ocgmx-qn7',
    api_base_url='https://dev-v321duxg30j1tevd.us.auth0.com',
    access_token_url='https://dev-v321duxg30j1tevd.us.auth0.com/oauth/token',
    authorize_url='https://dev-v321duxg30j1tevd.us.auth0.com/authorize',
    client_kwargs={'scope': 'openid profile email'},
    jwks_uri='https://dev-v321duxg30j1tevd.us.auth0.com/.well-known/jwks.json',
)

# Decorator to require authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return redirect('http://localhost:5173')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/callback')
def callback():
    global email_id_forjson
    global active_chat
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    user_info = resp.json()
    session['profile'] = {
        'user_id': user_info['sub'],
        'name': user_info['name'],
        'email': user_info['email']
    }
    email_id_forjson = user_info['email']
    # After login, initialize the user data JSON
    setup_user_data_file()
    
    # Generate next sequential chat_id
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
    
    if email_id_forjson in user_data.keys():
    
        # Determine next chat_id
        existing_chats = list(user_data[email_id_forjson].keys())
        if existing_chats:
            next_chat_number = existing_chats[-1]
            next_chat_number = int(next_chat_number[-1])
            # chat_id = f"chat_{next_chat_number}"
            # next_chat_number = len(existing_chats)
            active_chat = f"chat_{next_chat_number}"
        else:
            active_chat = "chat_0"
            user_data[email_id_forjson][active_chat] = {}
        print(active_chat)

    
    return redirect('http://localhost:5173/doc_process')

@app.route('/dashboard')
@requires_auth
def dashboard():
    return f'Hello, {session["profile"]["name"]}! <a href="/logout">Logout</a>'

@app.route('/user_profile')
@requires_auth
def user_profile():
    return jsonify(session['profile'])


@app.route('/logout')
def logout():
    session.clear()
    delete_folder_contents('./uploads')
    delete_folder_contents('./DocEx_frontend/backend/temp')
    
    
    return redirect(f'https://dev-v321duxg30j1tevd.us.auth0.com/v2/logout?client_id=qLihQMXNaEl08heMIy21cTzySyvgGjgq&returnTo={url_for("home", _external=True)}')

def delete_folder_contents(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # Remove file or link
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Remove empty directory
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def setup_user_data_file():
    """Setup a JSON file for the current user based on their email."""
    # email = session.get('profile', {}).get('email')
    email = email_id_forjson
    print(email)
    if not email:
        return

    
    # Define the path to the user data file
    user_data_file = os.path.join('DocEx_frontend', 'user_data', 'user_data.json')
    app.config['USER_DATA_FILE'] = user_data_file
    
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
                              
    if email not in user_data.keys():
        user_data[email] = {}
        with open(user_data_file, 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
        
    print(user_data[email])

    # Ensure the user data file exists
    if not os.path.exists(user_data_file):
        with open(user_data_file, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
            
            
            
# def update_user_data(email, chat_id, prompt, response, extracted_data):
#     """Update the user's JSON file with new chat data."""
#     user_data_file = app.config['USER_DATA_FILE']
    
#     with open(user_data_file, 'r', encoding='utf-8') as file:
#         user_data = json.load(file)

#     if email not in user_data:
#         user_data[email] = {}

#     if chat_id not in user_data[email]:
#         user_data[email][chat_id] = {
#             "prompts": {},
#             "extracted_data": {}
#         }
    
#     # Update the prompts and extracted data
#     user_data[email][chat_id]["prompts"][prompt] = response
#     user_data[email][chat_id]["extracted_data"] = extracted_data

#     with open(user_data_file, 'w', encoding='utf-8') as file:
#         json.dump(user_data, file, ensure_ascii=False, indent=4)



def update_user_data(email, chat_id, prompt, response, extracted_data, description):
    """Update the user's JSON file with new chat data."""
    user_data_file = app.config['USER_DATA_FILE']
    
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    if email not in user_data:
        user_data[email] = {}

    if chat_id not in user_data[email]:
        user_data[email][chat_id] = {
            "prompts": [],
            "extracted_data": {},
            "description": "No chat"
        }
    
    # Append the prompt-response pair to the list of prompts
    user_data[email][chat_id]["prompts"].append({
        "prompt": prompt,
        "response": response
    })
    
    user_data[email][chat_id]["description"] = description
    
    # Update extracted data if provided
    if extracted_data:
        user_data[email][chat_id]["extracted_data"] = extracted_data

    with open(user_data_file, 'w', encoding='utf-8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)

        
        
        
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

progress = 0  # To track the overall progress
result_data = ""
conversation_id = ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    pdf_file = request.files['pdf_file']
    expected_filename = request.form.get('filename')

    if pdf_file and allowed_file(pdf_file.filename):
        if pdf_file.filename != expected_filename:
            return jsonify({'error': 'Filename mismatch'}), 400
        
        filename = secure_filename(pdf_file.filename)
        pdf_path = os.path.join('uploads', filename)
        pdf_file.save(pdf_path)
        
        return jsonify({'message': 'PDF uploaded', 'pdf_path': pdf_path}), 200
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload_prompt', methods=['POST'])
def upload_prompt():
    if 'prompt_file' not in request.files:
        return jsonify({'error': 'No prompt file provided'}), 400

    prompt_file = request.files['prompt_file']
    expected_filename = request.form.get('filename')

    if prompt_file and allowed_file(prompt_file.filename):
        if prompt_file.filename != expected_filename:
            return jsonify({'error': 'Filename mismatch'}), 400
        
        filename = secure_filename(prompt_file.filename)
        prompt_path = os.path.join('uploads', filename)
        prompt_file.save(prompt_path)
        
        return jsonify({'message': 'Prompt uploaded', 'prompt_content': prompt_path}), 200
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/progress')
def progress_stream():
    def generate():
        global progress
        while progress < 100:
            time.sleep(1)
            yield f"data:{progress}\n\n"
        yield "data:100\n\n"
    return Response(generate(), mimetype='text/event-stream')


# @app.route('/process_pdf', methods=['POST'])
# def process_pdf():
#     global progress
#     pdf_file = request.json.get('pdf_file')
#     prompt_file = request.json.get('prompt_file')

#     with open(prompt_file, 'r') as file:
#         system_prompt = file.read()

#     if not pdf_file or not prompt_file:
#         return jsonify({'error': 'No file or prompt provided'}), 400

#     progress = 60  # Start processing
#     extracted_text = process_text(pdf_file, system_prompt)
    
#     progress = 80  # Processing nearing completion
#     json_data = json.dumps(extracted_text, ensure_ascii=False, indent=4)
    
#     # Update the user data file
#     email = session.get('profile', {}).get('email')
#     chat_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     update_user_data(email, chat_id, system_prompt, json_data, extracted_text)
    
#     progress = 100  # Processing complete
#     return jsonify(extracted_text), 200


# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_message = data.get('message')
#     if not user_message:
#         return jsonify({'reply': 'No message provided'}), 400

#     email = session.get('profile', {}).get('email')
#     chat_id = data.get('session_id', datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    

#     user_data_file = app.config['USER_DATA_FILE']
#     with open(user_data_file, 'r', encoding='utf-8') as file:
#         user_data = json.load(file)

#     if email not in user_data:
#         user_data[email] = {}

#     if chat_id not in user_data[email]:
#         user_data[email][chat_id] = {
#             "prompts": {},
#             "extracted_data": {}
#         }

#     conversation_history = []
#     if user_data[email][chat_id]["prompts"]:
#         conversation_history = [
#             {"role": "user", "content": k}
#             for k in user_data[email][chat_id]["prompts"].keys()
#         ]
#         conversation_history.append({"role": "system", "content": user_data[email][chat_id]["extracted_data"]})

#     # Initialize Groq client with API key
#     client = Groq(api_key="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")

#     # Set the system prompt
#     system_prompt = {
#         "role": "system",
#         "content": "You are a helpful assistant who answers questions based on the provided data."
#     }
    
#     # Append user message to the conversation history
#     conversation_history.append({"role": "user", "content": user_message})

#     # Get the response from Groq
#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=conversation_history,
#         max_tokens=1024,
#         temperature=1.2
#     )

#     assistant_reply = response.choices[0].message.content

#     # Update the user's data file with the new prompt and response
#     update_user_data(email, chat_id, user_message, assistant_reply, user_data[email][chat_id]["extracted_data"])

#     return jsonify({'reply': assistant_reply}), 200




@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    global progress
    global active_chat
    pdf_file = request.json.get('pdf_file')
    prompt_file = request.json.get('prompt_file')

    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    if not pdf_file or not prompt_file:
        return jsonify({'error': 'No file or prompt provided'}), 400

    progress = 60  # Start processing
    extracted_text = process_text(pdf_file, system_prompt)
    
    progress = 80  # Processing nearing completion
    json_data = json.dumps(extracted_text, ensure_ascii=False, indent=4)
    
    # Update the user data file
    # email = session.get('profile', {}).get('email')
    email = email_id_forjson
    
    # Generate next sequential chat_id
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    if email not in user_data:
        user_data[email] = {}

    # Determine next chat_id
    # existing_chats = user_data[email].keys()
    # next_chat_number = len(existing_chats)
    existing_chats = list(user_data[email].keys())
    
    if len(existing_chats) > 1:
        next_chat_number = existing_chats[-1]
        next_chat_number = int(next_chat_number[-1])
        chat_id = f"chat_{next_chat_number}"
    else:
        chat_id = "chat_0"
    
    session['active_chat_id'] = chat_id
    active_chat = session['active_chat_id']
    
    active_chat = chat_id

    # Update user data
    # update_user_data(email, chat_id, system_prompt, json_data, extracted_text)
    update_user_data(email, chat_id, "", "", extracted_text, "No chat")
    
    # Check if the folder exists
    folder_path = './DocEx_frontend/backend/extracted_images'
    if os.path.exists(folder_path):
        # Remove the folder and its contents
        shutil.rmtree(folder_path)
        print(f"The folder '{folder_path}' has been deleted.")
    else:
        print(f"The folder '{folder_path}' does not exist.")
    
    progress = 100  # Processing complete
    return extracted_text, 200


@app.route('/download_results', methods=['GET'])
def download_results():
    pdf_filename = request.args.get('pdf_filename')
    
    if not pdf_filename:
        return jsonify({'error': 'No PDF filename provided'}), 400
    
    # Generate next sequential chat_id
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
    
    # Retrieve the results for the specified PDF
    # user_data = load_user_data()
    # email = session['profile']['email']
    # email = session.get('profile', {}).get('email')
    email = email_id_forjson
    # existing_chats = user_data[email].keys()
    # next_chat_number = len(existing_chats)
    # chat_id = f"chat_{next_chat_number}"
    
    
    existing_chats = list(user_data[email].keys())
    next_chat_number = existing_chats[-1]
    next_chat_number = int(next_chat_number[-1])
    chat_id = f"chat_{next_chat_number}"
    
    
    if email not in user_data:
        return jsonify({'error': 'User data not found'}), 404
    
    results = {}
    # for chat_id, chat_data in user_data[email].items():
    #     if 'result' in chat_data:
    #         results[chat_id] = chat_data['result']
    results = user_data[email][chat_id]["extracted_data"]
    
    # Create a JSON response for download
    result_data = json.dumps(results, ensure_ascii=False, indent=4)
    result_json = json.loads(result_data)
    return Response(result_json, mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=results.json'})



@app.route('/chat', methods=['POST'])
def chat():
    global active_chat
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'reply': 'No message provided'}), 400

    email = email_id_forjson
    # email = session.get('profile', {}).get('email')
    print(email)
    
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    if email not in user_data:
        user_data[email] = {}

    # # Determine next chat_id if not provided
    # existing_chats = user_data[email].keys()
    # next_chat_number = len(existing_chats)
    # chat_id = f"chat_{next_chat_number}"
    # print(chat_id)
    
    # # Use the active chat ID from the session
    # chat_id = session.get('active_chat_id')
    
    # if not chat_id:
    #     return jsonify({'error': 'No active chat loaded'}), 400
    
    # Use session['active_chat_id'] or default to the next chat if not set
    # chat_id = session.get('active_chat_id')
    chat_id = active_chat
    print(chat_id)
    if not chat_id:
        # Determine next chat_id
        # existing_chats = user_data[email].keys()
        # next_chat_number = len(existing_chats)
        # chat_id = f"chat_{next_chat_number}"
        
        existing_chats = list(user_data[email].keys())
        # next_chat_number = existing_chats[-1]
        # next_chat_number = int(next_chat_number[-1])
        # chat_id = f"chat_{next_chat_number}"
        
        if len(existing_chats) > 1:
            next_chat_number = existing_chats[-1]
            next_chat_number = int(next_chat_number[-1])
            chat_id = f"chat_{next_chat_number}"
        else:
            chat_id = "chat_0"
        
        print(chat_id)
        
        session['active_chat_id'] = chat_id  # Set it in session
        active_chat = session['active_chat_id']

    if chat_id not in user_data[email]:
        user_data[email][chat_id] = {
            "prompts": [],
            "extracted_data": {},
            "description": "No chat"
        }

    conversation_history = []
    # if user_data[email][chat_id]["prompts"]:
    #     conversation_history = [
    #         {"role": "user", "content": k}
    #         for k in user_data[email][chat_id]["prompts"]
    #     ]
    #     conversation_history.append({"role": "system", "content": user_data[email][chat_id]["extracted_data"]})
    # print(conversation_history)
    print(user_data[email][chat_id]["extracted_data"])

    # Initialize Groq client with API key
    client = Groq(api_key="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")

    # Set the system prompt
    system_prompt = {
        "role": "system",
        "content": f"You are a professional medical report analyst. You act as an assistant who answers questions based on this provided data: {str(user_data[email][chat_id]["extracted_data"])}."
    }
    
    # Append user message to the conversation history
    # conversation_history.append({"role": "user", "content": user_message})
    # conversation_history.append(str(user_data[email][chat_id]["extracted_data"]))

    # Get the response from Groq
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
        "role": "system",
        "content": f"You are a helpful assistant who answers questions based on this provided data: {str(user_data[email][chat_id]["extracted_data"])}."
            },
            {"role": "user", "content": user_message}
            ],
        max_tokens=1024,
        temperature=1.2
    )

    assistant_reply = response.choices[0].message.content
    
    # Update the description with the AI-generated summary
    # user_data[email][chat_id]["description"] = summary
    if user_data[email][chat_id]["description"] == "No chat":
        # if len(user_data[email][chat_id]["prompts"]) > 1:
        #     summary = generate_summary_with_ai(user_data[email][chat_id]["prompts"])
        # else:
        prompts = [{'prompt': user_message, 'response': assistant_reply}]
        summary = generate_summary_with_ai(prompts)
        
    else:
        summary = user_data[email][chat_id]["description"]
        
    update_user_data(email, chat_id, user_message, assistant_reply, user_data[email][chat_id]["extracted_data"], summary)

    return jsonify({'reply': assistant_reply}), 200





def generate_summary_with_ai(prompts):
    """Generate a three-word summary using AI."""
    # Prepare the messages for the AI model
    
    client = Groq(api_key="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")
    print(prompts)
    
    conversation_history = ' '.join([p['response'] for p in prompts])
    print(conversation_history)
    summary_response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Summarize the given text in one to three words. Your response must only be the one to three words and nothing else. Make use of some words from the given text"},
            {"role": "user", "content": conversation_history}
        ],
        max_tokens=10,  # Adjust as needed
        temperature=0.5
    )

    # Get the summary
    summary = summary_response.choices[0].message.content.strip()
    return summary




@app.route('/results_history', methods=['GET'])
def results_history():
    email = session.get('profile', {}).get('email')
    user_data_file = app.config['USER_DATA_FILE']

    try:
        with open(user_data_file, 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        if email not in user_data:
            return jsonify([]), 200

        results = [
            {
                'chat_id': chat_id,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'extracted_data': chat_data.get('extracted_data')
            }
            for chat_id, chat_data in user_data[email].items()
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/chat_history', methods=['GET'])
# def chat_history():
#     # email = session.get('profile', {}).get('email')
#     email = email_id_forjson
#     user_data_file = app.config['USER_DATA_FILE']

#     try:
#         with open(user_data_file, 'r', encoding='utf-8') as file:
#             user_data = json.load(file)

#         if email not in user_data:
#             return jsonify([]), 200

#         chats = [
#             {
#                 'chat_id': chat_id,
#                 # 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'prompts': chat_data.get('prompts')
#             }
#             for chat_id, chat_data in user_data[email].items()
#         ]
#         return jsonify(chats), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route('/chat_history', methods=['GET'])
def chat_history():
    # Use the global email variable or retrieve it from the session
    email = email_id_forjson
    user_data_file = app.config['USER_DATA_FILE']

    try:
        with open(user_data_file, 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        # If the email doesn't exist in the user data, return an empty array
        if email not in user_data:
            return jsonify([]), 200

        # Prepare the chats list with chat_id and the corresponding prompts
        chats = [
            {
                'chat_id': chat_id,
                'description': chat_data.get('description', '')
                # 'prompts': [
                #     {'prompt': p.get('prompt'), 'response': p.get('response')}
                #     for p in chat_data.get('prompts', [])
                # ],
                # 'extracted_data': chat_data.get('extracted_data', '')  # Return extracted_data as string
            }
            for chat_id, chat_data in user_data[email].items()
        ]
        print(jsonify(chats))

        return chats, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/load_chat', methods=['GET'])
def load_chat():
    global active_chat
    # Get the session ID from the query parameters
    chat_id = request.args.get('chat_id')
    print(chat_id)
    email = email_id_forjson
    user_data_file = app.config['USER_DATA_FILE']

    if not chat_id:
        return jsonify({'error': 'No chat ID provided'}), 400

    try:
        with open(user_data_file, 'r', encoding='utf-8') as file:
            user_data = json.load(file)

        if email not in user_data or chat_id not in user_data[email]:
            return jsonify({'error': 'Chat not found'}), 404

        chat_data = user_data[email][chat_id]
        
        session['active_chat_id'] = chat_id
        active_chat = session['active_chat_id']

        print(active_chat)
        
        
        # return chat_data

        return {
            'chat_id': chat_id,
            'prompts': chat_data.get('prompts', []),
            'extracted_data': chat_data.get('extracted_data', '')
        }, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
# New route to start a new chat
@app.route('/new_chat', methods=['POST'])
def new_chat():
    global active_chat
    # Determine next chat_id if not provided
    user_data_file = app.config['USER_DATA_FILE']
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)

    
    email = email_id_forjson
    existing_chats = list(user_data[email].keys())
    print(existing_chats)
    # prev_chat_number = len(existing_chats)
    # next_chat_number = len(existing_chats) + 1
    next_chat_number = existing_chats[-1]
    next_chat_number = int(next_chat_number[-1]) + 1
    print(next_chat_number)
    # prev_chat_id = f"chat_{prev_chat_number}" 
    next_chat_id = f"chat_{next_chat_number}" 
    # print(chat_id)
    
    # if chat_id not in user_data[email]:
    #     user_data[email][chat_id] = {
    #         "prompts": [],
    #         "extracted_data": {}
    #     }
    
    session['active_chat_id'] = next_chat_id
    active_chat = session['active_chat_id']
    print(active_chat)
    
    # update_user_data(email, next_chat_id, "", "", user_data[email][prev_chat_id]["extracted_data"])
    update_user_data(email, next_chat_id, "", "", "{}", "")
    
    with open(user_data_file, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
    
    chat_data = user_data[email][next_chat_id]
    print(chat_data)
    
    return {
            'chat_id': next_chat_id,
            'prompts': chat_data.get('prompts', []),
            'extracted_data': chat_data.get('extracted_data', '')
        }, 200
    
    return jsonify({'message': 'New chat started'}), 200


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
