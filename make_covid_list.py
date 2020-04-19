import json
import os
from pathlib import Path

# these are the new words and scores
english_covid_words = {
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

all_translation = json.loads(
    (
        Path(os.environ.get("HOME"))
        / Path("projects/2020/tweet_utils/data/opt_data/translations.json")
    ).read_text()
)

covid_words = {"english": english_covid_words}
translations = {"english": {x: x for x in english_covid_words.keys()}}
for lang, translation in all_translation.items():
    covid_words[lang] = dict()
    translations[lang] = dict()
    for word, scores in covid_words["english"].items():
        # if we have a translation, use it
        if word in translation:
            # we can have multiple (this is a list)
            # so loop over it
            for lang_word in translation[word]:
                if len(lang_word.split(" ")) == 1:
                    covid_words[lang][lang_word.lower()] = scores
                    translations[lang][lang_word.lower()] = word
        # keep the words even if they don't have translations
        else:
            covid_words[lang][word] = scores
            translations[lang][word] = word

for lang, lang_covid_words in covid_words.items():
    lang_translations = translations[lang]
    print("-" * 80)
    print("-" * 80)
    print(lang)
    print(lang_covid_words)
    print(lang_translations)

    words = Path("LabMT/labMTwords-" + lang + ".csv").read_text().strip().split("\n")
    scores = Path("LabMT/labMTscores-" + lang + ".csv").read_text().strip().split("\n")
    stddevs = Path("LabMT/labMTscoresStd-" + lang + ".csv").read_text().strip().split("\n")
    if os.path.isfile(Path("LabMT/labMTwordsEn-" + lang + ".csv")):
        words_en = Path("LabMT/labMTwordsEn-" + lang + ".csv").read_text().strip().split("\n")
    else:
        words_en = words
    lookup = {word: score for word, score in zip(words, scores)}
    lookup_nohashtags = {
        word: (score, stddev)
        for word, score, stddev in zip(words, scores, stddevs)
        if ((word[0] not in {"#", "@"}) and (word[:3] not in {"rt@", "#-@"}) and (word[:2] != "-@"))
    }
    lookup_nohashtags_en = {
        word: word_en
        for word, word_en in zip(words, words_en)
        if ((word[0] not in {"#", "@"}) and (word[:3] not in {"rt@", "#-@"}) and (word[:2] != "-@"))
    }
    print(
        "removed",
        len(lookup),
        "-",
        len(lookup_nohashtags),
        "=",
        len(lookup) - len(lookup_nohashtags),
        "words",
    )
    print(
        "those words are:",
        ", ".join([word for word in lookup.keys() if word not in lookup_nohashtags]),
    )

    # add the new words
    combined_nohashtag = dict()
    combined_nohashtag.update(lookup_nohashtags)
    combined_nohashtag.update(lang_covid_words)

    combined_nohashtag_en = dict()
    combined_nohashtag_en.update(lookup_nohashtags_en)
    combined_nohashtag_en.update(lang_translations)

    print(
        "with covid words, list is now",
        len(combined_nohashtag),
        "-",
        len(lookup_nohashtags),
        "=",
        len(combined_nohashtag) - len(lookup_nohashtags),
        "words longer",
    )

    for word in lang_covid_words:
        if word in lookup_nohashtags:
            print(
                "word existed already:",
                word,
                combined_nohashtag_en.get(word),
                "old score/stddev:",
                lookup_nohashtags[word],
                "new score/stddev:",
                combined_nohashtag[word],
            )

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
    words_en = list(combined_nohashtag_en.values())
    hashtags_en = list(map(lambda x: "#" + x, words_en))
    Path("labMT/labMTwordsEn-" + lang + "-covid.csv").write_text("\n".join(words_en + hashtags_en))
    Path("labMT/labMTwords-" + lang + "-v2-2020-03-28.csv").write_text("\n".join(words))
    Path("labMT/labMTscores-" + lang + "-v2-2020-03-28.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[0])), scores))
    )
    Path("labMT/labMTscoresStd-" + lang + "-v2-2020-03-28.csv").write_text(
        "\n".join(map(lambda x: "{0:.2f}".format(float(x[1])), scores))
    )
    Path("labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv").write_text("\n".join(words_en))
    # diagnostics:
    # print("wc labMT/labMTwords-" + lang + "-covid.csv")
    # print("wc labMT/labMTscores-" + lang + "-covid.csv")
    # print("head labMT/labMTwords-" + lang + "-covid.csv")
    # print("head labMT/labMTscores-" + lang + "-covid.csv")
    # print("tail labMT/labMTwords-" + lang + "-covid.csv")
    # print("tail labMT/labMTscores-" + lang + "-covid.csv")
    # print("wc labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    # print("wc labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    # print("head labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    # print("head labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    # print("tail labMT/labMTwords-" + lang + "-v2-2020-03-28.csv")
    # print("tail labMT/labMTscores-" + lang + "-v2-2020-03-28.csv")
    # if lang != "english":
    #     print("wc labMT/labMTwordsEn-" + lang + "-covid.csv")
    #     print("head labMT/labMTwordsEn-" + lang + "-covid.csv")
    #     print("tail labMT/labMTwordsEn-" + lang + "-covid.csv")
    #     print("wc labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
    #     print("head labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
    #     print("tail labMT/labMTwordsEn-" + lang + "-v2-2020-03-28.csv")
