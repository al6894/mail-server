# SecureMail

A project focused on end-to-end cryptography solutions for a mail server.

## To see the web page (not a requirement for functionality):

Install Node.js on your computer [using this link](https://nodejs.org/en).

Navigate to the frontend directory with:
`cd frontend`

Run `npm install` while inside the frontend directory to install all packages in the included packages.json

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

`pip install -r requirements.txt`

## Run the Flask app:

Navigate to the backend directory with:
`cd backend`

Then run:

```bash
python app.py
or
python3 app.py
```

## Run the local smtp server:

Navigate to the backend directory with:
`cd backend`

Then run:

```bash
python smtp.py
or
python3 smtp.py
```

All email information can be seen in the terminal running the SMTP server once sent.

## Send an email without the frontend:

Use the provided template in the backend directory, request.py, to create an email of your liking.

Run the request with:

```bash
python request.py
or
python3 request.py
```

The encrypted email can be seen in the terminal running smtp.py. A success message will be displayed in the terminal you ran the
request from.

## Run tests

All tests can be ran once you are in the backend/tests directory via:

```bash
python test_name.py
or
python3 test_name.py
```

## Notes:

The symmetric key is included in the .env file as SHARED_KEY.

The public and private keys for the sender and recipient are included in the
spublic.pem, sprivate.pem, rpublic.pem, rprivate.pem files, respectively.

The script for generating the keys is included in /backend/scripts as generate_rsa_keys.py
