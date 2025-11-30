Where Does This Mill’s Water Come From?
A Data-Driven Analysis of Rural Idioms in Modern European Languages
Author: Tavit Nisanyan
Date: November 2025
Course: DSA210
1. Abstract
This project investigates the linguistic "fossilization" of rural culture across 10 European languages. It tests the hypothesis that languages from nations with more recent agrarian histories (e.g., Turkey, Poland) retain a significantly higher frequency of rural-themed idioms in contemporary speech compared to early-industrialized nations (e.g., UK, Germany).
Using a massive dataset of movie subtitles (374 million lines of dialogue), I performed a comparative frequency analysis of 250 verified rural proverbs. All code was written by Gemini 3.0, though the process involved significant brainstorming and error correction to reach its final stage. At the end, I believe I have uncovered truths never before considered, though significant errors still remain (explained below) which will be an easy fix for the next iteration of this project.	
2. The Dataset
	•	Source: OPUS OpenSubtitles Corpus (v2018).
	•	Scale: ~13 GB of raw text (Monolingual extraction).
	•	Scope: 10 Languages.
	•	Total Volume: ~374,000,000 sentences.
3. Methodology
My approach evolved from simple keyword counting (which failed due to polysemy) to a "Semantic Anchor" dictionary search.
	1	Data Acquisition: I wrote a custom Python script (download_opensubs_dual_mirror.py) to bypass broken mirrors and extract monolingual data from parallel Moses zip files.
	2	Lexicon Generation: I curated a "Gold Standard" list of 25 idioms per language (250 total) focusing on rural themes (shepherds, mills, harvest, livestock).
	3	Algorithm: The final miner (idiom_miner_dictionary.py) uses a "Semantic Anchor" logic. It strips stopwords and counts a hit only if >60% of the idiom's core nouns/verbs appear in a single line, allowing for morphological variation and casual speech patterns.
	4	Normalization: All counts are normalized to "Frequency Per Million Lines" (PMW) to allow direct comparison between languages of different dataset sizes.
4. Results & Analysis
The Success: Agrarian vs. Industrial
The data strongly supports the core hypothesis when comparing the primary target languages:
	•	Turkish (Agrarian History): 1,988 idioms per million lines.
	•	English (Early Industrial): 774 idioms per million lines.
	•	German (Early Industrial): 583 idioms per million lines.
Turkish speakers use rural metaphors 2.5x more frequently than English speakers and 3.4x more frequently than German speakers in movie subtitles. This suggests a strong "gravitational pull" of agrarian language in Turkish, even when the content (Hollywood movies) is modern and urban.
The Anomaly: Romance Languages
The data revealed an unexpected spike in Romance languages:
	•	Italian: 8,035/million
	•	French: 4,385/million
	•	Spanish: 4,187/million
Analysis: This likely indicates a "Cultural-Linguistic" variable I did not account for. Romance languages may simply be more metaphorical or "flowery" in general, preserving idioms longer than Germanic languages regardless of industrialization rates. Furthermore, high-frequency idioms like "Faire l'autruche" (To play the ostrich / bury head in sand) in French skewed the data significantly.
Failure Points & Limitations
	1	Encoding Mismatch (Greek & Russian): The tokenizer failed to correctly handle the native script encodings for Greek (el) and Russian (ru), resulting in near-zero returns. These languages were excluded from the final correlation graph to maintain statistical integrity.
	2	The "Un" Problem: In Turkish, the word "Un" (Flour) created false positives due to its similarity to the genitive suffix for foreign names (e.g., John'un). I implemented a capitalization filter to mitigate this, but some noise remains.
5. Future Improvements
To refine this study, I would:
	1	Implement character-set detection to properly tokenize Cyrillic and Greek scripts.
	2	Apply "Stop-Idiom" Filtering: Remove outliers like Faire l'autruche from the Romance dataset if they are determined to be too generic/common, thus isolating the truly "rural" signal.
	3	Sentiment Analysis: Analyze how these idioms are used (e.g., are they used to describe backwardness or wisdom?).
6. Repository Structure
	•	final_research_report.txt: The Results. A detailed breakdown of every idiom found and its frequency.
	•	final_idiom_stats.csv: The Data. A machine-readable CSV for statistical testing.
	•	rural_density_chart.png: The Visualization. A bar chart comparing idiom density.
	•	METHODOLOGY_LOG.txt: The Process. A personal log detailing the failures and pivots that led to the final strategy.
	•	idiom_miner_dictionary.py: The main analysis script.
	•	download_opensubs_dual_mirror.py: The data collection script.
