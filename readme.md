# Live Server
- fast api
- code: backend/app
- deployed: railway.com
- URL:  http://34.122.150.197:8000/docs

# Live frontend
- streamlit
- code: backend/fronted
- deployed: cloud.google.com
- URL:  http://34.122.150.197:8501/

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
-  OPENAI_API_key
-  QDRANT_URL
-  QDRANT_API_KEY

#### Open Terminal and run following command
4. uvicorn backend.app.main:app --reload

##### - Note : Only first time It take time to download pytorch_models or safe.tensor models . Please be patient. then click on.

5. Open your browser and navigate to http://127.0.0.1:8000/docs

#### Open Another Terminal And Run the following command
6. streamlit run frontend.frontend.py
7. Open a web browser and navigate to http://127.0.0.1:8501/


#### Result should be stored in Json files of Open and Closed Source When Hadiths are submitted through routes or frontend

------------------------------------------------------------------------------


### Using Frontend

sample  Inputs


```
Asbagh bin Nabata related to me from Suhayl ibn Abu Salih from Yahya from Abu Hurayra that the Messenger of Allah, may Allah bless him and grant him peace, said,  "When you hear a man say, 'The people are ruined,' he himself is the most ruined of them all.
```

```
Yahya related to me from Malik that he had heard the people of knowledge say that when a man hit game and something else might have contributed to death, like water or an untrained dog, that game was not to be eaten unless it was beyond doubt that it was the arrow of the hunter that had killed it by reaching a vital organ, so that it did not have any life after that.
```

```
Yahya related to me from Malik that Safwan ibn Sulaym heard that the Prophet, may Allah bless him and grant him peace, said, "I and the one who guards the orphan, whether for himself or for someone else, will be like these two in the Garden, when he has taqwa," indicating his middle and index fingers.
```

```
Yahya related to me from Malik from Rabia ibn Abi Abd ar-Rahman that Muhammad ibn Ali ibn al-Husayn said, "Fatima, the daughter of the Messenger of Allah, may Allah bless him and grant him peace, weighed the hair of Hasan and Husayn, and gave away in sadaqa the equivalent weight in silver.
```