# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 00:09:00 2021

@author: Izabele
"""

def translate_text(text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client.from_service_account_json("COVIDURLS.json")
    

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language='en')

    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
    
    return result["translatedText"]


def main():
    
    #sample_text1 = "GOBIERNO APRUEBA USO DE PLAYAS PARA REGIONES DE NIVEL MODERADO Y ALTO POR COVID-19 https://t.co/NPMJ14euK5â€¦ https://t.co/NBpkHeMFKh"
    sample_text2 = 'Pirmieji prisiminimai apie tėtį kažkodėl susiję su žvejojimu ir grybavimu – tai vienas smagiausių ne tik mudviejų, bet ir visos mūsų šeimos pomėgių.'
    
    translate_text(sample_text2)
    
main()