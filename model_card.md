# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  

**SuperCoolRecommender 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This recommender generates ranked song suggestions based on a user's stated taste profile. It assumes the user can describe their preferences in structured terms — a preferred genre, a mood word, and a numeric energy level — and that those terms map directly to how songs are labeled in the catalog. It is built for classroom exploration: the goal is to make the recommendation process transparent and testable, not to serve real listeners at scale.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Every song in the catalog gets a score based on three things: genre, mood, and energy. If a song's genre matches what the user wants, it gets 2 points — the biggest reward in the system. If the mood also matches, it gets 1 more point. Finally, the system checks how close the song's energy level is to what the user is looking for and awards up to 1 more point based on how small the gap is. All three numbers are added together and every song is ranked from highest to lowest. The top five become the recommendations, each with a short explanation of what contributed to its score. The user profile also includes preferences for tempo, danceability, acousticness, and other features, but those are not yet used in scoring.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog contains 19 songs across 14 genres including pop, kpop, lofi, trap, rock, synthwave, ambient, jazz, indie pop, rage rap, emo trap, electronic pop, reggaeton, and synth-pop. Moods represented include happy, chill, intense, relaxed, hype, moody, focused, melancholic, euphoric, and playful. No songs were added or removed. The catalog is unbalanced — lofi has 3 songs, kpop and trap have 2 each, and every other genre has exactly 1 — which means some users get more relevant candidates than others before scoring even runs. Large genres like R&B, country, metal, classical, and Latin (beyond reggaeton) are missing entirely.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best for users whose preferred genre is well-represented in the catalog and whose target energy is in the mid-to-high range (0.7–0.93), where most songs cluster. In those cases genre correctly surfaces the most relevant songs first, and energy proximity meaningfully separates candidates within the same genre. Each recommendation also comes with a plain-language explanation showing exactly which signals fired, making it easy to understand why a song ranked where it did. The system also degrades gracefully — even when no genre or mood matches exist, it still returns results ranked by energy rather than crashing.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The most significant weakness discovered through testing is that the genre bonus (+2.0 points) is so large relative to all other scoring signals that it effectively locks users into a genre bubble regardless of how well the song actually fits their taste. Because a genre match alone outweighs the maximum possible combined score from mood and energy together (2.0 vs a maximum of 2.0), two kpop songs claimed the top two spots in every test run — even when their mood did not match the user's preference at all. This means a user who primarily cares about vibe or energy level will still receive genre-first recommendations, which may not reflect what they actually want to hear. The problem is compounded by catalog imbalance: genres like kpop and lofi have multiple entries while genres like jazz and ambient have only one, so users whose taste aligns with a well-represented genre are systematically rewarded over niche-genre listeners. Removing the mood check entirely during one experiment produced nearly identical top-2 results, confirming that mood and energy are effectively decorative for users whose genre is in the catalog.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Testing used nine adversarial profiles in addition to the original kpop/hype profile, each designed to stress a specific part of the scoring logic. The original profile (genre: kpop, mood: hype, energy: 0.85) produced ANTIFRAGILE and Hype Boy at the top, which felt reasonable — but it was surprising that Hype Boy never received a mood bonus because its catalog tag is "happy," not "hype." The two songs scored almost identically for opposite reasons: ANTIFRAGILE won on pure energy proximity, Hype Boy on a slightly different energy gap, and neither ever matched the mood the user asked for.

The most surprising result came from temporarily disabling the mood check entirely. The top two recommendations did not change at all — ANTIFRAGILE and Hype Boy held their positions with identical scores. This confirmed that mood was contributing nothing to the top of the list, because the genre bonus alone was large enough to lock in the ranking. Below the top two, removing mood caused Up 2 Me (trap/hype) to fall from #3 to #5 and Blinding Lights (synth-pop/intense) to rise from #5 to #3 — two very different artists swapping places purely due to a 0.01 energy gap, which does not feel like a meaningful distinction.

The ghost genre test (genre: "country") was also revealing. With no genre match available, the scoring range collapsed from a possible 4.0 to a maximum of 2.0, and the top results were decided entirely by mood and energy proximity. This made it clear how much of the system's apparent "intelligence" depends on having the user's genre represented in the catalog at all. The out-of-range energy test (energy: 2.0) confirmed there is no input validation — negative energy scores appeared in the output without any warning, and the label still read "energy similarity -0.09/1.0," which is misleading to a user reading the explanation.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

The highest priority improvement would be expanding the catalog to cover more genres and ensuring each genre has multiple entries so the genre bonus is meaningful for a wider range of users. Alongside that, the scoring logic should be updated to use the user profile's full set of preferences — tempo, danceability, valence, acousticness, and loudness are already collected but currently ignored. Incorporating those signals would allow the system to match users to songs based on how a track actually sounds, not just its genre label. A longer-term goal would be building a profile-to-genre matching layer: rather than requiring users to name an exact genre, the system could infer likely genre preferences from their numeric preferences (e.g., high energy + high danceability + low acousticness likely maps to electronic or kpop) and use that to guide recommendations even for users whose stated genre has no catalog representation.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this recommender made it clear that the core algorithm does not have to be complex to produce results that feel reasonable — three signals and some basic arithmetic are enough to generate a ranked list that makes intuitive sense most of the time. But the more interesting lesson was realizing how much craft goes into tuning the weights. A genre bonus that is even slightly too large drowns out every other signal, and a mood check that seems useful can turn out to contribute almost nothing in practice. The real challenge in recommendation is not writing the scoring function — it is calibrating it so the system is neither so broad that genre alone decides everything, nor so narrow that only a perfect match on every field ever surfaces. That balance is genuinely difficult, and the adversarial testing made it visible in a way that just reading the code never would have.
