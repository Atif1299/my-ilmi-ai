# Live Server
- fast api
- code: backend/app
- deployed: railway.com
- URL:  quran-rag-backend-production.up.railway.app/docs

# Live frontend
- streamlit
- code: backend/fronted
- deployed: https://streamlit.io/cloud
- URL:  https://quran-rag-frontend-7hdwh8xq7acjkhvfsk4gqf.streamlit.app/

# Live Vector DB
- Qdrant: https://qdrant.tech/
- URL:  https://d11670de-47bc-4a14-8b3a-c495cb7dc19d.eu-central-1-0.aws.cloud.qdrant.io:6333

# Test Input Samples
- *.json

# Compile And Run

1. uv venv
2. .venv\Scripts\activate
3. uv pip install -r requirements.txt

Create .env file and set these keys in that file
-  GOOGLE_API_KEY
-  HF_TOKEN
-  OPENAI_API_key
-  QDRANT_URL
-  QDRANT_API_KEY

#### Open Terminal and run following command
4. uvicorn backend.app.main:app --reload

##### - Note : Only first time It take time to download pytorch_models or safe.tensor models . Please be patient. then click on.

5. Open your browser and navigate to http://127.0.0.1:8000/docs

#### Open Another Terminal And Run the following command
6. streamlit run backend.frontend.frontend.py
7. Open a web browser and navigate to http://127.0.0.1:8501/


#### Result should be stored in Json files of Open and Closed Source When Hadiths are submitted through routes or frontend

------------------------------------------------------------------------------


### If Using Backend Fastapi Swagger UI then sample inputs

sample 1 :


```
It was narrated from Yahya bin Bukayr, from Al-Layth, from 'Uqayl, from Ibn Shuhbah, from 'Urwah, from Aisha, that the Messenger of Allah ﷺ said: 'Whoever innovates something in this matter of ours (i.e., Islam), that is not part of it, will have it rejected.'
```

```
It was narrated from Yahya bin Bukayr, from Al-Layth, from 'Uqayl, from Ibn Shuhbah, from 'Urwah, from Aisha, that the Messenger of Allah ﷺ said: 'Whoever innovates something in this matter of ours (i.e., Islam), that is not part of it, will have it rejected.'
```