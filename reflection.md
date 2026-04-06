# Profile Comparison Reflections

---

## Original Profile vs. Adversarial 1 (Contradiction — energy 0.95 + mood "melancholic")

The original kpop/hype profile produces two kpop songs at the top with scores near 3.0, then a sharp drop to trap songs around 1.9. The contradiction profile (emo trap + melancholic + high energy) produces XO Tour Llif3 at 3.79 — the only song that matches all three signals — followed by pure energy matches at ~0.97. This makes sense: when a user's genre, mood, and energy all point at the same song, the system rewards it heavily. The interesting part is that #2–5 in the contradiction profile are totally unrelated genres (pop, rock, reggaeton), placed there only because their energy is close to 0.95. High-energy users get "contaminated" recommendations from genres they didn't ask for, because the energy gap is the only differentiator once genre and mood bonuses run out.

---

## Adversarial 2 (Ghost Genre) vs. Adversarial 5 (Case Mismatch)

Both profiles produce a top 5 where the genre bonus never fires, but for different reasons — one asks for a genre not in the catalog ("country"), the other asks for "KPop" when the catalog stores "kpop". The outputs look nearly identical in structure: mood wins where it can, then energy fills the rest. The case mismatch profile is the more alarming result because it's a silent failure — the user typed a valid genre that exists in the catalog, but a capitalization difference caused zero genre matches. A real recommender would normalize input before comparing; here, the user just gets worse results with no explanation of why.

---

## Adversarial 3 (Ignored Prefs) vs. Original Profile

The ignored prefs profile sets tempo, valence, danceability, acousticness, and loudness to extreme values (tempo: 999, loudness: -60) that should produce terrible matches — but the results are identical to a clean lofi/chill/0.4 profile because those keys are never read by score_song. This pair shows the gap between what the user profile *looks like* it's doing and what it actually does. The original profile also carries this problem: it has 10 keys defined but only 3 influence the score. The extra keys give a false sense of precision without changing any output.

---

## Adversarial 6 (Missing Mood) vs. Original Profile

The original profile (mood: "hype") and the missing-mood profile (mood: "sad") both target kpop, so both end up with ANTIFRAGILE and Hype Boy at the top. The scores shift slightly — missing mood drops from 2.99/2.92 to 2.94/2.97 (order flips) — because without any mood match firing, the ranking collapses to genre + energy only. "Sad" is not a mood in the catalog, so the +1.0 bonus never applies. The fact that the recommendations are nearly the same regardless of whether mood is "hype" or "sad" illustrates the filter bubble: once you're in a represented genre, mood stops mattering. The genre bonus is strong enough to make two very different emotional requests produce almost the same list.

---

## Adversarial 7 (Empty Profile) vs. Adversarial 2 (Ghost Genre)

The empty profile defaults to energy: 0.5 with no genre or mood, so the entire ranking is determined by proximity to mid-energy. The top results (Midnight Coding, Focus Flow, Coffee Shop Stories) are all low-energy lofi/jazz songs that happen to sit near 0.5. The ghost genre profile targets energy: 0.7 and mood: "happy," producing a different top 3 (Rooftop Lights, Hype Boy, Sunrise City). The comparison shows that energy target alone meaningfully shifts which songs surface — moving from 0.5 to 0.7 pulls the recommendations from calm lofi into upbeat indie pop territory. This is the one dimension where the scoring produces intuitive, continuous behavior: higher energy preference reliably shifts results toward higher-energy songs, even without any categorical matches.

---

## Adversarial 4 (Out-of-Range Energy) vs. Adversarial 8 (k > Catalog Size)

These two profiles expose infrastructure bugs rather than preference-matching problems. Profile 4 (energy: 2.0) produces negative energy scores — Storm Runner at #5 scores -0.09, and the explanation reads "energy similarity -0.09/1.0," which contradicts itself. Profile 8 (k=100) silently returns only 19 songs instead of 100, with no warning. Neither case crashes the system, which might seem fine, but both produce misleading output: one shows scores that are mathematically invalid, the other returns fewer results than requested without telling the caller. In production systems these would both require explicit error handling or input validation rather than silent degradation.
