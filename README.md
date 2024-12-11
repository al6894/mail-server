# SecureMail

A project focused on end-to-end cryptography solutions for a mail server.

## To see the web page:

Navigate to the frontend directory with:
cd frontend

Then run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Requirements

Please install all requirements in the requirements.txt file located inside the backend directory.

pip install -r requirements.txt

## Run the Flask app:

Navigate to the backend directory with:
cd backend

Then run:
python app.py
or
python3 app.py

## Run the local smtp server:

Navigate to the backend directory with:
cd backend

Then run:
python smtp.py
or
python3 smtp.py

All email information can be seen in the terminal running the SMTP server once sent.

# Run tests

All tests can be ran once you are in the backend/tests directory via:

python test_name.py
or
python3 test_name.py

# Notes:

The symmetric key is included in the .env file as SHARED_KEY.

The public and private keys for the sender and recipient are included in the
spublic.pem, sprivate.pem, rpublic.pem, rprivate.pem files, respectively.

The script for generating the keys is included in /backend/scripts as generate_rsa_keys.py
