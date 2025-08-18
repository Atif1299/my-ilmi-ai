from langchain.prompts import PromptTemplate
from langchain.output_parsers import RegexParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import List
from ..models.query import AyahResult
load_dotenv()



def filter_relevant_ayahs(ayahs, hadith_text, llm=None, threshold=7):
    if llm is None:
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo" ,openai_api_key=os.getenv("OPENAI_API_KEY"))

    prompt = PromptTemplate(
        input_variables=["hadith", "ayah"],
        template="""
Hadith: "{hadith}"

Quranic Ayah: "{ayah}"

Only respond with a number from 1 to 10 for how closely this Ayah relates to the Hadith. Your answer must be formatted exactly like this: Score: <number>
Score:
"""
    )

    parser = RegexParser(regex=r"(\d+)", output_keys=["score"])

    chain = prompt | llm | parser

    filtered = []
    print("Total ayas before filtering : " , len(ayahs))
    for ayah in ayahs:
        ayah_text = f"{ayah.english_translation} (Surah: {ayah.surah_name_english}, Ayah: {ayah.aya_number})"
        try:
            result = chain.invoke({"hadith": hadith_text, "ayah": ayah_text})
            score = int(result["score"])
            if score >= threshold:
                filtered.append(ayah)
        except Exception as e:
            print(f"Parsing error for ayah {ayah.aya_number}: {e}")
            continue
    print("Number of filtered ayahs are : " , len(filtered))
    return filtered;




def score_all_ayahs_with_gpt(hadith_text: str, ayahs: List[AyahResult]) -> List[AyahResult]:
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo" ,openai_api_key= os.getenv("OPENAI_API_KEY"))

    prompt = PromptTemplate(
        input_variables=["hadith", "ayah"],
        template="""
Hadith: "{hadith}"

Quranic Ayah: "{ayah}"

Rate the relevance on a scale of 1 to 5, where:
1 = Not relevant
3 = Somewhat relevant
5 = Highly relevant

Only respond with a number from 1 to 5. Your answer must be formatted exactly like this: Score: <number>
Score:
"""
    )

    parser = RegexParser(regex=r"(\d+)", output_keys=["score"])
    chain = prompt | llm | parser

    for ayah in ayahs:
        ayah_text = f"{ayah.english_translation} (Surah: {ayah.surah_name_english}, Ayah: {ayah.aya_number})"
        try:
            result = chain.invoke({"hadith": hadith_text, "ayah": ayah_text})
            score = int(result["score"])
            if score in [1, 2, 3, 4, 5]:
                ayah.score = round(float(score), 2)
            else:
                ayah.score = 0.00
        except Exception as e:
            print(f"Error scoring ayah {ayah.aya_number}: {e}")
            ayah.score = 0.00
    return ayahs
