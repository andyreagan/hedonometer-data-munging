from pathlib import Path

# these are the new words and scores
covid_words = {
    "corona": ("1.72", "0.97"),
    "coronavirus": ("1.34", "0.66"),
    "covid": ("1.6", "0.76"),
    "distancing": ("3.16", "1.28"),
    "epidemic": ("1.72", "0.99"),
    "kits": ("5.14", "1.14"),
    "lockdown": ("2.04", "0.90"),
    "masks": ("3.38", "1.58"),
    "ncov19": ("1.84", "1.04"),
    "outbreak": ("2.46", "1.30"),
    "pandemic": ("1.6", "1.01"),
    "quarantine": ("2.18", "1.08"),
    "quarantined": ("2.14", "1.01"),
    "sanitizer": ("5.14", "1.55"),
    "self-quarantine": ("3.14", "1.80"),
    "ventilator": ("2.98", "1.70"),
    "ventilators": ("3.26", "1.97"),
}

spanish_translation = {
    "corona": ["corona"],
    "coronavirus": ["coronavirus"],
    "covid": ["covid"],
    "distancing": ["distanciamiento"],
    "epidemic": ["epidemia"],
    "kits": ["kits"],
    "lockdown": ["encierro", "cierre", "confinamiento"],
    "masks": ["mascarilla", "cubrebocas"],
    "outbreak": ["epidemia"],
    "pandemic": ["pandemia"],
    "quarantine": ["cuarentena"],
    "quarantined": ["cuarentena"],
    "sanitizer": ["desinfectante"],
    "self-quarantine": ["autoaislamiento"],
    "ventilator": ["respirador"],
    "ventilators": ["respiradores"],
}

covid_words = {"english": covid_words, "spanish": {}}
translations = {"spanish": {}}
for word, score in covid_words["english"].items():
    if word in spanish_translation:
        for spanish_word in spanish_translation[word]:
            if len(spanish_word.split(' ')) == 1:
                covid_words["spanish"][spanish_word] = score
                translations["spanish"][spanish_word] = word


for lang in {"english", "spanish"}:
    print(lang)
    words = Path("LabMT/labMTwords-" + lang + ".csv").read_text().strip().split("\n")
    scores = Path("LabMT/labMTscores-" + lang + ".csv").read_text().strip().split("\n")
    stddevs = Path("LabMT/labMTscoresStd-" + lang + ".csv").read_text().strip().split("\n")
    if lang != "english":
        words_en = Path("LabMT/labMTwordsEn-" + lang + ".csv").read_text().strip().split("\n")
        lookup_nohashtags_en = {
            word: word_en for word, word_en in zip(words, words_en) if word[0] not in {"#", "@"}
        }
    lookup = {word: score for word, score in zip(words, scores)}
    lookup_nohashtags = {
        word: (score, stddev)
        for word, score, stddev in zip(words, scores, stddevs)
        if word[0] not in {"#", "@"}
    }
    len(lookup)  # 10222
    len(lookup_nohashtags)  # 10192
    lookup_hashtags = {
        word: (score, lookup.get(word[1:])) for word, score in zip(words, scores) if word[0] == "#"
    }  # included this output above

    for word in covid_words[lang]:
        if word in lookup_nohashtags:
            print("word exists already:", word, lookup_nohashtags[word], covid_words[lang][word])

    # add the new words
    combined_nohashtag = {}
    combined_nohashtag.update(lookup_nohashtags)
    combined_nohashtag.update(covid_words[lang])
    len(combined_nohashtag)  # 10209
    if lang != "english":
        combined_nohashtag_en = {}
        combined_nohashtag_en.update(lookup_nohashtags_en)
        combined_nohashtag_en.update(translations[lang])

    # write them out, first the nonhashtags then the hashtags
    words = list(combined_nohashtag.keys())
    hashtags = list(map(lambda x: "#" + x, combined_nohashtag.keys()))
    scores = list(combined_nohashtag.values())
    Path("labMT/labMTwords-" + lang + "-covid.csv").write_text("\n".join(words + hashtags))
    Path("labMT/labMTscores-" + lang + "-covid.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[0])), scores + scores))
    )
    Path("labMT/labMTscoresStd-" + lang + "-covid.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[1])), scores + scores))
    )
    if lang != "english":
        words_en = list(combined_nohashtag_en.values())
        hashtags_en = list(map(lambda x: "#" + x, words_en))
        Path("labMT/labMTwordsEn-" + lang + "-covid.csv").write_text(
            "\n".join(words_en + hashtags_en)
        )
    Path("labMT/labMTwords-" + lang + "-v2-2020-03-28.csv").write_text("\n".join(words))
    Path("labMT/labMTscores-" + lang + "-v2-2020-03-28.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[0])), scores))
    )
    Path("labMT/labMTscoresStd-" + lang + "-v2-2020-03-28.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[1])), scores))
    )
    if lang != "english":
        Path("labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv").write_text("\n".join(words_en))
    print("wc labMT/labMTwords-" + lang + "-covid.csv")
    print("wc labMT/labMTscores-" + lang + "-covid.csv")
    print("head labMT/labMTwords-" + lang + "-covid.csv")
    print("head labMT/labMTscores-" + lang + "-covid.csv")
    print("tail labMT/labMTwords-" + lang + "-covid.csv")
    print("tail labMT/labMTscores-" + lang + "-covid.csv")
    print("wc labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    print("wc labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    print("head labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    print("head labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    print("tail labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    print("tail labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    if lang != "english":
        print("wc labMT/labMTwordsEn-" + lang + "-covid.csv")
        print("head labMT/labMTwordsEn-" + lang + "-covid.csv")
        print("tail labMT/labMTwordsEn-" + lang + "-covid.csv")
        print("wc labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
        print("head labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
        print("tail labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
